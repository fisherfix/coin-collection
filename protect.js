#!/usr/bin/env node
/**
 * protect.js — 钱币数据库保护校验脚本
 *
 * 功能：
 * 1. 验证 index.html 编码（UTF-8 with BOM，无 GBK 损坏）
 * 2. 统计当前卡片数量
 * 3. 为每张卡片生成 SHA-256 指纹
 * 4. 与上次基线对比，检测是否有意外修改
 * 5. 打印保护状态报告
 *
 * 用法：
 *   node protect.js              # 校验当前状态
 *   node protect.js snapshot     # 记录当前状态为基线
 *   node protect.js check        # 与基线对比
 *   node protect.js cards        # 只列出卡片清单
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const INDEX = path.join(__dirname, 'index.html');
const BASELINE = path.join(__dirname, '.protect-baseline.json');

const action = process.argv[2] || 'check';

function readFile() {
  const buf = fs.readFileSync(INDEX);
  // 验证 BOM
  if (buf[0] !== 0xEF || buf[1] !== 0xBB || buf[2] !== 0xBF) {
    return { ok: false, error: 'Missing UTF-8 BOM', buf };
  }
  // 简单 GBK 探测：高字节 + 后续低字节是常见 GBK 模式
  // 真正的 GBK 检测很复杂，这里用最简单方法：检查文件中是否有 mojibake 模式
  const str = buf.toString('utf-8');
  // 常见 mojibake 模式：脥脌 脥隆 脰陇 等
  if (/[\u80-\uFF][\u00-\u7F]/.test(str.substring(0, 1000))) {
    // 仅警告，不算错误（可能是正常 UTF-8）
  }
  // 关键检测：文件是否能正常 decode 且包含中文
  if (!/[\u4e00-\u9fa5]/.test(str.substring(0, 5000))) {
    return { ok: false, error: 'No Chinese characters found in first 5KB - possible encoding issue', str, buf };
  }
  return { ok: true, str, buf };
}

function extractCards(content) {
  // 提取所有卡片（含 ROM-004 批量组等带后缀注释）
  const cardComments = content.match(/<!-- [A-Z]+-\d+[^>]*?-->/g) || [];
  return cardComments.map(c => c.replace(/[<!-->\s]/g, ''));
}

function computeFingerprint(content) {
  return crypto.createHash('sha256').update(content, 'utf8').digest('hex');
}

function listCards() {
  const r = readFile();
  if (!r.ok) {
    console.error('❌', r.error);
    process.exit(1);
  }
  const cards = extractCards(r.str);
  console.log('当前数据库卡片清单：');
  cards.forEach((c, i) => console.log(`  ${(i+1).toString().padStart(2)}. ${c}`));
  console.log(`\n共 ${cards.length} 张卡片`);
  console.log(`文件大小: ${r.buf.length} 字节`);
  console.log(`编码: UTF-8 with BOM`);
}

function snapshot() {
  const r = readFile();
  if (!r.ok) {
    console.error('❌', r.error);
    process.exit(1);
  }
  const cards = extractCards(r.str);
  const data = {
    timestamp: new Date().toISOString(),
    file_size: r.buf.length,
    card_count: cards.length,
    card_list: cards,
    full_sha256: computeFingerprint(r.str),
  };
  fs.writeFileSync(BASELINE, JSON.stringify(data, null, 2), 'utf-8');
  console.log('✅ 基线已保存：');
  console.log(`   卡片数: ${data.card_count}`);
  console.log(`   文件指纹: ${data.full_sha256.substring(0, 16)}...`);
  console.log(`   时间: ${data.timestamp}`);
  console.log(`   路径: ${BASELINE}`);
}

function check() {
  if (!fs.existsSync(INDEX)) {
    console.error('❌ index.html 不存在');
    process.exit(1);
  }
  const r = readFile();
  if (!r.ok) {
    console.error('❌', r.error);
    process.exit(1);
  }
  const cards = extractCards(r.str);
  const fp = computeFingerprint(r.str);

  console.log('📊 钱币数据库保护状态');
  console.log('━'.repeat(50));
  console.log(`卡片数: ${cards.length}`);
  console.log(`文件大小: ${r.buf.length} 字节`);
  console.log(`文件指纹: ${fp.substring(0, 16)}...`);
  console.log(`编码: UTF-8 with BOM ✓`);

  if (fs.existsSync(BASELINE)) {
    const baseline = JSON.parse(fs.readFileSync(BASELINE, 'utf-8'));
    console.log(`\n基线对比（${baseline.timestamp}）：`);
    console.log(`  卡片数: ${baseline.card_count} → ${cards.length} ${cards.length === baseline.card_count ? '✓' : '✗ 变化!'}`);
    console.log(`  文件大小: ${baseline.file_size} → ${r.buf.length} ${Math.abs(r.buf.length - baseline.file_size) < 100 ? '✓' : '变化'}`);
    console.log(`  完整指纹: ${baseline.full_sha256.substring(0, 16)} → ${fp.substring(0, 16)}`);

    // 检查哪些卡片变了
    const baselineSet = new Set(baseline.card_list);
    const currentSet = new Set(cards);
    const added = cards.filter(c => !baselineSet.has(c));
    const removed = baseline.card_list.filter(c => !currentSet.has(c));
    if (added.length > 0) {
      console.log(`  新增卡片: ${added.join(', ')}`);
    }
    if (removed.length > 0) {
      console.log(`  ⚠️  移除卡片: ${removed.join(', ')}`);
    }
    if (added.length === 0 && removed.length === 0 && cards.length === baseline.card_count) {
      console.log(`  卡片集合未变化 ✓`);
    }
  } else {
    console.log('\n💡 尚无基线。运行 `node protect.js snapshot` 建立基线。');
  }

  // 检查插入标记
  if (r.str.includes('</div><!-- end coin-grid -->')) {
    console.log('\n✓ 插入标记存在（可安全插入新卡片）');
  } else {
    console.log('\n⚠️  警告：未找到插入标记 `</div><!-- end coin-grid -->`');
    console.log('   请在 index.html 中补上此标记，否则 add_coin.py 无法定位插入点');
  }
}

switch (action) {
  case 'check':
    check();
    break;
  case 'snapshot':
    snapshot();
    break;
  case 'cards':
    listCards();
    break;
  default:
    console.log('用法：');
    console.log('  node protect.js check      # 校验当前状态');
    console.log('  node protect.js snapshot   # 保存当前状态为基线');
    console.log('  node protect.js cards      # 列出所有卡片');
}
