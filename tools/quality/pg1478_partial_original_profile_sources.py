"""SSC266 source-only current owned readonly profiling; starts/stops/retirement0."""
import ast
import inspect
from pg1450_current_cold_retry import java as cold_java,observer as cold_observer
from pg1477_publication_observation_retry import payload as observed_payload
from pg1475_failed_publication_owner_observation import within_root_period

SAVE='pg1481-partial-original-profile-v1'
TOOLS='pg1478-partial-original-tools-v1'
BASE='/var/lib/pgpt-s1-preservation/pg1477-failed-publication-owner-v1/observed.private.json'
SHA='bcfd08285abe448ebe28c2adffc39acca0346e25b1769c44d72f43290da38cd5'


def java():
    raw=cold_java().replace('Pg1450CurrentColdPreparation','Pg1478PartialOriginalProfile').replace('pg1450-current-cold-tools-v1',TOOLS).replace('pg1452-current-cold-prepared-v1',SAVE).replace('pg1450_current_cold_refs.py','pg1478_partial_original_refs.py').replace('PG1452_','PG1481_')
    raw=raw.replace('d2e3a86f-27a4-4c2a-be21-b512eebf1216','15700a87-9117-4f63-a0ff-768dd604d0f1').replace('2026-10-10T23:30:23.481632Z','2026-10-11T21:18:59.040097Z').replace('841b507c-2713-4ffe-8882-68f5fb3f87f5','9e706936-a3c9-4a09-bb66-e2b1e8bbef66').replace('PG243-cold-empty','PG266-readonly-profile')
    raw=raw.replace('"prepare".equals(args[0])','"profile".equals(args[0])')
    start=raw.index('  static void original(');end=raw.index('  static final class References',start)
    raw=raw[:start]+'''  static void original(MaintenanceRunFiles.Session session)throws Exception {
    if(Pg983BootstrapExisting.lease!=null)Pg983BootstrapExisting.pulse();
    long begin=System.nanoTime();
    var proof=session.observeStartup(ORIGINAL);
    require(proof.activation().equals(ORIGINAL) && proof.completed().isEmpty());
    require(proof.equals(session.observeStartup(ORIGINAL)));
    long duration=System.nanoTime()-begin;
    require(duration>=0);
    Files.writeString(SAVE.resolve("original-profile.safe.jsonl"),
        "{\\"twoWholeGraphObservationsNanos\\":"+duration+",\\"completed\\":false}\\n",
        StandardCharsets.US_ASCII,StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    if(Pg983BootstrapExisting.lease!=null)Pg983BootstrapExisting.pulse();
  }
'''+raw[end:]
    start=raw.index('  static boolean readonlyOptions(');end=raw.index('  public static void main',start)
    raw=raw[:start]+raw[end:]
    start=raw.index('              phase="OWNED_HOST_RO";');end=raw.index('              refs.check("prepared");original(session);',start)
    raw=raw[:start]+'''              phase="IMMUTABLE_CURRENT_VERIFIER";
              var approval=Pg387TrustedDeployment.verify();
              require(approval.manifestSha256().equals("ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99")
                  && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
'''+raw[end:]
    raw=raw.replace('finitePreparation=true','readonlyProfile=true').replace('finitePreparation','readonlyProfile')
    raw=raw.replace('SSC243/244: finite completed-cold preparation. No epoch, DB or business writes.','SSC266: current pending original readonly profile under fresh M-A/RODB/tenRef; mutation0.')
    return raw


def refs():
    old=ast.parse(cold_observer())
    prefix=[]
    for node in old.body:
        if isinstance(node,ast.Try):break
        if isinstance(node,ast.FunctionDef)and node.name in ['snapshot','runtime_check']:continue
        prefix.append(node)
    raw=ast.unparse(ast.Module(body=prefix,type_ignores=[]))
    raw=raw.replace('Pg1450CurrentColdPreparation','Pg1478PartialOriginalProfile').replace("b'prepare'","b'profile'").replace('PG243-cold-empty','PG266-readonly-profile').replace('pg1452-current-cold-prepared-v1',SAVE)
    snapshot=next(n for n in ast.parse(observed_payload()).body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    # The caller-owned DB backend is the only permitted client, authenticated by
    # the existing independent full peer/advisory predicate, not a count1 claim.
    snapshot.body=[n for n in snapshot.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='peers'for t in n.targets))
       and not(isinstance(n,ast.Expr)and 'peers.splitlines()'in ast.unparse(n))]
    source=ast.unparse(snapshot).replace("actor['statusSha256'] = hashlib.sha256(actor.pop('status').encode()).hexdigest()","actor.pop('status')")
    raw+='\n'+inspect.getsource(within_root_period)+'\n'+source+'\n'+BODY
    compile(raw,'<pending current owned readonly profile refs>','exec');return raw


BODY=r'''
expected_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1477-failed-publication-owner-v1/observed.private.json').read_bytes()
require(hashlib.sha256(expected_raw).hexdigest()=='bcfd08285abe448ebe28c2adffc39acca0346e25b1769c44d72f43290da38cd5')
expected_current=json.loads(expected_raw)
try:
 phase='CURRENT_FULL_READONLY_BEFORE'
 # Keep all signed source/pin/approval FDs continuously, same qualified contract.
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM)
 data=json.loads(manifest);records=data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':BOM}]
 sums=contract.canonical_sum_bytes(data['artifacts'],BOM);require((release/'SHA256SUMS').read_bytes()==sums)
 records.append({'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()})
 held.append(contract.HeldInventory(str(release),records,0).open())
 for path,size,digest in [(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),44,'3378dbf29039d9fd0194f8c949a8793f00aff460bfeb6c69aba492498f4de221'),(BASE/'pg1292-manifest.sig',64,'97fd4c41a795c5f2465cf2f5074831723db0c3942fa8d62d16a5aad54cb318f7')]:
  body=path.read_bytes();require(len(body)==size and hashlib.sha256(body).hexdigest()==digest)
  held.append(contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file())
 approval=pathlib.Path('/etc/schubert-nk/release-approval/current');body=approval.read_bytes()
 require(body==('NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256='+BOM+'\n').encode())
 held.append(contract.HeldInventory(str(approval.parent),[{'path':approval.name,'size':len(body),'sha256':hashlib.sha256(body).hexdigest()}],0).open_file())
 before_inventory=[h.capture()for h in held];fixed_parent=actor()
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in UNITS:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 def verify_current():
  value=snapshot();require(value==expected_current and value==snapshot());peer_check();inventory_check();return value
 first=verify_current();framing('REF_READY')
 for line in sys.stdin:
  action=line.strip();require(action in {'prepare','prepared','run','release'})
  if action=='run':PEER_CLOSED=True
  phase='READONLY_'+action.upper();value=verify_current()
  if action=='release':
   require(PEER_CLOSED)
   for name in reversed(refs):manager.UnrefUnit(name)
   refs=[];bus.close();bus=None
   for h in reversed(held):h.close()
   held=[]
   encoded=json.dumps({'current':value,'parent':fixed_parent,'mutation0':True},sort_keys=True).encode()
   with(SAVE/'after.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
   framing('REF_RELEASED');break
  framing('REF_CHECKED')
 else:raise ValueError('readonly profile framing incomplete')
except BaseException as failure:retain(failure)
'''
