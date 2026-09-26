import csv, gzip, io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', '..', 'uik-protocols')
def read(name):
    return csv.DictReader(io.TextIOWrapper(gzip.open(os.path.join(HERE, 'src', name)), encoding='utf-8'))

rows = list(read('uik_protocols.csv.gz'))
single_participants = {}
for r in read('uik_single_mandate_full.csv.gz'):
    if r['is_candidate'] != '1' and r['line'] in ('9', '10'):
        single_participants[r['uuid']] = single_participants.get(r['uuid'], 0) + int(r['value'] or 0)
federal_participants = {r['uuid']: int(r['l09_invalid'] or 0) + int(r['l10_valid'] or 0) for r in read('uik_federal_full.csv.gz')}
by_district = {r['district']: r['region'] for r in rows if r['region'] not in ('', 'None')}
for r in rows:
    if r['region'] in ('', 'None'):
        r['region'] = by_district[r['district']]
regions = sorted({r['region'] for r in rows})
ridx = {n: i for i, n in enumerate(regions)}
tiks = sorted({(r['region'], r['tik']) for r in rows})
tidx = {t: i for i, t in enumerate(tiks)}
names = sorted({r['power_name'] for r in rows} | {r['pick_name'] for r in rows})
nidx = {n: i for i, n in enumerate(names)}
rows.sort(key=lambda r: (tidx[(r['region'], r['tik'])], int(r['uik'])))
def num(v): return int(v) if v != '' else -1
def pct(v): return round(float(v) * 100) if v != '' else -1
cols = {k: [] for k in 't u v i va fv sp fp tp pw pwp pk pkp er erp f d nw nk'.split()}
for r in rows:
    cols['t'].append(tidx[(r['region'], r['tik'])])
    cols['u'].append(int(r['uik']))
    cols['v'].append(num(r['voters']))
    cols['i'].append(num(r['issued']))
    cols['va'].append(num(r['valid']))
    cols['fv'].append(num(r['federal_valid']))
    cols['sp'].append(single_participants.get(r['uuid'], -1))
    cols['fp'].append(federal_participants.get(r['uuid'], -1))
    cols['tp'].append(pct(r['turnout_pct']))
    for name_key, votes_key, pct_key, vc, pc in (('power_name', 'power_votes', 'power_pct', 'pw', 'pwp'), ('pick_name', 'pick_votes', 'pick_pct', 'pk', 'pkp')):
        if r[name_key] and r[pct_key] == '' and num(r['valid']) > 0:
            votes = max(num(r[votes_key]), 0)
            cols[vc].append(votes)
            cols[pc].append(round(votes / int(r['valid']) * 10000))
        else:
            cols[vc].append(num(r[votes_key]))
            cols[pc].append(pct(r[pct_key]))
    cols['er'].append(num(r['er_list_votes']))
    cols['erp'].append(pct(r['er_list_pct']))
    cols['f'].append((r['is_deg'] == '1') | (r['repeated'] == '1') << 1 | (r['source'] != 'cik_api') << 2)
    cols['d'].append(int(r['district']))
    cols['nw'].append(nidx[r['power_name']])
    cols['nk'].append(nidx[r['pick_name']])
data = {'regions': regions, 'tiks': [[ridx[a], b] for a, b in tiks], 'names': names, 'cols': cols}
js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
import hashlib
detail_dir = os.path.join(SITE, 'detail')
digest = hashlib.sha1()
for name in sorted(os.listdir(detail_dir)):
    digest.update(open(os.path.join(detail_dir, name), 'rb').read())
out = (open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
       .replace('/*DATA*/null', js)
       .replace('/*DETAIL_VERSION*/', digest.hexdigest()[:10]))
title = re.match(r'<title>[^<]*</title>', out).group(0)
page = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        + title + '</head><body style="margin:0">' + out[len(title):] + '</body></html>')
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page)
print(round(len(page) / 1e6, 2), 'MB')
