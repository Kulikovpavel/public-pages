import csv, gzip, io, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'uik-protocols', 'detail')
os.makedirs(OUT, exist_ok=True)

def rows(name):
    return csv.DictReader(io.TextIOWrapper(gzip.open(os.path.join(HERE, 'src', name)), encoding='utf-8'))

PARTY_KEYS = ['РОДИНА', 'ЕДИНАЯ РОССИЯ', 'КПРФ', 'ПЕНСИОНЕРОВ', 'НОВЫЕ ЛЮДИ', 'прямой демократии', 'ЗЕЛЁНЫЕ', 'КОММУНИСТЫ РОССИИ', 'ЛДПР', 'СПРАВЕДЛИВАЯ РОССИЯ']
fed_reader = rows('uik_federal_full.csv.gz')
line_cols = [c for c in fed_reader.fieldnames if c[:1] == 'l' and c[1:3].isdigit()]
party_cols = [next(c for c in fed_reader.fieldnames if key in c) for key in PARTY_KEYS]
fed = {r['uuid']: [int(r[c] or 0) for c in line_cols + party_cols] for r in fed_reader}

districts = {}
for r in rows('uik_single_mandate_full.csv.gz'):
    d = districts.setdefault(int(r['district']), {'name': r['district_name'], 'cands': [], 'cand_idx': {}, 'uiks': {}})
    u = d['uiks'].setdefault(r['uik'], {'uuid': r['uuid'], 'l': [0] * 12, 'c': {}})
    if u['uuid'] != r['uuid']:
        raise SystemExit(f"duplicate UIK {r['uik']} in district {r['district']}")
    v = int(r['value'] or 0)
    if r['is_candidate'] == '1':
        if r['line_name'] not in d['cand_idx']:
            d['cand_idx'][r['line_name']] = len(d['cands'])
            d['cands'].append([r['line_name'], r['party'], (r['iditena_power'] == '1') | (r['iditena_pick'] == '1') << 1])
        u['c'][d['cand_idx'][r['line_name']]] = v
    else:
        u['l'][int(r['line']) - 1] = v

sizes = []
for num, d in districts.items():
    out = {'name': d['name'], 'cands': d['cands'], 'uiks': {
        k: [u['l'], [u['c'].get(i, 0) for i in range(len(d['cands']))], fed.get(u['uuid'])]
        for k, u in d['uiks'].items()}}
    path = os.path.join(OUT, f'{num}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    sizes.append((os.path.getsize(path), num))
sizes.sort()
print('files', len(sizes), 'total MB', round(sum(s for s, _ in sizes) / 1e6, 2), 'min', sizes[0], 'median', sizes[len(sizes) // 2], 'max', sizes[-1])
print('lines', len(line_cols), 'parties', party_cols)
print('uiks without federal', sum(1 for d in districts.values() for u in d['uiks'].values() if u['uuid'] not in fed))
