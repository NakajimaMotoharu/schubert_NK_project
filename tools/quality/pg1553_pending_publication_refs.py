"""Compose current partial observer with finite no-epoch publication data gates."""
import ast
from pathlib import Path
from pg1546_pending_candidate_ro_sources import refs as previous,CLASS as OLD_CLASS,TOOLS as OLD_TOOLS,SAVE as OLD_SAVE
from pg1553_pending_publication_java import CLASS,TOOLS,SAVE

def once(s,a,b):
    if s.count(a)!=1:raise ValueError('fixed partial publication observer boundary refused')
    return s.replace(a,b)

def source():
    s=previous().replace(OLD_CLASS,CLASS).replace(OLD_TOOLS,TOOLS).replace(OLD_SAVE,SAVE).replace('PG269-candidate-ro','PG270-pending-code').replace("b'prepare-ro'","b'activate'")
    tree=ast.parse(s)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    old=ast.unparse(node);new=old
    new=new.replace("release = pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')", "selected_source=NEW_SOURCE if publication_phase in ['old-linked-private','release']else SOURCE\n    selected_bom=NEW_BOM if publication_phase in ['old-linked-private','release']else BOM\n    release = pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544'if publication_phase in ['old-linked-private','release']else'/opt/schubert-nk/releases/0.1.0-PG1292')")
    new=new.replace('== BOM','== selected_bom').replace("data['source']['commit'] == SOURCE", "data['source']['commit'] == selected_source").replace("str(BASE / 'pg1292-manifest.sig')", "str(BASE / ('pg1544-manifest.sig'if publication_phase in ['old-linked-private','release']else'pg1292-manifest.sig'))")
    new=new.replace("'source': SOURCE", "'source': selected_source").replace("'manifestSha256': BOM", "'manifestSha256': selected_bom")
    s=once(s,old,new)
    begin=s.index('def inventory_check():');end=s.index('\ndef ',begin+4)
    s=s[:begin]+'''def inventory_check():
 for h in held:publication_capture(h,contract,oracle,public_before,public_actual,publication_phase,begin_ns,time.time_ns())
 require(actor()==fixed_parent)
'''+s[end:]
    marker='try:\n phase=';i=s.index(marker)
    definitions='\nNEW_SOURCE=\'4d6bcbddb417b76d27e52d5d9640752c300edccf\'\nNEW_BOM=\'e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c\'\npublication_phase=\'before\'\n'
    for name in ['pg1551_pending_publication_contract.py','pg1552_publication_inventory.py']:
        raw=Path(__file__).with_name(name).read_text()
        # The one imports only independent primitive row/time validators. Its
        # frozen helper module is explicitly staged, never inferred from cwd.
        definitions+='EMBED_'+name.split('_')[0].upper()+'='+repr(raw)+'\n'
    definitions+="oracle=types.ModuleType('fixed_partial_publication');oracle.__file__='/var/lib/pgpt-s1-preservation/pg1553-pending-publication-tools-v1/pg1551_pending_publication_contract.py';exec(EMBED_PG1551,oracle.__dict__)\ninv_gate=types.ModuleType('fixed_full_publication_inventory');exec(EMBED_PG1552,inv_gate.__dict__)\npublication_capture=inv_gate.capture\nfrom pg1090_cold_finite_capture import direct_tree,fd_record\nfrom pg1554_pending_exchange_io import linked_attributes,exchange,move_old_link\n"
    definitions+=INITIAL_AND_FUNCTIONS
    s=s[:i]+definitions+s[i:]
    marker='first=verify_current();framing(\'REF_READY\')'
    s=once(s,marker,'first=verify_current();initialize_publication();framing(\'REF_READY\')')
    # Before initialization the original full capture remains required.
    s=s.replace(' for h in held:publication_capture(', ' for h in held:\n  if public_before is None:h.capture();continue\n  publication_capture(')
    begin=s.index(" for line in sys.stdin:",s.index("phase='CURRENT_FULL_READONLY_BEFORE'"));end=s.index("except BaseException as failure:retain(failure)",begin)
    s=s[:begin]+LOOP+s[end:]
    s=once(s,'  value=snapshot();require(value==profile_expected and value==snapshot());peer_check();inventory_check();return value',CHECK_CURRENT)
    compile(s,'<partial no-epoch observer exact full current>','exec');return s

