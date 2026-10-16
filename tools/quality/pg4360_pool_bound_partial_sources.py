"""SSC293 same current actors: historical pool movement is not boundary instability."""
import ast
import inspect
import pg4338_current_partial_sources as previous
import pg4358_ordinary_fd_contract as fd_contract
import pg4160_retained_config_read as retained_read
from pg4060_original_profile_dual_stack import once

PARTIAL = 'pg4360-pool-bound-partial-v3'
POST = 'pg4362-pool-bound-post-v3'
KEEPER = 'pg4364-pool-bound-keeper-v3'
REFERENCE_SHA = 'cd2d8421d9fb9c70821d2f5a3d9b05ba491c1a24ff5988122bde14e12ceabb75'

CAPTURE = r'''
fd_contract={};exec(FD_SOURCE,fd_contract)
raw_snapshot=snapshot
def capture_snapshot():
 value=raw_snapshot()
 table=[];servers={}
 try:
  for peer in value['database']['peers']:
   if peer['user']in fd_contract['ROLES']:servers[peer['pid']]=server_proc(peer['pid'])
  table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]
  holder=globals().get('owned');backend=holder[1]if holder is not None and any(p['pid']==holder[1]for p in value['database']['peers'])else None
  account=pwd.getpwnam('postgres')
  value['ordinaryDatabaseFds']=fd_contract['bind'](value,table,servers,tcp_pair,endpoint,set(globals().get('completed_units',{})),backend,(account.pw_uid,account.pw_gid))
 except BaseException:
  save_pair('rejected-bind',{'snapshot':value,'tcp':table,'servers':servers})
  raise
 value['ordinaryDatabaseRawEvidence']={'tcp':table,'servers':servers}
 return value
'''

SAVING = r'''
def proof_record(name,value):
 if 'private_record'in globals():return globals()['private_record'](name,value)
 encoded=json.dumps(value,sort_keys=True).encode();globals()['durable_save'](name,encoded)
 return hashlib.sha256(encoded).hexdigest()
def save_pair(label,parts):
 require(type(label)is str and label.replace('-','').isascii()and label.replace('-','').isalpha())
 hashes={}
 for key,value in parts.items():
  require(type(key)is str and key.isascii()and key.isalpha())
  name=label+'.'+key+'.private.json';hashes[name]=proof_record(name,value)
 proof_record(label+'.index.private.json',{'partSha256':hashes,'complete':True,'rawExported':False})
'''

BOUNDARY = r'''
def snapshot():
 first=capture_snapshot();second=capture_snapshot()
 keys=['units','actors','detailedActors','durable','native','startup','runtime','ordinaryDatabaseFds']
 changed=[k for k in keys if first[k]!=second[k]]
 if first['database']['rows']!=second['database']['rows']:changed.append('databaseRows')
 if changed:
  save_pair('rejected-boundary-pair',{'before':first,'after':second,'changed':changed})
  raise ValueError('current complete boundary two-read mismatch; no retry')
 return second
'''


def keeper():
    raw = previous.keeper()
    raw = once(raw, "save=base/('" + previous.KEEPER + "-'+MODE)", "save=base/('" + KEEPER + "-'+MODE)")
    raw = once(raw, "reference=Path('/var/lib/pgpt-s1-preservation/pg4336-current-unknown-read-v1/observed.private.json').read_bytes()",
               "reference=Path('/var/lib/pgpt-s1-preservation/pg4356-current-pool-witness-v1/observed.private.json').read_bytes()")
    raw = once(raw, previous.OBSERVED_SHA, REFERENCE_SHA)
    marker = "reference=json.loads(reference)"
    raw = once(raw, marker, marker + "\nrequire(reference['referenceDelta']=={'detailedActors':['/schubert-nk-api.service/fds/93/metadata','/schubert-nk-api.service/fds/93/target']})\n# Old fd93 TCP ownership remains unclassified; this is a new fully bound current admission, not historical repair.")
    marker = "materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]"
    raw = once(raw, marker, extension() + BOUNDARY + '\n' + marker)
    old = " for key in ['units','actors','detailedActors','durable','native','startup','runtime']:require(value[key]==expected[key])"
    new = """ try:
  for key in ['units','actors','durable','native','startup','runtime']:require(value[key]==expected[key])
  require(fd_contract['same_details'](expected['detailedActors'],value['detailedActors'],reference['ordinaryDatabaseFds'],value['ordinaryDatabaseFds']))
 except BaseException:
  save_pair('rejected-reference-pair',{'reference':expected,'current':value,'referencePool':reference['ordinaryDatabaseFds']})
  raise"""
    raw = once(raw, old, new)
    raw = once(raw, 'first=pair();second=pair();require(first==second)',
               "first=pair();second=pair()\n require(all(first[k]==second[k]for k in ['java','python','configuration']))\n require({k:v for k,v in first['current'].items()if k!='ordinaryDatabaseRawEvidence'}=={k:v for k,v in second['current'].items()if k!='ordinaryDatabaseRawEvidence'})")
    raw = once(raw, "proof_sha=private_record('proof.private.json',first)",
               "proof_sha=private_record('proof.private.json',first)\n proof_second_sha=private_record('proof-second.private.json',second)")
    raw = once(raw, "'proofSha256':proof_sha,'signalsIssued':2", "'proofSha256':proof_sha,'proofSecondSha256':proof_second_sha,'signalsIssued':2")
    return raw.replace('SSC292_', 'SSC293_')


def partial():
    raw = previous.partial()
    raw = once(raw, "save=base/('" + previous.PARTIAL + "-'+MODE)", "save=base/('" + PARTIAL + "-'+MODE)")
    # Partial checked() already performs full two-read equality and saves rejected pairs.
    marker = 'import time,sys,traceback'
    raw = once(raw, marker, extension() + '\nsnapshot=capture_snapshot\n' + marker)
    raw = once(raw, "keys=['units','actors','detailedActors','durable','native','startup','runtime']",
               "keys=['units','actors','detailedActors','durable','native','startup','runtime','ordinaryDatabaseFds']")
    raw = once(raw, "save_private('rejected-pair.private.json',{'before':before,'after':after,'changedKeys':changed})",
               "save_pair('rejected-pair',{'before':before,'after':after,'changed':changed})")
    return raw.replace('SSC292_', 'SSC293_')


def post():
    raw = previous.post()
    raw = once(raw, "save=base/'" + previous.POST + "'", "save=base/'" + POST + "'")
    return once(raw, "RECOVERY='/var/lib/pgpt-s1-preservation/" + previous.PARTIAL + "-recover'",
                "RECOVERY='/var/lib/pgpt-s1-preservation/" + PARTIAL + "-recover'")


def files():
    return {'keeper.py': keeper(), 'partial.py': partial(), 'post.py': post()}


def extension():
    proc = next(n for n in ast.parse(retained_read.BODY).body if isinstance(n, ast.FunctionDef) and n.name == 'proc')
    source = once(ast.get_source_segment(retained_read.BODY, proc), 'def proc(pid):', 'def server_proc(pid):')
    return 'import pwd\nFD_SOURCE=' + repr(inspect.getsource(fd_contract)) + '\n' + source + '\n' + SAVING + CAPTURE
