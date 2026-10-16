"""SS324 12.8/UI236 independent NONE query cleanup plus SS341 same-day skips.

Expected deletions use only immutable BEFORE and independently authenticated wire.
No Production methods, current-row inference, DB write or clock change.
"""
import ast
import inspect
import json
import re
from pathlib import Path
import pg2078_current_same_day_rows_oracle as previous
import pg553_inbox_oracle as wire
from pg553_inbox_oracle import require,plaintext

NTS={'dataLength':48,'recordLength':624,'maximumRecords':50,
 'dataFields':[['Page',0,6,'N','M'],['Size',6,3,'N','M'],['Amount',9,9,'N','M'],['Pages',18,6,'N','M'],['First',24,9,'N','M'],['Last',33,9,'N','M'],['Reserved',42,6,'X','F']],
 'recordFields':[['Notification ID',0,12,'N','M'],['Public ID',12,26,'X','M'],['Kind',38,12,'X','M'],['Status',50,12,'X','M'],['Accepted',62,17,'N','M'],['Updated',79,17,'N','M'],['Summary',96,512,'X','M'],['Deleted',608,1,'B','M'],['Reserved',609,15,'X','F']]}
QSD={'dataLength':8352,'recordLength':0,'maximumRecords':0,
 'dataFields':[['Question ID',0,12,'N','M'],['Public ID',12,26,'X','M'],['Username',38,64,'X','M'],['Answer status',102,12,'X','M'],['Question',114,4096,'X','M'],['Answer',4210,4096,'X','O'],['Accepted',8306,17,'N','M'],['Answered',8323,17,'X','C'],['Reserved',8340,12,'X','F']], 'recordFields':[]}


def base_source():
    raw=inspect.getsource(wire.validate).replace('def validate(','def validate_base(',1)
    raw=raw.replace("if rid=='UDTRSP01' else", "if rid in {'UDTRSP01','QSDRSP01'} else")
    return raw.replace("50 if rid=='USRRSP01' else 100","50 if rid in {'USRRSP01','NTSRSP01'} else 100")


def validate_base(row,body,layout):
    ns=dict(vars(wire));exec(base_source(),ns);return ns['validate_base'](row,body,layout)


def validate_query(row,body,layout):
    # Existing independent generic header/field checks, restricted literal codes.
    validate_base(row,body,layout)
    code=bytes(body[208:212]);rid=row['response_layout_id']
    require(code in ({b'0000',b'0104'}if rid=='QSDRSP01'else{b'0000',b'9001'}if rid=='NTSRSP01'else{b'0000',b'0104'}))
    if code!=b'0000':return
    data=body[256:256+layout['dataLength']]
    if rid=='QSDRSP01':
        require(int(data[:12])>0)
        require(re.fullmatch(b'[0-9A-HJKMNP-TV-Z]{26}',bytes(data[12:38]))is not None)
        state=bytes(data[102:114]).rstrip(b' ');require(state in {b'ANSWERED',b'UNANSWERED',b'ERROR'})
        require(bool(bytes(data[8323:8340]).strip())==(state==b'ANSWERED'))
        if state!=b'ANSWERED':require(data[4210:8306]==b' '*4096)
    elif rid=='NTSRSP01':
        size=int(data[6:9]);require(size==50)
        count=int(body[193:199])
        for index in range(count):
            record=body[304+624*index:304+624*(index+1)]
            require(int(record[:12])>0 and re.fullmatch(b'[0-9A-HJKMNP-TV-Z]{26}',bytes(record[12:38]))is not None)
            kind=bytes(record[38:50]).rstrip(b' ');state=bytes(record[50:62]).rstrip(b' ')
            require(kind in {b'ACCEPTED',b'COMPLETED',b'ERROR'}and state in {b'RECEIVED',b'PROCESSING',b'COMPLETED',b'ERROR',b'CANCELLED'})
            if record[608:609]==b'1':require(bytes(record[96:608]).rstrip(b' ').decode()=='削除済み')


