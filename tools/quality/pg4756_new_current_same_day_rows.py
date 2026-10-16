"""Actual all24 read-only capture, raw fsync before parse, independent same-day oracle."""
import json
from pyflakes.api import check
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as terminal
import pg4742_same_day_query_oracle as oracle
import pg4744_same_day_query_preflight as preflight

SLOT='pg4756-new-current-same-day-all24-v1'


def key_source():
    raw=preflight.payload();start=raw.index("path=Path('/etc/schubert-nk/credentials/api-inbox-response-aes-current')")
    return raw[start:raw.index("before=json.loads(raw)['rows'];now=")]


def payload(observed,before_hash):
    raw='SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nBINDING='+repr(observed)+'\nBEFORE_SHA='+repr(before_hash)+'\nSLOT='+repr(SLOT)+'\nONCE='+repr(admission.ONCE)+'\n'
    raw+=oracle.source()+r'''
import base64,hashlib,os,stat,subprocess
from pathlib import Path
require(os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
base=Path('/var/lib/pgpt-s1-preservation');out=base/SLOT;require(not os.path.lexists(out));os.umask(0o077);out.mkdir(mode=0o700)
def preserve(name,blob):
 require(type(blob)is bytes)
 with(out/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
 fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
br=(base/ONCE/'before.private.json').read_bytes();require(hashlib.sha256(br).hexdigest()==BEFORE_SHA)
before=json.loads(br)['rows'];require(len(before)==24)
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');mr=manifest.read_bytes()
require(hashlib.sha256(mr).hexdigest()==BOM and json.loads(mr)['source']['commit']==SOURCE)
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
for table in before:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+='commit;'
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=20)
preserve('sql-stdout.private.jsonl',r.stdout);preserve('sql-stderr.private.log',r.stderr);preserve('sql-exit.private.json',json.dumps({'actualExit':r.returncode}).encode())
require(r.returncode==0 and 0<len(r.stdout)<=67108864)
now={}
for line in r.stdout.splitlines():
 v=json.loads(line);require(v['table']not in now);now[v['table']]=v['rows']
upper=datetime.datetime.now(datetime.timezone.utc).isoformat()
preserve('after.private.json',json.dumps({'rows':now,'upper':upper},sort_keys=True).encode())
'''+key_source()+r'''
try:
 result=qualify(before,now,BINDING['run'],BINDING['cutoff'],upper)
 expected=candidates(before,BINDING['cutoff']);inbox=classify_query_inbox(before,expected['inbox_scan_candidates'],KEY,LAYOUTS)
finally:KEY[:]=b'\0'*len(KEY)
require(manifest.read_bytes()==mr and(base/ONCE/'before.private.json').read_bytes()==br)
value={**result,'actualExit':0,'source':SOURCE,'BOM':BOM,'run':BINDING['run'],'cutoff':BINDING['cutoff'],'upper':upper,'beforeSha256':BEFORE_SHA,'afterSha256':hashlib.sha256((out/'after.private.json').read_bytes()).hexdigest(),'rawSqlSha256':hashlib.sha256(r.stdout).hexdigest(),'expectedInboxDeleted':len(inbox['deleted']),'retainedNotificationCandidates':len(expected['notifications']),'startsStopsSqlWrites':0,'rawExported':False,'formalAccepted':False}
preserve('manifest.safe.json',json.dumps(value,sort_keys=True).encode());print(json.dumps(value))
'''
    if check(raw,'<new all24 same-day>'):raise ValueError('complete standalone namespace')
    compile(raw,'<private raw first all24>','exec');return raw


def main():
    term=json.loads((admission.W/terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(term['actualExit'])is int and term['actualExit']==0 and term['source']==admission.SOURCE and term['result']['genuineRootDone']is True):raise ValueError('same genuine terminal first')
    return admission.execute(SLOT,payload(admission.live(),admission.before()),90)


if __name__=='__main__':raise SystemExit(main())
