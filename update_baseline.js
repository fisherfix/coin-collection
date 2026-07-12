const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync('index.html', 'utf8');
const imgMatch = html.match(/images\/(GR|ROM|GK|UK|DE|NI)-\d+\.jpg/g) || [];
const imgs = [...new Set(imgMatch)].sort();
const hash = crypto.createHash('sha1').update(html).digest('hex');

const baseline = {
  hash: hash.substring(0, 16),
  images: imgs.length,
  files: imgs,
  date: new Date().toISOString()
};

fs.writeFileSync('.protect-baseline.json', JSON.stringify(baseline, null, 2));
console.log('Baseline updated:', baseline.hash, '|', imgs.length, 'images');
