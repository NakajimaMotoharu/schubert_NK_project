"""Rebind four fixed diagnostics to their original independent assertions and exact class bytes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PREFIX = 'dev/codex/schubert/nk/batch/'
BATCH = Path('src/schubert-nk-batch/src')
PKG = PREFIX + 'backup/'
TESTS = BATCH / 'test/java' / PKG
MAIN = BATCH / 'main/java' / PREFIX
PROFILE = 'BackupProfileTest'
VALUES = 'BackupManifestValuesTest'
TARGETS = (
    (41, 'BackupFileDigest', 'claim=<redacted>'),
    (42, 'BackupManifest', 'claims=<redacted>'),
    (43, 'BackupProfile', 'claims=<redacted>'),
    (44, 'BackupVersions', 'release=<redacted>'),
)
VALUE_DEPENDENCIES = dict(backup=('BackupFileDigest', 'BackupManifest', 'BackupVersions'),
                          repository=('BatchRun', 'BatchStep', 'BatchStepAttempt'))
VALUE_METHOD = 'nullAndRedaction'
PROFILE_METHOD = 'literalGoldenAndImmutableNonsecretClaims'


def digest(data):
    return sha256(data).hexdigest()


def reference(path):
    return dict(path=str(path.relative_to(ROOT) if path.is_absolute() and path.is_relative_to(ROOT) else path),
                sha256=digest(path.read_bytes()))


def load(path):
    return json.loads(path.read_bytes())


def git(*argv):
    return subprocess.check_output(['git', *argv], timeout=20)


def check_source(path, revisions, expected_sha):
    observed = [git('show', f'{rev}:{path}') for rev in revisions]
    assert all(data == observed[0] for data in observed)
    assert path.read_bytes() == observed[0] and digest(observed[0]) == expected_sha
    return reference(path)


def check_xml(path, expected_total, expected_sha):
    assert reference(path)['sha256'] == expected_sha
    root = ET.parse(path)
    assert not any(x.tag in ('failure', 'error', 'skipped') for x in root.iter())
    cases = {(row.get('classname'), row.get('name').split('(')[0]) for row in root.iter('testcase')}
    assert len(cases) == expected_total == sum(1 for _ in root.iter('testcase'))
    return cases


def check_body(path, method, expected):
    text = path.read_text()
    match = re.search(r'(?ms)^  void '+method+r'\(\) \{\n(.*?)^  \}', text)
    assert match is not None
    body = match.group(1)
    assert len(re.findall(r'assertEquals\("'+re.escape(expected)+r'", [^\n]+\.toString\(\)\);',body)) == 1
    return dict(method=method, assertLine=next(i for i, line in enumerate(text.splitlines(),1)
                                               if f'assertEquals("{expected}"' in line), bodySha256=digest(body.encode()))


def main():
    plan = next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('521_P01810*'))
    start = load(plan)['values']
    assert git('rev-parse','HEAD').decode().strip() == start['source']
    orig = {Path(row['path']).parent.name.split('-')[0]: Path(row['path']) for row in start['oracleReferences']}
    assert all(reference(Path(row['path'])) == row for row in start['oracleReferences'])
    catalog = orig['PG37452'].with_name('planned93-independent-cases.json')
    catalog_rows = {x['plannedCaseId']:x for x in load(catalog)}
    build, value, actual, post, independent = map(lambda n: load(orig[n]),
        ('PG39862','PG28166','PG14892','PG14895','PG14896'))
    assert value['actualExit'] == actual['actualExit'] == post['actualExit'] == independent['actualExit'] == build['actualExit'] == 0
    assert build['sourceCore'] == start['productionCoreMain']
    assert actual['source'] == post['source'] == independent['source']
    assert actual['execSha256'] == post['execSha256'] and independent['postSha256'] == reference(orig['PG14895'])['sha256']
    assert len(actual['cases']) == len(post['cases']) == 4 and actual['cases'] == post['cases']
    assert all(item['actualExit'] == 0 for item in actual['stages'])
    assert post['failures'] == post['errors'] == post['skipped'] == 0
    assert value['tests'] == 16 and not value['oldExecCombined'] and not value['manualCoverageExclusions']
    value_xml = orig['PG28166'].with_name('original-TEST-junit-jupiter.xml')
    value_cases = check_xml(value_xml,16,value['files'][value_xml.name])
    assert (PKG.replace('/','.').rstrip('.')+'.'+VALUES, VALUE_METHOD) in value_cases
    value_exec = orig['PG28166'].with_name('jacoco.exec')
    assert reference(value_exec)['sha256'] == value['files'][value_exec.name]
    [profile_xml_name] = actual['xmlHashes']
    profile_xml = orig['PG14895'].with_name(profile_xml_name)
    profile_cases = check_xml(profile_xml,4,actual['xmlHashes'][profile_xml_name])
    assert (PKG.replace('/','.').rstrip('.')+'.'+PROFILE, PROFILE_METHOD) in profile_cases
    assert profile_cases == {(case['classname'],case['name']) for case in actual['cases'] if case['result']=='PASS'}

    work = Path(build['cwd'])
    assert work.parent == ROOT.parent/'pgpt-runs/PG379' and work.resolve() == work
    byte_root = work / 'src/schubert-nk-batch/target/classes'
    verified = {}
    for package, names in VALUE_DEPENDENCIES.items():
        for name in names:
            file = MAIN/package/(name+'.java')
            old_class = PREFIX+package+'/'+name+'.class'
            assert value['physicalClassHashes'][old_class] == build['physicalClassHashes']['batch'][old_class]
            assert reference(byte_root/old_class)['sha256'] == value['physicalClassHashes'][old_class]
            verified[str(file)] = check_source(file,[value['productionCoreMain'],build['sourceCore']],value['inputHashes'][str(file)])
    for name in (VALUES,'BackupManifestFixture'):
        file = TESTS/(name+'.java')
        verified[str(file)] = check_source(file,[value['source'],start['source']],value['inputHashes'][str(file)])
    codec_path, = (k for k in value['inputHashes'] if k.endswith('/BackupManifestCodec.java'))
    assert digest(git('show',f'{build["sourceCore"]}:{codec_path}')) != value['inputHashes'][codec_path]
    assert all('BackupManifestCodec' not in Path(path).read_text() for path in verified)
    for name in ('BackupProfile','BackupVersions'):
        file = MAIN/'backup'/(name+'.java')
        historic = actual['begin']['sourceHashes'][str(file)]
        verified[str(file)] = check_source(file,[actual['source'],build['sourceCore']],historic)
    file = TESTS/(PROFILE+'.java')
    verified[str(file)] = check_source(file,[actual['begin']['fixtureSource'],start['source']],
                                      actual['begin']['testSourceHashes'][str(file.absolute())])
    profile_class = PKG+'BackupProfile.class'
    historic = post['sourcePhysicalInventory'][profile_class[:-6]]['sha256']
    assert reference(byte_root/profile_class)['sha256'] == historic == build['physicalClassHashes']['batch'][profile_class]

    jdk = ROOT.parent / 'toolchain/jdk-25.0.4/bin'
    assert reference(jdk/'java')['sha256'] == build['tools']['javaSha256']
    design, = git('-c','core.quotePath=false','ls-files','documents/300_SS/350_運用・品質/351_*').decode().splitlines()
    canonical = git('show','origin/main:'+design)
    assert b'SSC-454' in canonical and b'allowlist' in canonical
    rows = []
    for num,name,marker in TARGETS:
        identifier=f'PT-P01810-CATALOG-{num:03d}'
        oracle=catalog_rows[identifier]
        original=f'{name}[{marker}]'
        target=MAIN/'backup'/(name+'.java')
        assert str(target)==oracle['source']
        assert 'REDACTED' in oracle['independentExpected'][0]
        profiled=name=='BackupProfile'
        test_src=TESTS/((PROFILE if profiled else VALUES)+'.java')
        method=check_body(test_src,PROFILE_METHOD if profiled else VALUE_METHOD,original)
        cmd=[str(jdk/'javap'),'-p','-c',str(byte_root/(PKG+name+'.class'))]
        binary=subprocess.run(cmd,capture_output=True,timeout=15,check=True)
        assert not binary.stderr
        match=re.search(rb'(?s)public java.lang.String toString\(\);\n    Code:\n(.*?)(?:\n\n|\n\}\n)',binary.stdout)
        assert match is not None
        steps=match.group(1).decode().splitlines()
        assert len(steps)==2 and steps[0].strip().endswith('// String '+original) and steps[1].strip().endswith('areturn')
        rows.append(dict(catalogId=identifier,testId='BPROFILE001' if profiled else 'PT-BAT-183',
             designBasis='SS351 section 3, prepared CATALOG independent fixed diagnostic, SS343 Backup metadata boundary',
             expected=original, originalTest=dict(source=reference(test_src),**method),
             originalXml=reference(profile_xml if profiled else value_xml),
             originalRunManifest=reference(orig['PG14892'] if profiled else orig['PG28166']),
             originalExecSha256=actual['execSha256'] if profiled else reference(value_exec)['sha256'],
             originSource=actual['source'] if profiled else value['source'], exactCurrentClass=reference(byte_root/(PKG+name+'.class')),
             javapCommand=cmd,javapExit=binary.returncode,javapSha256=digest(binary.stdout),physicalMethodCode=steps))
    out=E/start['run']
    out.mkdir()
    result=dict(actualExit=0,source=start['productionCoreMain'],head=start['source'],rows=rows,
             eligibleValueScopeOnly=True,exactSourceFiles=verified,requiredStaticInspectionExit=0,
             previousSuites={'PG28166':16,'PG14892':4},scopeOutsideThisJoin=[codec_path],
             priorOriginalExecMeasuredOnlyByOriginalRuns=True,separateExecutionsAndCounters=True,newProductTests=0,
             typedRealSinkOrBackupExecuted=False,whole451Accepted=False,wholeP01810Accepted=False,newAcceptance=0,
             terminalAtUTC=datetime.now(timezone.utc).isoformat(),verifier=reference(Path(__file__).resolve()))
    (out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(len(rows),len(verified),reference(out/'manifest.json')['sha256'])


if __name__=='__main__':
    main()
