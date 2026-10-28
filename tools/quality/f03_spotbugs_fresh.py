"""Current-source six-artifact static analysis; reuse tool runtime bytes only, never an old Product result."""
import copy
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import out
from classfile_code_metadata import decode
import pg9666_pagination_static as runner

RUNTIME = ('PG13218-spotbugs-fresh-aux-plan-recovery-v1','a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564')

def stage(cfg,source,normal_pin,preflight):
    invocation = capture(__file__);target = out(cfg,cfg.STATIC_NUMBER);slot = data.ROOT.parent/'pgpt-runs/PG379'/target.name.lower()
    assert not target.exists() and not slot.exists()
    runtime = data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1])
    n = data.read_checked(out(cfg,cfg.NORMAL_NUMBER)/'manifest.json',normal_pin)
    p = data.read_checked(data.BASE/preflight[0]/'manifest.json',preflight[1])
    assert n['source'] == source and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(n['begin']['inputHashes'][path] == sha for path,sha in p['candidateSourceHashes'].items())
    tool_hashes = runtime['toolRuntimeHashes'];aux = {path:sha for path,sha in runtime['auxiliaryClasspathHashes'].items() if path not in runtime['currentJarHashes']}
    assert not any('/pgpt-runs/' in path or '/dev/codex/schubert/schubert-nk-' in path for path in aux)
    jars = {role:item['path'] for role,item in n['jars'].items()};jar_hashes = {item['path']:item['sha256'] for item in n['jars'].values()}
    aux.update(jar_hashes);hashes = {**tool_hashes,**aux}
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    expected = {}
    for role,jar in jars.items():
        with zipfile.ZipFile(jar) as archive:expected[role] = sorted(x for x in archive.namelist() if x.endswith('.class'))
    assert len(jars) == 6 and sum(map(len,expected.values())) == 1843
    slot.mkdir();runner.SLOT = slot;auxfile = slot/'fresh-aux-classpath.txt'
    with auxfile.open('x') as stream:stream.write(''.join(path+'\n' for path in sorted(aux)))
    configuration = dict(version='4.10.4',effort='max',threshold='low',excludes=[],onlyAnalyze=None,productTestsExecuted=0)
    begin = dict(source=source,invocation=invocation,allInputHashes=hashes,sourceInputHashes=n['begin']['inputHashes'],normalManifestSha256=normal_pin,
        runtimeComponentReference=dict(path=RUNTIME[0],sha256=RUNTIME[1],reuse='TOOL_RUNTIME_BYTES_ONLY_NOT_OLD_PRODUCT_ANALYSIS'),currentJarsByRole=jars,
        expectedClasses=expected,expectedMainClasses=1843,auxiliaryClasspathHashes=aux,configuration=configuration,productTestsExecuted=0,externalActions=0)
    data.write(slot/'begin.safe.json',begin);stages = [];reports = {};passed = True
    for role,jar in jars.items():
        report = slot/(role+'.xml')
        command = [str(runner.TC/'jdk-25.0.4/bin/java'),'-Xmx2g','-cp',os.pathsep.join(runtime['toolClasspath']),'edu.umd.cs.findbugs.FindBugs2',
            '-effort:max','-low','-xml:withMessages','-exitcode','-auxclasspathFromFile',str(auxfile),'-output',str(report),jar]
        result = runner.step(role+'-spotbugs',command,slot,timeout=300);stages.append(result)
        root = ET.fromstring(report.read_bytes()) if report.is_file() else None
        if root is None:reports[role] = dict(reportPresent=False,actualExit=result['actualExit']);passed = False;continue
        bugs = len(list(root.iter('BugInstance')));missing = [x.text for x in root.iter('MissingClass')];errors = len(list(root.iter('Error')))
        summary = root.find('FindBugsSummary');stats = [x.get('class') for x in root.iter('ClassStats')]
        names = {entry[:-6].replace('/','.') for entry in expected[role]};actual = set(stats)
        exact = actual == names and len(stats) == len(actual) and summary is not None and int(summary.get('total_classes')) == len(names)
        ok = result['actualExit'] == 0 and not result['timedOut'] and bugs == errors == 0 and not missing and exact
        reports[role] = dict(reportPresent=True,sha256=data.sha(report.read_bytes()),actualExit=result['actualExit'],bugs=bugs,missingClasses=missing,analysisErrors=errors,
            expectedClasses=len(names),observedClassStats=len(stats),exactPhysicalClassSet=exact,absentClassStats=sorted(names-actual),extraClassStats=sorted(actual-names),passed=ok)
        passed &= ok
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);target.mkdir()
    for role,row in reports.items():
        if row['reportPresent']:
            with (target/(role+'.xml')).open('xb') as stream:stream.write((slot/(role+'.xml')).read_bytes())
    data.write(target/'manifest.json',dict(actualExit=0 if passed else 1,source=source,invocation=invocation,beginSha256=data.sha((slot/'begin.safe.json').read_bytes()),stages=stages,reports=reports,
        normalManifestSha256=normal_pin,preflightManifestSha256=preflight[1],sourceHashes=p['candidateSourceHashes'],rawStatic=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],
        spotbugsSixExit=0 if passed else 1,spotbugsSixReports={role:row.get('sha256') for role,row in reports.items()},expectedMainClasses=1843,configuration=configuration,
        suppressionsAdded=False,oldAnalysisSuccessTransferred=False,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(json.dumps(dict(actualExit=0 if passed else 1,manifestSha256=data.sha((target/'manifest.json').read_bytes()),reports=reports)),flush=True)
    raise SystemExit(0 if passed else 1)

def strict(value,reference):
    assert json.dumps(value,sort_keys=True) == json.dumps(reference,sort_keys=True)

def independent(cfg,source,normal_pin,static_pin,number):
    invocation = capture(__file__);target = out(cfg,number);assert not target.exists()
    n = data.read_checked(out(cfg,cfg.NORMAL_NUMBER)/'manifest.json',normal_pin)
    result = data.read_checked(out(cfg,cfg.STATIC_NUMBER)/'manifest.json',static_pin)
    assert n['source'] == result['source'] == source and n['actualExit'] == result['actualExit'] == result['spotbugsSixExit'] == n['testsExecuted'] == 0
    assert result['configuration'] == dict(version='4.10.4',effort='max',threshold='low',excludes=[],onlyAnalyze=None,productTestsExecuted=0)
    slot = data.ROOT.parent/'pgpt-runs/PG379'/out(cfg,cfg.STATIC_NUMBER).name.lower()
    begin = data.read_checked(slot/'begin.safe.json',result['beginSha256'])
    assert begin['source'] == source and begin['normalManifestSha256'] == normal_pin
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in begin['allInputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in begin['sourceInputHashes'].items())
    assert len(result['stages']) == 6 and all(row['actualExit'] == 0 and not row['timedOut'] for row in result['stages'])
    rows = {};full = 0
    for role,item in n['jars'].items():
        jar = Path(item['path']);assert data.sha(jar.read_bytes()) == item['sha256']
        raw = (out(cfg,cfg.STATIC_NUMBER)/(role+'.xml')).read_bytes();assert data.sha(raw) == result['reports'][role]['sha256']
        root = ET.fromstring(raw);project = root.find('Project');assert root.get('version') == '4.10.4'
        assert [x.text for x in project.findall('Jar')] == [str(jar)]
        aux = [x.text for x in project.findall('AuxClasspathEntry')]
        assert len(aux) == len(set(aux)) and set(aux) == set(begin['auxiliaryClasspathHashes'])
        assert not [x for x in root.iter() if x.tag in ['BugInstance','MissingClass','Error']]
        expected = set()
        with zipfile.ZipFile(jar) as archive:
            for entry in archive.namelist():
                if entry.endswith('.class'):decode(archive.read(entry),entry);expected.add(entry[:-6].replace('/','.'))
        stats = [x.get('class') for x in root.iter('ClassStats')]
        assert len(stats) == len(set(stats)) and set(stats) == expected and int(root.find('FindBugsSummary').get('total_classes')) == len(expected)
        rows[role] = dict(physicalClasses=len(expected),reportedClasses=len(stats),reportSha256=data.sha(raw),exactClassSet=True);full += len(expected)
    assert full == 1843
    reference = dict(source=source,fullPhysicalMain=full,rows=rows,missingClasses=0,analysisErrors=0,bugs=0,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,oldAnalysisSuccessTransferred=False)
    strict(reference,reference);labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('physical',lambda x:x.update(fullPhysicalMain=1643)),('missing',lambda x:x.update(missingClasses=1)),
        ('error',lambda x:x.update(analysisErrors=1)),('bool-counter',lambda x:x.update(productTestsExecuted=False)),('PT',lambda x:x.update(productTestsExecuted=1843)),
        ('accepted',lambda x:x.update(newAccepted=1)),('old-domain',lambda x:x.update(oldAnalysisSuccessTransferred=True))]:
        bad = copy.deepcopy(reference);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(reference,sort_keys=True)
        try:strict(bad,reference)
        except AssertionError:labels.append(label)
        else:raise AssertionError('incorrect static source domain accepted')
    verify(invocation);target.mkdir();data.write(target/'verification.json',reference)
    data.write(target/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,staticManifestSha256=static_pin,verificationSha256=data.sha((target/'verification.json').read_bytes()),
        fullPhysicalMain=1843,currentMissingClasses=0,currentAnalysisErrors=0,currentBugs=0,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        productTestsExecuted=0,analysisReexecuted=False,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((target/'manifest.json').read_bytes()))
