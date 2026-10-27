"""Same-value fixture constants for four independent API request tests; no target execution."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as literal_transform

OUT = data.BASE/'PG11180-api-catalog-scalar-pool-literal-plan-v1'
NAMES = {'0000': 'SUCCESS_RESULT_CODE', 'API': 'API_SERVICE_VALUE', 'DEBUG': 'DEBUG_MODE', 'SUCCESS': 'SUCCESS_OUTCOME', 'active': 'ACTIVE_POOL_STATE', 'address': 'ADDRESS_LABEL', 'fixture': 'PROVIDER_FAILURE_MARKER', 'idle': 'IDLE_POOL_STATE', 'layout': 'LAYOUT_LABEL', 'max': 'MAXIMUM_POOL_STATE', 'nk.web.log': 'WEB_LOG_ADDRESS', 'outcome': 'OUTCOME_LABEL', 'pending': 'PENDING_POOL_STATE', 'queue': 'QUEUE_LABEL', 'result': 'RESULT_LABEL', 'service': 'SERVICE_LABEL', 'state': 'STATE_LABEL', 'status': 'STATUS_LABEL', 'store': 'STORE_LABEL'}
FILES = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/'+p+'Test.java' for p in ('ApiMetricCatalog','ApiScalarMetricExporter','DbPoolMetricRecorder')]


def inputs():
    normal = data.read_checked(data.BASE/'PG11158-api-metric-fixture-six-compile-v1/manifest.json',
        '580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    records = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows = [r for r in records if r['path'] in FILES and r['rule'] == 'AvoidDuplicateLiterals']
    assert len(rows) == 23
    table = {}
    for row in rows:
        path = row['path']
        before = (snapshot/path).read_text()
        assert data.sha(before.encode()) == row['inputSha256'] == normal['begin']['inputHashes'][path]
        match = re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
        assert match is not None and match[1] in NAMES
        literal = json.dumps(match[1],ensure_ascii=False)
        found = [m for m in LEX.finditer(before) if m.group() == literal]
        assert len(found) == int(match[2]) and before[:found[0].start()].count('\n')+1 == row['line']
        name = NAMES[match[1]]
        assert not any(m.group() == name for m in LEX.finditer(before))
        table.setdefault(path,[]).append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
    assert set(table) == set(FILES)
    return normal,snapshot,table



def transformed(before,stem,rows):
    return literal_transform(before,stem,rows)


def emit():
    _,snapshot,table = inputs()
    patch = '*** Begin Patch\n'
    for path,rows in table.items():
        before = (snapshot/path).read_text()
        assert (data.ROOT/path).read_text() == before
        after = transformed(before,Path(path).stem,rows)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot,table = inputs()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes = []
    for path,rows in table.items():
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after) == canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=changes,constantsAdded=23,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()


