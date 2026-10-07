"""SSC202 fixed pending migration witness; no start or runtime authority. Raw values stay private."""
import ast, hashlib, json, os, pathlib, re, stat, subprocess, sys, time, grp
import dbus

SAVE = pathlib.Path('/var/lib/pgpt-s1-preservation/pg503-resume-preparation-v1')
PROFILE = '/etc/schubert-nk/backup-profile.json'
OLD = '/opt/schubert-nk/releases/0.1.0-PG495'
NEXT = '/opt/schubert-nk/releases/0.1.0-PG495'
APPROVAL = '/etc/schubert-nk/release-approval/current'
NEW_APPROVAL = b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG495\nmanifest_sha256=f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44\n'
RUN = '91a748b4-1abe-484c-9682-44f46429b324'
RUN_ID=RUN; MORNING='schubert-nk-morning-controller.service'
RUNTIME=pathlib.Path('/run/systemd/system')/(MORNING+'.d')
NAME='pg492-once-resume.conf'
NATIVE=pathlib.Path('/etc/systemd/system')/(MORNING+'.d')/'pg477-native-coverage.conf'
def runtime_directory(path, empty):
    item=path.lstat()
    require(stat.S_ISDIR(item.st_mode) and item.st_uid==item.st_gid==0
            and stat.S_IMODE(item.st_mode)==0o755
            and 'system.posix_acl_access' not in os.listxattr(path)
            and 'system.posix_acl_default' not in os.listxattr(path))
    parent=path.parent.lstat()
    require(stat.S_ISDIR(parent.st_mode) and parent.st_uid==parent.st_gid==0
            and stat.S_IMODE(parent.st_mode)==0o755
            and 'system.posix_acl_access' not in os.listxattr(path.parent)
            and 'system.posix_acl_default' not in os.listxattr(path.parent))
    require(set(p.name for p in path.iterdir()) == (set() if empty else {NAME}))
    return True
BOOT = 'cc9ed874-7f4f-450e-a188-8de1e42c8441'
phase = 'PREFLIGHT'

def require(value):
    if not value:
        raise ValueError('fixed migration witness refused')

def profile_security(values, xattrs, group):
    return (isinstance(values, list) and len(values) == 9 and isinstance(group, int)
            and values[2:6] == [0, group, stat.S_IFREG | 0o640, 1]
            and 0 < values[6] <= 4096 and 'system.posix_acl_access' not in xattrs
            and 'system.posix_acl_default' not in xattrs)

def release_security(values, xattrs, group):
    return (isinstance(values,list) and len(values)==9 and isinstance(group,int)
            and values[2:6]==[0,group,stat.S_IFREG|0o640,1]
            and 0<values[6]<=16384 and 'system.posix_acl_access' not in xattrs
            and 'system.posix_acl_default' not in xattrs)

