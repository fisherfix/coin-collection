# -*- coding: utf-8 -*-
"""录入 GK-018：叙拉古·阿加索克勒斯 阿尔忒弥斯·索忒伊拉/带翼雷霆铜币
插入位置：<!-- GK-017 --> 卡片之后（本系列末尾）
原则：仅在锚点处切片插入，其余字节零改动。
"""
import hashlib, re, shutil

HTML = 'index.html'
NEW_ID = 'GK-018'

raw = open(HTML, 'rb').read()
shutil.copy2(HTML, 'index.html.bak')
t = raw.decode('utf-8')

a = t.find('<!-- GK-017 -->')
assert a > 0, 'GK-017 anchor not found'
end_marker = '  </div>\r\n</div>\r\n'
e = t.find(end_marker, a)
assert e > 0, 'card end not found'
e += len(end_marker)
assert 'prov-compact' in t[e-500:e], 'end position sanity check failed'

NEW_BLOCK = """<!-- GK-018 -->\r
<div class="coin-card" data-category="hellenistic" draggable="true">\r
  <div class="drag-handle">⋮⋮ 拖拽排序</div>\r
  <div class="coin-image">\r
    <span class="coin-number" contenteditable="true">GK-018</span>\r
    <span class="coin-grade" contenteditable="true">-</span>\r
    <img src="images/GK-018.jpg" alt="叙拉古·阿加索克勒斯 阿尔忒弥斯·索忒伊拉/带翼雷霆铜币" data-path="images/GK-018.jpg" onerror="this.style.display='none'">\r
    <div class="placeholder" onclick="triggerUpload(this)" style="display:none">+</div>\r
    <div class="img-overlay">\r
      <button class="img-btn" onclick="triggerUpload(this)">📷 上传图片</button>\r
      <button class="img-btn" onclick="editImgPath(this)">✏️ 路径</button>\r
    </div>\r
  </div>\r
  <div class="coin-info">\r
    <h2 class="coin-title" contenteditable="true">叙拉古·阿加索克勒斯 阿尔忒弥斯·索忒伊拉/带翼雷霆铜币</h2>\r
    <p class="coin-subtitle" contenteditable="true">SICILY · Syracuse · Agathokles · BC 317-289 (struck c. 304-289) · Artemis Soteira / Winged Thunderbolt · CNS II 138 / 142</p>\r
    <div class="coin-detail">\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">年代</div><div class="detail-value" contenteditable="true">BC 317-289（铸造约 BC 304-289）</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">面值</div><div class="detail-value" contenteditable="true">AE 青铜币</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">材质</div><div class="detail-value" contenteditable="true">Bronze 青铜 · 21mm · 8.2g</div></div>\r
      <div class="detail-item"><div class="detail-label" contenteditable="true">参考</div><div class="detail-value" contenteditable="true">CNS II 138 / 142 · SNG ANS 708 · HGC 2, 1537（同型标准参考，精确版别待铭文确认）</div></div>\r
    </div>\r
    <div class="description">\r
      <h4 contenteditable="true">📜 历史背景</h4>\r
      <p contenteditable="true"><strong>阿加索克勒斯(Agathokles, BC 317-289)</strong>是叙拉古历史上最具争议也最具野心的人物之一。他出身陶工家庭,凭借军功与政变于 BC 317 年夺取叙拉古政权,随后成为西西里希腊世界对抗迦太基的核心力量——曾率军远征北非,一度兵临迦太基城下;晚年正式采用<strong>「王」(BAΣIΛEYΣ)</strong>的称号,是西西里希腊城邦中最早称王者。西西里在古典时代是希腊人与迦太基人反复争夺的前线,叙拉古长期扮演希腊世界西部屏障的角色,阿加索克勒斯的军政生涯正是这一格局的顶点。\r
\r
本枚属其青铜币中的经典一类:正面为<strong>阿尔忒弥斯·索忒伊拉(Artemis Soteira,「救主阿尔忒弥斯」)</strong>披纱头像,发髻束于脑后,肩后佩箭袋。Soteira「救主」是叙拉古人赋予守护女神的尊称,与城邦的护佑职能紧密相关。背面<strong>带翼雷霆(winged thunderbolt)</strong>是宙斯神力的象征,在这套币中被用作王权的宣示,与背面铭文 ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」相配——这套币也是西部希腊世界最早带有正式王号的钱币之一,标志着希腊化时代君主制在西方的落地。\r
\r
<strong>本枚实物品相说明</strong>:直径 21mm、重 8.2g,与同型标准器(21-23mm、约 8-10g)吻合,图案主体(头像轮廓、带翼雷霆)可辨;两面粉末铭文磨损较重,正面 ΣΩΤΕΙΡΑ 与背面 ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ 系依同型标准释读,本枚仅存部分残余笔划。参考编号 CNS II 138 与 142 属同一类型下的细分版别(取决于正面铭文位置与箭袋细节),本枚因铭文磨损暂无法区分,故并列记录、标注待确认。</p>\r
    </div>\r
    <div class="obv-rev">\r
      <div class="obv" contenteditable="true">正面: 阿尔忒弥斯·索忒伊拉(Artemis Soteira)披纱头像向右,发髻束于脑后,肩后佩箭袋;右侧铭文ΣΩΤΕΙΡΑ(同型标准释读,本枚磨损仅见残余)</div>\r
      <div class="rev" contenteditable="true">反面: 带翼雷霆(winged thunderbolt);周围铭文ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」(同型标准释读,本枚磨损较重)</div>\r
    </div>\r
    <span class="tag" contenteditable="true">古希腊</span><span class="tag" contenteditable="true">希腊化</span><span class="tag" contenteditable="true">Sicily</span><span class="tag" contenteditable="true">西西里</span><span class="tag" contenteditable="true">叙拉古</span><span class="tag" contenteditable="true">Syracuse</span><span class="tag" contenteditable="true">阿加索克勒斯</span><span class="tag" contenteditable="true">Agathokles</span><span class="tag" contenteditable="true">阿尔忒弥斯</span><span class="tag" contenteditable="true">Artemis Soteira</span><span class="tag" contenteditable="true">带翼雷霆</span><span class="tag" contenteditable="true">Thunderbolt</span><span class="tag" contenteditable="true">王号币</span><span class="tag" contenteditable="true">青铜</span><span class="tag" contenteditable="true">Bronze</span><span class="tag" contenteditable="true">CNS II 138/142</span><span class="tag" contenteditable="true">HGC 2 1537</span><span class="tag" contenteditable="true">BC 317-289</span>\r
    <div class="bottom-row">\r
      <div><div class="price-value" contenteditable="true">¥683</div><div class="price-label" contenteditable="true">成交价</div></div>\r
      <div class="prov-compact" contenteditable="true"><strong>星盘世界钱币</strong> · 2026-08-23</div>\r
    </div>\r
  </div>\r
</div>\r
\r
\r
"""

