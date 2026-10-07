"""SSC217 fixed GC_AFTER_KNOWN_20 reader; preserved20 stays historical, currentGC only idle."""
import ast
import datetime
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess

from pg535_bootstrap_contract import normal20, same_terminal_cohort, credential_tree, native_tree, UNIT, SOURCES
from pg529_dependency_graph import dependency_graph
from pg537_bootstrap_gc_contract import current_gc_after_known20

TOOLS = pathlib.Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1')
OLD = pathlib.Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1')
PINS = {'Pg535BootstrapExisting.class':'a16aa52925ae21982817b538693be8f9015f969977a73759da61f77813bb5480',
        'Pg535BootstrapExisting$References.class':'737415ae40b6c57a711e201f4241e5312acb0dc103a480d6cb388e7d3510e6d7',
        'pg535_bootstrap_existing.py':'409f2c23e874f9fc6fcdb03b3e4fe49ef16afa849cbc2ef7457cb1b01fecb8ee',
        'pg535_bootstrap_contract.py':'270a8211601f423744d6944e85707b869ecdd783d178c360f9f90b7b5c2ace07',
        'pg529_dependency_graph.py':'5931ef9687aa24fa693f0d15d96d912b19c9ca7b365ffd25f4588d2c39f5de60',
        'pg457_stable_actor.py':'ae19f53d3440a63588b3df0bd525fb39762923dbffcc1cc595fedc818ee8ecb3'}
PROOFS = {'refs-prepare.private.log':'f33b963036b6dbdd1f589347ead5904c6331de976db58f132fbc0589ef68ed5e',
          'pid1.private.jsonl':'d34729d339150b5e9d659bc4a98bfd367b12ff948c5bb14edb98c3fa5660e34a',
          'dependencies-before.private.json':'a500ada9703a23b93bd8a395bb4d48f4ea3ced93b0a25b9024a53298cd8310d0',
          'start-reserved.private.json':'8ce3f38437e195c399d777e3ba438bae15301206d422d00e04ea6cd46a40f386',
          'before.private.json':'4f4bd05f92ca7e1aa128f7321af14e1ba2905a07a8be006b0d5c085a069373bd',
          'states.private.json':'485e1619e5c81ad3786461e134bd312cbd00db001ebccc7db7b9ad0c7bef8e94',
          'journal.private.jsonl':'dedf46cba1878e7364648acea9f233f11e41d1e494f5b5f033a94cade7499048',
          'actor.private.json':'0dd31425ac9c358c603cac135b995e4e14b27700e60c12a9efcfb2951afcb965'}
INV = '08face250787426aab68796452a0289f'


def require(value):
    if not value:
        raise ValueError('fixed post20 readback refused')


