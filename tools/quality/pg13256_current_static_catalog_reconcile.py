"""Saved public diagnostic multiset reconciliation; no analyzer or target replay."""
from collections import Counter, defaultdict
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_diagnostic_v3 import signature
from pg13248_business_delivery_trace import state_after as previous_state

OUT = data.BASE/'PG13256-current-static-catalog-reconcile-v1'
CURRENT = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
INPUTS = {}

def read(path,pin=None):
    raw = path.read_bytes();sha = data.sha(raw)
    if pin is not None:assert sha == pin
    INPUTS[str(path.relative_to(data.ROOT))] = sha
    return json.loads(raw)

def key(row):
    return row['path'],signature(row['attributes'],row['message'])

def known_rows():
    ids,refs,pending = previous_state();assert [len(x) for x in [ids,refs,pending]] == [8008,3273,1183]
    original = read(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows = [r for r in original if r['id'] in ids];assert len(rows) == 7990
    for folder,pin in [('PG11451-gc-fake-guard-context-v3','f36538f0046b3a1ff9dece16cfebf27a3606a6795277aa30d294d3eb634a1b71'),('PG11543-memory-http-guard-context-v1','81140466d89ae89677bf2294c80a6c108dfcd3342554b784a03c73ee2614e998')]:
        for r in read(data.BASE/folder/'new-diagnostics.json',pin):
            rows.append(dict(r,message=r['descriptor']['message']))
    for context,static in [('PG12904-reply-terminal-context-v1','PG12898-reply-terminal-static-v1'),('PG12964-public-receipt-context-v1','PG12960-public-receipt-static-v1')]:
        manifest = read(data.BASE/context/'manifest.json');review = read(data.BASE/context/'review.json',manifest['reviewSha256'])
        sm = read(data.BASE/static/'manifest.json');p = data.BASE/static/'pmd.xml';raw = p.read_bytes()
        assert data.sha(raw) == sm['reports']['pmd']['sha256'];INPUTS[str(p.relative_to(data.ROOT))] = data.sha(raw)
        nodes = [(str(Path(f.get('name'))).partition('/src/')[2],n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2] == 'file' for n in f if n.tag.rpartition('}')[2] == 'violation']
        for r in review['rows']:
            if r['id'] not in manifest['newFindingIds']:continue
            matches = [n for path,n in nodes if 'src/'+path == r['path'] and int(n.get('beginline')) == r['beginline'] and int(n.get('endline')) == r['endline'] and n.get('rule') == r['rule']]
            assert len(matches) == 1
            n = matches[0];rows.append(dict(id=r['id'],path=r['path'],attributes=dict(n.attrib),message=' '.join(''.join(n.itertext()).split())))
    supplement = read(data.BASE/'PG13243-business-delivery-baseline-refinement-v1/manifest.json','d31e0979ee6ca7808e165673b763ee16d2e401faef05bd31b5ac22fc2463960f')
    rows.extend(supplement['additionalStaticFindings'])
    assert len(rows) == len({r['id'] for r in rows}) == 8008 and {r['id'] for r in rows} == ids
    return rows

def reconcile(old,current):
    old_counts = Counter(key(r) for r in old);new_counts = Counter(key(r) for r in current)
    assert not old_counts-new_counts, 'active prior diagnostic is missing; never guess its identity'
    extra_counts = new_counts-old_counts;assert sum(extra_counts.values()) == 14
    assert all(r['tool'] == 'pmd' for r in current)
    extras = []
    for k,count in sorted(extra_counts.items()):
        assert k not in old_counts, 'ambiguous excess multiplicity needs separate manual review'
        matches = sorted((r for r in current if key(r) == k),key=lambda r:json.dumps(r,sort_keys=True))
        assert len(matches) == count
        extras.extend(matches)
    assert len(extras) == 14 and all(r['kind'] == 'test' and r['rule'] == 'CloseResource' for r in extras)
    groups = defaultdict(list)
    for r in old:groups[key(r)].append(r['id'])
    return extras,[dict(path=k[0],attributes=dict(k[1][0]),message=k[1][1],priorIds=sorted(v),currentMultiplicity=new_counts[k],
        individualOccurrenceIdentity='UNIQUE' if len(v) == 1 else 'MULTISET_ONLY_NOT_GUESSED') for k,v in sorted(groups.items())]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = read(data.BASE/CURRENT[0]/'manifest.json',CURRENT[1]);current = read(data.BASE/CURRENT[0]/'findings.json',m['findingsSha256'])
    old = known_rows();extras,groups = reconcile(old,current)
    labels = []
    for label,changed in [('missing-prior',current[1:]),('missing-extra',[r for r in current if r is not extras[0]]),('duplicate-extra',current+[extras[0]])]:
        try:reconcile(old,changed)
        except AssertionError:labels.append(label)
        else:raise AssertionError('invalid multiset accepted')
    additional = [dict(copy.deepcopy(r),id=f'PMD-NEW-PG13253-{i:03d}',actualViolation=None,manualPurposeReviewComplete=False,ptExecutionExempt=False,
        status='ADDITIONAL_STATIC_OBSERVATION_UNCLASSIFIED_NOT_COMPLETION') for i,r in enumerate(extras,1)]
    result = dict(source=m['source'],priorCatalog=8008,priorOriginalRetained=7990,priorSupplementalRetained=18,currentMeasured=8022,
        priorDiagnosticsMissing=0,additionalObservations=additional,matchedGroups=groups,metadataNegativeVectors=len(labels),negativeLabels=labels,
        originalGlobalCatalogRewritten=False,sourceOrOracleChanged=False,productTestsExecuted=0,newAccepted=0,effortPercent=None,actualViolationCount=None,qualityGateExit=1)
    verify(invocation);OUT.mkdir();data.write(OUT/'reconciliation.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,inputs=INPUTS,reconciliationSha256=data.sha((OUT/'reconciliation.json').read_bytes()),
        priorCatalog=8008,currentMeasured=8022,additionalObservations=14,priorDiagnosticsMissing=0,metadataNegativeVectors=len(labels),productTestsExecuted=0,newAccepted=0,qualityGateExit=1,actualViolationCount=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
