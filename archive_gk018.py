# -*- coding: utf-8 -*-
"""生成 GK-018 第三层存档（JSON + MD）"""
import json, io, os
from datetime import datetime

desc = ("阿加索克勒斯(Agathokles, BC 317-289)是叙拉古历史上最具争议也最具野心的人物之一。他出身陶工家庭,"
        "凭借军功与政变于 BC 317 年夺取叙拉古政权,随后成为西西里希腊世界对抗迦太基的核心力量——曾率军远征北非,"
        "一度兵临迦太基城下;晚年正式采用「王」(BAΣIΛEYΣ)的称号,是西西里希腊城邦中最早称王者。"
        "西西里在古典时代是希腊人与迦太基人反复争夺的前线,叙拉古长期扮演希腊世界西部屏障的角色。\n\n"
        "本枚属其青铜币中的经典一类:正面为阿尔忒弥斯·索忒伊拉(Artemis Soteira,「救主阿尔忒弥斯」)披纱头像,"
        "发髻束于脑后,肩后佩箭袋;背面带翼雷霆(winged thunderbolt)象征宙斯神力并被用作王权宣示,"
        "与背面铭文 ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」相配——这套币也是西部希腊世界最早带有正式王号的钱币之一。\n\n"
        "本枚直径 21mm、重 8.2g,与同型标准器(21-23mm、约 8-10g)吻合;两面粉末铭文磨损较重,"
        "正面 ΣΩΤΕΙΡΑ 与背面 ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ 系依同型标准释读。参考编号 CNS II 138 与 142 属同一类型下的细分版别,"
        "本枚因铭文磨损暂无法区分,故并列记录、标注待确认。")

d = {
    "id": "GK-018",
    "category": "hellenistic",
    "grade": "-",
    "title": "叙拉古·阿加索克勒斯 阿尔忒弥斯·索忒伊拉/带翼雷霆铜币",
    "subtitle": "SICILY · Syracuse · Agathokles · BC 317-289 (struck c. 304-289) · Artemis Soteira / Winged Thunderbolt · CNS II 138 / 142",
    "image": "images/GK-018.jpg",
    "era": "BC 317-289（铸造约 BC 304-289）",
    "denomination": "AE 青铜币",
    "material": "Bronze 青铜 · 21mm · 8.2g",
    "reference": "CNS II 138 / 142 · SNG ANS 708 · HGC 2, 1537（同型标准参考，精确版别待铭文确认）",
    "description": desc,
    "obverse": "正面: 阿尔忒弥斯·索忒伊拉(Artemis Soteira)披纱头像向右,发髻束于脑后,肩后佩箭袋;右侧铭文ΣΩΤΕΙΡΑ(同型标准释读,本枚磨损仅见残余)",
    "reverse": "反面: 带翼雷霆(winged thunderbolt);周围铭文ΑΓΑΘΟΚΛΕΟΣ ΒΑΣΙΛΕΟΣ「阿加索克勒斯王」(同型标准释读,本枚磨损较重)",
    "tags": ["古希腊", "希腊化", "Sicily", "西西里", "叙拉古", "Syracuse", "阿加索克勒斯", "Agathokles",
             "阿尔忒弥斯", "Artemis Soteira", "带翼雷霆", "Thunderbolt", "王号币", "青铜", "Bronze",
             "CNS II 138/142", "HGC 2 1537", "BC 317-289"],
    "price": "¥683",
    "price_currency": "CNY",
    "price_cny": 683,
    "seller": "星盘世界钱币",
    "auction": "2026-08-23",
    "lot": "",
    "year": "2026",
    "provenance_raw": "<strong>星盘世界钱币</strong> · 2026-08-23",
    "created_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    "image_size": os.path.getsize('images/GK-018.jpg'),
}

with io.open('coin-archive/GK-018.json', 'w', encoding='utf-8', newline='\n') as fp:
    json.dump(d, fp, ensure_ascii=False, indent=2)

tag_line = ' '.join('`' + x + '`' for x in d['tags'])

md = "# GK-018 — 叙拉古·阿加索克勒斯 阿尔忒弥斯·索忒伊拉/带翼雷霆铜币\n\n"
md += "**" + d['subtitle'] + "**\n\n"
md += "![" + d['title'] + "](images/GK-018.jpg)\n\n"
md += "## 基本信息\n\n| 字段 | 内容 |\n|------|------|\n"
md += "| 年代 | " + d['era'] + " |\n"
md += "| 面值 | " + d['denomination'] + " |\n"
md += "| 材质 | " + d['material'] + " |\n"
md += "| 品相 | - |\n"
md += "| 参考 | " + d['reference'] + " |\n"
md += "| 分类 | hellenistic |\n\n"
md += "## 历史背景\n\n" + desc + "\n\n"
md += "## 正面\n\n" + d['obverse'] + "\n\n"
md += "## 背面\n\n" + d['reverse'] + "\n\n"
md += "## 收藏信息\n\n| 字段 | 内容 |\n|------|------|\n"
md += "| 价格 | ¥683 |\n| 折合人民币 | ¥683 |\n"
md += "| 卖家 | " + d['seller'] + " |\n| 拍卖 | " + d['auction'] + " |\n| Lot |  |\n| 年份 | 2026 |\n\n"
md += "## 标签\n\n" + tag_line + "\n\n"
md += "## 元数据\n\n"
md += "- 创建时间: " + d['created_at'] + "\n"
md += "- 确认时间: \n"
md += "- Git commit: `未记录`\n"
md += "- 图片: images/GK-018.jpg (" + str(d['image_size']) + " bytes)\n"

open('coin-archive/GK-018.md', 'w', encoding='utf-8', newline='\n').write(md)

print('存档已生成')
print('JSON title:', json.load(open('coin-archive/GK-018.json', encoding='utf-8'))['title'])
print('image_size:', d['image_size'])
print('MD 行数:', len(open('coin-archive/GK-018.md', encoding='utf-8').readlines()))
