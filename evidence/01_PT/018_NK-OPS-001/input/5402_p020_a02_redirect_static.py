"""Check the exact comparator sources and compiled 17-type offline module."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import runpy


HERE = Path(__file__).resolve()
S = runpy.run_path(str(HERE.with_name('5228_p020_definition_static.py')))
Q, R, E, read, save, ref = (S[key] for key in ('Q', 'R', 'E', 'read', 'save', 'ref'))


def main():
    unit_dir = E / 'PG40658-p020-a02-redirect-green-v1'
    previous_dir = E / 'PG40210-p020-a02-session-census-static-v1'
    out = (E / 'PG40660-p020-a02-redirect-static-v1').resolve()
    unit_path = unit_dir / 'manifest.json'
    unit, begin = read(unit_path), read(unit_dir / 'begin.json')
    original = read(previous_dir / 'begin.json')
    assert unit['source'] == begin['source'] == R['git']('rev-parse', 'HEAD').decode().strip()
    assert len(unit['mainPhysical']) == 17 and unit['expected'] == 210
    assert all(stage['actualExit'] == 0 for stage in unit['stages'].values())
    assert all(ref(Path(row['path'])) == row for row in original['toolAndRulePins'])
    snapshot = Path(begin['snapshot'])
    classes = Path(unit['classesDir'])
    assert R['physical'](classes) == unit['mainPhysical']
    source_hashes = {name: begin['inputHashes'][name] for name in begin['sourceChanges']}
    assert len(source_hashes) == 2 and all(ref(snapshot / name)['sha256'] == value
                                           for name, value in source_hashes.items())
    out.mkdir()
    (out/'sources.txt').write_text(''.join(f'{snapshot/name}\n' for name in sorted(source_hashes)))
    old_snapshot = read(E/'PG40208-p020-a02-session-census-green208-v1'/'begin.json')['snapshot']
    commands = {name: [arg.replace(old_snapshot, str(snapshot)).replace(str(previous_dir.resolve()), str(out))
                       for arg in command] for name, command in original['commands'].items()}
    assert set(commands) == {'spotbugs', 'format', 'checkstyle', 'pmd'}
    save(out/'begin.json', dict(source=unit['source'], commands=commands, unit=ref(unit_path),
                                toolAndRulePins=original['toolAndRulePins'], sourceInputs=source_hashes))
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(Q['run'], name, command, out, snapshot) for name, command in commands.items()]
        stages = dict(future.result() for future in futures)
    (out/'spotbugs.xml').write_bytes((classes.parent/'spotbugsXml.xml').read_bytes())
    reports = {name: Q['parse_report'](name, out/(name+'.xml'), snapshot, source_hashes, set(unit['mainPhysical']))
               for name in ('checkstyle', 'pmd', 'spotbugs')}
    assert R['physical'](classes) == unit['mainPhysical']
    manifest = out/'manifest.json'
    save(manifest, dict(source=unit['source'], stageExits={k: v['actualExit'] for k, v in stages.items()},
                        reports=reports, unit=ref(unit_path), allPhysicalUnchanged=True,
                        productActions=0, whole451Accepted=False, terminalAtUTC=R['utc']()))
    print(ref(manifest), {k: v['actualExit'] for k, v in stages.items()})


if __name__ == '__main__':
    main()
