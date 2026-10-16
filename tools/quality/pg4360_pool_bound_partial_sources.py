"""SSC293 same current actors: historical pool movement is not boundary instability."""
import inspect
import pg4338_current_partial_sources as previous
import pg4358_ordinary_fd_contract as fd_contract
from pg4060_original_profile_dual_stack import once

PARTIAL = 'pg4360-pool-bound-partial-v1'
POST = 'pg4362-pool-bound-post-v1'
KEEPER = 'pg4364-pool-bound-keeper-v1'
REFERENCE_SHA = 'cd2d8421d9fb9c70821d2f5a3d9b05ba491c1a24ff5988122bde14e12ceabb75'

CAPTURE = r'''
fd_contract={};exec(FD_SOURCE,fd_contract)
raw_snapshot=snapshot
def capture_snapshot():
 value=raw_snapshot()
 table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]
 servers={p['pid']:inodes(p['pid'])for p in value['database']['peers']if p['user']in fd_contract['ROLES']}
 holder=globals().get('owned');backend=holder[1]if holder is not None and any(p['pid']==holder[1]for p in value['database']['peers'])else None
 value['ordinaryDatabaseFds']=fd_contract['bind'](value,table,servers,tcp_pair,endpoint,set(globals().get('completed_units',{})),backend)
 return value
'''

BOUNDARY = r'''
def snapshot():
 first=capture_snapshot();second=capture_snapshot()
 keys=['units','actors','detailedActors','durable','native','startup','runtime','ordinaryDatabaseFds']
 changed=[k for k in keys if first[k]!=second[k]]
 if first['database']['rows']!=second['database']['rows']:changed.append('databaseRows')
 if changed:
  private_record('rejected-boundary-pair.private.json',{'before':first,'after':second,'changedKeys':changed})
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
    raw = once(raw, marker, 'FD_SOURCE=' + repr(inspect.getsource(fd_contract)) + '\n' + CAPTURE + BOUNDARY + '\n' + marker)
    old = " for key in ['units','actors','detailedActors','durable','native','startup','runtime']:require(value[key]==expected[key])"
    new = """ try:
  for key in ['units','actors','durable','native','startup','runtime']:require(value[key]==expected[key])
  require(fd_contract['same_details'](expected['detailedActors'],value['detailedActors'],reference['ordinaryDatabaseFds'],value['ordinaryDatabaseFds']))
 except BaseException:
  private_record('rejected-reference-pair.private.json',{'reference':expected,'current':value,'referencePool':reference['ordinaryDatabaseFds']})
  raise"""
    raw = once(raw, old, new)
    return raw.replace('SSC292_', 'SSC293_')


def partial():
    raw = previous.partial()
    raw = once(raw, "save=base/('" + previous.PARTIAL + "-'+MODE)", "save=base/('" + PARTIAL + "-'+MODE)")
    # Partial checked() already performs full two-read equality and saves rejected pairs.
    marker = 'import time,sys,traceback'
    raw = once(raw, marker, 'FD_SOURCE=' + repr(inspect.getsource(fd_contract)) + '\n' + CAPTURE + '\nsnapshot=capture_snapshot\n' + marker)
    return raw.replace('SSC292_', 'SSC293_')


def post():
    raw = previous.post()
    raw = once(raw, "save=base/'" + previous.POST + "'", "save=base/'" + POST + "'")
    return once(raw, "RECOVERY='/var/lib/pgpt-s1-preservation/" + previous.PARTIAL + "-recover'",
                "RECOVERY='/var/lib/pgpt-s1-preservation/" + PARTIAL + "-recover'")


def files():
    return {'keeper.py': keeper(), 'partial.py': partial(), 'post.py': post()}
