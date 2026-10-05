"""Read-only D3 native REQUEST event correlation. Not an outage/replay or CHR acceptance."""
import datetime,hashlib,json,os,pathlib,re,subprocess,sys,uuid
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='d3bba6db6eb9fec13e4847a10541cf337f575731'
INV='88e5d93fbeb443f9a1c3c769105c6c4d'
PID='2006107'
START=datetime.datetime.fromisoformat('2026-10-05T16:47:00+00:00')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-oBatchMode=yes','-oConnectTimeout=5','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
def command(text,timeout=20):
    r=subprocess.run(SSH+[text],text=True,capture_output=True,timeout=timeout)
    assert r.returncode==0
    return r.stdout
def private(name,data):
    with os.fdopen(os.open(WORK/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
def timestamp(value):
    return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(datetime.timezone.utc)
def events(journal,end):
    result={}
    for record in journal:
        if record.get('_SYSTEMD_INVOCATION_ID')!=INV or record.get('_PID')!=PID: continue
        message=record.get('MESSAGE','')
        m=re.fullmatch(r'(?:(?:INFO|WARNING|SEVERE): )?(\{.*\})',message)
        if not m: continue
        value=json.loads(m.group(1))
        if value.get('action')!='HTTP_REQUEST_COMPLETED' or value.get('category')!='REQUEST': continue
        at=timestamp(value['timestamp'])
        if not START<=at<=end: continue
        assert value['service']=='WEB' and value['details']['projectionStatus']=='PENDING'
        key=str(uuid.UUID(value['messageId']))
        assert key not in result
        result[key]=value
    return result
def compare(local,rows):
    projected={}
    for r in rows:
        key=str(uuid.UUID(r['event']))
        assert key not in projected
        projected[key]=r
    assert local and set(local)==set(projected)
    for key,event in local.items():
        row=projected[key]
        for a,b in [('requestId','request'),('correlationId','correlation'),('httpMethod','method'),('path','path'),('status','status'),('level','level'),('actorUsername','username'),('remoteAddress','address')]:
            assert event.get(a)==row.get(b)
        assert row['source']==key and row['action']=='HTTP_REQUEST_COMPLETED' and row['service']=='WEB' and row['category']=='REQUEST'
        assert timestamp(event['timestamp'])==timestamp(row['at'])
        assert event['details']['responseBytes']==row['details']['responseBytes']
        assert event.get('actorRole')==row['details'].get('actorRole')
        assert row['details']['projectionStatus']=='PENDING'
        assert min(event['elapsedMs'],999999999)==row['elapsed']
    return len(local)
def selftest():
    key='00000000-0000-0000-0000-000000000001'
    event={'messageId':key,'requestId':key,'correlationId':key,'httpMethod':'GET','path':'/logs','status':200,'level':'INFO','service':'WEB','category':'REQUEST','action':'HTTP_REQUEST_COMPLETED','timestamp':'2026-10-05T17:00:00.000Z','elapsedMs':7,'details':{'responseBytes':31,'projectionStatus':'PENDING'}}
    row={'event':key,'source':key,'request':key,'correlation':key,'method':'GET','path':'/logs','status':200,'level':'INFO','service':'WEB','category':'REQUEST','action':'HTTP_REQUEST_COMPLETED','at':'2026-10-05T17:00:00+00:00','elapsed':7,'details':{'responseBytes':31,'projectionStatus':'PENDING'}}
    assert compare({key:event},[row])==1
    rejected=0
    for field in row:
        bad=dict(row);bad[field]=({'responseBytes':32,'projectionStatus':'PENDING'} if field=='details' else None)
        try: compare({key:event},[bad])
        except (AssertionError,ValueError,TypeError,AttributeError): rejected+=1
        else: raise AssertionError('independent negative projection unexpectedly accepted')
    for bad in [[],[row,row]]:
        try:compare({key:event},bad)
        except AssertionError:rejected+=1
        else:raise AssertionError('missing/duplicate unexpectedly accepted')
    until=timestamp('2026-10-05T17:01:00Z')
    record={'_SYSTEMD_INVOCATION_ID':INV,'_PID':PID,'MESSAGE':'INFO: '+json.dumps(event)}
    assert events([record],until)=={key:event}
    assert events([{**record,'_PID':'1'}],until)=={}
    assert events([{**record,'_SYSTEMD_INVOCATION_ID':'0'*32}],until)=={}
    assert events([record],START)=={}
    try:events([record,record],until)
    except AssertionError:rejected+=1
    else:raise AssertionError('duplicate local unexpectedly accepted')
    print(json.dumps({'independentNegatives':rejected,'selftestExit':0,'mutations':0}))
def main():
    if sys.argv[1:]==['--selftest']:selftest();return
    assert sys.argv[1:]==['--native-v1']
    os.umask(0o077)
    before=command('systemctl show schubert-nk-web.service --property=MainPID,InvocationID,ActiveState,SubState')
    assert 'MainPID='+PID in before and 'InvocationID='+INV in before and 'ActiveState=active' in before and 'SubState=running' in before
    info=json.loads(command('curl --fail --silent --max-time 5 http://127.0.0.1:8081/actuator/info'))
    assert info=={'commit':SOURCE,'app':'0.1.0-SNAPSHOT','config':'1','schema':'027','protocol':'0.1.0-SNAPSHOT'}
    end=datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(seconds=10)
    raw=command('sudo -n journalctl _SYSTEMD_INVOCATION_ID='+INV+' --output=json --no-pager',40).encode()
    private('pg469-d3-web-journal-v1.private.jsonl',raw)
    local=events([json.loads(l) for l in raw.decode().splitlines() if l.strip()],end)
    sql="select coalesce(json_agg(json_build_object('event',message_id,'source',source_message_id,'request',request_id,'correlation',correlation_id,'method',http_method,'path',request_uri,'status',status_code,'level',level,'service',service,'category',category,'action',action,'at',logged_at,'elapsed',duration_ms,'username',actor_username,'address',host(remote_address),'details',details) order by id),'[]'::json) from schubert.app_logs where service='WEB' and category='REQUEST' and logged_at>='"+START.isoformat()+"' and logged_at<='"+end.isoformat()+"';"
    result=subprocess.run(SSH+['sudo -n -u postgres /usr/bin/psql -X -qAt -v ON_ERROR_STOP=1 -d schubert_nk'],input='begin read only;\n'+sql+'\ncommit;',text=True,capture_output=True,timeout=20)
    assert result.returncode==0
    private('pg469-d3-web-db-v1.private.json',result.stdout.encode())
    rows=json.loads(result.stdout);count=compare(local,rows)
    after=command('systemctl show schubert-nk-web.service --property=MainPID,InvocationID,ActiveState,SubState')
    assert after==before
    summary={'productionSource':SOURCE,'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cutoff':end.isoformat(),'localEventIdMatchedRows':count,'missing':0,'duplicates':0,'fieldMismatch':0,'samePeerBeforeAfter':True,'outageReplayTested':False,'chrPass':False,'mutations':0,'journalSha256':hashlib.sha256(raw).hexdigest(),'dbSha256':hashlib.sha256(result.stdout.encode()).hexdigest()}
    private('pg469-d3-log-readback-v1.safe.json',json.dumps(summary,indent=2).encode());print(json.dumps(summary))
if __name__=='__main__':
    try:main()
    except BaseException as failure:
        frames=[];tb=failure.__traceback__
        while tb:
            if tb.tb_frame.f_code.co_filename==__file__:frames.append(tb.tb_lineno)
            tb=tb.tb_next
        print(json.dumps({'failureType':type(failure).__name__,'ownSourceLines':frames,'accepted':False}),file=sys.stderr)
        sys.exit(1)
