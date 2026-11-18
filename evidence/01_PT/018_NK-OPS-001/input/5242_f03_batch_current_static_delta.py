"""Run typed analysis on the exact eligible Batch change set of the current candidate."""
from pathlib import Path
import gzip
import runpy
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve()
COMMON = runpy.run_path(str(HERE.with_name('5224_f03_storage_bootstrap_module_static.py')))
ROOT, E, DOC = (COMMON[key] for key in ('ROOT', 'E', 'H'))
G, ref, load, save = (COMMON[key] for key in ('G', 'ref', 'load', 'save'))
EXACT = {'BackupCommitService', 'CleanupRepository', 'LogCleanupService',
         'ProcessResourceScope', 'StepCleanupService'}
FORBIDDEN = COMMON['FORBIDDEN'] | {'NativeNkA01Capture', 'NativeNkL01Capture', 'SnapshotKeyCloseWitness'}


def basename(relative):
    return Path(relative).stem.split('$',1)[0]


def allowed(relative):
    name = basename(relative)
    return name not in FORBIDDEN and not name.startswith('Root')


def checked_data(root, relative, expected):
    path = root / relative
    assert path.resolve() == path and not path.is_symlink()
    content = path.read_bytes()
    assert COMMON['sha'](content) == expected
    return content


def setup(start):
    paths = [Path(row['path']) for row in start['oracleReferences']]
    assert [ref(p) for p in paths] == start['oracleReferences']
    now, old, original_static, corrected, previous, edges = map(load,paths)
    assert now['sourceCore'] == edges['source'] == start['productionCoreMain']
    assert now['actualExit'] == old['actualExit'] == original_static['actualExit'] == corrected['actualExit'] == 0
    assert original_static['source'] == old['sourceCore']
    assert corrected['onlyAdditionalAux'] in previous['toolAndRulePins']
    assert original_static['checks']['batch']['actualExit'] == 0
    assert now['productTestsExecuted'] == 0 and now['inputHashesReverified']
    before, after = old['physicalClassHashes']['batch'], now['physicalClassHashes']['batch']
    selected = {key for key, digest in after.items() if before.get(key) != digest}
    assert len(selected) == 8 and {basename(p) for p in selected} == EXACT
    assert set(before)-set(after) == {p for p in before if p.endswith('/CleanupRepository$1.class')}
    assert all(allowed(name) for name in selected)
    work = Path(now['cwd'])
    assert work.parent == ROOT.parent/'pgpt-runs/PG379' and work.resolve() == work
    return paths, now, corrected, previous, selected, work


