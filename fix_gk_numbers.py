import os, re
path = r'C:\Users\zhaojingyun\.qclaw\workspace-agent-d8b9b18a\coin-collection\index.html'
with open(path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

old_to_new = {
    'GK-002': 'GK-009',
    'GK-003': 'GK-003',
    'GK-004': 'GK-002',
    'GK-006': 'GK-005',
    'GK-007': 'GK-007',
    'GK-008': 'GK-001',
    'GK-009': 'GK-006',
    'GK-010': 'GK-008',
    'GK-011': 'GK-010',
    'GK-012': 'GK-004',
}

count = 0
for old_id, new_id in old_to_new.items():
    c0 = content.count(f'<!-- {old_id} -->')
    c1 = content.count(f'>{old_id}<')
    c2 = content.count(f'images/{old_id}.jpg')
    n = c0 + c1 + c2
    if n > 0:
        content = content.replace(f'<!-- {old_id} -->', f'<!-- {new_id} -->')
        content = content.replace(f'>{old_id}<', f'>{new_id}<')
        content = content.replace(f'images/{old_id}.jpg', f'images/{new_id}.jpg')
        count += n
        print(old_id, '->', new_id, ':', n, 'changes')

with open(path, 'w', encoding='utf-8-sig') as f:
    f.write(content)
print('Done. Total changes:', count)

found = sorted(set(re.findall(r'GK-0\d\d?', content)))
print('Remaining GK refs:', found)
