"""Handwritten SS193 directory/inode/closed argv vectors; no VM preparation or command."""
import stat
from pg471_prepare_native import identity_ok,parent_after,configuration,ROLES
checks=0
def check(ok):
 global checks
 assert ok,'independent SSC193 vector'
 checks+=1
check(ROLES=={'root-api193':(0,0),'root-web193':(0,0),'ordinary-api193':(999,981),'ordinary-web193':(997,980)})
for directory,uid,gid,mode,links,kind in [(True,0,0,0o711,7,stat.S_IFDIR),(True,999,981,0o700,2,stat.S_IFDIR),(True,997,980,0o700,2,stat.S_IFDIR),(False,0,0,0o644,1,stat.S_IFREG)]:
 v=(1,42,uid,gid,mode,links,kind);check(identity_ok(v,uid,gid,mode,directory));check(not identity_ok(None,uid,gid,mode,directory));check(not identity_ok(list(v),uid,gid,mode,directory))
 for n in range(7):
  for x in [None,True,'wrong']:
   wrong=list(v);wrong[n]=x;check(not identity_ok(tuple(wrong),uid,gid,mode,directory))
 for n,x in [(0,0),(1,0),(2,uid+1),(3,gid+1),(4,mode+1),(5,1 if directory else 2),(6,stat.S_IFLNK)]:
  wrong=list(v);wrong[n]=x;check(not identity_ok(tuple(wrong),uid,gid,mode,directory))
before=(1,42,0,0,0o711,7);after=(1,42,0,0,0o755,11)
check(parent_after(before,after));check(not parent_after(None,after));check(not parent_after(before,None))
for n in range(6):
 wrong=list(after);wrong[n]+=1;check(not parent_after(before,tuple(wrong)))
for role in ['api','web']:
 base='!/usr/bin/java --enable-native-access=ALL-UNNAMED -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.RootServiceLauncher '+role.upper()
 expected=('# SSC193194 isolated PT only; default signed base unchanged, no vendor pathname writer\n[Service]\nExecStart=\nExecStart=!/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid='+role.upper()+'-${INVOCATION_ID}-root --enable-native-access=ALL-UNNAMED -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.RootServiceLauncher '+role.upper()+'\nReadWritePaths=\nReadWritePaths='+('/srv/schubert-nk/data/transfer ' if role=='api' else '')+'/run/schubert-nk/pt-coverage/root-'+role+'193 /run/schubert-nk/pt-coverage/ordinary-'+role+'193\n').encode('ascii')
 check(configuration(role,base)==expected)
 for r,b in [(None,base),('batch',base),(role,None),(role,''),(role,base+'\n'),(role,base+' OTHER'),(role,base.replace('!/usr/bin/java','!/arbitrary/java')),(role,base.replace(' -cp ',' -javaagent:/arbitrary.jar -cp '))]:
  try:configuration(r,b);raise RuntimeError('must reject')
  except AssertionError:checks+=1
print('PG471_NATIVE_PREPARATION independentAssertions='+str(checks)+' productionPT0=true nativeMutation0=true')
