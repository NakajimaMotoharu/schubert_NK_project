"""Current completed runtime retirement inside qualified owned full scopes.

SS343/353, PT-DEP-1224001..004. No Root/start/permit/DB writes.
"""
import ast
import inspect
import json
from pathlib import Path
import pg1223_completed_runtime_contract as contract
from pg1216_current_full32_stop_binding import generate as previous
from pg1220_current_full32_terminal_post import proof

BASE='/var/lib/pgpt-s1-preservation/pg1216-native-stop-v1/after.private.json'
SHA='21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36'
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')

def replace(s,a,b):
    if s.count(a)!=1:raise ValueError('exact current retirement source insertion rejected')
    return s.replace(a,b)

def generated():
    values={n.replace('1216','1224'):s.replace('Pg1216','Pg1224').replace('pg1216','pg1224').replace('PG1216','PG1224')for n,s in previous(proof()).items()}
    name='Pg1224NativeStop.java';j=values[name]
    j=replace(j,'"stop".equals(args[0])','"retire".equals(args[0])')
    j=replace(j,'new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg1224_native_refs.py").toString(),"stop",Integer.toString(pid))','new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg1224_native_refs.py").toString(),"retire",Integer.toString(pid))')
    start=j.index('              for(var unit:');end=j.index('              pulse();phase="DB_CLOSE";',start)
    j=j[:start]+'              phase="EXACT_COMPLETED_RUNTIME_RETIREMENT";refs.check("retire");phase="ALL_TERMINAL";refs.check("terminal");verifyOriginal();\n'+j[end:]
    j=j.replace('allEightOwnedTerminal=true','allTenAlreadyTerminal=true').replace('starts0=true\\noldUnknownNormalized=false','starts0=true\\nruntimeRetiredOnly=true\\noldUnknownNormalized=false')
    j=replace(j,'name.startsWith("stop:")','"retire".equals(name)')
    values[name]=j
    values['Pg1224NativeArgumentTest.java']=replace(values['Pg1224NativeArgumentTest.java'],'new String[]{"retire"}','new String[]{"stop"}')
    r=values['pg1224_native_refs.py']
    r=replace(r,"sys.argv[1]=='stop'","sys.argv[1]=='retire'")
    old='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/full32-stop-owner-handoff-v1/after.private.json'
    if r.count(old)!=2:raise ValueError('exact fixed before paths required')
    r=r.replace(old,BASE).replace('bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a',SHA)
    r=replace(r,"stages=[];captures=None;first=None","changed=False;first=None\n import pg1223_completed_runtime_contract as retirement")
    start=r.index("  for u,v in cfg.items():");end=r.index("  runtime=tree(",start)
    r=r[:start]+"  original_value=json.loads(original)\n  extra={k:tree(pathlib.Path(min(v,key=len)))for k,v in original_value['extraDurable'].items()}\n  files=original_value['unitFilesActual'];file_entries={p:metadata(pathlib.Path(p))+[hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()]for p in files if not changed or p!=retirement.TARGET}\n"+r[end:]
    r=replace(r,"'runtime':runtime}","'runtime':runtime,'native':tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}")
    start=r.index(' def check_data(now):');end=r.index(' def save(name,v):',start)
    r=r[:start]+" def check_data(now):\n  require(first is not None)\n  if changed:require(retirement.same_except_runtime(first,now,exec_record))\n  else:require(same_value(first,now))\n"+r[end:]
    start=r.index(" require(prior['source']");end=r.index(" print('REF_READY'",start)
    r=r[:start]+" require(all(same_value(first[k],v)for k,v in prior.items()))\n h.parent_receipt()\n for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)\n"+r[end:]
    start=r.index("  require(action in ");end=r.index("  if action=='release':",start)
    r=r[:start]+ACTION+r[end:]
    values['pg1224_native_refs.py']=r
    values['pg1223_completed_runtime_contract.py']=inspect.getsource(contract)
    # The oracle dependency is frozen alongside it; no host path or old source execution.
    values['pg847_configuration.py']=Path(__file__).with_name('pg847_configuration.py').read_text()
    for n,s in values.items():
        if n.endswith('.py'):compile(s,'<actual '+n+'>','exec')
    return values

ACTION=r'''
  require(action in ['before','retire','terminal','release'])
  check_data(capture_data(action!='release'))
  if action=='retire':
   require(not changed);directory=pathlib.Path(retirement.ROOT)
   flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC;fds=[]
   try:
    fd=os.open('/',flags);fds.append(fd)
    for part in ['run','systemd','system','schubert-nk-morning-controller.service.d']:
     child=os.open(part,flags,dir_fd=fd);fds.append(child)
     st=os.fstat(child);require(st.st_uid==st.st_gid==0 and stat.S_ISDIR(st.st_mode)and not st.st_mode&0o022 and not os.listxattr(child));fd=child
    retirement.retire_entry(fd,first['runtime'][retirement.ROOT]['metadata'],first['unitFilesActual'][retirement.TARGET])
    for index,part in enumerate(['run','systemd','system','schubert-nk-morning-controller.service.d'],1):
     s=os.stat(part,dir_fd=fds[index-1],follow_symlinks=False);t=os.fstat(fds[index]);require((s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)==(t.st_dev,t.st_ino,t.st_mode,t.st_uid,t.st_gid))
   finally:
    for fd in reversed(fds):os.close(fd)
   command(['/usr/bin/systemctl','daemon-reload']);changed=True;check_data(capture_data(True))
  if action in ['terminal','release']:
   require(changed)
   for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
'''

if __name__=='__main__':
    print(json.dumps({'files':sorted(generated()),'mutations0':True}))