def load(owner):
    env = {'datetime':datetime, 'hashlib':hashlib, 'json':json, 'os':os, 'pathlib':pathlib,
           're':re, 'stat':stat, 'subprocess':subprocess, 'require':require,
           'normal20':normal20, 'same_terminal_cohort':same_terminal_cohort,
           'credential_tree':credential_tree, 'native_tree':native_tree,
           'UNIT':UNIT, 'SOURCES':SOURCES, 'dependency_graph':dependency_graph}
    raw = pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    source = ast.parse(raw)
    names = {'command', 'metadata', 'strict', 'show', 'tree', 'configuration_fields', 'kernel'}
    nodes = [n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in names]
    require(len(nodes) == len(names))
    nodes += [n for n in source.body if isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in {'UNITS', 'FIELDS'} for t in n.targets)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<sealed reader>', 'exec'), env)
    strict, tree = env['strict'], env['tree']
    require({p.name for p in TOOLS.iterdir()} == set(PINS) and {p.name for p in OLD.iterdir()} == set(PROOFS))
    for folder, pins, mode in ((TOOLS, PINS, 0o400), (OLD, PROOFS, 0o600)):
        for name, sha in pins.items():
            require(hashlib.sha256(strict(folder/name, mode, 33554432)).hexdigest() == sha)
    code = ast.parse((TOOLS/'pg535_bootstrap_existing.py').read_bytes())
    nodes = [n for n in code.body if isinstance(n, ast.FunctionDef) and n.name in {'verify_batch', 'verify_pid1'}]
    nodes += [n for n in code.body if isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in {'BOOT', 'INV', 'START', 'END'} for t in n.targets)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<sealed parent/DB oracle>', 'exec'), env)
    preserved = pathlib.Path('/var/lib/pgpt-s1-preservation/pg527-prestop-owned-handoff-v1')
    raw = strict(preserved/'before.private.json', 0o600, 33554432)
    require(hashlib.sha256(raw).hexdigest() == 'c8c6b915a380902c3c8d022de24ab91a28e726e0d914a6ae88060bc8c360d5e3')
    baseline = json.loads(raw)
    original = json.loads((OLD/'before.private.json').read_bytes())
    creds = pathlib.Path('/etc/schubert-nk/credentials')
    current = tree(creds)
    prepared = {str(creds/n):current[str(creds/n)] for n in SOURCES}
    require(strict(creds/'bootstrap-admin-username', 0o400, 256) == b'pgpt_bootstrap_535_existing')
    require(re.fullmatch(b'[A-Za-z0-9_-]{43}', strict(creds/'bootstrap-admin-password', 0o400, 256)))
    credential_tree(original['credentials'], current, prepared)
    handoff=pathlib.Path('/var/lib/pgpt-s1-preservation/pg536-bootstrap-owned-handoff-v1')
    sealed=strict(handoff/'after.private.json',0o600,33554432)
    require(hashlib.sha256(sealed).hexdigest()=='aa8f92166b01b23a7ffd0fa56474fae0048ce20a544f90a3ec06b211732e37ad')
    terminal=json.loads(sealed)['units'][UNIT]
    current_terminal=env['show'](UNIT,env['FIELDS'])
    require(current_gc_after_known20(terminal,current_terminal))
    require(normal20(terminal) and terminal['InvocationID'] == INV
            and terminal['ExecMainStartTimestampMonotonic'] == '28725207186'
            and terminal['ExecMainExitTimestampMonotonic'] == '28726873290')
    actor = json.loads((OLD/'actor.private.json').read_bytes())
    require(actor == {'pid':'567513', 'ticks':'2872520', 'invocation':INV, 'zeroCapabilities':True})
    states = json.loads((OLD/'states.private.json').read_bytes())
    observed = [s for s in states if s.get('MainPID') == actor['pid'] and s.get('entry') == 'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain' and not s.get('race')]
    require(observed and all(s['InvocationID'] == INV and str(s['startTicks']) == actor['ticks'] for s in observed))
    for s in observed:
        p=s['process']; require(p['Uid'].split()==['999']*4 and p['Gid'].split()==['981']*4
                and sorted(p['Groups'].split(),key=int)==['980','981','982','986'] and p['NoNewPrivs']=='1'
                and all(int(p[k],16)==0 for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')))
    pid1=[json.loads(l) for l in (OLD/'pid1.private.jsonl').read_bytes().splitlines()]
    jobs={s['Job'] for s in states if s.get('Job','').isdigit() and int(s['Job'])>0}
    done=[r for r in pid1 if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf' and r.get('JOB_TYPE')=='start' and r.get('JOB_RESULT')=='done']
    require(len(jobs)==len(done)==1 and done[0]['JOB_ID'] in jobs
            and all(r.get('_PID')=='1' and r.get('_UID')=='0' and r.get('_COMM')=='systemd'
                    and r.get('_BOOT_ID')=='cc9ed8747f4f450ea1888de1e42c8441' and r.get('INVOCATION_ID')==INV for r in pid1))
    held=owner()
    env.update(baseline=baseline, preserved=preserved, terminal=None, native_invocation=INV,
               prepared=prepared, credentials_before=original['credentials'], CREDS=creds,
               last_dependencies={}, held=held, owner=owner)
    def connection(present):
        require(present is False)
        q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0'])
    env['connection']=connection
    def validate_configuration(values):
        require(values==baseline['configuration'])
        require(current_gc_after_known20(terminal,env['show'](UNIT,env['FIELDS'])))
        return True
    env['validate_configuration']=validate_configuration
    node=next(n for n in ast.walk(code) if isinstance(n, ast.FunctionDef) and n.name=='snapshot')
    changed=0
    class FixedHistory(ast.NodeTransformer):
        def visit_Compare(self, n):
            nonlocal changed
            if ast.unparse(n)=="configuration == baseline['configuration']":
                changed+=1
                return ast.copy_location(ast.Call(func=ast.Name(id='validate_configuration',ctx=ast.Load()),args=[ast.Name(id='configuration',ctx=ast.Load())],keywords=[]),n)
            return self.generic_visit(n)
    node=FixedHistory().visit(node); ast.fix_missing_locations(node); require(changed==1)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed full snapshot history join>','exec'),env)
    def snapshot():
        value=env['snapshot'](False)
        require(value['units'][UNIT] == current_terminal)
        value['bootstrapOldProofs']=tree(OLD)
        value['bootstrapTools']=tree(TOOLS)
        return value
    return env, snapshot
