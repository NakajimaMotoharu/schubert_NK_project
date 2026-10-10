"""Independent whole newcurrent/oldlinked/zero resources post, no authority."""
import ast
import datetime
import json
from pg1098_partial_exchange_preflight import payload as previous
from pg1041_cold_policy_diagnostic import W
from pg1051_cold_tree_preflight_v2 import dispatch


def nanos(value):
    t=datetime.datetime.fromisoformat(value)
    return int(t.timestamp())*1000000000+t.microsecond*1000


def payload():
    actual=json.loads((W/'pg1102-preserve-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or not actual['linkedOriginalPreservationAccepted']:raise ValueError('normal actual linked preservation required')
    tree=ast.parse(previous());nodes=[]
    for n in tree.body:
        if isinstance(n,ast.Try):break
        if isinstance(n,ast.FunctionDef)and n.name in ('actor','peer','tree_identity','read'):continue
        nodes.append(n)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    start=raw.index('query = ');end=raw.index('expected_runtime = ',start)
    raw=raw[:start]+"env['OWNER_PID']=0;env['OWNER_BACKEND']=0\nenv['owned_flocks']=lambda lines,m,pid:contract.free_flocks(lines,m)\n"+raw[end:]
    start=raw.index('save = OLD_SAVE / ');end=raw.index('held = []',start)
    raw=raw[:start]+"save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1103-newcurrent-post-v1');assert not os.path.lexists(save);save.mkdir(mode=0o700)\n"+raw[end:]
    raw=raw.replace('PG1098-partial-exchange-preflight-v1','PG1103-linked-preservation-post-v1')
    raw+='\n'+BODY
    ast.parse(raw)
    return 'LINK_BEGIN_NS='+repr(nanos(actual['startedUTC']))+'\nLINK_END_NS='+repr(nanos(actual['completedUTC']))+'\n'+raw


BODY=r'''
def exact_modes(root):
 for p in (root,*root.rglob('*')):
  s=p.lstat();relative=p.relative_to(root).as_posix()
  executable=relative in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
  assert not p.is_symlink()and not os.listxattr(p)and s.st_uid==0 and s.st_gid==986
  assert stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)and s.st_nlink==1
  assert stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640)
def post():
 control=env['controls']();first=env['snapshot']();assert first==env['snapshot']()
 assert all(first[k]==sealed[k]for k in ('units','rows','durable','artifacts'))
 for n,v in first['configuration'].items():assert env['same'](sealed['configuration'][n],v,env['exec_record'])
 trees={r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}
 pub.verify(original_before['trees'],trees,'after',epoch,begin_ns,time.time_ns())
 assert not os.path.lexists(pathlib.Path(pub.CURRENT)/'pg1088-current.part')
 archived=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1100-linked-preservation-v1/current-link.private')
 row=io.path_record(archived)
 pub.verify_retained(pub.CURRENT+'/current',original_before['trees'][pub.CURRENT][pub.CURRENT+'/current'],row,'after',trees,LINK_BEGIN_NS,LINK_END_NS)
 assert row['metadata'][5]==1 and row['target']==pub.OLD_LINK
 receipt=archived.parent/'complete.private'
 assert receipt.read_bytes()==b'allScopesReturnedNormally=true\nlinkedOriginalPreserved=true\nepochDbBusinessWrites=0\n'
 assert env['controls']()==control
 return {'snapshot':first,'trees':trees,'runtime':runtime(),'archived':row,'receiptSha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'controls':control,'heldWholeMetadata':safe([h.capture()for h in held])}
try:
 phase='RESOURCE_ZERO'
 assert not pathlib.Path('/proc/16222').exists()and not pathlib.Path('/proc/16248').exists()
 peers=env['command'](['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',env['owned_peer_sql'](0)],4096)
 assert peers.splitlines()==[b'0',b'0',b'0']
 phase='TEN_REFS';bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in env['old']['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='WHOLE_SIGNED'
 release(pathlib.Path(pub.OLD_LINK),env['BOM'],env['SOURCE'])
 release(pathlib.Path(pub.NEW_LINK),'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','d5b00104280028d9ea81b44c1d1c805f3c2861ed')
 exact_modes(pathlib.Path(pub.OLD_LINK));exact_modes(pathlib.Path(pub.NEW_LINK))
 pin(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),env['PIN_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),env['SIG_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 pin(pathlib.Path(pub.APPROVAL)/'current',hashlib.sha256(pub.NEW_APPROVAL).hexdigest())
 pin(pathlib.Path('/run/schubert-nk/startup/epoch.current'),hashlib.sha256(epoch).hexdigest())
 phase='WHOLE_POST';after=post();assert after==post()
 private=json.dumps(after,sort_keys=True).encode()
 with(save/'after.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 phase='NORMAL_CLOSE'
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 for h in reversed(held):h.close()
except BaseException as failure:retain(failure)
print(json.dumps({'run':'PG1103-linked-preservation-post-v1','actualExit':0,'current1068FullSigned':True,'old932FullPreserved':True,'linkedOriginalNineFieldsAclVerified':True,'startupInvalidUnchanged':True,'allOriginalsUnchangedTwice':True,'allResources0':True,'observerNormalClose':True,'afterPrivateSha256':hashlib.sha256(private).hexdigest(),'formalAccepted':False}))
'''


if __name__=='__main__':dispatch('PG1103-linked-preservation-post-v1','pg1103-linked-preservation-post-v1',payload())
