"""Exact child then Java one pidfd TERM each; no business operations or old normal close."""
import ast
import pg1353_bootstrap_fixed_handoff as original
import pg1360_bootstrap_failed_pair_proof as proof
from pg1334_published_owned_stop_sources_v2 import SOURCE

PROOF = 'c88a721a3c412c42a6605737f0bf6c1655a3a3753f2ccc3034788d0784de04e1'
BODY = r'''
proof_raw=(base/'pg1360-bootstrap-failed-pair-v1/before.private.json').read_bytes();require(hashlib.sha256(proof_raw).hexdigest()==PROOF);proven=json.loads(proof_raw)
require(proven['current']==after and proven['owner']['pid']==839626 and proven['owner']['ticks']==7753101 and proven['owner']['argvSha256']=='4d34aeae7feb470287f972b652f1603ceecaf75cd91686eea9c17019f449f0cf'and proven['owner']['child']['pid']==839655 and proven['owner']['child']['ticks']==7753240 and proven['owner']['child']['argvSha256']=='8805b2a9cc0ffda56de123acc4deb05a74a80859e8dc7c15788f5e06aeb68efd')
SAVE=base/'pg1361-bootstrap-fixed-pair-handoff-v1';require(not os.path.lexists(SAVE));owner=proven['owner'];signals=0;reserved=set();reservation_fd=None
def verify(pid,ticks):
 require((pid,ticks)in((839655,7753240),(839626,7753101)))
 if pid==839655:
  value=fixed_owner();require(value==proven['owner']);return value
 value=parent_only();require(value=={**proven['owner'],'child':None}and not pathlib.Path('/proc/839655').exists());return value
def reserve(pid,value):
 require(pid not in reserved);reserved.add(pid)
 digest=proven['owner']['child']['argvSha256']if pid==839655 else proven['owner']['argvSha256']
 durable_reservation(reservation_fd,str(pid)+'.term-reserved.private.json',json.dumps({'pid':pid,'ticks':7753240 if pid==839655 else 7753101,'argvSha256':digest,'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(len(reserved)==signals+1 and signals<2);signals+=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN)
 if not poll.poll(30000):return False
 pid=839655 if signals==1 else 839626;deadline=time.monotonic()+3
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<deadline:time.sleep(.01)
 return not pathlib.Path('/proc',str(pid)).exists()
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 require(fixed_owner()==proven['owner']and owned_snapshot()==proven['native']and owned_snapshot()==proven['native']and fixed_owner()==proven['owner'])
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);writer.save(SAVE,'before.private.json',proof_raw)
 terminate_once(839655,7753240,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(parent_only()=={**proven['owner'],'child':None}and not pathlib.Path('/proc/839655').exists())
 terminate_once(839626,7753101,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==2 and not pathlib.Path('/proc/839626').exists()and not pathlib.Path('/proc/839655').exists()and free_snapshot()==proven['native']and free_snapshot()==proven['native'])
 writer.save(SAVE,'after.private.json',json.dumps({'current':after,'native':proven['native'],'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','fixedOldJavaHelperGone':True,'oldNormalClose':False,'allClientAdvisoryFlocks0':True},sort_keys=True).encode());os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reserved:
  print('PG1361_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'run':'PG1361-bootstrap-fixed-pair-handoff-v1','privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'fixedOldJavaHelperGone':True,'full24Full32Signed187OriginalBackupNativePreserved':True,'allClientAdvisoryFlocks0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''

def payload(seals):
    raw = original.payload(seals)
    prefix = raw[:raw.index('proof_path=')]
    actual = proof.payload(seals)
    tree = ast.parse(actual)
    replacement = {n.name: ast.get_source_segment(actual,n) for n in tree.body
                   if isinstance(n,ast.FunctionDef) and n.name in {'candidate','fixed_owner'}}
    oldtree = ast.parse(prefix)
    for n in reversed(oldtree.body):
        if isinstance(n,ast.FunctionDef) and n.name in replacement:
            lines=prefix.splitlines(keepends=True)
            prefix=''.join(lines[:n.lineno-1])+replacement[n.name]+'\n'+''.join(lines[n.end_lineno:])
    parent = replacement['fixed_owner'].replace('def fixed_owner():','def parent_only():')
    start=parent.index(' kids=');end=parent.index(' q=',start)
    parent=parent[:start]+" require(not pathlib.Path('/proc/839655').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))\n"+parent[end:]
    parent=parent.replace("'child':child", "'child':None")
    raw = prefix + '\n' + parent + '\nPROOF=' + repr(PROOF) + '\n' + BODY
    compile(raw,'<actual fixed child Java handoff>','exec')
    return raw

def source():
    return proof.source().replace('pg1360-bootstrap-failed-pair-v1','pg1361-bootstrap-fixed-pair-handoff-v1')

def main():
    env=dict(proof.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<actual pair handoff transport>','exec'),env)
    return env['main']()

if __name__=='__main__':
    raise SystemExit(main())