def main():
    start_path = next(DOC.glob('523_F03*'))
    start = load(start_path)['values']
    assert G['git']('rev-parse','HEAD').decode().strip() == start['source']
    paths, now, corrected, previous, selected, work = setup(start)
    directories = {m:work/f'src/schubert-nk-{m}/target/classes' for m in now['physicalClassHashes']}
    now_main = {key:h for key,h in now['sourceInputs'].items() if
                key.startswith('src/schubert-nk-batch/src/main/java/') and Path(key).stem in EXACT}
    assert len(now_main) == 5
    for path, digest in now_main.items():
        assert ref(work/path)['sha256'] == digest
        assert G['git']('show',f'{now["sourceCore"]}:{path}') == (work/path).read_bytes()
    selected_paths = [directories['batch']/p for p in sorted(selected)]
    jdk = COMMON['JAVA']
    assert ref(jdk)['sha256'] == now['tools']['javaSha256']
    current_aux = [p for p in previous['sdkJars']]
    current_aux.append(corrected['onlyAdditionalAux']['path'])
    assert all(ref(Path(p))['sha256'] == previous['sdkJars'][p] for p in previous['sdkJars'])
    assert ref(Path(current_aux[-1])) == corrected['onlyAdditionalAux']
    old_cmd = previous['exactCommands']['spotbugs']
    repo = [Path(p) for p in old_cmd[old_cmd.index('-cp')+1].split(':')]
    known = {p['path']:p for p in previous['toolAndRulePins']}
    assert all(ref(p) == known[str(p)] for p in repo)
    assert ['-effort:max','-low','-xml:withMessages','-exitcode'] == old_cmd[old_cmd.index('-effort:max'):old_cmd.index('-exitcode')+1]
    out=(E/start['run']).resolve()
    stage=ROOT.parent/'pgpt-runs/PG379'/start['run'].lower()
    out.mkdir()
    stage.mkdir(mode=0o700)
    allowed_jar = stage/'closed-physical-aux.jar'
    aux_inputs, denied = {}, []
    with ZipFile(allowed_jar, 'x', compression=ZIP_DEFLATED) as bundle:
        for module, hashes in now['physicalClassHashes'].items():
            for relative, digest in sorted(hashes.items()):
                if not allowed(relative):
                    denied.append((module,relative))
                elif module!='batch' or relative not in selected:
                    assert relative not in aux_inputs
                    aux_inputs[relative]=digest
                    bundle.writestr(relative,checked_data(directories[module],relative,digest))
    assert len(aux_inputs) + len(denied) + len(selected) == 1102
    for path in selected_paths:
        # Hold guards ran before any byte was read; check exactly the consumed primary file.
        relative=str(path.relative_to(directories['batch']))
        checked_data(directories['batch'],relative,now['physicalClassHashes']['batch'][relative])
    xml=out/'spotbugs.xml'
    auxdef=out/'spotbugs-aux.txt'
    auxdef.write_text('\n'.join([str(allowed_jar),*current_aux])+'\n')
    cmd=[*old_cmd[:old_cmd.index('-auxclasspathFromFile')+1],str(auxdef),'-output',str(xml),*map(str,selected_paths)]
    begin=dict(command=cmd,groupStart=ref(start_path),prior=[ref(p) for p in paths],source=now['sourceCore'],
               targets={name:now['physicalClassHashes']['batch'][name] for name in sorted(selected)},
               allowedMain=now_main,externalSdkCount=len(current_aux),
               closedAux=ref(allowed_jar),excludedFromTargetsAndAux=len(denied),auxInputCount=len(aux_inputs),
               includedRootTypeBodies=0, productJobs=0,startedAtUTC=COMMON['utc']())
    save(out/'begin.json',begin)
    _,terminal=COMMON['run']('spotbugs',cmd,out,work)
    reported=COMMON['parse_report']('spotbugs',xml,work,now_main,selected)
    xml_root=COMMON['ET'].parse(xml).getroot() if xml.exists() else None
    found={} if xml_root is None else {
      'checks':[dict(type=x.get('type'),primary=x.find('Class').get('classname')) for x in xml_root.findall('BugInstance')],
      'missing':[x.text for x in xml_root.findall('.//MissingClass')]}
    for file in ('stdout','stderr'):
        pin=terminal[file]
        arc=Path(pin['archive']['path'])
        assert ref(arc)==pin['archive']
        assert COMMON['sha'](gzip.decompress(arc.read_bytes()))==pin['exactSha256']
    okay=(terminal['actualExit']==0 and reported.get('exactPhysical') and
          all(reported.get(key)==0 for key in ('findings','missingClasses','errors')))
    result=dict(actualExit=0 if okay else 1, source=now['sourceCore'], begin=ref(out/'begin.json'),
                toolTerminal=ref(out/'spotbugs-exit.json'), realAnalysisExit=terminal['actualExit'], result=reported,
                resultDetails=found, currentExactTargets=len(selected), currentMainOwners=len(now_main),
                previousFullReportReplayed=False, priorCoverageImported=False, productTrials=0,
                wholeF03Accepted=False, whole451Accepted=False, newAcceptance=0,
                terminalAtUTC=COMMON['utc'](), verifier=ref(HERE))
    save(out/'manifest.json',result)
    print(result)
    return result['actualExit']


if __name__=='__main__':
    raise SystemExit(main())
