"""Fresh post-DONE full24 raw captured before parsing/comparison; no business writes."""
import json
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as acceptance
from pg1446_current_cold_stage import W

SLOT='pg4628-current-raw24-capture-v1'


def payload():
    return 'ONCE='+repr(admission.ONCE)+'\nSOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nBEFORE_SHA='+repr(admission.before())+r'''
import datetime,hashlib,json,os,pathlib,stat,subprocess
require=lambda v:None if v else(_ for _ in()).throw(ValueError('fresh raw24 observation refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');os.umask(0o077);save=base/'pg4628-current-raw24-capture-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
def persist(name,raw):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(raw).hexdigest()
p=base/ONCE/'before.private.json';s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1))
br=p.read_bytes();require(hashlib.sha256(br).hexdigest()==BEFORE_SHA);persist('before.private.json',br);before=json.loads(br)['database']['rows'];require(len(before)==24)
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');mr=manifest.read_bytes();require(hashlib.sha256(mr).hexdigest()==BOM and json.loads(mr)['source']['commit']==SOURCE)
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
import re
for table in before:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+='commit;'
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=20)
raw_sha=persist('sql-stdout.private.jsonl',r.stdout);persist('sql-stderr.private.log',r.stderr)
persist('sql-result.private.json',json.dumps({'actualExit':r.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},sort_keys=True).encode())
require(r.returncode==0 and 0<len(r.stdout)<=67108864)
now={}
for line in r.stdout.splitlines():
 v=json.loads(line);require(v['table']not in now);now[v['table']]=v['rows']
upper=datetime.datetime.now(datetime.timezone.utc).isoformat();image_sha=persist('after.private.json',json.dumps({'rows':now,'upper':upper},sort_keys=True).encode())
require(set(now)==set(before)and len(now)==24 and manifest.read_bytes()==mr and p.read_bytes()==br)
summary={table:{'before':len(before[table]),'after':len(now[table])}for table in before}
print(json.dumps({'actualExit':0,'source':SOURCE,'BOM':BOM,'beforeSha256':BEFORE_SHA,'rawSqlSha256':raw_sha,'imageSha256':image_sha,'upper':upper,'tableCounts':summary,'tables':24,'startsStopsSqlWrites':0,'rawExported':False,'oracleNotYetQualified':True,'formalAccepted':False}))
'''


def main():
    term=json.loads((W/acceptance.TERM/'manifest.safe.json').read_bytes())
    if term['actualExit']!=0 or term['source']!=admission.SOURCE or term['result']['genuineRootDone']is not True:raise ValueError('genuine same-source terminal0 first')
    return admission.execute(SLOT,payload())


if __name__=='__main__':raise SystemExit(main())