new = t[:e] + NEW_BLOCK + t[e:]
open(HTML, 'wb').write(new.encode('utf-8'))

# ===== 字节级验证 =====
old = open('index.html.bak', 'rb').read()
ver = open(HTML, 'rb').read()
nb = NEW_BLOCK.encode('utf-8')
stripped = ver.replace(nb, b'', 1)   # 从新文件中精确移除插入块
print('插入前字节:', len(old), '→ 插入后:', len(ver), '| 净增:', len(ver) - len(old))
print('新块字节数:', len(nb), '| 净增==新块:', len(ver) - len(old) == len(nb))
print('移除新块后与插入前逐字节相同:', stripped == old)
print('新块在文件中出现次数:', ver.count(nb))
ids = re.findall(r'<!--\s*([A-Z]{2,3}-\d{3})\s*-->', ver.decode('utf-8'))
print('标记卡片数:', len(ids))
k = ids.index('GK-018')
print('GK-018 位置:', k, '| 前:', ids[k-1], '| 后:', ids[k+1] if k+1 < len(ids) else '(末尾)')
print('BOM:', ver[:3] == b'\xef\xbb\xbf', '| CRLF/裸LF:', ver.count(b'\r\n'), '/', ver.count(b'\n') - ver.count(b'\r\n'))
print('sha256:', hashlib.sha256(ver).hexdigest()[:16])
