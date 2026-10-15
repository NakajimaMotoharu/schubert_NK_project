"""One exact Test-only maintenance admission/readback related54 group."""
import ast
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3348_related_boundary_group as prior

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
    prior.require(changed == CHANGED, 'exact two Test-only changes, no Main/resource/settings')
    for module, names in CLASSES.items():
        for name, count in names.items():
            path = 'src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java'
            raw = subprocess.check_output(['git', 'show', snapshot + ':' + path], cwd=ROOT, text=True)
            prior.require(raw.count('@Test\n') == count, 'every selected static method counted')
    return r


def server():
    raw = prior.SERVER.replace('PG3348', 'PG3366').replace('source-full-PG3330', 'source-full-PG3350')
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
    raw = ast.unparse(ast.fix_missing_locations(tree))
    compile(raw, '<related54 template before actual data embedding>', 'exec')
    complete = ('INPUT={}\n' + inspect.getsource(prior.require) + '\n'
                + inspect.getsource(prior.classify) + '\n' + raw)
    prior.require(check(complete, '<related54 final namespace>') == 0, 'complete namespace')
    return raw


def main():
    raw = inspect.getsource(prior.main).replace('pg3348-related-boundary-group-v1', 'pg3366-maintenance-boundary-group-v1').replace('PG3348', 'PG3366')
    namespace = {**prior.__dict__, 'CLASSES': CLASSES, 'validate': validate, 'SERVER': server()}
    exec(compile(raw, '<related54 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
