"""Apply the unchanged characterization module static policies to the frozen login comparator."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve()
S=runpy.run_path(str(HERE.with_name('5228_p020_definition_static.py')))
Q,R=S['Q'],S['R']
E=S['E']
read,save,ref=S['read'],S['save'],S['ref']
BASE=E/'PG39832-p020-definition-static-v1'
PREVIOUS=E/'PG39830-p020-definition-green144-v3'


def main(unit_name, out_name):
    unit_dir=E/unit_name
    out=(E/out_name).resolve()
    unit_path=unit_dir/'manifest.json'
    actual=read(unit_path)
    previous=read(BASE/'begin.json')
    prior_unit=read(PREVIOUS/'begin.json')
    begin=read(unit_dir/'begin.json')
    assert actual['source']==begin['source']==R['git']('rev-parse','HEAD').decode().strip()
    assert (actual['expected'],unit_name) in {(148,'PG39904-p020-approved-login-title148-v1'),
        (153,'PG39922-p020-approved-all-brand153-v1'),(153,'PG39923-p020-approved-all-brand153-v2'),
        (161,'PG39944-p020-cache-and-session161-v1'),(161,'PG39946-p020-cache-and-session161-v2')}
    assert actual['stages']['unit']['actualExit']==0
    snapshot=Path(begin['snapshot'])
    classes=Path(actual['classesDir'])
    assert len(actual['mainPhysical'])==17 and R['physical'](classes)==actual['mainPhysical']
    assert all(ref(Path(p['path']))==p for p in previous['toolAndRulePins'])
    assert read(BASE/'manifest.json')['stageExits']['spotbugs']==0
    out.mkdir()
    src={name:begin['inputHashes'][name] for name in begin['sourceInputsUnchangedOutside']}
    assert len(src)==2
    for name,digest in src.items():
        assert ref(snapshot/name)['sha256']==digest
    listing=out/'sources.txt'
    listing.write_text(''.join(f'{snapshot/path}\n' for path in sorted(src)))
    commands={}
    for name,cmd in previous['commands'].items():
        command=[entry.replace(prior_unit['snapshot'],str(snapshot)).replace(str(BASE.resolve()),str(out)) for entry in cmd]
        if name=='format':
            assert all(part.endswith('.java') for part in command[6:])
            command=command[:6]+[str(snapshot/path) for path in sorted(src)]
        commands[name]=command
    save(out/'begin.json',dict(source=actual['source'],unit=ref(unit_path),commands=commands,
          priorToolRecipe=ref(BASE/'begin.json'),toolAndRulePins=previous['toolAndRulePins'],sourceInputs=src,productActions=0))
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(Q['run'],name,cmd,out,snapshot) for name,cmd in commands.items()]
        stages=dict(fut.result() for fut in futures)
    (out/'spotbugs.xml').write_bytes((classes.parent/'spotbugsXml.xml').read_bytes())
    result={name:Q['parse_report'](name,out/(name+'.xml'),snapshot,src,set(actual['mainPhysical']))
            for name in ('checkstyle','pmd','spotbugs')}
    manifests=dict(source=actual['source'],stageExits={k:v['actualExit'] for k,v in stages.items()},reports=result,
        unit=ref(unit_path),allPhysicalUnchanged=R['physical'](classes)==actual['mainPhysical'],
        coverageWaiver=0,productActions=0,whole451Accepted=False,terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(out/'manifest.json',manifests)
    print(manifests['stageExits'],result)


if __name__=='__main__':
    main(*sys.argv[1:])
