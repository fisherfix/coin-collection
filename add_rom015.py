# -*- coding: utf-8 -*-
"""录入 ROM-015：罗马行省铜币（归属待考）
标准：切片插入，绝不整文件重写；已有卡片字节必须完全不变。
"""
import shutil, re, io, os, hashlib

HTML = 'index.html'
NEW_ID = 'ROM-015'

CARD = '''<!-- ROM-015 -->
<div class="coin-card" data-category="roman" draggable="true">
  <div class="drag-handle">⠿ 拖拽排序</div>
  <div class="coin-image">
    <span class="coin-number" contenteditable="true">ROM-015</span>
    <span class="coin-grade" contenteditable="true">-</span>
    <img src="images/ROM-015.jpg" alt="罗马行省 芒冠蓄须头像 铜币" data-path="images/ROM-015.jpg" onerror="this.style.display='none'">
    <div class="placeholder" onclick="triggerUpload(this)" style="display:none">🪙</div>
    <div class="img-overlay">
      <button class="img-btn" onclick="triggerUpload(this)">📷 上传图片</button>
      <button class="img-btn" onclick="editImgPath(this)">🔗 改路径</button>
    </div>
  </div>
  <div class="coin-info">
    <h2 class="coin-title" contenteditable="true">罗马行省·芒冠蓄须头像 铜币（归属待考）</h2>
    <p class="coin-subtitle" contenteditable="true">ROMAN PROVINCIAL · AE · Radiate Bearded Bust / Standing Figure · Attribution Pending</p>
    <div class="coin-detail">
      <div class="detail-item"><div class="detail-label" contenteditable="true">年代</div><div class="detail-value" contenteditable="true">待考</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">面值</div><div class="detail-value" contenteditable="true">AE 行省铜币</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">材质</div><div class="detail-value" contenteditable="true">Bronze 青铜 · 25.5mm · 7.85g</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">参考</div><div class="detail-value" contenteditable="true">—</div></div>
    </div>
    <div class="description">
      <h4 contenteditable="true">📜 历史背景</h4>
      <p contenteditable="true">罗马行省铜币(Roman Provincial AE)。行省币是罗马帝国授权各行省城市自行打制的流通货币,与罗马本土造币厂发行的币种并行流通。其典型特征是正面沿用皇帝肖像与拉丁铭文,背面保留希腊语城名与地方神祇、城市象征——同一枚币上并存两种语言与两套图像体系,这是行省币最鲜明的辨识特征,也是研究帝国地方治理与城市认同的重要实物。

本枚为铜质,直径 25.5mm、重 7.85g,属行省币中等规格。正面为蓄须男性头像向右,头戴芒冠(radiate);背面为站立人像,周围与底部有铭文行。因币面磨损较重,皇帝归属、发行城市与背面神祇名称均无法可靠释读,故年代与参考编号暂记「待考」。

后续若取得拍卖方标注、同版清晰图录或可靠参考编号,可据此补全归属。按本库原则,未确认的归属不写入卡片,以免形成错误档案。</p>
    </div>
    <div class="obv-rev">
      <div class="obv" contenteditable="true">正面: 蓄须男性头像向右,头戴芒冠;周围环绕铭文(磨损,不可释读)</div>
      <div class="rev" contenteditable="true">反面: 站立人像,周围及底部铭文行(磨损,不可释读)</div>
    </div>
    <span class="tag" contenteditable="true">古罗马</span><span class="tag" contenteditable="true">罗马行省</span><span class="tag" contenteditable="true">行省铜币</span><span class="tag" contenteditable="true">铜币</span><span class="tag" contenteditable="true">Bronze</span><span class="tag" contenteditable="true">待考</span>
    <div class="bottom-row">
      <div><div class="price-value" contenteditable="true">¥120</div><div class="price-label" contenteditable="true">成交价</div></div>
      <div class="prov-compact" contenteditable="true"><strong>琋语集藏</strong> · 2026-08-09</div>
    </div>
  </div>
</div>
'''

def read_html(path):
    return open(path, 'rb').read().decode('utf-8-sig')

def cards_of(text):
    """按注释标记切出所有卡片的 (id, 卡片HTML) 映射"""
    marks = [(m.start(), m.group(1)) for m in re.finditer(r'<!--\s*([A-Z]{2,3}-\d{3})\s*-->', text)]
    out = {}
    for i, (start, cid) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else text.find('</div><!-- end coin-grid -->')
        out[cid] = text[start:nxt]
    return out

old = read_html(HTML)
# 统一按 CRLF 写入新卡片（沿用主文件行尾，不改变全文行尾风格）
card = CARD.replace('\r\n', '\n').replace('\n', '\r\n')

anchor = '<!-- UK-001 -->'
pos = old.find(anchor)
assert pos > 0, '未找到插入锚点'

missing = [i for i in [NEW_ID] if f'<!-- {NEW_ID} -->' in old]
assert not missing, f'{NEW_ID} 已存在，拒绝重复插入'

# 备份
shutil.copy2(HTML, HTML + '.bak')
new = old[:pos] + card + '\r\n\r\n' + old[pos:]

# 写回（保持无 BOM + CRLF，与当前文件一致）
with io.open(HTML, 'w', encoding='utf-8', newline='') as fp:
    fp.write(new)

# ===== 验证 =====
ver = read_html(HTML)
old_cards, new_cards = cards_of(old), cards_of(ver)
changed = [k for k in old_cards if old_cards[k] != new_cards.get(k)]
print('已有卡片数:', len(old_cards), '→', len(new_cards))
print('字节级校验: 变化的已有卡片 =', changed if changed else '无（全部保持原字节）')
# 严格校验：从新文件移除插入块后，必须与旧文件逐字节相同
stripped = ver.replace(card + '\r\n\r\n', '', 1)
print('严格校验(移除新卡后与旧文件完全一致):', stripped == old)
print('新卡片已插入:', f'<!-- {NEW_ID} -->' in ver)
ids = re.findall(r'<!--\s*([A-Z]{2,3}-\d{3})\s*-->', ver)
print('ROM-015 位置:', ids.index('ROM-015'), '/ 总数', len(ids), '| 前:', ids[ids.index('ROM-015')-1], '| 后:', ids[ids.index('ROM-015')+1])
print('文件大小:', len(old), '→', len(ver))
print('新文件 sha256:', hashlib.sha256(ver.encode('utf-8')).hexdigest()[:16])
