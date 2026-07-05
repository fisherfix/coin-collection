#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
rebuild_index.py — 从 JSON 存档重建 index.html

用法：
  python rebuild_index.py        # 从 JSON 重建，保留 ROM-004 批量组
  python rebuild_index.py --diff  # 仅对比，不写入
"""

import os, sys, io, json, shutil, hashlib, re

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = r"C:\Users\zhaojingyun\.qclaw\workspace-agent-d8b9b18a\coin-collection"
ARCHIVE_DIR = os.path.join(BASE_DIR, "coin-archive")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
BAK_PATH = os.path.join(BASE_DIR, "index.html.bak")
MARKER = "</div><!-- end coin-grid -->"
ROM004_BATCH_COMMENT = "<!-- ROM-004 批量组 -->"


def generate_card(data):
    """生成标准卡片 HTML（不含 ROM-004 批量组）"""
    if data["id"] == "ROM-004":
        return None  # ROM-004 用批量组格式，不走这里
    tags_html = "".join(
        [f'<span class="tag" contenteditable="true">{tag}</span>' for tag in data.get("tags", [])]
    )
    return f'''
<!-- {data["id"]} -->
<div class="coin-card" data-category="{data.get("category", "other")}" draggable="true">
  <div class="drag-handle">⠿ 拖拽排序</div>
  <div class="coin-image">
    <span class="coin-number" contenteditable="true">{data.get("id", "")}</span>
    <span class="coin-grade" contenteditable="true">{data.get("grade", "")}</span>
    <img src="{data.get("image", "")}" alt="{data.get("title", "")}" data-path="{data.get("image", "")}" onerror="this.style.display='none'">
    <div class="placeholder" onclick="triggerUpload(this)" style="display:none">🪙</div>
    <div class="img-overlay">
      <button class="img-btn" onclick="triggerUpload(this)">📷 上传图片</button>
      <button class="img-btn" onclick="editImgPath(this)">🔗 改路径</button>
    </div>
  </div>
  <div class="coin-info">
    <h2 class="coin-title" contenteditable="true">{data.get("title", "")}</h2>
    <p class="coin-subtitle" contenteditable="true">{data.get("subtitle", "")}</p>
    <div class="coin-detail">
      <div class="detail-item"><div class="detail-label" contenteditable="true">年代</div><div class="detail-value" contenteditable="true">{data.get("era", "")}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">面值</div><div class="detail-value" contenteditable="true">{data.get("denomination", "")}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">材质</div><div class="detail-value" contenteditable="true">{data.get("material", "")}</div></div>
      <div class="detail-item"><div class="detail-label" contenteditable="true">参考</div><div class="detail-value" contenteditable="true">{data.get("reference", "")}</div></div>
    </div>
    <div class="description">
      <h4 contenteditable="true">📜 历史背景</h4>
      <p contenteditable="true">{data.get("description", "")}</p>
    </div>
    <div class="obv-rev">
      <div class="obv" contenteditable="true">{data.get("obverse", "")}</div>
      <div class="rev" contenteditable="true">{data.get("reverse", "")}</div>
    </div>
    {tags_html}
    <div class="bottom-row">
      <div><div class="price-value" contenteditable="true">{data.get("price", "")}</div><div class="price-label" contenteditable="true">成交价</div></div>
      <div class="prov-compact" contenteditable="true">{data.get("provenance_raw", "")}</div>
    </div>
  </div>
</div>
'''


def rebuild(diff_only=False):
    """重建 index.html"""
    if not os.path.exists(ARCHIVE_DIR):
        print("ERROR: archive dir not found")
        return False

    # 读取 JSON
    json_files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".json")])
    print("Found %d JSON archives" % len(json_files))

    coins_data = []
    for fname in json_files:
        with open(os.path.join(ARCHIVE_DIR, fname), "r", encoding="utf-8") as f:
            coins_data.append(json.load(f))

    # 生成卡片（跳过 ROM-004）
    cards = {}
    for d in coins_data:
        html = generate_card(d)
        if html:
            cards[d["id"]] = html
            print("  card: %s" % d["id"])
        else:
            print("  skip: %s (batch block)" % d["id"])

    # 定义卡片顺序（ROM-004 批量组在第 6 位）
    ORDER = ["GR-001","ROM-001","GK-002","ROM-002","ROM-003","ROM-004",
             "GK-003","GK-004","GK-005","GK-006","GK-007","UK-001","DE-001","DE-002"]

    cards_html_parts = []
    for cid in ORDER:
        if cid == "ROM-004":
            # 从原始 HTML 提取 ROM-004 批量组块
            if os.path.exists(INDEX_PATH):
                with open(INDEX_PATH, "r", encoding="utf-8-sig") as f:
                    orig_html = f.read()
            else:
                orig_html = ""
            batch_start = orig_html.find(ROM004_BATCH_COMMENT)
            if batch_start >= 0:
                next_comment = orig_html.find("<!-- ", batch_start + len(ROM004_BATCH_COMMENT))
                if next_comment == -1:
                    next_comment = len(orig_html)
                batch_block = orig_html[batch_start:next_comment]
                cards_html_parts.append(batch_block)
                print("  batch: ROM-004 (preserved from original, %d chars)" % len(batch_block))
            else:
                print("  WARNING: ROM-004 batch block not found in original HTML")
        elif cid in cards:
            cards_html_parts.append(cards[cid])
        else:
            print("  MISSING: %s" % cid)

    cards_html = "\n".join(cards_html_parts)

    # 从原始 HTML 提取 head 和 tail
    if os.path.exists(INDEX_PATH):
        # 使用二进制读取保留 CRLF
        with open(INDEX_PATH, "r", encoding="utf-8-sig") as f:
            orig_content = f.read()
        # newline 参数已经在 open() 中处理了

        grid_m = re.search(r'<div[^>]*class="coin-grid"[^>]*>', orig_content)
        if grid_m:
            grid_end = grid_m.end()
            head = orig_content[:grid_end]
        else:
            head = orig_content[:orig_content.find("</body>")]

        mi = orig_content.find(MARKER)
        if mi != -1:
            tail = orig_content[mi:]
        else:
            tail = MARKER + "\n</div></div>"

        if not diff_only:
            shutil.copy2(INDEX_PATH, BAK_PATH)
            print("Backup: %s" % BAK_PATH)
        print("head=%d tail=%d cards=%d" % (len(head), len(tail), len(cards_html)))
    else:
        print("ERROR: index.html not found")
        return False

    new_content = head + "\n" + cards_html + "\n" + tail

    if diff_only:
        # 仅对比
        orig_bytes = orig_content.encode("utf-8")
        new_bytes = new_content.encode("utf-8")
        print("\n--- DIFF ONLY ---")
        print("Orig:  %d bytes" % len(orig_bytes))
        print("New:   %d bytes" % len(new_bytes))
        print("Match: %s" % (orig_bytes == new_bytes))
        if orig_bytes != new_bytes:
            # 找第一个差异
            for i in range(min(len(orig_bytes), len(new_bytes))):
                if orig_bytes[i] != new_bytes[i]:
                    print("First diff at byte %d: 0x%02x vs 0x%02x" % (i, orig_bytes[i], new_bytes[i]))
                    print("  Context orig: %r" % orig_bytes[max(0,i-20):i+20])
                    print("  Context new:  %r" % new_bytes[max(0,i-20):i+20])
                    break
            else:
                print("One is prefix of other: orig=%d new=%d" % (len(orig_bytes), len(new_bytes)))
        return True

    # 写入（保留行尾格式）
    with open(INDEX_PATH, "w", encoding="utf-8-sig") as f:
        f.write(new_content)

    # 验证
    with open(INDEX_PATH, "rb") as f:
        new_bytes = f.read()
    bom_ok = new_bytes[:3] == b'\xef\xbb\xbf'
    fp = hashlib.sha256(new_bytes).hexdigest()
    orig_bytes = orig_content.encode("utf-8")
    match = (orig_bytes == new_bytes)

    # 验证每张卡
    with open(INDEX_PATH, "r", encoding="utf-8-sig") as f:
        rebuilt_html = f.read()
    all_ok = True
    for cid in ORDER:
        if cid == "ROM-004":
            if ROM004_BATCH_COMMENT not in rebuilt_html:
                print("  MISSING: %s batch" % cid)
                all_ok = False
        else:
            if "<!-- %s -->" % cid not in rebuilt_html:
                print("  MISSING: %s" % cid)
                all_ok = False
    if all_ok:
        print("All cards verified")

    print("Result: %d bytes, SHA256: %s..., BOM: %s, ByteMatch: %s" % (
        len(new_bytes), fp[:16], "OK" if bom_ok else "FAIL", "YES" if match else "NO"))
    return all_ok and match


if __name__ == "__main__":
    diff = "--diff" in sys.argv
    ok = rebuild(diff_only=diff)
    sys.exit(0 if ok else 1)
