"""Thirty-three same-value Web supplied metric fixture names; no target execution."""
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

OUT=data.BASE/'PG11206-web-supplied-metric-fixture-plan-v1'
FILES=['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/'+n+'Test.java' for n in ('MediaBytesMetricRecorder','MediaStreamsMetricRecorder','WebDbPoolMetricRecorder','WebOutboxMetricRecorder')]
NAMES={'AUDIO': 'AUDIO_TYPE_NAME', 'DEBUG': 'DEBUG_MODE', 'DOWNLOAD': 'DOWNLOAD_MODE_NAME', 'ERROR': 'ERROR_STATUS', 'INLINE': 'INLINE_MODE_NAME', 'MUSIC': 'MUSIC_TYPE_NAME', 'PENDING': 'PENDING_STATUS', 'RANGE': 'RANGE_MODE_NAME', 'SENT': 'SENT_STATUS', 'VIDEO': 'VIDEO_TYPE_NAME', 'WEB': 'WEB_SERVICE_VALUE', 'active': 'ACTIVE_POOL_STATE', 'idle': 'IDLE_POOL_STATE', 'max': 'MAXIMUM_POOL_STATE', 'media_type': 'MEDIA_TYPE_LABEL', 'mode': 'MODE_LABEL', 'nk_media_bytes_total': 'MEDIA_BYTES_NAME', 'nk_media_streams': 'MEDIA_STREAMS_NAME', 'nk_outbox_oldest_seconds': 'OUTBOX_AGE_NAME', 'nk_outbox_rows': 'OUTBOX_ROWS_NAME', 'pending': 'PENDING_POOL_STATE', 'service': 'SERVICE_LABEL', 'status': 'STATUS_LABEL', 'store': 'STORE_LABEL'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json','b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[r for r in original if r['path'] in FILES and r['rule']=='AvoidDuplicateLiterals']
    assert len(rows)==32
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
    if stem!='MediaBytesMetricRecorderTest':
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
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,factoryCallConstant=2 if Path(path).stem=='MediaBytesMetricRecorderTest' else None))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=32,factoryCallConstants=1,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
