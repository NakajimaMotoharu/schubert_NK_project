"""Nine same-value Test String declarations; unchanged Main, method and oracle tokens."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed

OUT = data.BASE/'PG12374-pool-batch-plan-v1'
NORMAL = '5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0'
COUNTS = dict(DbPoolMetricCollectorTest=8,WebDbPoolMetricCollectorTest=8,TransferMetricRecorderTest=8,MonitoringRetentionConfigurationTest=8,MetricContractTest=6)
NAMES = {'"active"':'ACTIVE_STATE_LABEL','"DEBUG"':'DEBUG_MONITORING_MODE','".part"':'PART_SUFFIX_LABEL','".ready"':'READY_SUFFIX_LABEL','"CONFIG_DRIFT"':'CONFIGURATION_DRIFT_CODE','"CONFIG_INVALID"':'INVALID_CONFIGURATION_CODE'}
IDS = {'PMD-02118','PMD-02119','PMD-08324','PMD-08325','PMD-04910','PMD-04911','PMD-04912','PMD-04868','PMD-04842'}

def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inputs():
    normal = data.read_checked(data.BASE/'PG12352-pool-capacity-six-compile-v1/manifest.json',NORMAL)
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    table = {}
    for row in original:
        if row['id'] not in IDS:
            continue
        p = row['path'];text = (snapshot/p).read_text()
        assert Path(p).stem in COUNTS and row['rule'] == 'AvoidDuplicateLiterals'
        assert data.sha(text.encode()) == row['inputSha256'] == normal['begin']['inputHashes'][p]
        line = int(row['attributes']['beginline']);column = int(row['attributes']['begincolumn'])
        start = sum(map(len,text.splitlines(keepends=True)[:line-1]))+column-1
        literal = next(m.group() for m in LEX.finditer(text) if m.start() == start)
        count = int(re.search(r' appears ([0-9]+) times',row['message'])[1])
        assert literal in NAMES and raw(text).count(literal) == count and NAMES[literal] not in raw(text)
        assert len(re.findall(r'@Test\s+void ',text)) == COUNTS[Path(p).stem]
        table.setdefault(p,[]).append(dict(id=row['id'],name=NAMES[literal],literal=literal,references=count,type='String'))
    assert len(table) == 5 and sum(map(len,table.values())) == 9
    return normal,snapshot,table

def emit():
    _,snapshot,table = inputs();patch = '*** Begin Patch\n'
    for p,rows in table.items():
        before = (snapshot/p).read_text();assert (data.ROOT/p).read_text() == before
        after = transformed(before,Path(p).stem,rows)
        patch += '*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation = capture(__file__);assert not OUT.exists();normal,snapshot,table = inputs()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes = []
    for p,rows in table.items():
        before = (snapshot/p).read_text();after = (data.ROOT/p).read_text()
        assert raw(after) == raw(transformed(before,Path(p).stem,rows))
        changes.append(dict(path=p,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=9,stringReferences=sum(r['references'] for rows in table.values() for r in rows),originalMethods=38,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