INITIAL_AND_FUNCTIONS=r'''
public_before=None;public_actual=None;begin_ns=0;pubfds={};save_fd=None
def public():return {p:direct_tree(p)for p in [oracle.STARTUP,oracle.APPROVAL,oracle.CURRENT]}
def initialize_publication():
 global public_before,public_actual,begin_ns,save_fd
 public_before=public();require(public_before==public());public_actual=public_before;begin_ns=time.time_ns()
 for p in [oracle.STARTUP,oracle.APPROVAL,oracle.CURRENT]:pubfds[p]=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 for p in [oracle.STARTUP+'/epoch.current',oracle.APPROVAL+'/current']:pubfds[p]=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 pubfds[oracle.CURRENT+'/current']=os.open(oracle.CURRENT+'/current',os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC)
 save_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 phase_observe('before')
def phase_observe(phase):
 global public_actual
 observed=public();require(observed==public());end=time.time_ns();oracle.verify(public_before,observed,phase,begin_ns,end)
 for path,fd in pubfds.items():
  if path==oracle.CURRENT+'/current':
   parent=save_fd if phase in ['old-linked-private','release']else pubfds[oracle.CURRENT]
   name='current-link.private'if phase in ['old-linked-private','release']else 'pg1551-current.part'if phase=='exchanged'else'current'
   row=linked_attributes(parent,name,fd)
  else:row=fd_record(fd)
  oracle.verify_retained(path,public_before[oracle.APPROVAL if path.startswith(oracle.APPROVAL)else oracle.STARTUP if path.startswith(oracle.STARTUP)else oracle.CURRENT][path],row,phase,observed,begin_ns,end)
 public_actual=observed
def protected_current(v):
 expected=dict(profile_expected)
 if publication_phase in ['old-linked-private','release']:
  expected['source']=NEW_SOURCE;expected['manifestSha256']=NEW_BOM
  raw=(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544')/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==NEW_BOM)
  data=json.loads(raw);expected['artifacts']={r['path']:r['sha256']for r in data['artifacts']}
 require(v==expected)
'''
CHECK_CURRENT=r'''
  value=snapshot();protected_current(value);require(value==snapshot());peer_check()
  if public_before is not None:phase_observe(publication_phase)
  inventory_check();return value'''
LOOP=r'''
 for line in sys.stdin:
  action=line.strip();require(action in {'prepare','approval','exchange','run','release'})
  require(action=='prepare'and publication_phase=='before'or action=='approval'and publication_phase=='before'or action=='exchange'and publication_phase=='approval'or action in {'run','release'}and publication_phase=='old-linked-private')
  if action=='approval':publication_phase='approval'
  if action=='exchange':
   verify_current();directory=pubfds[oracle.CURRENT]
   os.symlink(oracle.NEW_LINK,'pg1551-current.part',dir_fd=directory);os.fsync(directory);phase_observe('link-staged')
   exchange(directory,'pg1551-current.part');os.fsync(directory);phase_observe('exchanged')
   move_old_link(directory,save_fd,pubfds[oracle.CURRENT+'/current']);publication_phase='old-linked-private'
  if action=='run':PEER_CLOSED=True
  phase='CODE_ONLY_'+action.upper();value=verify_current()
  if action=='release':
   require(PEER_CLOSED);phase_observe('release')
   encoded=json.dumps({'current':value,'parent':fixed_parent,'pendingCodeOnly':True,'epochAndAllBusinessOriginalsUnchanged':True,'publicBefore':public_before,'publicAfter':public_actual},sort_keys=True).encode()
   with(SAVE/'after.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
   for fd in reversed(list(pubfds.values())):os.close(fd)
   pubfds.clear();os.close(save_fd);save_fd=None
   for name in reversed(refs):manager.UnrefUnit(name)
   refs=[];bus.close();bus=None
   for h in reversed(held):h.close()
   held=[];framing('REF_RELEASED');break
  framing('REF_CHECKED')
 else:raise ValueError('partial publication framing incomplete')
'''
