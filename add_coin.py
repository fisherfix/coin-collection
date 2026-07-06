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
        "number": "GK-012",
        "image": "images/GK-012.jpg",
        "grade": "VF",
        "title": "塞琉古帝国塞琉古一世铜币",
        "subtitle": "SELEUCID EMPIRE · ELEPHANT & BUCERAS",
        "era": "公元前312-前281年",
        "denomination": "Chalkous 铜币",
        "material": "Bronze 青铜 · 22mm · 6.42g",
        "reference": "—",
        "description": "公元前323年亚历山大大帝骤然离世，其帝国随即陷入继业者战争（War of the Diadochi）。塞琉古（Seleucus）作为亚历山大的近身护卫官，于公元前321年被迫流亡埃及。公元前312年，在托勒密一世的支持下，塞琉古重返巴比伦，宣布独立，开启了塞琉古帝国长达两百余年的统治，是年便成为塞琉古纪元的元年。公元前301年伊普苏斯战役（Battle of Ipsus），塞琉古与利西马科斯（Lysimachus）联手击败安提柯（Antigonus），瓜分亚历山大帝国的东部版图，塞琉古一跃成为从安纳托利亚延伸至印度的庞大帝国之君，领土面积仅次于孔雀王朝印度。\n\n阿帕美亚（Apamaea on the Orontes）位于奥隆特斯河畔，是塞琉古帝国最繁华的城市之一，以其母——塞琉古一世之妻阿帕美亚（Apama）命名，与安条克、塞琉西亚并列为帝国三大都城。\n\n此币正面亚洲象向右行走，象征塞琉古从印度孔雀王朝君主旃陀罗笈多（Chandragupta）手中换取的五百头战象，这些战象是伊普苏斯战役决定性胜利的关键；背面戴牛角之马头为布克法罗斯（Bucephalus）的形象，据传是亚历山大大帝的传奇坐骑，塞琉古以布克法罗斯自比，昭示其作为亚历山大正统继承人的身份；船锚则暗指塞琉古大腿根部形似锚状的胎记，同时也象征其祖先尼卡托尔（Nicator，意为「胜利者」）作为亚历山大海军指挥官与腓力二世时期的海军将领之出身，将希腊世界的海上传统与新帝国紧紧相连。",
        "obverse": "正面: 亚洲象向右行走 · 体态健壮 · 背上驮有辎重",
        "reverse": "背面: 戴牛角之马头向右 · 下方船锚 ⚓ · 铭文 ΒΑΣΙΛΕΩΣ ΣΕΛΕΥΚΟΥ",
        "tags": ["塞琉古", "塞琉古一世", "胜利者", "Nikator", "亚洲象", "布克法罗斯", "Bucephalus", "阿帕美亚", "伊普苏斯", "继业者战争", "船锚"],
        "price": "¥360",
        "provenance": "<strong>西西里晚祷</strong> · 私洽 · 2025-03",
        "category": "greek",
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
