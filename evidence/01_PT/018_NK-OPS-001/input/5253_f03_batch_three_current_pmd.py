"""Acquire missing full-rules PMD evidence for the exact eligible Batch source changes."""
from pathlib import Path
import gzip
import runpy
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__)
SB = runpy.run_path(str(HERE.with_name('5242_f03_batch_current_static_delta.py')))
E, DOC, ROOT = (SB[key] for key in ('E','DOC','ROOT'))
ref, load, save, allowed, checked_data = (SB[key] for key in ('ref','load','save','allowed','checked_data'))
common = SB['COMMON']
remaining = {'BackupCommitService', 'LogCleanupService', 'StepCleanupService'}


def main():
    start_path = next(DOC.glob('547_*'))
    start = load(start_path)['values']
    assert SB['G']['git']('rev-parse','HEAD').decode().strip() == start['source']
    pins = start['oracleReferences']
    assert all(ref(Path(row['path'])) == row for row in pins)
    build, spotbugs, historic, scope, cleanup = (load(Path(row['path'])) for row in pins)
    assert build['sourceCore'] == start['productionCoreMain'] == spotbugs['source']
    assert {Path(p).stem for p in spotbugs['allowedMain']} == remaining | {'ProcessResourceScope','CleanupRepository'}
    assert scope['actualExit'] == cleanup['actualExit'] == 0
    workspace = Path(build['cwd'])
    assert workspace.parent == ROOT.parent/'pgpt-runs/PG379'
    sources = {p:h for p, h in spotbugs['allowedMain'].items() if Path(p).stem in remaining}
    for name, digest in sources.items():
        assert allowed(name) and checked_data(workspace,name,digest) == SB['G']['git']('show',f'{build["sourceCore"]}:{name}')
        assert digest == build['sourceInputs'][name]
    assert len(sources) == 3

    original = historic['command']
    rules = Path(original[original.index('--rulesets')+1])
    assert ref(rules)['sha256'] == historic['originalFullRulesetSha256']
    assert ref(Path(original[0]))['sha256'] == build['tools']['javaSha256']
    pmd_jars = original[original.index('-cp')+1].split(':')
    assert all(ref(Path(path))['sha256'] == historic['originalToolAndSdkHashes'][path] for path in pmd_jars)
    sdk = [s for s in original[original.index('--aux-classpath')+1].split(':') if s.endswith('.jar')]
    assert sdk and sdk[0].endswith('/lib/jrt-fs.jar')
    jrt = ref(Path(sdk[0]))
    assert Path(jrt['path']).parent == Path(original[0]).parents[1]/'lib'
    for path in sdk[1:]:
        assert ref(Path(path))['sha256'] == historic['originalToolAndSdkHashes'][path]

    out = (E/start['run']).resolve()
    stage = ROOT.parent/'pgpt-runs/PG379'/start['run'].lower()
    oldjar = Path(spotbugs['closedAux']['path'])
    assert ref(oldjar) == spotbugs['closedAux']
    out.mkdir()
    stage.mkdir(mode=0o700)
    typed = stage/'eligible-typed-aux.jar'
    with ZipFile(oldjar) as before, ZipFile(typed,'x',compression=ZIP_DEFLATED) as after:
        paths = before.namelist()
        assert len(paths) == spotbugs['auxInputCount'] and len(set(paths)) == len(paths)
        assert all(p.endswith('.class') and allowed(p) for p in paths)
        for path in paths:
            after.writestr(path,before.read(path))
        assert not set(paths) & spotbugs['targets'].keys()
        for relative, digest in spotbugs['targets'].items():
            assert allowed(relative) and digest == build['physicalClassHashes']['batch'][relative]
            after.writestr(relative,checked_data(workspace,
                  'src/schubert-nk-batch/target/classes/'+relative,digest))
    files = out/'sources.txt'
    files.write_text(''.join(str(workspace/name)+'\n' for name in sorted(sources)))
    report = out/'pmd.xml'
    command = list(original)
    for flag, value in (('--file-list',str(files)),('--aux-classpath',':'.join([sdk[0],str(typed),*sdk[1:]])),
                        ('--report-file',str(report))):
        command[command.index(flag)+1] = value
    assert ['--use-version','java-25','--no-cache'] == [*command[command.index('--use-version'):command.index('--use-version')+2],
                                                         command[command.index('--no-cache')]]
    save(out/'begin.json',dict(source=build['sourceCore'], start=ref(start_path), oracleReferences=pins,
         sourceInput=sources, auxiliary=ref(typed), auxiliaries=spotbugs['auxInputCount']+len(spotbugs['targets']),
         auxSource=spotbugs['closedAux'], priorRootAndExactHoldExclusion=spotbugs['excludedFromTargetsAndAux'],
         fullRules=ref(rules), javaRuntimeImageLoader=jrt, command=command, productJobs=0, startedAtUTC=common['utc']()))
    _, terminal = common['run']('pmd',command,out,workspace)
    findings = []
    inspection = {}
    if report.exists():
        inspection = common['parse_report']('pmd',report,workspace,sources,set())
        root = common['ET'].parse(report).getroot()
        ns = root.tag.partition('}')[0]+'}'
        for file in root.findall(ns+'file'):
            name = str(Path(file.get('name')).relative_to(workspace))
            assert name in sources
            findings.extend(dict(file=name,start=int(v.get('beginline')),end=int(v.get('endline')),
                                 column=int(v.get('begincolumn')),rule=v.get('rule'),text=(v.text or '').strip())
                            for v in file.findall(ns+'violation'))
        assert inspection['findings'] == len(findings)
    for stream in ('stdout','stderr'):
        archived = terminal[stream]
        p = Path(archived['archive']['path'])
        assert ref(p) == archived['archive'] and common['sha'](gzip.decompress(p.read_bytes())) == archived['exactSha256']
    usable = terminal['actualExit'] in (0,4) and 'processingErrors' in inspection and inspection['processingErrors']==0
    save(out/'manifest.json',dict(actualExit=0 if usable else 1, realPmdExit=terminal['actualExit'], source=build['sourceCore'],
         begin=ref(out/'begin.json'), toolTerminal=ref(out/'pmd-exit.json'), raw=inspection, rawFindings=findings,
         usedNewRuleExclusions=False, productTests=0, formalAccepted=False, dispositionPending=len(findings),
         preparationGuardExit1='Reading existing manifest via Path corrected before PMD started',
         terminalAtUTC=common['utc']()))
    print(terminal['actualExit'],len(findings),[(Path(row['file']).name,row['start'],row['rule']) for row in findings])
    return 0 if usable else 1


if __name__ == '__main__':
    raise SystemExit(main())
