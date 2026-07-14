const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Check FJ-005 and FJ-006 structures
const fj5 = html.indexOf('<!-- FJ-005 -->');
const fj6 = html.indexOf('<!-- FJ-006 -->');
const fm1 = html.indexOf('<!-- FM-001 -->');
console.log('FJ-005 starts:', fj5, 'FJ-006 starts:', fj6, 'FM-001 starts:', fm1);
console.log('FJ-005 present:', fj5 > 0);
console.log('FJ-006 present:', fj6 > 0);

// Check key structural elements in the new format
const detailDiv = (html.match(/detail-item"><div class="detail-label"/g) || []).length;
const h4Header = (html.match(/<h4 contenteditable="true">📜 历史背景<\/h4>/g) || []).length;
const priceLabel = (html.match(/price-label" contenteditable="true">成交价<\/div>/g) || []).length;
const contenteditable = (html.match(/contenteditable="true"/g) || []).length;
const bottomRow = (html.match(/<div class="bottom-row">/g) || []).length;
const priceValue = (html.match(/<div class="price-value" contenteditable="true">/g) || []).length;

// Check no data-id attributes on FJ cards
const fjDataId = (html.match(/data-category="FJ" data-id/g) || []).length;
const coinCardFj = (html.match(/data-category="FJ" draggable="true">/g) || []).length;

console.log('--- Structural checks ---');
console.log('detail-item with div:', detailDiv, '(expect 8 = 4 items x 2 cards)');
console.log('h4 headers:', h4Header, '(expect 2)');
console.log('price-label "成交价":', priceLabel, '(expect 2)');
console.log('contenteditable attrs:', contenteditable, '(expect many)');
console.log('bottom-row divs:', bottomRow, '(expect 2)');
console.log('price-value divs:', priceValue, '(expect 2)');
console.log('FJ data-id leftover:', fjDataId, '(expect 0)');
console.log('FJ coin-card divs:', coinCardFj, '(expect 2)');
