"""All851/1666/ABI and unsuppressed raw18 proof after ordinary API15/921; never executes PT."""
import hashlib
import json
import subprocess
import re
from collections import Counter
import pg5992_web_contract_static as previous
import pg5942_private_lock_static as namespace_engine
from pg5940_private_lock_compile import ROOT, W, TC, sha
from pg6006_api_bounds_selected import PLAN, PLAN_SHA, OLD


def plan():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('immutable15/18 API declaration')
    return json.loads(PLAN.read_bytes())


def validate_source(source, root):
    data = plan(); paths = {r['path'] for r in data['sourcePlans']}
    if len(paths) != 15 or set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != paths:
        raise ValueError('only15 declared Main source changes')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('no Test/oracle/template/SQL/quality gate change')
    before = json.loads((W/'pg5992-web-contract-static-v1/manifest.safe.json').read_bytes()); expected = dict(before['allSourceHashes'])
    if before['source'] != OLD or before['actualExit'] != 0:
        raise ValueError('actual same-source baseline851/1666')
    for row in data['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('exact current original source')
        expected[row['path']] = row['predictedAfterSha256']
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
    if actual != expected or len(actual) != 851:
        raise ValueError('all851 source and15 predicted changes fixed')
    return actual


def physical_changes(old, new):
    owners = {'api:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    if len(old) != 1666 or set(new) != set(old) or not owners <= changed or any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changed):
        raise ValueError('all1666/15 required outer; only those nested/debug changes allowed')
    return sorted(changed)


def expected_rules(before, actual):
    expected = Counter(before); expected['AvoidLiteralsInIfCondition'] -= 18
    if expected != Counter(actual) or expected['AvoidLiteralsInIfCondition'] < 0:
        raise ValueError('exact18 raw literal removal only; no exclusions/lost other diagnostics')


def debug_proof(before, current, changed):
    owners = {'api:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}; nested = sorted(set(changed)-owners)
    if not nested:
        return dict(classes=[], bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=None)
    names = [k.split(':', 1)[1][:-6].replace('/', '.') for k in nested]
    def disassemble(root):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-c', '-p', '-s', '-classpath', str(root/'src/schubert-nk-api/target/classes'), *names])
    a, b = disassemble(before), disassemble(current)
    if a != b:
        raise ValueError('unexpected nested executable/descriptor changes; keep unresolved')
    return dict(classes=nested, bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=hashlib.sha256(b).hexdigest())


def executable_sections(text):
    """Drop field declarations, retain every executable descriptor and symbolic instruction."""
    result=[]; block=[]
    def finish():
        if any(line.strip()=='Code:' for line in block):
            result.extend(block)
    for line in text.splitlines():
        if re.match(r'^  \S',line) or line=='}':
            finish();block=[]
        if '//' in line:
            instruction,comment=line.split('//',1)
            line=re.sub(r'#\d+', '#CP',instruction)+'//'+comment
        block.append(line.rstrip())
    finish()
    if not result:
        raise ValueError('at least one actual executable code section required')
    return '\n'.join(result)


def executable_proof(before,current):
    names=[r['path'].split('/src/main/java/')[1][:-5].replace('/','.') for r in plan()['sourcePlans']]
    def read(root):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-c','-p','-s','-classpath',str(root/'src/schubert-nk-api/target/classes'),*names],text=True)
    left=executable_sections(read(before));right=executable_sections(read(current))
    if left!=right:
        raise ValueError('literal constants must preserve every15 outer method instruction/descriptor; unknown delta held')
    return dict(classes=names,allMethodDescriptorsAndSymbolicInstructionsEqual=True,normalizedDisassemblySha256=hashlib.sha256(right.encode()).hexdigest(),normalization='Only field sections and numeric constant-pool operands removed; symbolic comments including bootstrap indices retained')


def runner_source():
    raw=previous.runner_source()
    changes={
        "'pg5978-web-form-static-v1/manifest.safe.json'":"'pg5992-web-contract-static-v1/manifest.safe.json'",
        "'PG5978-web-form-static-v1/manifest.json'":"'PG5992-web-contract-static-v1/manifest.json'",
        '61143deb9c99e713be46e913ba885e700125268f0e069535d3a143f59d4404c9':'4a31fe4157861fa2d636815e71256f5e4014ea05c1ad9bd21bb9d59e2d2b1eeb',
        'pg5984-web-form-selected921-v2/source':'pg5990-web-contract-selected921-v1/source',
        'pg5978-web-form-static-v1/aux-classpath.txt':'pg5992-web-contract-static-v1/aux-classpath.txt',
        'rawDiagnosticsRemovedByPg=42':'rawDiagnosticsRemovedByPg=18',
        '(921,149)':'(1021,175)',
        'all24ExecutableProof':'all15ExecutableProof',
        "target = BASE/'PG5992-web-contract-static-v1'":"target = BASE/'PG6008-api-bounds-static-v1'"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact API15/18 static binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<API15 all851 static>','exec')
    return raw


def main():
    scope = {**vars(namespace_engine), 'OLD': OLD, 'COMPILE': 'pg6006-api-bounds-selected1021-v1', 'SLOT': 'pg6008-api-bounds-static-v1',
             'plan': plan, 'validate_source': validate_source, 'physical_changes': physical_changes, 'expected_rules': expected_rules, 'debug_proof': debug_proof, 'executable_proof': executable_proof}
    exec(compile(runner_source(), '<API18 all-source static>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
