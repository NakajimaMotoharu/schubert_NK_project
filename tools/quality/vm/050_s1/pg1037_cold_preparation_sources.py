"""SSC243/244 fresh completed-cold preparation; generated operator, not Production.

PreRO authenticated bytes are provided by the held child, not immutable verifier.
Java invokes the unchanged full verifier only after fixed host readonly mount.
"""
import ast
from pathlib import Path
from pg1033_cold_handoff_preflight_v6 import payload as qualified

HERE = Path(__file__).resolve().parent


def java():
    raw = (HERE / 'Pg1023ColdOwnedReadback.java').read_text()
    raw = raw.replace('Pg1023ColdOwnedReadback', 'Pg1037ColdOwnedPreparation')
    raw = raw.replace('SSC243: completed/no-active cold ownership readback only. No epoch, directory or mount writes.',
                      'SSC243/244: finite completed-cold preparation. No epoch, DB or business writes.')
    raw = raw.replace('pg1023-cold-tools-v1', 'pg1037-cold-tools-v1').replace('pg1023-cold-owned-v1', 'pg1037-cold-prepared-v1')
    raw = raw.replace('pg1023_cold_refs.py', 'pg1037_cold_refs.py').replace('PG1023_', 'PG1037_')
    raw = raw.replace('"verify".equals(args[0])', '"prepare".equals(args[0])')
    begin = '            var approval=Pg387TrustedDeployment.verify();'
    end = '            phase="DATABASE_ADMISSION";'
    if raw.count(begin) != 1 or raw.count(end) != 1:
        raise ValueError('fixed cold signature order refused')
    raw = raw[:raw.index(begin)] + raw[raw.index(end):]
    marker = '              original(session);refs.check("prepare");original(session);'
    replacement = marker + '''
              phase="OWNED_HOST_RO";
              var mount=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/findmnt","--target",Pg387TrustedDeployment.RELEASE.toString(),"--noheadings","--output","VFS-OPTIONS");
              if(!readonlyOptions(new String(mount,StandardCharsets.US_ASCII).strip()))Pg387TrustedDeployment.freezeCandidate();
              phase="IMMUTABLE_FULL_VERIFIER";
              var approval=Pg387TrustedDeployment.verify();
              require(approval.manifestSha256().equals("b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524")
                  && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
              phase="FINITE_EMPTY_NAMESPACES";environment();
              refs.check("prepared");original(session);
'''
    if raw.count(marker) != 1:
        raise ValueError('fixed finite preparation insertion refused')
    raw = raw.replace(marker, replacement)
    raw = raw.replace('Set.of("prepare","run")', 'Set.of("prepare","prepared","run")')
    raw = raw.replace('readbackOnly=true\\n', 'finitePreparation=true\\n')
    raw = raw.replace('epochNamespaceMountWrites=0\\n', 'epochDbBusinessWrites=0\\n')
    raw = raw.replace('readbackOnly=true allScopesReturnedNormally=true preparationAccepted=false',
                      'finitePreparation=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false')
    methods = r'''
  static boolean readonlyOptions(String options) {
    require(options!=null && options.matches("[a-z0-9_=.-]+(,[a-z0-9_=.-]+)*"));
    var flags=Arrays.asList(options.split(","));
    require(new HashSet<>(flags).size()==flags.size() && flags.contains("ro")!=flags.contains("rw"));
    return flags.contains("ro");
  }
  static void environment()throws Exception {
    Path run=Path.of("/run/schubert-nk");
    var namespaces=List.of("startup","backup-request","cleanup-request","expiry-request","pt-coverage");
    for(String name:namespaces)require(!Files.exists(run.resolve(name),LinkOption.NOFOLLOW_LINKS));
    for(String name:namespaces)Pg428ColdBootPreparation.newDirectory(run.resolve(name),0,0);
    Path coverage=run.resolve("pt-coverage");
    for(String name:List.of("parent","cleanup","expiry","root-api"))Pg428ColdBootPreparation.newDirectory(coverage.resolve(name),0,0);
    for(var role:Map.of("backup","schubert-backup","inspector","schubert-inbox-inspector").entrySet()) {
      var uid=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-u",role.getValue());
      var gid=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-g",role.getValue());
      Pg428ColdBootPreparation.newDirectory(coverage.resolve(role.getKey()),Integer.parseInt(new String(uid,StandardCharsets.US_ASCII).strip()),Integer.parseInt(new String(gid,StandardCharsets.US_ASCII).strip()));
    }
    Files.setPosixFilePermissions(coverage,java.nio.file.attribute.PosixFilePermissions.fromString("rwx--x--x"));
    Pg387TrustedDeployment.sync(run);Pg387TrustedDeployment.sync(coverage);
  }
'''
    marker = '  public static void main(String[] args)throws Exception {'
    if raw.count(marker) != 1:
        raise ValueError('fixed Java entry refused')
    return raw.replace(marker, methods + '\n' + marker)


