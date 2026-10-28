"""Same SpotBugs4.10.4/Max/Low, six complete current Main artifacts with only fresh sibling aux JARs."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = '6d7f55c22a3ffec8a9013e706282ac845c595492'
OUT = data.BASE/'PG13216-spotbugs-fresh-six-cli-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13216-spotbugs-fresh-six-cli-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    plan = data.read_checked(data.BASE/'PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json','a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564')
    n = data.read_checked(data.BASE/'PG13208-resource-db-literal-v1/manifest.json','01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4')
    p = data.read_checked(data.BASE/'PG13207-resource-db-literal-preflight-recovery-v1/manifest.json','abcff1ed823336314e9f56f1f66cde531a44c6e954d14830738fd511733d4b22')
    assert plan['source'] == n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert not plan['analysisExecuted'] and plan['originalHelpActualExit'] == 1
    hashes = {**plan['toolRuntimeHashes'],**plan['auxiliaryClasspathHashes'],**plan['currentJarHashes']}
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert all(n['begin']['inputHashes'][path] == sha for path,sha in p['candidateSourceHashes'].items())
    SLOT.mkdir();runner.SLOT = SLOT;aux = SLOT/'fresh-aux-classpath.txt'
    with aux.open('x') as stream:stream.write(''.join(path+'\n' for path in plan['auxiliaryClasspathHashes']))
    begin = dict(source=SOURCE,invocation=invocation,allInputHashes=hashes,sourceInputHashes=n['begin']['inputHashes'],
        planManifestSha256='a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564',normalManifestSha256='01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4',
        expectedClasses=plan['expectedClasses'],configuration=plan['configuration'],expectedMainClasses=1843,productTestsExecuted=0,externalActions=0)
    data.write(SLOT/'begin.safe.json',begin);stages = [];reports = {};passed = True
    for role,jar in plan['currentJarsByRole'].items():
        report = SLOT/(role+'.xml')
        command = [str(runner.TC/'jdk-25.0.4/bin/java'),'-Xmx2g','-cp',os.pathsep.join(plan['toolClasspath']),
            'edu.umd.cs.findbugs.FindBugs2','-effort:max','-low','-xml:withMessages','-exitcode','-auxclasspathFromFile',str(aux),'-output',str(report),jar]
        stage = runner.step(role+'-spotbugs',command,SLOT,timeout=300);stages.append(stage)
        root = ET.fromstring(report.read_bytes()) if report.is_file() else None
        if root is None:
            reports[role] = dict(reportPresent=False,actualExit=stage['actualExit']);passed = False;continue
        bugs = len(list(root.iter('BugInstance')));missing = [x.text for x in root.iter('MissingClass')];errors = len(list(root.iter('Error')))
        summary = root.find('FindBugsSummary');stats = [x.get('class') for x in root.iter('ClassStats')]
        expected = {entry[:-6].replace('/','.') for entry in plan['expectedClasses'][role]}
        actual = set(stats);exact = actual == expected and len(stats) == len(actual) and summary is not None and int(summary.get('total_classes')) == len(expected)
        ok = stage['actualExit'] == 0 and not stage['timedOut'] and bugs == errors == 0 and not missing and exact
        reports[role] = dict(reportPresent=True,sha256=data.sha(report.read_bytes()),actualExit=stage['actualExit'],bugs=bugs,missingClasses=missing,analysisErrors=errors,
            expectedClasses=len(expected),observedClassStats=len(stats),exactPhysicalClassSet=exact,absentClassStats=sorted(expected-actual),extraClassStats=sorted(actual-expected),passed=ok)
        passed &= ok
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir()
    for role,row in reports.items():
        if row['reportPresent']:
            with (OUT/(role+'.xml')).open('xb') as stream:stream.write((SLOT/(role+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,beginSha256=data.sha((SLOT/'begin.safe.json').read_bytes()),stages=stages,reports=reports,
        normalManifestSha256=begin['normalManifestSha256'],preflightManifestSha256='abcff1ed823336314e9f56f1f66cde531a44c6e954d14830738fd511733d4b22',sourceHashes=p['candidateSourceHashes'],
        rawStatic=98,rawStaticGateExit=1,spotbugsSixExit=0 if passed else 1,spotbugsSixReports={role:row.get('sha256') for role,row in reports.items()},
        expectedMainClasses=1843,oldUnresolvedClassOccurrences=18,configuration=plan['configuration'],suppressionsAdded=False,oldIncompleteReportsOverwritten=False,
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(json.dumps(dict(actualExit=0 if passed else 1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),reports=reports)),flush=True)
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':main()
