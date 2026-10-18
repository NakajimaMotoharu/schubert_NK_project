"""Allowlisted failed-source metadata and locked SpotBugs detector evidence, no acceptance."""
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg5240_startup_view_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5240-startup-view-owner-green-v1'


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['sourceSnapshot']!='673888c95a6a3de6b0c7884e9a80e25242f131bf' or result['actualExit']!=1 or result['phaseExits']!=[0,1]:
        raise ValueError('immutable original failed source673 only')
    if result['tests']!=829 or result['suites']!=98:raise ValueError('original829 complete inventory')
    findings=[]
    for module in selected.BUILT:
        report=RUN/('source/src/schubert-nk-'+module+'/target/spotbugsXml.xml')
        bugs=ET.parse(report).getroot().findall('.//BugInstance')
        for bug in bugs:
            findings.append({'module':module,'type':bug.get('type'),'priority':bug.get('priority'),
                'class':[c.get('classname') for c in bug.findall('Class')],
                'method':[c.get('name') for c in bug.findall('Method')]})
    if len(findings)!=1 or findings[0]['type']!='THROWS_METHOD_THROWS_RUNTIMEEXCEPTION':
        raise ValueError('exact known unqualified style finding')
    jar=selected.TC/'m2/repository/com/github/spotbugs/spotbugs/4.10.4/spotbugs-4.10.4.jar'
    raw=subprocess.check_output([str(selected.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(jar),
        'edu.umd.cs.findbugs.detect.ThrowingExceptions'])
    if b'Ljava/lang/RuntimeException;' not in raw or b'THROWS_METHOD_THROWS_RUNTIMEEXCEPTION' not in raw:
        raise ValueError('actual locked detector evidence')
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    targets=[c for c in report.findall('package/class') if c.get('name').endswith('/StartupAdmissionFile$ViewOwner')]
    if len(targets)!=1:raise ValueError('one actual failed-source Owner')
    four={v.get('type'):{'covered':int(v.get('covered')),'missed':int(v.get('missed'))}
        for v in targets[0].findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    value={'source':result['sourceSnapshot'],'originalRunnerActualExit':1,'phaseExits':[0,1],'tests':829,'suites':98,
        'originalManifestSha256':selected.sha(RUN/'manifest.safe.json'),'logSha256':result['logSha256'],
        'xmlSha256':result['xmlSha256'],'originalOwnerFourCounters':four,'findings':findings,
        'lockedDetectorJarSha256':selected.sha(jar),'lockedDetectorJavapSha256':hashlib.sha256(raw).hexdigest(),
        'detectorCondition':'ATHROW stack signature exactly java/lang/RuntimeException; no origin-identity exemption',
        'correctionPlan':'preserve Runtime/Error union primary in native catch while bounded phases drain remainder; primitive secondary bitmap; same oracle; no synthetic/sneaky/suppression trick',
        'sourceQualified':False,'formalAccepted':False,'acceptedLeafDelta':0,'wholeHorizontalComplete':False,
        'bugs':['BUG1432','BUG1414'],'ykt':['YKT1196','YKT1178'],'ssc':['SSC308'],'testReplays':0,'vmActions':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5247-view-runtime-diagnostic-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'originalExit':1,'tests':829,'staticIssues':1,'sourceQualified':False,
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
