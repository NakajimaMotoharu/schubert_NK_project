"""Exact failed Java one pidfd TERM, original business/fullscope unchanged."""
import ast
import inspect
import pg1352_bootstrap_expired_peer_proof as prior
import pg1026_cold_observation_contract as once
import pg611_durable as durable
from pg1334_published_owned_stop_sources_v2 import SOURCE

PROOF = '7c41c19ae521bda5aff525b5e629d79ba7a45c412963a423ffae909595638e50'

BODY = r'''
proof_path=base/'pg1352-bootstrap-expired-peer-v1/before.private.json';proof_raw=proof_path.read_bytes();require(hashlib.sha256(proof_raw).hexdigest()==PROOF);proven=json.loads(proof_raw)
require(proven['current']==after and proven['owner']['pid']==838452 and proven['owner']['ticks']==7697543 and proven['owner']['argvSha256']=='37e2460760781aadb46ad0213bb906641a535d50015ff9870f59fd6620911ddb'and proven['owner']['expiredDbPeerGone']is True)
SAVE=base/'pg1353-bootstrap-fixed-handoff-v1';require(not os.path.lexists(SAVE));owner=proven['owner'];signals=0;reserved=False;reservation_fd=None
def verify(pid,ticks):
 require((pid,ticks)==(838452,7697543));value=fixed_owner();require(value==proven['owner']);return value
def reserve(pid,value):
 global reserved
 require(not reserved and value==proven['owner']);reserved=True
 durable_reservation(reservation_fd,'838452.term-reserved.private.json',json.dumps({'pid':pid,'ticks':7697543,'argvSha256':value['argvSha256'],'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(reserved and signals==0);signals=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN)
 if not poll.poll(30000):return False
 deadline=time.monotonic()+3
 while pathlib.Path('/proc/838452').exists()and time.monotonic()<deadline:time.sleep(.01)
 return not pathlib.Path('/proc/838452').exists()
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 require(fixed_owner()==proven['owner']and owned_snapshot()==proven['native']and owned_snapshot()==proven['native']and fixed_owner()==proven['owner'])
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);writer.save(SAVE,'before.private.json',proof_raw)
 terminate_once(838452,7697543,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==1 and not pathlib.Path('/proc/838452').exists()and free_snapshot()==proven['native']and free_snapshot()==proven['native'])
 writer.save(SAVE,'after.private.json',json.dumps({'current':after,'native':proven['native'],'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','fixedOldJavaGone':True,'oldNormalClose':False,'allClientAdvisoryFlocks0':True},sort_keys=True).encode());os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reserved:
  print('PG1353_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'run':'PG1353-bootstrap-fixed-handoff-v1','privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'fixedOldJavaGone':True,'full24Full32Signed187OriginalBackupNativePreserved':True,'allClientAdvisoryFlocks0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''

def payload(seals):
    raw = prior.payload(seals)
    parsed = ast.parse(raw)
    block = next(n for n in parsed.body if isinstance(n, ast.Try) and n.body and isinstance(n.body[0], ast.For))
    prefix = ''.join(raw.splitlines(keepends=True)[:block.lineno - 1])
    function = next(n for n in block.body if isinstance(n, ast.FunctionDef) and n.name == 'snapshot')
    function.name = 'owned_snapshot'
    owned = ast.unparse(function)
    free = owned.replace('def owned_snapshot():', 'def free_snapshot():')
    # Replace the entire AST FLOCK-only branch; never broaden protected data fields.
    free_ast = ast.parse(free)
    outer = next(n for n in ast.walk(free_ast) if isinstance(n, ast.If) and
                 "owner['pid']" in ast.unparse(n) and "'FLOCK'" not in ast.unparse(n.test))
    outer.body = [ast.Expr(value=ast.Call(func=ast.Name(id='require', ctx=ast.Load()),
        args=[ast.UnaryOp(op=ast.Not(), operand=outer.test)], keywords=[]))]
    # With a matching inode the above branch must reject, not require its inverse twice.
    outer.test = ast.Constant(value=True)
    free = ast.unparse(ast.fix_missing_locations(free_ast))
    nodes = [n for n in ast.parse(inspect.getsource(once)).body if isinstance(n, ast.FunctionDef)
             and n.name in {'durable_reservation', 'terminate_once'}]
    raw = prefix + '\n' + owned + '\n' + free + '\nimport signal,select,types\n'
    raw += ast.unparse(ast.Module(body=nodes, type_ignores=[]))
    raw += '\nPROOF=' + repr(PROOF) + '\nWRITER=' + repr(inspect.getsource(durable))
    raw += '\nwriter=types.ModuleType("actual_durable");exec(WRITER,writer.__dict__)\n' + BODY
    compile(raw, '<current exact failed Java handoff>', 'exec')
    return raw

def source():
    return prior.source().replace('pg1352-bootstrap-expired-peer-v1', 'pg1353-bootstrap-fixed-handoff-v1')

def main():
    env = dict(prior.previous.prior.prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<fixed Java-only handoff transport>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
