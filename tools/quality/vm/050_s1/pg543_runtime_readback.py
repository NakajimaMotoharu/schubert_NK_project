"""Current PG537 post-retirement full provenance; no mutation and no implicit old owner."""
import ast
import hashlib
import grp
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import pathlib
from pg543_retirement_contract import validate_snapshot, configurations, release_metadata, MORNING, CADDY, require

OLD = Path('/var/lib/pgpt-s1-preservation/pg537-bootstrap-retire-v1')
RUNTIME = Path('/run/systemd/system/'+MORNING+'.d/pg492-once-resume.conf')
BOOT = 'cc9ed874-7f4f-450e-a188-8de1e42c8441'


def load(owner=None):
    raw = Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    names = {'command','show','metadata','tree','strict','kernel'}
    nodes = [n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in names]
    require(len(nodes) == len(names))
    nodes += [n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'UNITS','FIELDS'} for t in n.targets)]
    env = dict(globals()); env.update(pathlib=pathlib,subprocess=subprocess)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<sealed provenance readers>','exec'),env)
    strict, tree, show, command = (env[n] for n in ('strict','tree','show','command'))
    a = strict(OLD/'before.private.json',0o600,33554432)
    b = strict(OLD/'after.private.json',0o600,33554432)
    require(hashlib.sha256(a).hexdigest() == '62402b7b0b1f1d1d0ec8799652e8ad1a7f6c3a24dedb6b4baac6f29c34eae4db')
    require(hashlib.sha256(b).hexdigest() == 'c34c058226c43e55b90ce3342a6b21cc74e6137a1a4084daaba7662ad04add59')
    baseline = json.loads(b); validate_snapshot(baseline)
    require(strict(OLD/'complete.private',0o600,4096) == b'newSyntheticSourcesRetired=true\nallNewScopesReturnedNormally=true\nnormal20Preserved=true\nall24DatabaseUnchanged=true\nunitActions0=true\n')
    before = json.loads(a)
    for name in ('bootstrap-admin-username','bootstrap-admin-password'):
        src = Path('/etc/schubert-nk/credentials')/name
        retired = OLD/(name+'.retired.private'); old = before['credentials'][str(src)]
        require(not os.path.lexists(src) and env['metadata'](retired)[:7] == old['metadata'][:7])
        require(hashlib.sha256(strict(retired,0o400,256)).hexdigest() == old['sha256'])
    require(len(baseline['rows']) == 24 and len(baseline['rows']['schubert.batch_runs']) == 462)
    paths = {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup',
             'originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup',
             'native':'/run/schubert-nk/pt-coverage','oldProofs':'/var/lib/pgpt-s1-preservation/pg526-native-stop-v1',
             'bootstrapOldProofs':'/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1',
             'bootstrapTools':'/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1'}
    depraw = Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1/pg529_dependency_graph.py').read_bytes()
    require(hashlib.sha256(depraw).hexdigest() == '5931ef9687aa24fa693f0d15d96d912b19c9ca7b365ffd25f4588d2c39f5de60')
    deps = dict(re=re); exec(compile(depraw,'<sealed dependency set policy>','exec'),deps)
    caddy_pre = show(CADDY,{'ExecStartPre'})['ExecStartPre']
    native = strict(Path('/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'),0o644,4096)
    basepath = Path('/opt/schubert-nk/releases/0.1.0-PG495/systemd')/MORNING
    bm=env['metadata'](basepath); release_metadata(bm)
    require(grp.getgrnam('schubert').gr_gid==986 and 'system.posix_acl_access' not in os.listxattr(basepath))
    base=basepath.read_bytes(); require(env['metadata'](basepath)==bm)
    manifest_raw=Path('/opt/schubert-nk/releases/0.1.0-PG495/RELEASE-MANIFEST.json').read_bytes()
    require(hashlib.sha256(manifest_raw).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
    artifact=[v for v in json.loads(manifest_raw)['artifacts'] if v['path']=='systemd/'+MORNING]
    require(len(artifact)==1 and artifact[0]['size']==len(base) and artifact[0]['sha256']==hashlib.sha256(base).hexdigest())
    # Independent declared golden comes from signed/native bytes, not observed argv.
    require(native.startswith(b'# PGPT only:') and b'--resume' not in native)
    lines = [l[10:] for l in native.decode('ascii').splitlines() if l.startswith('ExecStart=') and l != 'ExecStart=']
    require(len(lines) == 1 and lines[0].startswith('/usr/bin/java -javaagent:'))
    require(b'ExecStart=/usr/bin/java ' in base)
    expected = ('/usr/bin/java',lines[0],'no')
    captured_files = {}
    for u, conf in baseline['configuration'].items():
        fragment = show(u,{'FragmentPath'})['FragmentPath']
        require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
        for name in [fragment,*conf['DropInPaths'].split()]:
            if name == str(RUNTIME):
                continue
            p = Path(name); meta = env['metadata'](p)
            require(stat.S_ISREG(meta[4]) and meta[2] == 0 and meta[5] == 1 and 'system.posix_acl_access' not in os.listxattr(p))
            captured_files[name] = {'metadata':meta,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            require(meta == env['metadata'](p))
    def snapshot(changed=False):
        require(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == BOOT)
        if owner is not None:
            owner()
        require(str(Path('/opt/schubert-nk/current').readlink()) == '/opt/schubert-nk/releases/0.1.0-PG495')
        manifest = Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
        require(hashlib.sha256(manifest).hexdigest() == 'f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
        value = {k:tree(Path(p)) for k,p in paths.items()}
        require(all(v == baseline[k] for k,v in value.items()))
        value['units'] = {u:show(u,env['FIELDS']) for u in env['UNITS']}
        require(value['units'] == baseline['units'])
        for u in env['UNITS']:
            env['kernel'](u)
        value['configuration'] = {u:show(u,set(c)) for u,c in baseline['configuration'].items()}
        nowpre = show(CADDY,{'ExecStartPre'})['ExecStartPre']
        if changed:
            configurations(baseline['configuration'],value['configuration'],expected,caddy_pre,nowpre)
        else:
            require(value['configuration'] == baseline['configuration'] and nowpre == caddy_pre)
        value['dependencies'] = deps['dependency_graph']({u:show(u,set(deps['GRAPH_FIELDS'])) for u in env['UNITS']},env['UNITS'])
        require(value['dependencies'] == baseline['dependencies'])
        value['parentPid1'] = [json.loads(l) for l in command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+MORNING,'INVOCATION_ID=8f4514e19fd94c429f2587af71edb53a','-o','json','--no-pager']).splitlines()]
        require(value['parentPid1'] == baseline['parentPid1'])
        value['pid1Stop'] = {}
        for u, expected_stop in baseline['pid1Stop'].items():
            rows = [json.loads(l) for l in command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+u,'-o','json','--no-pager']).splitlines()]
            actual = [r for r in rows if r.get('MESSAGE_ID') == '9d1aaa27d60140bd96365438aad20286' and r.get('JOB_ID') == expected_stop[0]['JOB_ID'] and r.get('JOB_TYPE') == 'stop' and r.get('JOB_RESULT') == 'done']
            require(actual == expected_stop); value['pid1Stop'][u] = actual
        sql = "begin isolation level repeatable read read only;set local timezone='UTC';"
        for table in baseline['rows']:
            require(re.fullmatch(r'schubert\.[a-z_]+',table) is not None)
            sql += "select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
        value['rows'] = {}
        for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;']).splitlines():
            row=json.loads(line); require(row['table'] not in value['rows']); value['rows'][row['table']] = row['rows']
        require(value['rows'] == baseline['rows'])
        if changed:
            require(not os.path.lexists(RUNTIME) and not list(RUNTIME.parent.iterdir())); value['runtime'] = None
        else:
            value['runtime'] = {'metadata':env['metadata'](RUNTIME),'sha256':hashlib.sha256(strict(RUNTIME,0o644,4096)).hexdigest()}
            require(value['runtime'] == baseline['runtime'] and {p.name for p in RUNTIME.parent.iterdir()} == {RUNTIME.name})
        for name, expected_file in captured_files.items():
            p = Path(name); require(env['metadata'](p) == expected_file['metadata'] and hashlib.sha256(p.read_bytes()).hexdigest() == expected_file['sha256'])
        require(value['units'] == {u:show(u,env['FIELDS']) for u in env['UNITS']})
        if owner is not None:
            owner()
        return value
    return env, baseline, snapshot, caddy_pre, expected, captured_files
