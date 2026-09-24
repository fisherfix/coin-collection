# -*- coding: utf-8 -*-
"""GK-018 精简：缩短历史背景与正反面描述。仅替换 GK-018 卡片内对应片段。"""
import re, shutil, hashlib

HTML = 'index.html'
raw = open(HTML, 'rb').read()
shutil.copy2(HTML, 'index.html.bak')
t = raw.decode('utf-8')

a = t.find('<!-- GK-018 -->')
b = t.find('<!-- BT-005 -->')
assert a > 0 and b > a
block = t[a:b]
orig_block = block

DESC_OLD_START = '<p contenteditable="true"><strong>阿加索克勒斯'
i = block.find(DESC_OLD_START)
j = block.find('</p>', i)
assert i > 0 and j > i
desc_new = ('<p contenteditable="true"><strong>阿加索克勒斯(Agathokles, BC 317-289)</strong>出身陶工,'
            '以政变夺权成为叙拉古僭主,后正式称王(ΒΑΣΙΛΕΥΣ),是西西里希腊世界抗衡迦太基的核心人物。\r\n'
            '\r\n'
            '正面为「救主」阿尔忒弥斯(Artemis Soteira)披纱头像,肩后佩箭袋;背面带翼雷霆配铭文'
            'ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」,是西部希腊世界最早的王号钱币之一。\r\n'
            '\r\n'
            '本枚 21mm/8.2g,与同型标准器吻合;铭文磨损较重,ΣΩΤΕΙΡΑ 与王号铭文系依同型标准释读,'
            'CNS II 138 与 142 的细分版别待铭文确认。</p>')
block = block[:i] + desc_new + block[j + len('</p>'):]

OBV_OLD = block[block.find('<div class="obv"'):block.find('</div>', block.find('<div class="obv"')) + 6]
obv_new = '<div class="obv" contenteditable="true">正面: 阿尔忒弥斯·索忒伊拉披纱头像向右,肩后佩箭袋;右侧铭文ΣΩΤΕΙΡΑ(磨损,依同型释读)</div>'
block = block.replace(OBV_OLD, obv_new, 1)

REV_OLD = block[block.find('<div class="rev"'):block.find('</div>', block.find('<div class="rev"')) + 6]
rev_new = '<div class="rev" contenteditable="true">反面: 带翼雷霆;铭文ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」(磨损,依同型释读)</div>'
block = block.replace(REV_OLD, rev_new, 1)

new = t[:a] + block + t[b:]
open(HTML, 'wb').write(new.encode('utf-8'))

# ===== 验证 =====
old = open('index.html.bak', 'rb').read()
ver = open(HTML, 'rb').read()
rebuilt = (t[:a] + orig_block + t[b:]).encode('utf-8')
print('其余部分逐字节一致:', rebuilt == old)
print('大小:', len(old), '->', len(ver), '| 缩减:', len(old) - len(ver), '字节')
print('CRLF/裸LF:', ver.count(b'\r\n'), '/', ver.count(b'\n') - ver.count(b'\r\n'))
print('卡片标记数:', len(re.findall(r'<!--\s*[A-Z]{2,3}-\d{3}', ver.decode('utf-8'))))
print('sha256:', hashlib.sha256(ver).hexdigest()[:16])
