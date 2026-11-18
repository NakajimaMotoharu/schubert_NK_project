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


def main(unit_name, out_name, prior_same_main=None):
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
        (161,'PG39944-p020-cache-and-session161-v1'),(161,'PG39946-p020-cache-and-session161-v2'),
        (165,'PG39964-p020-invalid-range165-v1'),(165,'PG39965-p020-invalid-range165-v2'),
        (170,'PG39990-p020-search-empty170-v1'),
        (176,'PG40014-p020-game-onchange176-v1'),
        (182,'PG40034-p020-l01-required-actions-v1'),(182,'PG40035-p020-l01-required-actions-v2'),
        (187,'PG40056-p020-error-disclosure187-v1'),(187,'PG40057-p020-error-disclosure187-v2')}
    assert actual['stages']['unit']['actualExit']==0
    snapshot=Path(begin['snapshot'])
    classes=Path(actual['classesDir'])
    assert len(actual['mainPhysical'])==17 and R['physical'](classes)==actual['mainPhysical']
    assert all(ref(Path(p['path']))==p for p in previous['toolAndRulePins'])
    assert read(BASE/'manifest.json')['stageExits']['spotbugs']==0
    out.mkdir()
    src={name:begin['inputHashes'][name] for name in begin['sourceInputsUnchangedOutside']}
    assert len(src)==(4 if 'l01-required-actions' in unit_name else 2)
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
    old_typed=None
    if prior_same_main:
        assert (unit_name,prior_same_main) in {
            ('PG39965-p020-invalid-range165-v2','PG39968-p020-invalid-range-static-v1'),
            ('PG40035-p020-l01-required-actions-v2','PG40036-p020-l01-required-actions-static-v1'),
            ('PG40057-p020-error-disclosure187-v2','PG40058-p020-error-disclosure-static-v1')}
        receipt=E/prior_same_main/'manifest.json'
        before=read(receipt)
        prior_manifest=Path(before['unit']['path'])
        assert ref(prior_manifest)==before['unit']
        prior=read(prior_manifest)
        assert before['allPhysicalUnchanged'] and before['stageExits']['spotbugs']==0
        assert prior['mainPhysical']==actual['mainPhysical']==R['physical'](classes)
        source_inputs={p:h for p,h in begin['inputHashes'].items() if '/src/main/' in p or p.endswith('pom.xml')}
        assert all(prior['inputHashes'][p]==h for p,h in source_inputs.items())
        pin=before['reports']['spotbugs']['raw']
        old_xml=Path(pin['path'])
        assert ref(old_xml)==pin and before['reports']['spotbugs']['exactPhysical']
        old_typed=dict(receipt=ref(receipt),report=pin,actualArchivedExit=0,executedInCurrentScope=False)
        commands.pop('spotbugs')
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(Q['run'],name,cmd,out,snapshot) for name,cmd in commands.items()]
        stages=dict(fut.result() for fut in futures)
    if old_typed:
        stages['spotbugs']={'actualExit':0,'priorExactMain':old_typed}
        (out/'spotbugs.xml').write_bytes(Path(old_typed['report']['path']).read_bytes())
    else:
        (out/'spotbugs.xml').write_bytes((classes.parent/'spotbugsXml.xml').read_bytes())
    result={name:Q['parse_report'](name,out/(name+'.xml'),snapshot,src,set(actual['mainPhysical']))
            for name in ('checkstyle','pmd','spotbugs')}
    manifests=dict(source=actual['source'],stageExits={k:v['actualExit'] for k,v in stages.items()},reports=result,
        unit=ref(unit_path),allPhysicalUnchanged=R['physical'](classes)==actual['mainPhysical'],
        coverageWaiver=0,productActions=0,priorExactMainTyped=old_typed,whole451Accepted=False,
        terminalAtUTC=R['utc'](),verifier=ref(HERE))
    save(out/'manifest.json',manifests)
    print(manifests['stageExits'],result)


if __name__=='__main__':
    main(*sys.argv[1:])
