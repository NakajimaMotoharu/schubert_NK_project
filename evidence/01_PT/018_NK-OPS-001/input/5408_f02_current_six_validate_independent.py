"""Verify original Maven phase, all inputs and all seven lifecycle terminals."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def verified(ref):
    path = Path(ref['path'])
    assert pin(path) == ref
    return path


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    run = next(OPS.glob('PG40670-*'))
    terminal = run/'terminal.json'
    result = json.loads(terminal.read_bytes())
    begin = json.loads(verified(result['begin']).read_bytes())
    inventory = json.loads(verified(begin['inventory']).read_bytes())
    assert result['source'] == begin['source']
    core = result['productionCore']
    assert core == begin['productionCore'] and result['actualExit'] == 0
    assert begin['productTestSourcesCopied'] == begin['artifactFilesBefore'] == 0
    assert result['productClassfilesAfter'] == result['testResultDirectories'] == result['productJarsAfter'] == 0
    assert result['inputUnchanged'] and sum(begin['mainCounts'].values()) == 1027
    assert len(inventory) == 1035 and begin['pomCount'] == 8
    assert begin['command'][-1] == 'validate' and '-o' in begin['command'] and '-am' in begin['command']
    verified(begin['java'])
    verified(begin['maven'])
    assert all(hashlib.sha256(git('show', f'{core}:{name}')).hexdigest() == digest
               for name, digest in inventory.items())

    recipe = next(OPS.glob('PG40650-*/manifest.json'))
    lineage = json.loads(recipe.read_bytes())
    assert lineage['productionCore'] == core and len(lineage['exactPoms']) == 8
    assert {p: digest for p, digest in inventory.items() if p.endswith('pom.xml')} == lineage['exactPoms']
    new_paths = set(inventory)
    old_inventory = json.loads(next(OPS.glob('PG38184-*/manifest.json')).read_bytes())['inputHashes']
    assert set(old_inventory) <= new_paths
    assert len(new_paths - set(old_inventory)) == 1
    assert next(iter(new_paths - set(old_inventory))).endswith('/JdbcFailureGraph.java')

    text = verified(result['steps']).read_text()
    expected = {'schubert-nk'} | {f'schubert-nk-{module}' for module in begin['mainCounts']}
    results = {}
    for label, goal in (('enforcer', 'enforcer:3.6.3:enforce'), ('spotless', 'spotless:3.10.2:check')):
        modules = re.findall(rf'^\[INFO\] --- {re.escape(goal)} [^\n]* @ (schubert-nk[a-z-]*) ---$', text, re.M)
        assert len(modules) == len(expected) and set(modules) == expected
        results[label] = modules
    assert text.count('DependencyConvergence passed') == 7
    assert text.count('[INFO] BUILD SUCCESS') == 1
    assert not re.search(r'^\[INFO\] --- (compiler|surefire|failsafe):', text, re.M)
    out = OPS/'PG40672-f02-current-six-reactor-independent-v1'
    out.mkdir()
    manifest = out/'manifest.json'
    with manifest.open('x') as output:
        json.dump(dict(actualExit=0, source=result['source'], productionCore=core,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat(), terminal=pin(terminal),
                       inputFileCount=1035, exactCurrentMainFiles=1027, rootAndProducts=7,
                       modules=results, dependencyConvergence=7, previousQualifiedMavenModel=pin(recipe),
                       actualProductJars=0, actualProductClassfiles=0, actualProductTests=0,
                       wholeF02=False, wholeF03=False, whole451=False), output, indent=2)
        output.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
