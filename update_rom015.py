# -*- coding: utf-8 -*-
"""ROM-015 学术定级补全：默西亚·维米纳库姆 图拉真·德西乌斯
原则：仅替换 <!-- ROM-015 --> 至 <!-- UK-001 --> 之间的切片，其余字节零改动。
"""
import hashlib, re, shutil

HTML = 'index.html'
NEW_ID = 'ROM-015'

raw = open(HTML, 'rb').read()
shutil.copy2(HTML, 'index.html.bak')
t = raw.decode('utf-8')

i = t.find('<!-- ROM-015 -->')
j = t.find('<!-- UK-001 -->')
assert i > 0 and j > i, 'marker not found'
old_block = t[i:j]

NEW_BLOCK = """<!-- ROM-015 -->\r
<div class="coin-card" data-category="roman" draggable="true">\r
  <div class="drag-handle">⠿ 拖拽排序</div>\r
  <div class="coin-image">\r
    <span class="coin-number" contenteditable="true">ROM-015</span>\r
    <span class="coin-grade" contenteditable="true">-</span>\r
    <img src="images/ROM-015.jpg" alt="罗马行省 维米纳库姆 图拉真·德西乌斯 铜币" data-path="images/ROM-015.jpg" onerror="this.style.display='none'">\r
    <div class="placeholder" onclick="triggerUpload(this)" style="display:none">🪙</div>\r
    <div class="img-overlay">\r
      <button class="img-btn" onclick="triggerUpload(this)">📷 上传图片</button>\r
      <button class="img-btn" onclick="editImgPath(this)">🔗 改路径</button>\r
    </div>\r
  </div>\r
  <div class="coin-info">\r
    <h2 class="coin-title" contenteditable="true">罗马行省·上默西亚 维米纳库姆 图拉真·德西乌斯 铜币</h2>\r
    <p class="coin-subtitle" contenteditable="true">MOESIA SUPERIOR · VIMINACIUM · Trajan Decius · AD 249-251</p>\r
    <div class="coin-detail">\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">年代</div><div class="detail-value" contenteditable="true">AD 249-251（AN XII = AD 250/251）</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">面值</div><div class="detail-value" contenteditable="true">AE 行省铜币</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">材质</div><div class="detail-value" contenteditable="true">Bronze 青铜 · 25.5mm · 7.85g</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">参考</div><div class="detail-value" contenteditable="true">RPC IX 12 / 17 / 21-23（精确版别待铭文确认）</div></div>\r
    </div>\r
    <div class="description">\r
      <h4 contenteditable="true">📜 历史背景</h4>\r
      <p contenteditable="true">罗马行省铜币(Roman Provincial AE)。行省币是罗马帝国授权各行省城市自行打制的流通货币,正面沿用皇帝肖像与拉丁铭文,背面保留城名与地方象征,是研究帝国地方治理与城市认同的重要实物。\r
\r
维米纳库姆(Viminacium)位于上默西亚行省(今塞尔维亚境内),是帝国早期重要的殖民城市与军团驻地。AD 239 年获殖民市地位(P M S COL VIM = Provinciae Moesiae Superioris Colonia Viminacium)后自行打制铜币,以"默西亚化身立于公牛与狮子之间"为标志性背面——公牛与狮子分别象征多瑙河两岸的默西亚军事力量。币面纪年 AN XII 为殖民纪年第十二年,对应 AD 250/251。\r
\r
本枚正面为图拉真·德西乌斯(Trajan Decius, AD 249-251)桂冠、披袍执甲半身像向右;反面为 P M S COL VIM · AN XII 铭文环绕默西亚化身立像向左,两侧伴以公牛(左)与狮子(右)。参考编号依 RPC IX,精确版别待铭文进一步确认后可细化。</p>\r
    </div>\r
    <div class="obv-rev">\r
      <div class="obv" contenteditable="true">正面: 桂冠、披袍执甲半身像向右(图拉真·德西乌斯);周围环绕铭文</div>\r
      <div class="rev" contenteditable="true">反面: P M S COL VIM, AN XII;默西亚化身立像向左,两侧公牛与狮子</div>\r
    </div>\r
    <span class="tag" contenteditable="true">古罗马</span><span class="tag" contenteditable="true">罗马行省</span><span class="tag" contenteditable="true">维米纳库姆</span><span class="tag" contenteditable="true">图拉真·德西乌斯</span><span class="tag" contenteditable="true">铜币</span><span class="tag" contenteditable="true">Bronze</span>\r
    <div class="bottom-row">\r
      <div><div class="price-value" contenteditable="true">¥120</div><div class="price-label" contenteditable="true">成交价</div></div>\r
      <div class="prov-compact" contenteditable="true"><strong>琋语集藏</strong> · 2026-08-09</div>\r
    </div>\r
  </div>\r
</div>\r
\r
\r
"""

new = t[:i] + NEW_BLOCK + t[j:]
data = new.encode('utf-8')
open(HTML, 'wb').write(data)

# ===== 字节级验证 =====
old = open('index.html.bak', 'rb').read()
ver = open(HTML, 'rb').read()
ids = re.findall(r'<!--\s*([A-Z]{2,3}-\d{3})\s*-->', ver.decode('utf-8'))
print('卡片总数:', len(ids))
# 重建旧文件（把新块换回旧块）应与备份逐字节一致
rebuilt = (t[:i] + old_block + t[j:]).encode('utf-8')
print('除 ROM-015 外逐字节一致:', rebuilt == old)
print('BOM 保持:', ver[:3] == b'\xef\xbb\xbf')
print('CRLF/裸LF:', ver.count(b'\r\n'), '/', ver.count(b'\n') - ver.count(b'\r\n'))
print('大小:', len(old), '->', len(ver))
print('sha256:', hashlib.sha256(ver).hexdigest()[:16])
