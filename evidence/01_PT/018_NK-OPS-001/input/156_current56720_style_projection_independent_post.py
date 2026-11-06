"""Check every saved diagnostic occurrence and source anchor; run no Product or engine."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import subprocess
r = Path.cwd()
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21976-current56720-main-style-projection-v1/manifest.json'
assert sha(p) == 'ea8172824b44ed6e7a67f2ce30b7e063e175517263ddc7f93ec72c322090bff3'
m = load(p)
assert m['actualExit'] == m['applicableViolations'] == m['unclassified'] == 0
assert m['mainSources'] == 967 and m['rawPmdOccurrences'] == 1494
for ref in m['refs']:
    path = r/ref['path']
    assert sha(path) == ref['sha256']
    assert hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+ref['path']])).hexdigest() == ref['sha256']
raw = load(r/m['refs'][0]['path'])
review = load(r/m['refs'][1]['path'])
old = {x['id']:x for x in review['classified']}
rows_path = p.parent/m['occurrences']['path']
assert sha(rows_path) == m['occurrences']['sha256']
rows = load(rows_path)
assert len(rows) == len({x['originalId'] for x in rows}) == 1494
assert set(old) == {x['originalId'] for x in rows}
assert sorted(x['originalOrdinal'] for x in rows) == list(range(1494))
source_cache, current_indices = {}, []
for row in rows:
    prior = old[row['originalId']]
    n = row['finding']['path']
    assert n == prior['rawFinding']['path']
    assert row['currentSourceSha256'] == m['currentMainInputHashes'][n] == sha(r/n)
    assert row['reason'] == prior['reason'] and row['classification'] == prior['classification'] == 'CONTEXTUAL_NONAPPLICABLE'
    assert row['actualViolation'] is False and row['finding']['message'] == prior['rawFinding']['message']
    a, b = dict(prior['rawFinding']['attributes']), dict(row['finding']['attributes'])
    old_begin, old_end = int(a.pop('beginline')), int(a.pop('endline'))
    new_begin, new_end = int(b.pop('beginline')), int(b.pop('endline'))
    assert a == b  # columns, method/class, rule, priority and all other attributes remain exact.
    if row['currentConsumerOccurrence'] is not None:
        current_indices.append(row['currentConsumerOccurrence'])
        if n not in source_cache:
            data = subprocess.check_output(['git','show',raw['normalSource']+':'+n])
            assert hashlib.sha256(data).hexdigest() == raw['sourceInputHashes'][n]
            source_cache[n] = (data.decode().splitlines(), (r/n).read_text().splitlines())
        before, after = source_cache[n]
        assert before[old_begin-1:old_end] == after[new_begin-1:new_end]
    else:
        assert row['basis'] == 'EXACT_SOURCE_BYTE_UNCHANGED_FROM20150'
        assert row['currentSourceSha256'] == raw['sourceInputHashes'][n]
assert sorted(current_indices) == list(range(101)) and len(source_cache) == 4
canonical = collections.Counter(json.dumps(x['finding'],sort_keys=True) for x in rows)
assert len(canonical) == 1442
assert sum(v > 1 for v in canonical.values()) == 52 and sum(v-1 for v in canonical.values()) == 52
normalp = r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
normal = load(normalp)
inputs = {n:h for n,h in normal['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')}
assert inputs == m['currentMainInputHashes'] and len(inputs) == 967
assert all(sha(r/n) == h for n,h in inputs.items())
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21978-current56720-f03-independent-post-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,
    checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionMainSource=normal['source'],
    original=dict(path=str(p.relative_to(r)),sha256=sha(p)),mainSources=967,rawPmdOccurrences=1494,
    currentConsumerOccurrences=101,unchangedSourceOccurrences=1393,canonicalOccurrences=1442,
    duplicateGroups=52,extraDuplicateOccurrences=52,perOccurrenceColumnsMethodsRulesExact=True,
    currentAndPriorConsumerCodeSpansEqual=True,applicableViolations=0,unclassified=0,
    checkstyleIssues=0,rawGateExitPreserved=m['rawGateExitPreserved'],
    productTestsExecuted=0,enginesReplayed=0,coverage=None,newSourceProofs=0,newAcceptance=0,
    wholeF03Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,rawOccurrences=1494,currentBound=101,unclassified=0,
                     manifestSha256=sha(out/'manifest.json'))))