def guest():
    tree = ast.parse(qualified())
    functions = {'require','command','metadata','tree','show','cold','snapshot',
                 'complete_configuration','configuration_value','exec_record','same','controls','safe_json'}
    constants = {'BOOT','SOURCE','BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS',
                 'CONTRACT_SOURCE','LOCK_SOURCE','MANIFEST_SIZE','CHECKSUM_HASH'}
    nodes = [n for n in tree.body if isinstance(n, ast.Import)
             or isinstance(n, ast.ImportFrom) and not (n.module or '').startswith('pg')
             or isinstance(n, ast.FunctionDef) and n.name in functions
             or isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in constants for t in n.targets)]
    raw = ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    marker = "require(not pathlib.Path('/run/schubert-nk/startup').exists() and (not pathlib.Path('/run/schubert-nk/pt-coverage').exists()))"
    if raw.count(marker) != 1:
        raise ValueError('fixed namespace boundary refused')
    raw = raw.replace(marker, 'runtime_namespaces()')
    code = raw + '\n' + BODY
    ast.parse(code)
    return code


BODY = r'''
import types,sys,time,dbus
contract=types.ModuleType('pg1037_contract');exec(CONTRACT_SOURCE,contract.__dict__)
locks_module=types.ModuleType('pg1037_locks');exec(LOCK_SOURCE,locks_module.__dict__)
owned_flocks=locks_module.owned_flocks
require(len(sys.argv)==3 and sys.argv[1]=='verify'and sys.argv[2].isdigit())
OWNER_BACKEND=int(sys.argv[2]);require(1<OWNER_BACKEND<2147483647)
OWNER_PID=os.getppid();require(OWNER_PID>1 and os.geteuid()==0)
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
require(pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes()
require(hashlib.sha256(base).hexdigest()==BASELINE_HASH);old=json.loads(base)
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1004-cold-readonly-v3/after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='1cbb10fa83df138d5f3fe6b40b8107e16475e280745797f6e9e5a58d030073a9');sealed=json.loads(raw)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1')
require(metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2])
PREPARED=False;held=[];directory_fds=[];refs=[];bus=None;phase='ENTRY';captured_parent=None
def owned_peer_sql(backend):
 tag="usename='schubert_batch'and application_name='PG243-cold-empty'and backend_type='client backend'and state in('idle in transaction','active')"
 return (contract.all_client_sql(backend)+"select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted and pid<>"+str(backend)+";"
  "select count(*)from pg_stat_activity a where datname='schubert_nk'and pid="+str(backend)+" and "+tag+
  "and exists(select 1 from pg_locks l where l.pid=a.pid and locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock'and granted);")
def parent():
 p=pathlib.Path('/proc')/str(OWNER_PID);s=p.joinpath('stat').read_text();ticks=int(s.rpartition(')')[2].split()[19])
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 argv=(p/'cmdline').read_bytes();require(argv.split(b'\0')[-3:]==[b'Pg1037ColdOwnedPreparation',b'prepare',b''])
 require({int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={os.getpid()})
 fixed={n:metadata(pathlib.Path('/run/schubert-nk')/n)for n in ['maintenance.lock','startup-admission.lock']}
 owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),fixed,OWNER_PID)
 return {'pid':OWNER_PID,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),
  'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb')},'cgroup':(p/'cgroup').read_text(),'locks':fixed}
def runtime_namespaces():
 root=pathlib.Path('/run/schubert-nk');names=['startup','backup-request','cleanup-request','expiry-request','pt-coverage']
 workers={name:(int(command(['id','-u',role],32)),int(command(['id','-g',role],32)))for name,role in [('backup','schubert-backup'),('inspector','schubert-inbox-inspector')]}
 expected={'maintenance.lock','startup-admission.lock'}
 if not PREPARED:
  contract.namespace_layout({'@root':[p.name for p in root.iterdir()]},{'@root':metadata(root)},workers,False);return {}
 expected.update(names);require({p.name for p in root.iterdir()}==expected)
 result={}
 for name in names:
  p=root/name;m=metadata(p);require(m[2:5]==[0,0,stat.S_IFDIR|(0o711 if name=='pt-coverage'else 0o700)]and not os.listxattr(p))
  result[name]=m
  if name!='pt-coverage':require(not list(p.iterdir()))
 coverage=root/'pt-coverage';require({p.name for p in coverage.iterdir()}=={'parent','cleanup','expiry','root-api','backup','inspector'})
 for name in ['parent','cleanup','expiry','root-api','backup','inspector']:
  p=coverage/name;m=metadata(p);owner=(0,0)
  if name in ('backup','inspector'):
   role='schubert-backup'if name=='backup'else'schubert-inbox-inspector'
   owner=(int(command(['id','-u',role],32)),int(command(['id','-g',role],32)))
  require(m[2:5]==[owner[0],owner[1],stat.S_IFDIR|0o700]and not list(p.iterdir())and not os.listxattr(p))
  result['pt-coverage/'+name]=m
 entries={'@root':[p.name for p in root.iterdir()]};metas={'@root':metadata(root)}
 for name in result:
  p=root/name;entries[name]=[x.name for x in p.iterdir()];metas[name]=metadata(p)
 contract.namespace_layout(entries,metas,workers,True);result['@root']=metadata(root)
 return result
def hold_material(path,size,digest):
 h=contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file();held.append(h)
 require(h.capture()[-1][1][2:6]==(0,0,stat.S_IFREG|0o400,1))
def authenticate():
 manifest=(RELEASE/'RELEASE-MANIFEST.json').read_bytes();require(len(manifest)==MANIFEST_SIZE and hashlib.sha256(manifest).hexdigest()==BOM)
 records=json.loads(manifest)['artifacts'];canonical=contract.canonical_sum_bytes(records,BOM)
 require(hashlib.sha256(canonical).hexdigest()==CHECKSUM_HASH)
 records=records+[{'path':'RELEASE-MANIFEST.json','size':MANIFEST_SIZE,'sha256':BOM},{'path':'SHA256SUMS','size':len(canonical),'sha256':CHECKSUM_HASH}]
 h=contract.HeldInventory(str(RELEASE),records,0).open();held.append(h)
 hold_material(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),44,PIN_HASH)
 hold_material(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),64,SIG_HASH)
 approval=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256='+BOM+'\n').encode()
 hold_material(pathlib.Path('/etc/schubert-nk/release-approval/current'),len(approval),hashlib.sha256(approval).hexdigest())
def fds():
 for path,fd,fixed in directory_fds:
  m=metadata(path);s=os.fstat(fd)
  require((s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)==tuple(m[:5])and m[:5]==fixed[:5])
  if str(path)!='/run/schubert-nk'or not PREPARED:require(m==fixed)
  else:require(m[5]==fixed[5]+5)
def read_pair():
 require(parent()==captured_parent);controls();fds()
 for h in held:h.capture()
 a=snapshot();b=snapshot();require(a==b)
 require(a['units']==sealed['units']and a['rows']==sealed['rows']and a['durable']==sealed['durable']and a['artifacts']==sealed['artifacts'])
 for name,v in a['configuration'].items():
  require(same(sealed['configuration'][name],v,exec_record));start=exec_record(v['ExecStart'])
  require(start is not None and start[3:]==('n/a','n/a','0','(null)','0/0')and v['ExecStop']=='')
 require(parent()==captured_parent);fds()
 for h in held:h.capture()
 return a
def private(name,value):
 with(SAVE/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def retain(failure):
 print('PG1037_REFS_UNKNOWN phase='+phase+' type='+type(failure).__name__+' isolationRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
try:
 phase='BYTE_AUTH';captured_parent=parent();controls();authenticate()
 phase='HELD_DIRECTORIES'
 for name in ['/run/schubert-nk','/var/lib/schubert-nk/maintenance']:
  p=pathlib.Path(name);fixed=metadata(p);require(fixed[2]==fixed[3]==0 and stat.S_ISDIR(fixed[4])and not os.listxattr(p))
  directory_fds.append((p,os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW),fixed))
 phase='TEN_REFS';bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in old['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 print('REF_READY',flush=True)
 phase='BEFORE';require(sys.stdin.readline()=='prepare\n');before=read_pair();private('before.private.json',before);print('REF_CHECKED',flush=True)
 phase='PREPARED';require(sys.stdin.readline()=='prepared\n');PREPARED=True
 prepared=read_pair();require(prepared==before);runtime=runtime_namespaces();require(runtime==runtime_namespaces())
 private('prepared.private.json',{'snapshot':prepared,'runtime':runtime});print('REF_CHECKED',flush=True)
 phase='DATABASE_CLOSED';require(sys.stdin.readline()=='run\n');OWNER_BACKEND=0
 after=read_pair();require(after==before and runtime==runtime_namespaces());private('after.private.json',{'snapshot':after,'runtime':runtime});print('REF_CHECKED',flush=True)
 phase='NORMAL_RELEASE';require(sys.stdin.readline()=='release\n');fds()
 for h in held:h.capture()
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 for _,fd,_ in reversed(directory_fds):os.close(fd)
 for h in reversed(held):h.close()
 print('REF_RELEASED',flush=True)
except BaseException as failure:retain(failure)
'''


