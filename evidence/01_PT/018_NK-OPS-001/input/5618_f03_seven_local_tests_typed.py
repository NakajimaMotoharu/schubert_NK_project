"""Type-check exactly the six recently added or changed Web test sources."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
BIN, OPS, WEB = (H[k] for k in ('BIN','OPS','WEB'))
pin, read, sha, check = (H[k] for k in ('pin','read','sha','check'))
DOMAIN = 'dev/codex/schubert/nk/web'
RUN = 'PG41198-f03-seven-local-tests-typed-v1'
MAIN_OWNER = {
    'view/AnimationListViewModel': ('Video','Row'),
    'view/MusicCategoryViewModel': ('Card',),
    'view/MusicSectionViewModel': ('Card',),
    'view/MusicTrackViewModel': (),
    'media/HttpByteRangeParser': ('Full','Partial','Selection','Unsatisfiable'),
    'media/MediaRangeService': ('ReadOperation','FileSource','Response'),
    'media/MediaBodyStreamer': (),
    'media/MediaDeliveryException': ('Reason',),
    'media/ContentDispositionFactory': (),
}
TEST_OWNER = {
    'view/AnimationListCountBoundaryTest': (),
    'view/MusicCategoryCountBoundaryTest': (),
    'view/MusicSectionCountBoundaryTest': (),
    'view/MusicTrackCountBoundaryTest': (),
    'media/HttpByteRangeLongBoundaryTest': (),
    'media/MediaRangePortTest': ('Probe','Reply','Reply$1','MemoryChannel','Vector','1','1$1'),
}
CLOSED_NAMES = {'TemporaryInfrastructureException', 'FingerprintKeyRing',
                'ResponseSnapshotCodec', 'WebStartupException'}


def physical_names(owners):
    return {f'{DOMAIN}/{name}{suffix}.class' for name,children in owners.items()
            for suffix in ('',*(f'${nested}' for nested in children))}


def main():
    ref, = Path('documents/400_PGPT/470_PMO').glob('601_*/1628_*.json')
    context = read(ref)['values']
    assert all(pin(Path(row['path']))==row for row in context['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free >= 64*1024**2 and shutil.disk_usage('.').free >= 64*1024**2
    test_runs = [Path(row['path']) for row in context['oracleReferences'][1:7]]
    sdk_path = Path(context['oracleReferences'][-1]['path'])
    existing_static = Path(context['oracleReferences'][-2]['path'])
    tools = read(sdk_path)['dependencies']
    pinned = {'current-protocol176.jar','jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar',
              'qualified-web-safe18.jar','spring-core-7.0.9.jar','spring-web-7.0.9.jar'}
    aux = [Path(name) for name in tools if Path(name).name in pinned]
    assert {p.name for p in aux}==pinned and all(pin(p)['sha256']==tools[str(p)] for p in aux)
    inventory = {}
    for p in aux:
        with ZipFile(p) as jar:
            inventory[p.name] = [name for name in jar.namelist() if name.endswith('.class')]
            assert all(Path(name).stem.split('$',1)[0] not in CLOSED_NAMES for name in inventory[p.name])
    assert len(inventory['qualified-web-safe18.jar']) == 18
    tested_files = {}
    for receipt in test_runs:
        result = read(receipt)
        assert result['actualExit']==0 and result['productionCore']==context['productionCoreMain']
        actual = result['testSource']
        assert pin(Path(actual['path'])) == actual
        tested_files[actual['path']] = actual['sha256']
    main_sources = [WEB/'main/java'/DOMAIN/(name+'.java') for name in MAIN_OWNER]
    test_sources = [WEB/'test/java'/DOMAIN/(name+'.java') for name in TEST_OWNER]
    assert set(tested_files)==set(map(str,test_sources))
    for path in main_sources:
        body = subprocess.check_output(['git','show',f'{context["productionCoreMain"]}:{path}'],timeout=15)
        assert body==path.read_bytes()
    for path in test_sources:
        body = subprocess.check_output(['git','show',f'{context["source"]}:{path}'],timeout=15)
        assert sha(body)==tested_files[str(path)]
    out = OPS/RUN
    out.mkdir()
    report = out/'spotbugs.xml'
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-f03-new-tests-') as tmp:
        root = Path(tmp)
        target, peers = root/'test',root/'main'
        target.mkdir()
        peers.mkdir()
        cp = os.pathsep.join(map(str,aux))
        compiler = [BIN/'javac','--release','25','-g','-Xlint:all','-Werror','-proc:none']
        main_stage, made = check([*compiler,'-cp',cp,'-d',peers,*main_sources])
        assert made.returncode==0,made.stderr
        test_stage, made = check([*compiler,'-cp',str(peers)+os.pathsep+cp,'-d',target,*test_sources])
        assert made.returncode==0,made.stderr
        actual_main = {str(p.relative_to(peers)):p for p in peers.rglob('*.class')}
        actual_test = {str(p.relative_to(target)):p for p in target.rglob('*.class')}
        assert set(actual_main)==physical_names(MAIN_OWNER), set(actual_main)^physical_names(MAIN_OWNER)
        assert set(actual_test)==physical_names(TEST_OWNER), set(actual_test)^physical_names(TEST_OWNER)
        compiled_main = {name:sha(path.read_bytes()) for name,path in actual_main.items()}
        compiled_test = {name:sha(path.read_bytes()) for name,path in actual_test.items()}
        cmd = read(existing_static)['stagedStatic']['spotbugs']['command'][:13]
        assert cmd[4]=='edu.umd.cs.findbugs.FindBugs2'
        assert cmd[9]=='-auxclasspath' and cmd[11]=='-output'
        cmd[10]=str(peers)+os.pathsep+cp
        cmd[12]=str(report)
        static_stage, outcome = check([*cmd,*[actual_test[k] for k in sorted(actual_test)]])
        assert outcome.returncode in (0,1),outcome.stderr
    xml = ET.parse(report).getroot()
    findings = [dict(type=f.get('type'),rank=f.get('rank'),className=f.find('Class').get('classname'))
                for f in xml.findall('BugInstance')]
    processing_errors = len(xml.findall('.//Error'))
    missing = len(xml.findall('.//MissingClass'))
    valid = not findings and processing_errors==missing==0 and outcome.returncode==0
    data = dict(actualExit=0 if valid else 1,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                toolExit=outcome.returncode,source=context['source'],productionCore=context['productionCoreMain'],
                findings=findings,errors=processing_errors,missing=missing,scopedMainPhysical=compiled_main,
                admittedTestPhysical=compiled_test,sourceInputs=list(map(pin,main_sources+test_sources)),
                toolInputDescription={key:dict(count=len(names),inventorySha256=sha('\n'.join(sorted(names)).encode()))
                                      for key,names in inventory.items()},
                admittedDependencies=list(map(pin,aux)),staticReference=pin(existing_static),
                plansCheckedBeforeAnalyzer=True,stages=[main_stage,test_stage,static_stage],
                report=pin(report),fullyQualifiedWholeF03=False,rootNullAwayExecuted=False,
                whole451=False,heldClassReads=0,productTestsReplayed=0,formalDelta=0)
    manifest = out/'manifest.json'
    with manifest.open('x') as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(pin(manifest),len(compiled_main),len(compiled_test),findings,processing_errors,missing)
    return data['actualExit']


if __name__=='__main__':
    raise SystemExit(main())
