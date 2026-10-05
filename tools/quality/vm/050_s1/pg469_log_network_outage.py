"""SS324§9/351: actual WEB->Broker link refusal, not broker process stop/CHR PASS.

Dedicated PG/PT guest only. A new table affects uid997 IPv4 loopback61616 only.
All original nft rules must be empty; exact table is removed in finally, never flush.
No DB writes/credential reads/deployment/start/stop. HTTP itself creates test logs.
Raw cookies/events/rows remain Root-private; output only aggregates and hashes.
"""
import datetime, hashlib, http.client, json, os, pathlib, re, ssl, subprocess, time, uuid
SOURCE='d3bba6db6eb9fec13e4847a10541cf337f575731'
TABLE='pg469_log_outage_v1'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg469-log-network-outage-v1')
PEERS={'schubert-nk-web.service':('2006107','88e5d93fbeb443f9a1c3c769105c6c4d'),
 'schubert-nk-api.service':('2004047','5382161425dd4edcac8758357f747c0e'),
 'caddy.service':('2011228','9aa28af50ac74d84a6c6067f26619356'),
 'artemis.service':('1887227','0c97d581cb0d460389c777b8052c3284')}
def command(args, data=None):
    r=subprocess.run(args,input=data,capture_output=True,timeout=10)
    if r.returncode:raise RuntimeError('fixed native command refused')
    return r.stdout
def save(name,value):
    with os.fdopen(os.open(SAVE/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:
        f.write(value);f.flush();os.fsync(f.fileno())
def peer_snapshot():
    result={}
    for unit,(pid,inv) in PEERS.items():
        raw=command(['/usr/bin/systemctl','show',unit,'--property=MainPID,InvocationID,ActiveState,SubState,ControlPID,Job'])
        d=dict(line.split('=',1) for line in raw.decode().splitlines())
        assert d==dict(MainPID=pid,InvocationID=inv,ActiveState='active',SubState='running',ControlPID='0',Job='')
        result[unit]=d
    return result
def query(sql):
    raw=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],('begin read only; set local statement_timeout=\'5s\';\n'+sql+';\ncommit;').encode())
    return json.loads(raw)
def rows(keys):
    assert keys and len(keys)==5 and len(set(keys))==5
    literals=','.join("'"+str(uuid.UUID(key))+"'" for key in keys)
    return query("select json_build_object('outbox',coalesce((select json_agg(json_build_object('event',message_id,'status',status,'attempts',attempt_count) order by message_id) from schubert_web_session.web_log_outbox where message_id in ("+literals+")),'[]'::json),'db',coalesce((select json_agg(json_build_object('event',source_message_id,'category',category,'action',action,'service',service) order by source_message_id) from schubert.app_logs where source_message_id in ("+literals+")),'[]'::json))")
def blocked_rows(value,keys):
    if not isinstance(value,dict) or set(value)!= {'outbox','db'} or value['db']!=[] or not isinstance(value['outbox'],list):return False
    seen=set()
    for row in value['outbox']:
        if not isinstance(row,dict) or set(row)!= {'event','status','attempts'}:return False
        if row['event'] not in keys or row['event'] in seen or row['status']!='ERROR' or type(row['attempts']) is not int or not 1<=row['attempts']<=100:return False
        seen.add(row['event'])
    return seen==set(keys)
def recovered_rows(value,keys):
    if not isinstance(value,dict) or set(value)!= {'outbox','db'}:return False
    if not isinstance(value['outbox'],list) or not isinstance(value['db'],list):return False
    seen=set()
    for row in value['outbox']:
        if not isinstance(row,dict) or set(row)!= {'event','status','attempts'}:return False
        if row['event'] not in keys or row['event'] in seen or row['status']!='SENT' or type(row['attempts']) is not int or row['attempts']<1:return False
        seen.add(row['event'])
    projected=set()
    for row in value['db']:
        if not isinstance(row,dict) or row.get('event') not in keys or row.get('event') in projected:return False
        if row != dict(event=row['event'],category='REQUEST',action='HTTP_REQUEST_COMPLETED',service='WEB'):return False
        projected.add(row['event'])
    return seen==projected==set(keys)
