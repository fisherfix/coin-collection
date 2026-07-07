import os, json

base = r'C:\Users\zhaojingyun\.qclaw\workspace-agent-d8b9b18a\coin-collection\coin-archive'
old_to_new = {
    'GK-002': 'GK-009',
    'GK-004': 'GK-002',
    'GK-006': 'GK-005',
    'GK-008': 'GK-001',
    'GK-009': 'GK-006',
    'GK-010': 'GK-008',
    'GK-011': 'GK-010',
    'GK-012': 'GK-004',
}

for old_id, new_id in old_to_new.items():
    old_json = os.path.join(base, f'{old_id}.json')
    new_json = os.path.join(base, f'{new_id}.json')
    old_md = os.path.join(base, f'{old_id}.md')
    new_md = os.path.join(base, f'{new_id}.md')

    if os.path.exists(old_json):
        with open(old_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['id'] = new_id
        data['image'] = f'images/{new_id}.jpg'
        with open(new_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.remove(old_json)
        print(f'JSON: {old_id} -> {new_id}')

    if os.path.exists(old_md):
        with open(old_md, 'r', encoding='utf-8') as f:
            txt = f.read()
        txt = txt.replace(f'# {old_id} ', f'# {new_id} ')
        txt = txt.replace(f'images/{old_id}.jpg', f'images/{new_id}.jpg')
        with open(new_md, 'w', encoding='utf-8') as f:
            f.write(txt)
        os.remove(old_md)
        print(f'MD: {old_id} -> {new_id}')

# Update image path for self-mapping IDs (GK-003, GK-007)
for sid in ['GK-003', 'GK-007']:
    jp = os.path.join(base, f'{sid}.json')
    if os.path.exists(jp):
        with open(jp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['image'] = f'images/{sid}.jpg'
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'JSON img fix: {sid}')

print('Archive rename done')
