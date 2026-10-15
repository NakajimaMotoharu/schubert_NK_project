"""One exact Test-only maintenance admission/readback related54 group."""
import ast
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3348_related_boundary_group as prior
from db_fixture_lifecycle_audit import scan as lifecycle_scan

ROOT, SOURCE, W = prior.ROOT, prior.SOURCE, prior.W
CHANGED = {
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepositoryTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningControlScopeTest.java'}
CLASSES = {**prior.CLASSES,
           'protocol': {'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest': 7},
           'batch': {'dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest': 8,
                     'dev.codex.schubert.nk.batch.file.MorningControlScopeTest': 19}}
METHODS = [('dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest',
            'exp3366001PriorSuccessRevalidatesEveryReadbackWithoutMutation'),
           ('dev.codex.schubert.nk.batch.file.MorningControlScopeTest',
            'mctrl019NativeEntryNullContractsNeverReachTrustedWork')]


def validate(snapshot):
    full = json.loads((W / 'pg3352-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    native = json.loads((W / 'pg3354-oracle-boundary-native-qualified-v1/manifest.safe.json').read_bytes())
    r = full['result']; n = native['result']
    prior.require(full['actualExit'] == native['actualExit'] == r['actualExit'] == n['actualExit'] == 0
                  and r['tests'] == n['qualifiedFullTests'] == 3704 and r['productionSource'] == SOURCE
                  and n['mainClassesIdentical'] == 1643 and n['qualifiedNativeStreams'] == 28,
                  'genuine previous3704/native28 required')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', r['sourceSnapshot'], snapshot,
                                          '--', *prior.engine.SCOPE], cwd=ROOT, text=True).splitlines())
    before = json.loads((ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3368-db-fixture-lifecycle/before.json').read_bytes())
    lifecycle = {row[0] for row in before['entries'] if any(not call[2] for call in row[6])}
    prior.require(len(lifecycle) == 94 and changed == CHANGED | lifecycle,
                  'exact original two Test files plus registered94 lifecycle fixes, no Main/resource/settings')
    after = lifecycle_scan(ROOT)
    prior.require(len(after) == 129 and all(row['status'] in ['GUARDED', 'NO_NULLABLE_STATIC_DB_STOP']
                  and all(c['guarded'] for c in row.get('cleanupCalls', [])) for row in after),
                  'all129 lifecycle scopes and nullable sibling owners guarded')
    for module, names in CLASSES.items():
        for name, count in names.items():
            path = 'src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java'
            raw = subprocess.check_output(['git', 'show', snapshot + ':' + path], cwd=ROOT, text=True)
            prior.require(raw.count('@Test\n') == count, 'every selected static method counted')
    return r


def server():
    raw = prior.SERVER.replace('PG3348', 'PG3366').replace('source-full-PG3330', 'source-full-PG3350').replace('PG3366-related-v1', 'PG3366-related-v2').replace('all44 actual cases', 'all54 actual cases')
    start = raw.index("\n if module=='batch':")
    end = raw.index('\nrequire(len(all_cases)', start)
    raw = raw[:start] + r'''
 if module=='batch':
  targets={'dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository','dev/codex/schubert/nk/batch/file/MorningControlScope'}
  result[module]['targetClassCounters']={c.get('name'):{x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in c.findall('counter')}for p in node.findall('package')for c in p.findall('class')if c.get('name')in targets}
  require(set(result[module]['targetClassCounters'])==targets,'both whole target classes measured')
''' + raw[end:]
    tree = ast.parse(raw); counts = 0; methods = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 44:
            node.value = 54; counts += 1
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'expected':
            node.iter = ast.parse(repr(METHODS), mode='eval').body; methods += 1
    prior.require(counts == 3 and methods == 1, 'exact template test-count and two-method gates retained')
    positions = [i for i, node in enumerate(tree.body) if isinstance(node, ast.Assign)
                 and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                         and t.value.id == 'env' and isinstance(t.slice, ast.Constant)
                         and t.slice.value == 'PATH' for t in node.targets)]
    prior.require(len(positions) == 1, 'one actual Maven environment setup')
    tree.body[positions[0] + 1:positions[0] + 1] = ast.parse(r'''
pg=B/'tools/postgresql18/usr';initdb=pg/'lib/postgresql/18/bin/initdb'
require(initdb.is_file(),'fixed server PG18 initdb required before selected tests')
pg_env={**env,'LD_LIBRARY_PATH':str(pg/'lib/x86_64-linux-gnu')+':'+str(pg/'lib/postgresql/18/lib')}
pg_version=subprocess.run([str(initdb),'--version'],env=pg_env,capture_output=True,text=True,check=True,timeout=10).stdout.strip()
require(pg_version.startswith('initdb (PostgreSQL) 18.') and len(pg_version)<80,'actual fixed PG18 version required')
env['SCHUBERT_PG_ROOT']=str(pg)
pg_meta={'root':str(pg),'version':pg_version,'initdbSha256':sha(initdb)}
''').body
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'value' for t in node.targets):
            prior.require(isinstance(node.value, ast.Dict), 'one genuine terminal result')
            node.value.keys.append(ast.Constant('postgresToolchain')); node.value.values.append(ast.Name('pg_meta', ast.Load()))
    raw = ast.unparse(ast.fix_missing_locations(tree))
    compile(raw, '<related54 template before actual data embedding>', 'exec')
    complete = ('INPUT={}\n' + inspect.getsource(prior.require) + '\n'
                + inspect.getsource(prior.classify) + '\n' + raw)
    prior.require(check(complete, '<related54 final namespace>') == 0, 'complete namespace')
    return raw


def main():
    raw = inspect.getsource(prior.main).replace('pg3348-related-boundary-group-v1', 'pg3366-maintenance-boundary-group-v2').replace('PG3348', 'PG3366').replace('PG3366-related-v1', 'PG3366-related-v2')
    namespace = {**prior.__dict__, 'CLASSES': CLASSES, 'validate': validate, 'SERVER': server()}
    exec(compile(raw, '<related54 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