def fixed_dropin(base,native):
 if not isinstance(base,bytes) or not isinstance(native,bytes):raise ValueError('fixed signed base required')
 starts=[r.removeprefix(b'ExecStart=') for r in base.splitlines() if r.startswith(b'ExecStart=')]
 require(len(starts)==1 and starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain') and b'--resume' not in starts[0] and b'-javaagent' not in starts[0])
 agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
 argv=starts[0].replace(b'/usr/bin/java ',agent,1);require(argv!=starts[0])
 expected=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
 require(native==expected)
 return b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume '+RUN_ID.encode()+b'\n'
def compare(actual,changed):
 require(set(actual)==set(before) and all(actual[k]==before[k] for k in before if k!='configuration'))
 if not changed:require(actual==before);return
 for unit,conf in before['configuration'].items():
  if unit==MORNING:
   got=actual['configuration'][unit]
   require(all(got[k]==conf[k] for k in CONFIG-{'ExecStart','DropInPaths'}))
   require(exec_record(got['ExecStart'])[:3]==('/usr/bin/java',new_argv,'no'))
   require(got['DropInPaths']==str(NATIVE)+' '+str(RUNTIME/NAME))
  else:
   got=actual['configuration'][unit]
   require(all(got[k]==conf[k] for k in CONFIG-{'ExecStart'}))
   old_decl=exec_record(conf['ExecStart']);new_decl=exec_record(got['ExecStart'])
   require(old_decl is not None and new_decl is not None and old_decl[:3]==new_decl[:3])
 require(strict(RUNTIME/NAME,0o644,4096)==dropin)
 require(set(p.name for p in RUNTIME.iterdir())=={NAME})

def execute():
    global phase, backend, source, digest, UNITS, FIELDS, before, CONFIG, new_argv, dropin, exec_record
    require(os.geteuid() == 0 and len(sys.argv) == 4 and sys.argv[1].isdigit())
    backend = int(sys.argv[1]); source = sys.argv[2]; digest = sys.argv[3]
    require(backend > 1 and re.fullmatch('[0-9a-f]{40}', source) and re.fullmatch('[0-9a-f]{64}', digest))
    os.umask(0o077)
    witness = pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py')
    raw = witness.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    names = {'command', 'show', 'metadata', 'tree', 'strict', 'locked_database', 'kernel', 'configuration_fields'}
    parsed = ast.parse(raw)
    definitions = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in names]
    require(len(definitions) == len(names))
    constants = [n for n in parsed.body if isinstance(n, ast.Assign)
                 and all(isinstance(t, ast.Name) and t.id in {'UNITS', 'FIELDS'} for t in n.targets)]
    class Binding(ast.NodeTransformer):
        def visit_Constant(self, n):
            if isinstance(n.value, str) and "a.application_name='PG480-fixed-recovery'" in n.value:
                text = n.value.replace('PG480-fixed-recovery', 'PG503-fixed-resume')
                text = text.replace("'schubert_api','schubert_web','schubert_inspector'", "'schubert_app','schubert_web_session','schubert_inbox_inspector','schubert_backup'")
                text = text.replace("l.objsubid=1 and l.granted", "l.objsubid=1 and l.mode='ExclusiveLock' and l.granted")
                return ast.copy_location(ast.Constant(text), n)
            return n
    code = Binding().visit(ast.Module(body=constants + definitions, type_ignores=[]))
    ast.fix_missing_locations(code); exec(compile(code, '<pinned immutable primitives>', 'exec'), globals())
    snapshot_file = pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/refs-after.private.json')
    saved = strict(snapshot_file, 0o600, 33554432)
    require(hashlib.sha256(saved).hexdigest() == '07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49')
    previous = json.loads(saved)
    require(len(previous['rows']) == 24 and len(previous['rows']['schubert.batch_runs']) == 442)
    require(not SAVE.exists())
    SAVE.mkdir(mode=0o700)
    complete = strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/complete.private'),0o600,4096)
    require(hashlib.sha256(complete).hexdigest() == 'e83c845bb124996d820dd47e50c52b8b05c1eb683a0be99c4fe75e452db03f29')
    require(not RUNTIME.exists() or runtime_directory(RUNTIME, True))
    policy = pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
    require(hashlib.sha256(policy).hexdigest() == 'b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
    definition = next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name == 'exec_record')
    exec(compile(ast.Module(body=[definition],type_ignores=[]),'<pinned declaration>','exec'),globals())
    cold_source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-tools-v1/pg502_cold_refs.py').read_bytes()
    require(hashlib.sha256(cold_source).hexdigest()=='06cc9b07c617417493358b3cc485f39984238f46cef4cc3f81dc116fbd8b7f3f')
    cold_definitions=[node for node in ast.parse(cold_source).body if isinstance(node,ast.FunctionDef) and node.name in {'cold','epoch_valid'}]
    require(len(cold_definitions)==2);exec(compile(ast.Module(body=cold_definitions,type_ignores=[]),'<pinned cold predicates>','exec'),globals())
    CONFIG = configuration_fields()
    native = strict(NATIVE,0o644,4096)
    phase='SIGNED_BASE_READ'
    base_path=pathlib.Path(NEXT)/'systemd'/MORNING
    base_meta=metadata(base_path);group=grp.getgrnam('schubert').gr_gid
    require(release_security(base_meta,os.listxattr(base_path),group))
    base=base_path.read_bytes()
    require(base_meta==metadata(base_path) and release_security(metadata(base_path),os.listxattr(base_path),group))
    dropin = fixed_dropin(base,native)
    new_argv = next(r.removeprefix(b'ExecStart=') for r in dropin.splitlines() if r.startswith(b'ExecStart=') and r != b'ExecStart=').decode('ascii')
    def owner():
        pid = os.getppid(); p = pathlib.Path('/proc')/str(pid)
        argv = (p/'cmdline').read_bytes().split(b'\0')
        require(argv[0] == b'/opt/jdk-25.0.4/bin/java'
                and argv[-4:] == [b'Pg503ResumePreparation', source.encode(), digest.encode(), b''])
        ticks = int((p/'stat').read_text().rpartition(')')[2].split()[19])
        held = []
        for fd in (p/'fd').iterdir():
            try: held.append(str(fd.readlink()))
            except FileNotFoundError: pass
        for name in ['maintenance.lock', 'startup-admission.lock']:
            path = pathlib.Path('/run/schubert-nk')/name
            strict(path, 0o600, 0); item = path.lstat(); require(str(path) in held)
            matches = []
            for line in pathlib.Path('/proc/locks').read_text().splitlines():
                f = line.split()
                if len(f) >= 8 and f[1:5] == ['FLOCK', 'ADVISORY', 'WRITE', str(pid)]:
                    dev = f[5].split(':')
                    if len(dev) == 3 and (int(dev[0],16),int(dev[1],16),int(dev[2])) == (os.major(item.st_dev),os.minor(item.st_dev),item.st_ino):
                        matches.append(line)
            require(len(matches) == 1)
        return pid, ticks
    held = owner()
    phase='REF_ACQUIRE'
    bus = dbus.SystemBus(private=True)
    manager = dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'), 'org.freedesktop.systemd1.Manager')
    refs = []
    for unit in UNITS:
        manager.RefUnit(unit); refs.append(unit)
    def snapshot(db_required=True):
        require(owner() == held and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip() == BOOT)
        profile = pathlib.Path(PROFILE)
        profile_before = metadata(profile)
        require(profile_security(profile_before, os.listxattr(profile), grp.getgrnam('schubert').gr_gid))
        parent_before = metadata(profile.parent)
        require(parent_before[2] == 0 and stat.S_ISDIR(parent_before[4]) and parent_before[4] & 0o022 == 0
                and 'system.posix_acl_access' not in os.listxattr(profile.parent)
                and 'system.posix_acl_default' not in os.listxattr(profile.parent))
        if db_required:
            locked_database()
        else:
            require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',
                             "select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_inbox_inspector','schubert_backup'); select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"],4096).splitlines() == [b'0',b'0'])
        units = {u: show(u,FIELDS) for u in UNITS}
        for u,v in units.items():
            require(v['Id'] == u and v['LoadState'] == 'loaded' and v['MainPID'] == v['ControlPID'] == '0' and not v['Job'])
            require(cold(v) and v == previous['units'][u])
            kernel(u); require(v == show(u,FIELDS))
        require(not manager.ListJobs())
        q = "begin isolation level repeatable read read only;set local timezone='UTC';"
        for table in previous['rows']:
            q += "select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
        q += 'commit;'; rows = {}
        for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
            value = json.loads(line); require(value['table'] not in rows); rows[value['table']] = value['rows']
        require(rows == previous['rows'])
        for name in ['backup-request','cleanup-request','expiry-request']:
            require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
        trees = {name: tree(pathlib.Path(name)) for name in previous['trees']}
        for name in ['startup','backup-request','cleanup-request','expiry-request','pt-coverage']:
            trees['/run/schubert-nk/'+name]=tree(pathlib.Path('/run/schubert-nk')/name)
        conf = {u: show(u,configuration_fields()) for u in UNITS}

        require(profile_before == metadata(profile) and parent_before == metadata(profile.parent)
                and profile_security(metadata(profile), os.listxattr(profile), grp.getgrnam('schubert').gr_gid))
        return {'units': units, 'trees': trees, 'configuration': conf, 'rows': rows, 'current': str(pathlib.Path('/opt/schubert-nk/current').readlink())}
    before = snapshot(); require(before == snapshot() and before['units'] == previous['units'] and before['current'] == OLD)
    require(all(before['trees'][name]==value for name,value in previous['trees'].items()))
    old_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly/refs-after.private.json').read_bytes()
    require(hashlib.sha256(old_raw).hexdigest()=='1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3')
    old_conf=json.loads(old_raw)['configuration']
    for unit,conf in before['configuration'].items():
        allowed={'ExecStart','DropInPaths'} if unit==MORNING else {'ExecStart'}
        require(all(conf[key]==old_conf[unit][key] for key in CONFIG-allowed))
        if unit!=MORNING:require(exec_record(conf['ExecStart'])[:3]==exec_record(old_conf[unit]['ExecStart'])[:3])
    epoch=pathlib.Path('/run/schubert-nk/startup/epoch.current')
    require(epoch_valid(strict(epoch,0o600,1024),strict(pathlib.Path('/var/lib/schubert-nk/maintenance/active'),0o600,512)))
    require(set(path.name for path in epoch.parent.iterdir())=={'epoch.current'})
    def save(name, value):
        with (SAVE/name).open('x') as f:
            os.fchmod(f.fileno(),0o600); json.dump(value,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
        fd = os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY); os.fsync(fd); os.close(fd)
    original = exec_record(before['configuration'][MORNING]['ExecStart'])
    require(original is not None and original[:3] == ('/usr/bin/java',new_argv.removesuffix(' --resume '+RUN_ID),'no'))
    require(before['configuration'][MORNING]['DropInPaths'] == str(NATIVE))
    save('refs-before.private.json', before); print('REF_READY',flush=True)
    changed = False
    for line in sys.stdin.buffer:
        phase = line.rstrip(b'\n').decode('ascii'); require(phase in ['before','prepare','release'])
        if phase == 'prepare':
            require(not changed); compare(snapshot(), False)
            if not RUNTIME.exists():
                parent=RUNTIME.parent;m=metadata(parent)
                require(m[2:5]==[0,0,stat.S_IFDIR|0o755] and 'system.posix_acl_access' not in os.listxattr(parent) and 'system.posix_acl_default' not in os.listxattr(parent))
                RUNTIME.mkdir(mode=0o755)
                fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
            require(runtime_directory(RUNTIME, True))
            target = RUNTIME/NAME
            fd = os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644)
            with os.fdopen(fd,'wb') as f:
                os.fchmod(f.fileno(),0o644);f.write(dropin);f.flush();os.fsync(f.fileno())
            fd=os.open(RUNTIME,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
            require(strict(target,0o644,4096)==dropin)
            phase='ONE_RELOAD';command(['/usr/bin/systemctl','daemon-reload'],4096);changed=True
        actual = snapshot(phase != 'release')
        compare(actual,changed)
        require(runtime_directory(RUNTIME,False) if changed else not RUNTIME.exists() or runtime_directory(RUNTIME,True))
        if phase == 'release':
            require(changed); save('refs-after.private.json',actual)
            for unit in reversed(refs): manager.UnrefUnit(unit)
            bus.close(); print('REF_RELEASED',flush=True); return
        print('REF_CHECKED',flush=True)
    raise ValueError('owner channel ended early')

if __name__ == '__main__':
    try: execute()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True)
        print('PG503_REFERENCE_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if frame.filename==__file__:print('PG503_REFERENCE_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True: time.sleep(1)
