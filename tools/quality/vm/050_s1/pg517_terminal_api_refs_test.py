"""Independent SSC209 namespace/stop fault oracles. No VM or live authority."""
import contextlib, copy, importlib.util, json, pathlib, sys, tempfile, types
from unittest.mock import patch
sys.modules.setdefault('dbus',types.SimpleNamespace())
import pg517_terminal_api_refs as h
count=0
h.revoked_phase=False
def check(v):
 global count
 count+=1
 if not v:raise AssertionError('single API independent oracle')
root='/run/schubert-nk/startup';epoch='31100027-4444-4333-8444-555555555555'
original={root:{'metadata':[28,1,0,0,16832,2,120,100,100],'sha256':None}}
for name in ['epoch.current',epoch+'.permit',epoch+'.owner',epoch+'.API.start.intent']:
 original[root+'/'+name]={'metadata':[28,len(original)+1,0,0,33152,1,0,100,100],'sha256':'b'*64}
check(h.startup_preserved(original,original))
after=copy.deepcopy(original);del after[root+'/'+epoch+'.API.start.intent'];after[root]['metadata'][6:]=[100,200,200]
check(h.startup_preserved(after,original))
for p in [None,{},dict(after,**{root+'/permit-start.intent':original[root]}),dict(after,**{root+'/'+epoch+'.WEB.start.intent':original[root]})]:check(not h.startup_preserved(p,original))
for path in after:
 for k in range(9):
  bad=copy.deepcopy(after);bad[path]['metadata'][k]+=1
  check(h.startup_preserved(bad,original)==(path==root and k in [6,7,8]))
 bad=copy.deepcopy(after);bad[path]['sha256']='a'*64;check(not h.startup_preserved(bad,original))
check(h.ORDER==['schubert-nk-expiry-cleanup.service','schubert-nk-cleanup.service','artemis.service'])
check(h.kernel_actor(['38602'],['','']))
for actors in [None,[],['38602','38602'],['38602','999'],['999'],{'38602'}]:check(not h.kernel_actor(actors,['']))
for children in [None,[],['999'],['','999'],[None],{' '}]:check(not h.kernel_actor(['38602'],children))
import pg517_confirm_ma as ma
args=[b'/opt/jdk-25.0.4/bin/java',b'-cp',b'/fixed/private/classes',b'Pg517TerminalApiRecovery',b'recover',b'']
check(ma.actor_arguments(args))
for v in [None,[],args[:-1],args[:-2]+[b'verify',b''],[b'/foreign']+args[1:],args[:-3]+[b'Other',b'recover',b'']]:check(not ma.actor_arguments(v))
import os
row=['1:','FLOCK','ADVISORY','WRITE','777','00:01:123','0','EOF'];dev=os.makedev(0,1)
check(ma.lock_match(row,777,dev,123))
for k in range(1,6):
 v=list(row);v[k]='foreign';check(not ma.lock_match(v,777,dev,123))
for v in [None,[],row[:5]]:check(not ma.lock_match(v,777,dev,123))

import ast
here=pathlib.Path(__file__).parent
source=ast.parse((here/'pg481_native_owned_stop.py').read_text())
exec(compile(ast.Module(body=[v for v in source.body if isinstance(v,ast.FunctionDef) and v.name=='terminal'],type_ignores=[]),'<pure terminal>','exec'),h.__dict__)
units=['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-api.service','schubert-nk-web.service','schubert-nk-bootstrap-admin.service','artemis.service','caddy.service']
fixture={u:{'Id':u,'ActiveState':'failed' if 'morning' in u or 'api.' in u else 'inactive','SubState':'failed' if 'morning' in u or 'api.' in u else 'dead','MainPID':'0','ControlPID':'0','Job':''} for u in units}
h.UNITS=units;h.FIELDS=set(fixture[units[0]]);h.baseline={'units':fixture};calls=[]
with patch.object(h,'show',lambda u,f:copy.deepcopy(fixture[u]),create=True),patch.object(h,'kernel',lambda u:calls.append(u),create=True):
 h.cohort();check(calls==units);check(h.all_terminal()==fixture)
for unit in units:
 for k,v in [('MainPID','777'),('ControlPID','888'),('Job','1'),('ActiveState','active'),('Id','foreign')]:
  bad=copy.deepcopy(fixture);bad[unit][k]=v
  with patch.object(h,'show',lambda u,f:bad[u],create=True),patch.object(h,'kernel',lambda u:None,create=True):
   try:h.cohort();raise AssertionError('terminal mutation accepted')
   except ValueError:check(True)
check(not hasattr(h,'stop'))
driver=(here/'Pg517TerminalApiRecovery.java').read_text()
check('refs.check("stop:' not in driver)
raw=('NKEPOCH1\nstate=ISSUED\nboot_id='+epoch+'\nepoch_id='+epoch+'\nrun_id='+epoch+
 '\ncutoff_utc=2026-09-27T15:00:00.000000Z\nactivation_id='+epoch+'\npermit_sha256='+'b'*64+'\n').encode()
expected=raw.replace(b'state=ISSUED',b'state=INVALID').replace(b'permit_sha256='+b'b'*64,b'permit_sha256=-')
check(h.canonical_invalid(raw)==expected)
for invalid in [None,b'',b'corrupt',raw.replace(b'ISSUED',b'INVALID'),raw+b'foreign=1\n',raw.replace(b'permit_sha256=',b'permit_hash='),raw[:-1]]:
 try:h.canonical_invalid(invalid);raise AssertionError('invalid vector accepted')
 except ValueError:check(True)
h.revoked_phase=True;h.invalid_hash='f'*64;h.invalid_length=300
changed=copy.deepcopy(original);current=root+'/epoch.current'
changed[current]['metadata'][1]=777;changed[current]['metadata'][6:]=[300,201,202];changed[current]['sha256']='f'*64
check(h.startup_preserved(changed,original))
for k in range(9):
 bad=copy.deepcopy(changed);bad[current]['metadata'][k]+=1
 check(h.startup_preserved(bad,original)==(k in [1,7,8]))
for path in changed:
 if path in [root,current]:continue
 bad=copy.deepcopy(changed);bad[path]['sha256']='a'*64;check(not h.startup_preserved(bad,original))
h.revoked_phase=False;check(not h.startup_preserved(changed,original))
print('PG517_TERMINAL_REFERENCE_ORACLE independentAssertions='+str(count)+' allTenTerminalAndStops0=true phaseSpecificCanonical=true vmActions0=true productionPT0=true')
