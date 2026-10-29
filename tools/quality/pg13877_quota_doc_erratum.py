"""Verify three append-only quota errata against the unchanged original numeric events."""
import copy
import json
from itertools import islice
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13877-quota-document-erratum-v1'
BEFORE = 'a1bd76c5208b51d9b0a750bf64799bedbdc5d377'
DOCS = [
    'evidence/01_PT/018_NK-OPS-001/2529_ReleaseApproval値型_現whole8実行結果.md',
    'documents/400_PGPT/450_品質/456_領域別進捗・利用枠・中断再開管理.md',
    'documents/400_PGPT/450_品質/460_基盤残件・再開優先順.md',
]

def strict(a,b):
    assert json.dumps(a,sort_keys=True) == json.dumps(b,sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists()
    rows = {}
    with Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl').open('rb') as stream:
        for raw in stream:
            row = json.loads(raw)
            if row['eventId'] in ['PGPT-20261008-2910','PGPT-20261008-2911']:
                assert row['eventId'] not in rows
                rows[row['eventId']] = (row,data.sha(raw))
    start = rows['PGPT-20261008-2910'][0];end = rows['PGPT-20261008-2911'][0]
    assert start['groupId'] == end['groupId'] == 'RELEASE_APPROVAL_VALUE_CURRENT_WHOLE8_PT_V1'
    a = start['freshQuota']['primary'];b = end['freshQuota']['primary']
    assert type(a['usedPercent']) is type(b['usedPercent']) is int
    assert type(a['resetsAt']) is type(b['resetsAt']) is int and a['resetsAt'] == b['resetsAt']
    reference = dict(source=end['source'],startUsed=a['usedPercent'],endUsed=b['usedPercent'],reset=b['resetsAt'],
        observedSharedPp=b['usedPercent']-a['usedPercent'],dedicatedPgptCostPp=None,actualTokensN=None,actualTokensT=None,newAccepted=0)
    strict(reference,dict(source='0061d178cda80c2ce3926290619c64db125dbcfc',startUsed=31,endUsed=32,reset=1793774153,
        observedSharedPp=1,dedicatedPgptCostPp=None,actualTokensN=None,actualTokensT=None,newAccepted=0))
    assert end['observedSharedPp'] == reference['observedSharedPp'] and end['actualAllocatedPp'] is None
    line = (f"event2910→2911/source{reference['source']}/共有{reference['startUsed']}→{reference['endUsed']}/同reset{reference['reset']}/"
        f"共有観測差{reference['observedSharedPp']}pp/専有費null/最後のfresh残{100-reference['endUsed']}（{end['freshQuota']['timeUTC']}）。")
    bindings = {}
    for path in DOCS:
        old = subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT)
        old_head = b'\n'.join(old.splitlines()[:18]).decode()
        assert ('31→31' if path != DOCS[2] else 'fresh31残69') in old_head
        with (data.ROOT/path).open() as stream:head = ''.join(islice(stream,32))
        assert line in head and 'BUG2081' in head
        bindings[path] = dict(originalSha256=data.sha(old),correctedSha256=data.sha((data.ROOT/path).read_bytes()),appendOnlyCorrectionFromOriginalEvent=True)
    strict(reference,reference);labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('wrong-shared-zero',lambda x:x.update(observedSharedPp=0)),
        ('different-window',lambda x:x.update(reset=x['reset']+1)),('bool-used',lambda x:x.update(endUsed=True)),
        ('unproven-dedicated-free',lambda x:x.update(dedicatedPgptCostPp=0)),('tokens-from-quota',lambda x:x.update(actualTokensN=1000))]:
        bad = copy.deepcopy(reference);change(bad)
        try:strict(bad,reference)
        except AssertionError:labels.append(label)
        else:raise AssertionError('incorrect quota attribution accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=end['source'],invocation=invocation,originalCommit=BEFORE,derivedFromUnmodifiedEvents={k:v[1] for k,v in rows.items()},
        reference=reference,mechanicallyGeneratedCorrectionLine=line,documents=bindings,positiveMetadataChecks=3,metadataNegativeVectors=len(labels),negativeLabels=labels,
        productTestsExecuted=0,sourceChanged=False,originalGroupEstimateUnchanged=True,originalEventsUnchanged=True,coverageChanged=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
