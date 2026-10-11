"""Actual PostgreSQL parses the generated peer SQL in read-only rolled-back scopes."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
import pg1380_bootstrap_role_sources_v3 as source
from pg1377_bootstrap_role_dispatch import SSH,W,SOURCE

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean source required')
    if (W/'pg1382-role-fixed-ref-handoff-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual prior owner recovery required')
    raw=source.files()['pg1380_bootstrap_role_refs.py'];tree=ast.parse(raw)
    holder=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='holder')
    query=next(n for n in holder.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='q'for t in n.targets))
    queries=[]
    for backend in (1,42,2147483647):
        scope={'backend':backend};exec(compile(ast.Module(body=[query],type_ignores=[]),'<actual generated SQL>','exec'),scope)
        queries.append(scope['q'])
    start=datetime.datetime.now(datetime.timezone.utc)
    code="import subprocess,json,hashlib\nqueries="+repr(queries)+"\n"
    code+="for q in queries:\n r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=('BEGIN READ ONLY; EXPLAIN '+q+'ROLLBACK;').encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)\n if r.returncode:raise ValueError('generated peer SQL parse refused')\nprint(json.dumps({'parsedQueries':len(queries),'sqlWrites':0,'analyze':False}))\n"
    base=W/'pg1383-role-sql-parse-v1'
    with base.with_suffix('.private.log').open('xb')as f:
        r=subprocess.run(SSH+['sudo -n python3 -B -'],input=code.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    result={'run':'PG1383-role-sql-parse-v1','actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parsedQueries':3 if r.returncode==0 else None,'sqlWrites':0,'formalAccepted':False,'helperSha256':hashlib.sha256(raw.encode()).hexdigest(),'privateLogSha256':hashlib.sha256(base.with_suffix('.private.log').read_bytes()).hexdigest()}
    with base.with_suffix('.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    with base.with_suffix('.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    print(json.dumps(result));return r.returncode

if __name__=='__main__':raise SystemExit(main())
