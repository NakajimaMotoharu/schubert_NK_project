"""Forty-three same-value fixture names for supplied scalar metrics, no product execution."""
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

OUT=data.BASE/'PG11154-api-metric-fixture-plan-v1'
FILES=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/'+n+'Test.java' for n in
    ('MqMessageMetricRecorder','MqProcessingDurationMetricRecorder','DbQueryDurationMetricRecorder','InboxReplayMetricRecorder')]
NAMES={'0000':'SUCCESS_CODE','0200':'IDEMPOTENT_CODE','ASYNC_JOB_STATE_COUNTS':'ASYNC_COUNT_QUERY','DEBUG':'DEBUG_MODE',
    'FAILURE':'FAILURE_OUTCOME','LGNREQ01':'LOGIN_REQUEST_LAYOUT','OUTBOX_STATUS_COUNTS_OLDEST':'OUTBOX_COUNT_QUERY',
    'QSBREQ01':'SUBMIT_REQUEST_LAYOUT','QWKREQ01':'QUESTION_WORK_LAYOUT','RECEIVE':'RECEIVE_DIRECTION','SEND':'SEND_DIRECTION',
    'SUCCESS':'SUCCESS_OUTCOME','WLGEVT01':'WEB_LOG_EVENT_LAYOUT','address':'ADDRESS_LABEL','direction':'DIRECTION_LABEL',
    'flow':'FLOW_LABEL','layout':'LAYOUT_LABEL','nk.sync.request':'SYNC_REQUEST_ADDRESS',
    'nk_db_query_duration_seconds':'DB_DURATION_NAME','nk_inbox_replays_total':'INBOX_REPLAY_NAME',
    'nk_mq_messages_total':'MQ_EVENT_NAME','nk_mq_processing_duration_seconds':'MQ_DURATION_NAME',
    'outcome':'OUTCOME_LABEL','query_id':'QUERY_LABEL','result':'RESULT_LABEL'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11132-web-presentation-six-compile-v1/manifest.json','6ba6867e803958aa47837d6628faeecdf42917be8d23bff7a38b5e1b18579eee')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[r for r in original if r['path'] in FILES and r['rule']=='AvoidDuplicateLiterals']
    assert len(rows)==39
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
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,factoryCallConstant=2))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=39,factoryCallConstants=4,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
