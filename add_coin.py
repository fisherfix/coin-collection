#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
add_coin.py v2 — 钱币卡片录入工具（隔离模式）

【核心原则】
- 录入新藏品时，已确认卡片不可变（immutable）
- 找到标记位置 → 切片插入 → 原子写
- 绝不用「读全文 → 改 → 写全文」的方式
- 每次写入前自动备份 index.html.bak
- 写入后做字节级验证：已有卡片字节必须完全保持

【用法】
1. 修改下方 coins 列表
2. 运行：python add_coin.py
3. 系统自动：备份 → 切片插入 → 验证 → 报告

【标记】
- 插入位置：</div><!-- end coin-grid -->
- 缺少此标记时拒绝运行（避免错误位置插入）
"""

import os
import sys
import io
import hashlib
import shutil

# Windows console 默认为 GBK，强制切到 UTF-8 以正确打印中文/emoji
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ============ 配置区域：录入新币 ============
# 每枚新币按以下结构添加。已确认卡片不要修改。
coins = [
    {
        "number": "ROM-005",
        "image": "images/ROM-005.jpg",
        "grade": "VF",
        "title": "君士坦丁一世追思币",
        "subtitle": "DIVVS CONSTANTINVS PT AVGG · VENERANDA MEMORIA",
        "era": "AD 337-340",
        "denomination": "AE2 / Nummus 青铜币",
        "material": "Bronze 青铜 · 16mm · 2.18g",
        "reference": "—",
        "description": "公元337年5月22日，君士坦丁大帝（Constantinus I，公元306-337年在位）在尼科米底亚驾崩，结束了对罗马帝国近三十年的统治。这位在位期间颁布《米兰敕令》（313年）、召开尼西亚公会议（325年）、迁都博斯普鲁斯海峡并以「新罗马」命名新都的皇帝，是罗马世界最具变革意义的统治者之一。\n\n君士坦丁驾崩后，其三位子嗣——君士坦丁二世、君士坦提乌斯二世、君士坦斯——共同继承帝位，史称「三兄共治」（337-340年）。按照罗马传统，前任皇帝在驾崩后即被元老院封神（Consecratio），纳入罗马神祇之列并享有祭祀。新任诸帝随即在各大造币厂发行追思币（Memorial Issue / Divus Issue），纪念亡父之「成神」，并以铭文宣告其「诸帝之父」（Pater Augustorum）的崇高地位。\n\n此枚追思币为君士坦提乌斯二世（Constantius II，公元337-361年在位）在位初期所发行。正面铭文「DV CONSTANTINVS PT AVGG」——意即「神化君主君士坦丁，诸帝之父」——其中「PT」（Pater，之父）是追思币特有的称号，标明逝者为在位诸帝之父。戴维露姆面纱（velum）的半身像表明君士坦丁已被纳入神之行列。**特别值得关注的是正面铭文采用「DV」而非常见的「DN」（Dominus Noster，吾主）**——此或为特定造币厂之变体写法，亦可能因实物磨损导致字母辨识存疑，故仍以实物记录为准。\n\n背面的「VN-MR」铭文实为「Veneranda Memoria」（应受崇敬之记忆）之缩写，是君士坦丁追思币中**特殊变体类型**之一。相较于更为常见的「CONS（Consecratio）」型封神图案（祭坛配阶梯），VN-MR型以**戴面纱穿托加的君士坦丁站姿全身像**为核心，配合「应受崇敬之记忆」的铭文，传达对已故君主的永恒怀念。底注「CONST」指示该币铸造于**君士坦丁堡造币厂**（Constantinople Mint），即君士坦丁大帝亲手建立的新都城。",
        "obverse": "正面: 戴维露姆面纱的君士坦丁一世半身像向右 · 铭文 DV CONSTANTINVS PT AVGG（神化君主君士坦丁，诸帝之父）",
        "reverse": "背面: 君士坦丁穿托加盖头之站姿全身像 · 铭文 VN - MR（Veneranda Memoria 应受崇敬之记忆）· 底注 CONST（君士坦丁堡造币厂）",
        "tags": ["罗马帝国", "君士坦丁一世", "Divus", "追思币", "封神", "Consecratio", "君士坦提乌斯二世", "VN-MR", "Veneranda Memoria", "君士坦丁堡", "4世纪", "晚期罗马", "三兄共治"],
        "price": "¥100",
        "provenance": "<strong>西西里晚祷</strong> · 私洽 · 2025-01",
        "category": "roman",
    },
]
# ============ 以下逻辑固定，无需修改 ============

BASE_DIR = r"C:\Users\zhaojingyun\.qclaw\workspace-agent-d8b9b18a\coin-collection"
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
BAK_PATH = os.path.join(BASE_DIR, "index.html.bak")
TMP_PATH = os.path.join(BASE_DIR, "index.html.tmp")
MARKER = "</div><!-- end coin-grid -->"


def card_fingerprint(card_html):
    """计算一张卡片 HTML 的 SHA-256 指纹"""
    return hashlib.sha256(card_html.encode("utf-8")).hexdigest()


def extract_existing_cards(content):
    """提取所有已确认卡片的指纹列表（按出现顺序）"""
    import re
    # 匹配所有 <!-- XXX-XXX --> 或 <!-- XXX-XXX 批量组 --> 注释
    comments = list(re.finditer(r'<!-- ([A-Z]+-\d+[^>]*?) -->', content))
    cards = []
    for i, m in enumerate(comments):
        start = m.start()
        end = comments[i + 1].start() if i + 1 < len(comments) else content.find('</div><!-- end coin-grid -->', start)
        if end == -1:
            end = len(content)
        # 截取该卡片块
        block = content[start:end].strip()
        cards.append((m.group(1), card_fingerprint(block)))
    return cards


def generate_card(coin):
    """生成单张卡片 HTML（与已确认卡片完全一致的模板）"""
    tags_html = "".join(
        [f'<span class="tag" contenteditable="true">{tag}</span>' for tag in coin["tags"]]
    )

    card = f'''
<!-- {coin["number"]} -->
<div class="coin-card" data-category="{coin["category"]}" draggable="true">
  <div class="drag-handle">⠿ 拖拽排序</div>
  <div class="coin-image">
    <span class="coin-number" contenteditable="true">{coin["number"]}</span>
    <span class="coin-grade" contenteditable="true">{coin["grade"]}</span>
    <img src="{coin["image"]}" alt="{coin["title"]}" data-path="{coin["image"]}" onerror="this.style.display='none'">
    <div class="placeholder" onclick="triggerUpload(this)" style="display:none">🪙</div>
    <div class="img-overlay">
      <button class="img-btn" onclick="triggerUpload(this)">📷 上传图片</button>
      <button class="img-btn" onclick="editImgPath(this)">🔗 改路径</button>
    </div>
  </div>
  <div class="coin-info">
    <h2 class="coin-title" contenteditable="true">{coin["title"]}</h2>
    <p class="coin-subtitle" contenteditable="true">{coin["subtitle"]}</p>
    <div class="coin-detail">
      <div class="detail-item"><div class="detail-label" contenteditable="true">年代</div><div class="detail-value" contenteditable="true">{coin["era"]}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">面值</div><div class="detail-value" contenteditable="true">{coin["denomination"]}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">材质</div><div class="detail-value" contenteditable="true">{coin["material"]}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">参考</div><div class="detail-value" contenteditable="true">{coin["reference"]}</div></div>
    </div>
    <div class="description">
      <h4 contenteditable="true">📜 历史背景</h4>
      <p contenteditable="true">{coin["description"]}</p>
    </div>
    <div class="obv-rev">
      <div class="obv" contenteditable="true">{coin["obverse"]}</div>
      <div class="rev" contenteditable="true">{coin["reverse"]}</div>
    </div>
    {tags_html}
    <div class="bottom-row">
      <div><div class="price-value" contenteditable="true">{coin["price"]}</div><div class="price-label" contenteditable="true">成交价</div></div>
      <div class="prov-compact" contenteditable="true">{coin["provenance"]}</div>
    </div>
  </div>
</div>
'''
    return card


def verify_isolation(before_content, after_content, expected_new_count):
    """验证：插入新卡片后，已有卡片字节完全保持"""
    before_cards = extract_existing_cards(before_content)
    after_cards = extract_existing_cards(after_content)

    if len(after_cards) != len(before_cards) + expected_new_count:
        return False, f"卡片数量异常：{len(before_cards)} → {len(after_cards)}（预期 +{expected_new_count}）"

    # 验证每张已有卡片在插入前后字节完全相同
    for (name, before_fp), (name2, after_fp) in zip(before_cards, after_cards[:len(before_cards)]):
        if name != name2 or before_fp != after_fp:
            return False, f"已有卡片被改动：{name}（指纹 {before_fp[:8]} → {after_fp[:8]}）"

    return True, f"已验证 {len(before_cards)} 张已有卡片字节完全保持"


def insert_coins():
    """主流程：备份 → 验证 → 切片插入 → 验证 → 写回"""
    if not coins:
        print("⚠️  coins 列表为空，请在脚本顶部添加钱币数据")
        return False

    if not os.path.exists(INDEX_PATH):
        print(f"❌ 错误：{INDEX_PATH} 不存在")
        return False

    # 1. 读取原文（UTF-8 with BOM）
    with open(INDEX_PATH, "r", encoding="utf-8-sig", newline="\n") as f:
        before_content = f.read()

    # 2. 验证编码
    if not before_content:
        print("❌ 错误：index.html 为空")
        return False

    # 3. 定位插入标记
    marker_idx = before_content.find(MARKER)
    if marker_idx == -1:
        print(f"❌ 错误：未找到插入标记 `{MARKER}`")
        print(f"   请在 index.html 中先补上此标记（应位于所有卡片之后、</div> 之前）")
        return False

    # 4. 备份
    shutil.copy2(INDEX_PATH, BAK_PATH)
    print(f"📦 已备份到 {BAK_PATH}")

    # 5. 切片插入
    cards_html = "".join([generate_card(coin) for coin in coins])
    new_content = (
        before_content[:marker_idx]
        + cards_html
        + "\n"
        + before_content[marker_idx:]
    )

    # 6. 验证隔离（这一步必须在写入前做，发现问题立即回滚）
    ok, msg = verify_isolation(before_content, new_content, len(coins))
    if not ok:
        print(f"❌ 隔离验证失败：{msg}")
        print(f"   已回滚，请检查后重试")
        return False
    print(f"✓ 隔离验证：{msg}")

    # 7. 原子写（先写临时文件，再替换）
    with open(TMP_PATH, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(new_content)

    # 8. 替换
    os.replace(TMP_PATH, INDEX_PATH)
    print(f"✓ 原子写完成")

    # 9. 二次验证（读取写入后的文件，再做一次指纹对比）
    with open(INDEX_PATH, "r", encoding="utf-8-sig", newline="\n") as f:
        final_content = f.read()
    ok2, msg2 = verify_isolation(before_content, final_content, len(coins))
    if not ok2:
        # 严重：磁盘上的文件被破坏！立即回滚
        print(f"❌ 二次验证失败：{msg2}")
        print(f"   紧急回滚到备份！")
        shutil.copy2(BAK_PATH, INDEX_PATH)
        return False
    print(f"✓ 二次验证：{msg2}")

    # 10. 报告
    final_size = os.path.getsize(INDEX_PATH)
    print(f"\n✅ 成功插入 {len(coins)} 枚钱币：")
    for coin in coins:
        print(f"   - {coin['number']}: {coin['title']}")
    print(f"\n文件大小: {final_size} 字节")
    print(f"备份位置: {BAK_PATH}")
    print(f"\n💡 下一步：")
    print(f"   1. 浏览器刷新查看效果")
    print(f"   2. 确认无误后：`git add index.html && git commit -m 'add {len(coins)} new coin(s)'`")
    print(f"   3. 如有问题：`node protect.js check` 查看状态，`cp {BAK_PATH} {INDEX_PATH}` 回滚")
    return True


if __name__ == "__main__":
    success = insert_coins()
    sys.exit(0 if success else 1)
