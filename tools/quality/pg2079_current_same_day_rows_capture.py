"""Read-only current newrun 24-table independent deletion/skip/backup oracle after genuine DONE."""
import inspect
import json
from pg1446_current_cold_stage import W
import pg2023_fresh_resume_rows_oracle as transport
from pg2078_current_same_day_rows_oracle import source

SLOT='pg2079-current-same-day-rows-capture-v1'


def payload():
    actual=json.loads((W/'pg2074-current-newrun-live-binding-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['productionSource']!=transport.SOURCE:raise ValueError('actual current noargs binding required')
    binding=actual['binding']
    raw=source()+"\nRUN="+repr(binding['run'])+'\nCUT='+repr(binding['cutoff'])+'\n'+r'''
import hashlib,os,pathlib,subprocess
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');br=(base/'pg2072-current-noargs-newrun-once-v1/before.private.json').read_bytes()
require(hashlib.sha256(br).hexdigest()=='796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05');before=json.loads(br)
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
for table in before['rows']:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+='commit;'
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=20);require(r.returncode==0 and 0<len(r.stdout)<=67108864)
now={}
for line in r.stdout.splitlines():
 v=json.loads(line);require(v['table']not in now);now[v['table']]=v['rows']
upper=datetime.datetime.now(datetime.timezone.utc).isoformat();result=qualify(before['rows'],now,RUN,CUT,upper)
out=base/'pg2079-current-same-day-rows-capture-v1';os.umask(0o077);out.mkdir(mode=0o700)
with(out/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump({'rows':now,'upper':upper,'result':result},f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({**result,'actualExit':0,'beforeSha256':hashlib.sha256(br).hexdigest(),'afterSha256':hashlib.sha256((out/'after.private.json').read_bytes()).hexdigest(),'startsStopsSqlWrites0':True,'privateOnly':True}))
'''
    from pyflakes.api import check
    if check(raw,'<whole current same-day newrun rows oracle>'):raise ValueError('all current rows exports required')
    compile(raw,'<same-day current independent rows>','exec');return raw


def entry():
    raw=inspect.getsource(transport.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2076-current-newrun-terminal-receipt-v1')
    ns={**transport.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current newrun readonly rows entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
