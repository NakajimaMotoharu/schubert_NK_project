"""SSC202 fixed pending migration witness; no start or runtime authority. Raw values stay private."""
import ast, hashlib, json, os, pathlib, re, stat, subprocess, sys, time
import dbus

SAVE = pathlib.Path('/var/lib/pgpt-s1-preservation/pg490-schema028')
PROFILE = '/etc/schubert-nk/backup-profile.json'
OLD = '/opt/schubert-nk/releases/0.1.0-PG486'
RUN = '91a748b4-1abe-484c-9682-44f46429b324'
BOOT = 'e07aa706-1acd-4e65-b309-d7f330f79d54'
phase = 'PREFLIGHT'

def require(value):
    if not value:
        raise ValueError('fixed migration witness refused')

def profile_only(old, new, expected):
    if set(old) != set(new):
        return False
    for root, values in old.items():
        if set(values) != set(new[root]):
            return False
        for name, value in values.items():
            actual = new[root][name]
            if name == PROFILE:
                if (actual['sha256'] != hashlib.sha256(expected).hexdigest()
                        or actual['metadata'][0] != value['metadata'][0]
                        or actual['metadata'][2:7] != value['metadata'][2:7]):
                    return False
            elif name == str(pathlib.Path(PROFILE).parent):
                if actual['metadata'][:7] != value['metadata'][:7] or actual['sha256'] != value['sha256']:
                    return False
            elif actual != value:
                return False
    return True

def execute():
    global phase, backend, source, digest, UNITS, FIELDS
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
                return ast.copy_location(ast.Constant(n.value.replace('PG480-fixed-recovery', 'PG490-fixed-migration')), n)
            return n
    code = Binding().visit(ast.Module(body=constants + definitions, type_ignores=[]))
    ast.fix_missing_locations(code); exec(compile(code, '<pinned immutable primitives>', 'exec'), globals())
    snapshot_file = pathlib.Path('/var/lib/pgpt-s1-preservation/pg487-parent-failure-v1/snapshot.private.json')
    saved = strict(snapshot_file, 0o600, 33554432)
    require(hashlib.sha256(saved).hexdigest() == '5c2108ca88f39b2a68c374b2314b569be0dbb844016bce1861801eb1b379ca87')
    previous = json.loads(saved)
    require(len(previous['rows']) == 24 and len(previous['rows']['schubert.batch_runs']) == 432)
    require(SAVE.is_dir() and not (SAVE/'refs-before.private.json').exists())
    expected = pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG489/config/effective/backup-profile.json').read_bytes()
    def owner():
        pid = os.getppid(); p = pathlib.Path('/proc')/str(pid)
        argv = (p/'cmdline').read_bytes().split(b'\0')
        require(argv[0] == b'/opt/jdk-25.0.4/bin/java'
                and argv[-4:] == [b'Pg490PendingMigration', source.encode(), digest.encode(), b''])
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
    bus = dbus.SystemBus(private=True)
    manager = dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'), 'org.freedesktop.systemd1.Manager')
    refs = []
    for unit in UNITS:
        manager.RefUnit(unit); refs.append(unit)
    def snapshot(db_required=True):
        require(owner() == held and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip() == BOOT)
        if db_required:
            locked_database()
        else:
            require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',
                             "select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector'); select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"],4096).splitlines() == [b'0',b'0'])
        units = {u: show(u,FIELDS) for u in UNITS}
        for u,v in units.items():
            require(v['Id'] == u and v['LoadState'] == 'loaded' and v['MainPID'] == v['ControlPID'] == '0' and not v['Job'])
            if u == 'schubert-nk-cleanup.service':
                require(v['ActiveState'] == 'active' and v['SubState'] == 'exited' and v['RemainAfterExit'] == 'yes'
                        and v['InvocationID'] == 'c887f51965bb4dbfba7bb9648a2b5059' and v['ExecMainCode'] == '1'
                        and v['ExecMainStatus'] == '0' and v['Result'] == 'success')
            else:
                require(v['ActiveState'] in ['inactive','failed'])
            kernel(u); require(v == show(u,FIELDS))
        parent = units['schubert-nk-morning-controller.service']
        require(parent['InvocationID'] == '86142754043b476aa46e33916eb1b1a1'
                and parent['ExecMainCode'] == '1' and parent['ExecMainStatus'] == '30' and parent['Result'] == 'exit-code')
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
        conf = {u: show(u,configuration_fields()) for u in UNITS}
        require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == OLD)
        return {'units': units, 'trees': trees, 'configuration': conf, 'rows': rows}
    before = snapshot(); require(before == snapshot() and before['trees'] == previous['trees'])
    def save(name, value):
        with (SAVE/name).open('x') as f:
            os.fchmod(f.fileno(),0o600); json.dump(value,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
        fd = os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY); os.fsync(fd); os.close(fd)
    save('refs-before.private.json', before); print('REF_READY',flush=True)
    changed = False
    for line in sys.stdin.buffer:
        phase = line.rstrip(b'\n').decode('ascii'); require(phase in ['before','after','release'])
        actual = snapshot(phase != 'release')
        if phase == 'before':
            require(not changed and actual == before)
        else:
            require(actual['units'] == before['units'] and actual['configuration'] == before['configuration'] and actual['rows'] == before['rows'])
            require(profile_only(before['trees'],actual['trees'],expected))
            profile = pathlib.Path(PROFILE)
            observed = metadata(profile)
            require(profile.read_bytes() == expected and observed == metadata(profile))
            changed = True
        if phase == 'release':
            require(changed); save('refs-after.private.json',actual)
            for unit in reversed(refs): manager.UnrefUnit(unit)
            bus.close(); print('REF_RELEASED',flush=True); return
        print('REF_CHECKED',flush=True)
    raise ValueError('owner channel ended early')

if __name__ == '__main__':
    try: execute()
    except Exception as failure:
        print('REF_FAILED',flush=True)
        print('PG490_REFERENCE_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
        while True: time.sleep(1)
