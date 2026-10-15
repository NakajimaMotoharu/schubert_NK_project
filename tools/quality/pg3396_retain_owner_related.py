"""Related33/eight suites for one new retain contract; all Main byte-preserving."""
import ast
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3348_related_boundary_group as base

ROOT, SOURCE, W = base.ROOT, base.SOURCE, base.W
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningStartupRetainOwnerTest.java'
CLASSES = {**base.CLASSES,
           'protocol': {'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest': 7},
           'batch': {'dev.codex.schubert.nk.batch.file.MorningStartupRetainOwnerTest': 1,
                     'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerTest': 3,
                     'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerAdmissionTest': 2}}
METHOD = ('dev.codex.schubert.nk.batch.file.MorningStartupRetainOwnerTest',
          'retainsCallerLockAcrossInterruptUntilOwnedTermination')


def validate(snapshot):
    f = json.loads((W / 'pg3374-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    n = json.loads((W / 'pg3376-oracle-boundary-native-qualified-v1/manifest.safe.json').read_bytes())
    r = f['result']; native = n['result']
    base.require(f['actualExit'] == n['actualExit'] == r['actualExit'] == native['actualExit'] == 0
                 and r['tests'] == native['qualifiedFullTests'] == 3706 and native['qualifiedNativeStreams'] == 28
                 and r['productionSource'] == SOURCE and native['mainClassesIdentical'] == 1643,
                 'actually completed previous3706/native28')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', r['sourceSnapshot'], snapshot,
                                          '--', *base.engine.SCOPE], cwd=ROOT, text=True).splitlines())
    base.require(changed == {TEST}, 'one new Test only; all Main/resources/POM/settings unchanged')
    for module, names in CLASSES.items():
        for name, count in names.items():
            path = f'src/schubert-nk-{module}/src/test/java/' + name.replace('.', '/') + '.java'
            raw = subprocess.check_output(['git', 'show', snapshot + ':' + path], cwd=ROOT, text=True)
            base.require(raw.count('@Test\n') == count, 'every explicitly selected method')
    base.require(sum(sum(v.values()) for v in CLASSES.values()) == 33, 'independent related33')
    return r


def server():
    # Template code only; genuine metadata is bound afterward by the transport.
    raw = base.SERVER.replace('PG3348', 'PG3396').replace('source-full-PG3330', 'source-full-PG3372')
    begin = raw.index("\n if module=='batch':")
    end = raw.index('\nrequire(len(all_cases)', begin)
    raw = raw[:begin] + r'''
 if module=='batch':
  target=next(c for p in node.findall('package')for c in p.findall('class')if c.get('name')=='dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner')
  method=next(m for m in target.findall('method')if m.get('name')=='retain')
  actual={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in method.findall('counter')}
  require(actual['LINE']=={'missed':0,'covered':3} and actual['METHOD']=={'missed':0,'covered':1},'actual retained owner method executed in child')
  result[module]['retainMethodCounters']=actual
''' + raw[end:]
    tree = ast.parse(raw); counts = 0; suites = 0; loops = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 44:
            node.value = 33; counts += 1
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 7:
            node.value = 8; suites += 1
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'expected':
            node.iter = ast.parse(repr([METHOD]), mode='eval').body; loops += 1
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'newMethods':
                    value.value = 1
    base.require(counts == 3 and suites == 2 and loops == 1, 'exact code-level counts and method list')
    raw = ast.unparse(ast.fix_missing_locations(tree))
    complete = 'INPUT={}\n' + inspect.getsource(base.require) + '\n' + inspect.getsource(base.classify) + '\n' + raw
    base.require(check(complete, '<related33>') == 0, 'complete standalone namespace')
    return raw


def main():
    raw = inspect.getsource(base.main).replace('pg3348-related-boundary-group-v1', 'pg3396-retain-owner-related-v1').replace('PG3348', 'PG3396')
    namespace = {**base.__dict__, 'CLASSES': CLASSES, 'validate': validate, 'SERVER': server()}
    exec(compile(raw, '<related33 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