def main():
    assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
    assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG469')
    assert json.loads(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes())['source']['commit']==SOURCE
    before=peer_snapshot();original=command(['/usr/sbin/nft','list','ruleset']);assert original==b''
    SAVE.mkdir(mode=0o700);save('reserved.private.json',json.dumps({'source':SOURCE,'peers':before,'table':TABLE,'started':datetime.datetime.now(datetime.timezone.utc).isoformat()}).encode())
    start=datetime.datetime.now(datetime.timezone.utc)
    installed=False
    try:
        # Reserve before the command: even an unknown client exit triggers exact-table cleanup.
        installed=True
        command(['/usr/sbin/nft','-f','-'],('add table inet '+TABLE+'\nadd chain inet '+TABLE+' output { type filter hook output priority -10; policy accept; }\nadd rule inet '+TABLE+' output meta skuid 997 ip daddr 127.0.0.1 tcp dport 61616 counter reject with tcp reset\n').encode())
        context=ssl.create_default_context(cafile='/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt')
        for _ in range(5):
            c=http.client.HTTPSConnection('10.0.2.15',55160,context=context,timeout=5)
            try:
                c.request('GET','/login');r=c.getresponse();body=r.read(131073)
                assert r.status==200 and len(body)<=131072 and b'schubert NK' in body
            finally:c.close()
        raw=command(['/usr/bin/journalctl','_SYSTEMD_INVOCATION_ID='+PEERS['schubert-nk-web.service'][1],'--since='+start.strftime('%Y-%m-%d %H:%M:%S UTC'),'--output=json','--no-pager'])
        save('local.private.jsonl',raw);events=[]
        for line in raw.splitlines():
            row=json.loads(line)
            if row.get('_PID')!=PEERS['schubert-nk-web.service'][0]:continue
            m=re.fullmatch(r'(?:(?:INFO|WARNING|SEVERE): )?(\{.*\})',row.get('MESSAGE',''))
            if not m:continue
            event=json.loads(m.group(1))
            if event.get('action')=='HTTP_REQUEST_COMPLETED' and event.get('path')=='/login' and event.get('httpMethod')=='GET' and event.get('status')==200:
                at=datetime.datetime.fromisoformat(event['timestamp'].replace('Z','+00:00'))
                if at>=start:events.append(event)
        keys=[str(uuid.UUID(e['messageId'])) for e in events];assert len(keys)==len(set(keys))==5
        deadline=time.monotonic()+45
        while True:
            blocked=rows(keys)
            if blocked_rows(blocked,keys):break
            assert time.monotonic()<deadline;time.sleep(1)
        firewall=command(['/usr/sbin/nft','list','table','inet',TABLE]);save('firewall.private.txt',firewall)
        m=re.search(rb'counter packets ([0-9]+) bytes ([0-9]+)',firewall);assert m and int(m[1])>0
        save('blocked.private.json',json.dumps(blocked).encode());assert peer_snapshot()==before
    finally:
        if installed:
            probe=subprocess.run(['/usr/sbin/nft','list','table','inet',TABLE],capture_output=True,timeout=10)
            if probe.returncode==0:command(['/usr/sbin/nft','delete','table','inet',TABLE])
            assert command(['/usr/sbin/nft','list','ruleset'])==original
            save('restored.private.json',b'{"originalRulesetRestored":true}')
    deadline=time.monotonic()+360
    while True:
        recovered=rows(keys)
        if recovered_rows(recovered,keys):break
        assert time.monotonic()<deadline;time.sleep(1)
    save('recovered.private.json',json.dumps(recovered).encode());assert peer_snapshot()==before
    summary=dict(source=SOURCE,events=5,http200=5,blockedErrors=5,dbBeforeRecovery=0,afterSent=5,afterDbExactOnce=5,firewallRestored=True,samePeers=True,brokerProcessStopped=False,actualWebBrokerCommunicationOutage=True,chrPass=False,formal=False,localSha256=hashlib.sha256(raw).hexdigest(),finished=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save('complete.safe.json',json.dumps(summary,indent=2).encode());print(json.dumps(summary))
if __name__=='__main__':
    try:main()
    except BaseException as failure:
        print(json.dumps({'failureType':type(failure).__name__,'accepted':False,'privateEvidence':str(SAVE)}))
        raise SystemExit(1)