def classify_query_inbox(rows,selected,key,layouts):
    ids=set(selected);found={r['message_id']:r for r in rows['schubert.request_inbox']if r['message_id']in ids}
    require(set(found)==ids);sessions={str(r['id'])for r in rows['schubert.auth_sessions']}
    deleted=[];protected=[]
    for mid,row in found.items():
        if (row['request_layout_id'],row['response_layout_id'],row['processing_state'],row['result_ref_type'],row['owner_user_id'])==('LGNREQ01','LGNRSP01','COMPLETED','AUTH_SESSION',None):
            require(row['result_ref_uuid']is not None and str(row['result_ref_uuid'])not in sessions);protected.append(mid)
        else:
            require(row['response_layout_id']in {'UDTRSP01','QSDRSP01','NTSRSP01'})
            body=plaintext(row,key);fixed=None
            try:
                fixed=query_wire(row['response_layout_id'],body)
                validate_query(row,fixed,layouts[row['response_layout_id']]);deleted.append(mid)
            finally:
                body[:]=b'\0'*len(body)
                if fixed is not None:fixed[:]=b'\0'*len(fixed)
    return {'deleted':sorted(deleted),'protected':sorted(protected)}


def query_wire(layout,body):
    require(type(body)is bytearray)
    if body[:7]==b'NKQRY1\0':
        require(layout in {'QSDRSP01','QSSRSP01'}and len(body)>=264 and bytes(body[7:8])in {b'U',b'A'})
        return bytearray(body[8:])
    require(body[:11]==b'SCHBNK01001')
    return bytearray(body)


def source():
    raw=previous.source()
    # Qualified independent2078 route is expanded, not silently treated applicable.
    raw=raw.replace("and not inbox['deleted']",'')
    raw=raw.replace("['notifications','questions','app_logs'","['questions','app_logs'")
    raw=raw.replace("'schubert.mq_outbox':expected['schubert.mq_outbox']}","'schubert.mq_outbox':expected['schubert.mq_outbox'],'schubert.request_inbox':inbox['deleted']}")
    raw=raw.replace("outboxes=sum(len(expected_deleted[t])for t in expected_deleted)","outboxes=len(expected[OUTBOX])+len(expected['schubert.mq_outbox'])")
    raw=raw.replace("outboxes+len(inbox['protected'])","outboxes+len(inbox['protected'])+len(inbox['deleted'])")
    raw=raw.replace("row['success_count']==outboxes","row['success_count']==outboxes+len(inbox['deleted'])")
    raw=raw.replace("p['inspected_count']==p['protected_count']==len(inbox['protected'])and p['deleted_count']==0","p['inspected_count']==len(expected['inbox_scan_candidates'])and p['protected_count']==len(inbox['protected'])and p['deleted_count']==len(inbox['deleted'])")
    raw=raw.replace("max(inbox['protected'],default=None)","max(expected['inbox_scan_candidates'],default=None)")
    raw=raw.replace("sum(map(len,expected_deleted.values()))","len(expected[OUTBOX])+len(expected['schubert.mq_outbox'])")
    # Notification candidates are retained because CLEAN_NOTIFICATION is skipped.
    raw=raw.replace("require('CLEAN_SESSION'in skips and 'CLEAN_LOG'in skips)","require({'CLEAN_SESSION','CLEAN_LOG','CLEAN_NOTIFICATION'}<=skips)")
    nodes=ast.parse(raw).body
    existing=next(n for n in nodes if isinstance(n,ast.FunctionDef)and n.name=='classify_inbox')
    raw=raw.replace(ast.get_source_segment(raw,existing),"def classify_inbox(rows,selected):return classify_query_inbox(rows,selected,KEY,LAYOUTS)")
    generic=base_source()
    extra='\n'.join(inspect.getsource(f)for f in [wire.aad,wire.plaintext,wire.fields])+'\n'+generic+'\n'+inspect.getsource(validate_query)+'\n'+inspect.getsource(query_wire)+'\n'+inspect.getsource(classify_query_inbox)
    raw='import struct,unicodedata,zlib\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\n'+raw+'\n'+extra
    layouts=json.loads((Path(wire.__file__).parent/'pg478_independent_layouts.json').read_bytes())
    raw+='\nLAYOUTS='+repr({'UDTRSP01':layouts['UDTRSP01'],'QSDRSP01':QSD,'NTSRSP01':NTS})+'\n'
    from pyflakes.api import check
    if check('KEY=bytes(32)\n'+raw,'<same-day independent query oracle>'):raise ValueError('complete emitted namespace required')
    compile(raw,'<SS324/341 same-day NONE oracle>','exec');return raw


def namespace(key):
    ns={'KEY':key};exec(source(),ns);return ns


if __name__=='__main__':raise SystemExit('library only; guest preflight uses verified private before/key')
