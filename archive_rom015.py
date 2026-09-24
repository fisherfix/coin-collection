# -*- coding: utf-8 -*-
"""为 ROM-015 生成 coin-archive 存档（JSON + MD），与 index.html 卡片内容一致"""
import json, io, datetime, os

DESC = """罗马行省铜币(Roman Provincial AE)。行省币是罗马帝国授权各行省城市自行打制的流通货币,与罗马本土造币厂发行的币种并行流通。其典型特征是正面沿用皇帝肖像与拉丁铭文,背面保留希腊语城名与地方神祇、城市象征——同一枚币上并存两种语言与两套图像体系,这是行省币最鲜明的辨识特征,也是研究帝国地方治理与城市认同的重要实物。

本枚为铜质,直径 25.5mm、重 7.85g,属行省币中等规格。正面为蓄须男性头像向右,头戴芒冠(radiate);背面为站立人像,周围与底部有铭文行。因币面磨损较重,皇帝归属、发行城市与背面神祇名称均无法可靠释读,故年代与参考编号暂记「待考」。

后续若取得拍卖方标注、同版清晰图录或可靠参考编号,可据此补全归属。按本库原则,未确认的归属不写入卡片,以免形成错误档案。"""

d = {
    "id": "ROM-015",
    "category": "roman",
    "grade": "-",
    "title": "罗马行省·芒冠蓄须头像 铜币（归属待考）",
    "subtitle": "ROMAN PROVINCIAL · AE · Radiate Bearded Bust / Standing Figure · Attribution Pending",
    "image": "images/ROM-015.jpg",
    "era": "待考",
    "denomination": "AE 行省铜币",
    "material": "Bronze 青铜 · 25.5mm · 7.85g",
    "reference": "—",
    "description": DESC,
    "obverse": "正面: 蓄须男性头像向右,头戴芒冠;周围环绕铭文(磨损,不可释读)",
    "reverse": "反面: 站立人像,周围及底部铭文行(磨损,不可释读)",
    "tags": ["古罗马", "罗马行省", "行省铜币", "铜币", "Bronze", "待考"],
    "price": "¥120",
    "price_currency": "CNY",
    "seller": "琋语集藏",
    "auction": "2026-08-09",
    "lot": "",
    "year": "2026",
    "provenance_raw": "<strong>琋语集藏</strong> · 2026-08-09",
    "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "image_size": os.path.getsize("images/ROM-015.jpg"),
}

with io.open("coin-archive/ROM-015.json", "w", encoding="utf-8", newline="\n") as fp:
    json.dump(d, fp, ensure_ascii=False, indent=2)

md = f"""# ROM-015 — {d['title']}

**{d['subtitle']}**

![{d['title']}]({d['image']})

## 基本信息

| 字段 | 内容 |
|------|------|
| 年代 | {d['era']} |
| 面值 | {d['denomination']} |
| 材质 | {d['material']} |
| 品相 | {d['grade']} |
| 参考 | {d['reference']} |
| 分类 | {d['category']} |

## 历史背景

{DESC}

## 正反面

- {d['obverse']}
- {d['reverse']}

## 来源

{d['provenance_raw']} · 成交价 {d['price']}

## 标签

{'、'.join(d['tags'])}
"""
with io.open("coin-archive/ROM-015.md", "w", encoding="utf-8", newline="\n") as fp:
    fp.write(md)

print("已生成 coin-archive/ROM-015.json 与 .md")
print("image_size:", d["image_size"])
chk = json.load(open("coin-archive/ROM-015.json", encoding="utf-8"))
print("回读校验 title:", chk["title"], "| era:", chk["era"], "| price:", chk["price"])
