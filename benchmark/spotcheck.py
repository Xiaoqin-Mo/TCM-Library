import csv, glob, json, collections

targets = ['q001', 'q019', 'q037', 'q054']
rows_by_q = collections.defaultdict(list)
for f in sorted(glob.glob('benchmark/gold/annotation_batch*.csv')):
    with open(f, encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh):
            if r['query_id'] in targets:
                rows_by_q[r['query_id']].append(r)

queries = {p['qid']: p['query'] for p in json.load(open('benchmark/data/pool_v1.json', encoding='utf-8'))}
for qid in targets:
    rows = rows_by_q[qid]
    print(f'===== {qid} (query={queries[qid]}) =====')
    for rel in (3, 2, 1, 0):
        one = next((r for r in rows if r['relevance'] == str(rel)), None)
        if one:
            print(f'  [{rel}] {one["candidate_id"]} | {one["book"]} | {one["section_title"][:45]}')
