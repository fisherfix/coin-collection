# -*- coding: utf-8 -*-
"""GK-018 描述定稿：保留有用史实，删除重复表述。"""
import re, shutil, hashlib

HTML = 'index.html'
raw = open(HTML, 'rb').read()
shutil.copy2(HTML, 'index.html.bak')
t = raw.decode('utf-8')

a = t.find('<!-- GK-018 -->')
b = t.find('<!-- BT-005 -->')
assert a > 0 and b > a
block = t[a:b]
orig = block

# 1) 历史背景
i = block.find('<p contenteditable="true"><strong>阿加索克勒斯')
j = block.find('</p>', i)
assert i > 0 and j > i
desc_new = ('<p contenteditable="true"><strong>阿加索克勒斯(Agathokles, BC 317-289)</strong>出身陶工家庭,'
            '以军功与政变夺取叙拉古政权,长期领导西西里希腊人抗击迦太基,曾率军远征北非、兵临迦太基城下;'
            '晚年正式称王(ΒΑΣΙΛΕΥΣ),是西西里最早称王的君主。\r\n'
            '\r\n'
            '本枚正面为「救主」阿尔忒弥斯(Artemis Soteira)披纱头像,肩后佩箭袋,铭文ΣΩΤΕΙΡΑ——'
            '该尊称体现女神的城邦护佑职能;背面带翼雷霆象征宙斯神力,配铭文ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ'
            '「阿加索克勒斯王」。这套币是西部希腊世界最早带正式王号的钱币之一,见证了希腊化王权在西西里的确立。\r\n'
            '\r\n'
            '本枚 21mm/8.2g,与同型标准器(AE21-23、8-10g)吻合;两面粉末铭文磨损较重、仅存部分笔划,'
            'CNS II 138 与 142 的细分版别待铭文确认。</p>')
block = block[:i] + desc_new + block[j + len('</p>'):]

# 2) 正反面：去掉重复的磨损注
OBV_OLD = block[block.find('<div class="obv"'):block.find('</div>', block.find('<div class="obv"')) + 6]
block = block.replace(OBV_OLD, '<div class="obv" contenteditable="true">正面: 阿尔忒弥斯·索忒伊拉披纱头像向右,肩后佩箭袋;右侧铭文ΣΩΤΕΙΡΑ</div>', 1)
REV_OLD = block[block.find('<div class="rev"'):block.find('</div>', block.find('<div class="rev"')) + 6]
block = block.replace(REV_OLD, '<div class="rev" contenteditable="true">反面: 带翼雷霆;铭文ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」</div>', 1)

new = t[:a] + block + t[b:]
open(HTML, 'wb').write(new.encode('utf-8'))

old = open('index.html.bak', 'rb').read()
ver = open(HTML, 'rb').read()
rebuilt = (t[:a] + orig + t[b:]).encode('utf-8')
print('其余部分逐字节一致:', rebuilt == old)
print('大小:', len(old), '->', len(ver))
print('CRLF/裸LF:', ver.count(b'\r\n'), '/', ver.count(b'\n') - ver.count(b'\r\n'))
print('sha256:', hashlib.sha256(ver).hexdigest()[:16])
