"""Twenty-five same-value Batch supplied metric/label fixture names; no product execution."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11234-batch-supplied-metric-label-fixture-plan-v1'
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/'+n+'Test.java' for n in ('ProcessRestartMetricRecorder','IntegrityFailureMetricRecorder','BatchMetricLabelPolicy')]
NAMES={'.part': 'PART_SUFFIX', '.ready': 'READY_SUFFIX', 'BACKUP_DB': 'BACKUP_DB_STEP_NAME', 'CONFIG': 'CONFIG_AREA_NAME', 'DEBUG': 'DEBUG_MODE', 'HASH': 'HASH_AREA_NAME', 'NONZERO_EXIT': 'NONZERO_EXIT_REASON', 'OOM': 'OOM_REASON', 'PATH': 'PATH_AREA_NAME', 'SIGNAL_EXIT': 'SIGNAL_EXIT_REASON', 'UNKNOWN': 'UNKNOWN_REASON', 'WEB': 'WEB_SERVICE_NAME', 'actor': 'ACTOR_LABEL', 'area': 'AREA_LABEL', 'nk_integrity_failures_total': 'INTEGRITY_COUNTER_NAME', 'nk_process_restarts_total': 'RESTART_COUNTER_NAME', 'reason': 'REASON_LABEL', 'service': 'SERVICE_LABEL', 'step': 'STEP_LABEL', 'suffix': 'SUFFIX_LABEL'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11210-web-supplied-metric-fixture-six-compile-v1/manifest.json','11fb92b0b53b9dba26b93c8aa3e08c09c6c754b1b43fca1c20767ac270666d73')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[r for r in original if r['path'] in FILES and r['rule']=='AvoidDuplicateLiterals']
    assert len(rows)==23
    table={}
    for row in rows:
        path=row['path']
        before=(snapshot/path).read_text()
        assert data.sha(before.encode())==row['inputSha256']==normal['begin']['inputHashes'][path]
        match=re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
        assert match and match[1] in NAMES
        literal=json.dumps(match[1],ensure_ascii=False)
        found=[m for m in LEX.finditer(before) if m.group()==literal]
        assert len(found)==int(match[2]) and before[:found[0].start()].count('\n')+1==row['line']
        name=NAMES[match[1]]
        assert not any(m.group()==name for m in LEX.finditer(before))
        table.setdefault(path,[]).append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
    assert set(table)==set(FILES)
    return normal,snapshot,table


def transformed(before,stem,rows):
    after=strings(before,stem,rows)
    if stem=='BatchMetricLabelPolicyTest':
        return after
    pattern=r'(if \((?:factories|registrations)\.incrementAndGet\(\) == )2(\))'
    after,count=re.subn(pattern,r'\g<1>FAILURE_FACTORY_CALL\2',after)
    assert count==1 and 'FAILURE_FACTORY_CALL' not in before
    marker='class '+stem+' {'
    assert after.count(marker)==1
    return after.replace(marker,marker+'\n  private static final int FAILURE_FACTORY_CALL = 2;',1)


def emit():
    _,snapshot,table=inputs()
    patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text()
        assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,rows)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for path,rows in table.items():
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,factoryCallConstant=2 if Path(path).stem!='BatchMetricLabelPolicyTest' else None))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=23,factoryCallConstants=2,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