def files():
    return {'Pg1037ColdOwnedPreparation.java': java(), 'pg1037_cold_refs.py': guest(),
            'Pg1037ColdOwnedPreparationTest.java': JAVA_TEST}


JAVA_TEST = r'''
public final class Pg1037ColdOwnedPreparationTest {
  static void rejected(String[] input) {
    try {Pg1037ColdOwnedPreparation.arguments(input);throw new AssertionError("invalid operation");}
    catch(IllegalStateException expected) { }
  }
  static void badOptions(String input) {
    try {Pg1037ColdOwnedPreparation.readonlyOptions(input);throw new AssertionError("invalid mount options");}
    catch(IllegalStateException expected) { }
  }
  public static void main(String[] args) {
    Pg1037ColdOwnedPreparation.arguments(new String[]{"prepare"});
    rejected(null);rejected(new String[0]);rejected(new String[]{null});
    rejected(new String[]{"verify"});rejected(new String[]{"execute"});
    rejected(new String[]{"prepare","extra"});rejected(new String[]{"PREPARE"});
    if(!Pg1037ColdOwnedPreparation.readonlyOptions("ro,relatime")
        || Pg1037ColdOwnedPreparation.readonlyOptions("rw,relatime"))throw new AssertionError("mount golden");
    for(String input:new String[]{null,"","ro,rw","relatime","ro,ro","RO","rw, ro","ro\n"})badOptions(input);
    if(!Pg1037ColdOwnedPreparation.ORIGINAL.run().id().toString().equals("eeae04ea-713c-4f2d-888d-358fb4bed274")
        ||!Pg1037ColdOwnedPreparation.ORIGINAL.id().toString().equals("091663ce-1cf4-47e7-8311-218ebb0c8653")
        ||!Pg1037ColdOwnedPreparation.ORIGINAL.run().cutoff().toString().equals("2026-10-09T23:31:22.087768Z"))throw new AssertionError("original golden");
    System.out.println("PT-DEP-1037001 argument/original/mount-options PASS; no VM or runtime mutation");
  }
}
'''
