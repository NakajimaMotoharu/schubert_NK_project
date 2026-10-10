"""One durable noargs external start after fresh qualified before and observer."""
import ast
import json
from pg1106_ordinary_cold_before import payload as before_payload
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W


def payload():
    m=json.loads((W/'pg1106-ordinary-cold-before-v1/manifest.safe.json').read_bytes())
    if m['actualExit']!=0 or not m['observed']['ordinaryNoargs']or not m['observed']['starts0']:raise ValueError('normal actual before required')
    t=ast.parse(before_payload());nodes=[]
    for n in t.body:
        if isinstance(n,ast.Try):break
        nodes.append(n)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    raw=raw.replace('pg1106-ordinary-cold-before-v1','pg1108-ordinary-cold-once-v1')
    raw=raw.replace('PG1106-ordinary-cold-before-v1','PG1108-ordinary-cold-once-v1')
    raw+='\n'+BODY
    ast.parse(raw)
    return 'BEFORE_SHA='+repr(m['observed']['afterPrivateSha256'])+'\n'+raw


BODY=r'''
def persist(name,value):
 with(save/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
try:
 phase='BEFORE_REAUTH';oldbefore=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/after.private.json').read_bytes()
 assert hashlib.sha256(oldbefore).hexdigest()==BEFORE_SHA
 before=json.loads(oldbefore)
 # The observer is staged/root-owned/immutable separately and already watching.
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in env['old']['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='SIGNED_ALL';release(pathlib.Path(pub.OLD_LINK),env['BOM'],env['SOURCE'])
 release(pathlib.Path(pub.NEW_LINK),'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','d5b00104280028d9ea81b44c1d1c805f3c2861ed')
 exact_modes(pathlib.Path(pub.OLD_LINK));exact_modes(pathlib.Path(pub.NEW_LINK))
 pin(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),env['PIN_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),env['SIG_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 pin(pathlib.Path(pub.APPROVAL)/'current',hashlib.sha256(pub.NEW_APPROVAL).hexdigest())
 pin(pathlib.Path('/run/schubert-nk/startup/epoch.current'),hashlib.sha256(epoch).hexdigest())
 assert ordinary_post()==before==ordinary_post()
 phase='DURABLE_ONCE_RESERVATION'
 persist('external-start-guard.private.json',{'atUTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
   'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','boot':env['BOOT'],'manifestSha256':'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',
   'beforeSha256':BEFORE_SHA,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
 assert ordinary_post()==before
 phase='ONCE_EXTERNAL_START'
 r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
 values=dict(line.split('=',1)for line in subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5).splitlines())
 persist('external-start-issued.private.json',dict(values,clientExit=r.returncode,clientSuccessIsNotParentSuccess=True))
 phase='OBSERVATION_CLOSE'
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 for h in reversed(held):h.close()
except BaseException as failure:retain(failure)
print(json.dumps({'run':'PG1108-cold-ordinary-once-v1','actualExit':r.returncode,'ordinaryNoargs':True,'externalStartIssuedOnce':True,
 'newRunRequired':True,'oldCompletedRunNotResumed':True,'originalBudgetSeconds':1800,'clientSuccessIsNotParentSuccess':True,'observerNormalClose':True,'formalAccepted':False}))
raise SystemExit(r.returncode)
'''


if __name__=='__main__':
    if not(W/'pg1107-watch-v1.started').exists()or(W/'pg1107-watch-v1.exit').exists():raise ValueError('live new observer required')
    watch=W/'pg1107-parent-watch-v1.private.jsonl'
    if not watch.exists()or watch.stat().st_size==0:raise ValueError('new observer first observation required')
    dispatch('PG1108-cold-ordinary-once-v1','pg1108-cold-ordinary-once-v1',payload())
