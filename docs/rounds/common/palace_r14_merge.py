import csv, sys
repo = '/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/research/xiyanglou/plate_keypoints.csv'
rows = list(csv.DictReader(open(repo, encoding='utf-8')))
fields = list(rows[0].keys())
have = {(r['photo_id'], r['point']) for r in rows}
added = 0
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f, encoding='utf-8')):
        r = {k: (r.get(k) or '').strip() for k in fields}
        if not r['photo_id'] or not r['point']:
            continue
        key = (r['photo_id'], r['point'])
        if key in have:
            print('dup kept old', key); continue
        r['x'] = str(int(round(float(r['x'])))); r['y'] = str(int(round(float(r['y']))))
        rows.append(r); have.add(key); added += 1
w = csv.DictWriter(open(repo, 'w', newline='', encoding='utf-8'), fieldnames=fields)
w.writeheader(); w.writerows(rows)
print('added', added)
