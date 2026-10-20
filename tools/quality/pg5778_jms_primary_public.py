"""Original normal14 and separately labelled API/Web purpose-red; no PT/runtime action."""
import hashlib
import json
import os
import platform
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5058_whole_case_projection import project_xml


def main():
    w=ROOT.parent/'pgpt-runs/PG379';path=w/'pg5774-jms-primary-green-v1/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source'
    ap=w/'pg5774-red-api-assessment-v1/manifest.safe.json';api=json.loads(ap.read_bytes());wp=w/'pg5774-jms-primary-red-web-v2/manifest.safe.json';web=json.loads(wp.read_bytes())
    sp=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5776-jms-primary-static-v1/manifest.json';static=json.loads(sp.read_bytes())
    if not(v['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(14,7)and static['actualExit']==0 and static['source']==v['source']and api['assessmentExit']==0 and api['purposefulApiRedEstablished']and not api['wholeRedEstablished']and web['actualExit']==1 and web['purposefulRedEstablished']and(web['tests'],web['suites'])==(10,7)):raise ValueError('actual green/independent static and separately qualified API/Web red first')
    cases=[]
    for name,row in sorted(v['xmlHashes'].items()):
        filename='TEST-'+name+'.xml';xml=snapshot/('src/schubert-nk-'+row['module']+'/target/surefire-reports')/filename
        cases.extend(project_xml(row['module'],filename,xml.read_bytes(),row['sha256']))
    if len(cases)!=14 or len({r['testId']for r in cases})!=14:raise ValueError('all14 original green cases')
    trace=[]
    for case in cases:
        if case['class'].endswith('.InboundTransactionsPrimaryContractTest'):
            name='src/schubert-nk-api/src/test/java/'+case['class'].replace('.','/')+'.java'
        elif case['class'].endswith('.ReplyIsolationPrimaryContractTest'):
            name='src/schubert-nk-web/src/test/java/'+case['class'].replace('.','/')+'.java'
        else:continue
        import re
        methods=re.findall(r'void (jmsP\d{3}[A-Za-z0-9_]+)\(', (snapshot/name).read_text())
        matches=[m for m in methods if hashlib.sha256((m+'()').encode()).hexdigest()==case['caseNameSha256']or hashlib.sha256(m.encode()).hexdigest()==case['caseNameSha256']]
        if len(matches)!=1:raise ValueError('one source-declared method per actual case')
        method=matches[0];trace.append({'designTestId':'PT-JMS-PRE'+method[4:7],'method':method,'actualTestId':case['testId'],'xmlSha256':case['xmlSha256']})
        if sha(snapshot/name)!=sha(w/'pg5774-jms-primary-red-v1/source'/name)or sha(snapshot/name)!=sha(w/'pg5774-jms-primary-red-web-v2/source'/name):raise ValueError('new seven test bodies unchanged across distinct red and green sources')
    if len(trace)!=7 or len({r['designTestId']for r in trace})!=7:raise ValueError('seven independent design traces')
    begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    if begin['source']!=v['source']or begin['archiveSha256']!=v['archiveSha256']:raise ValueError('same original source/archive/command')
    value={k:r for k,r in v.items()if k not in('coverage','allPhysicalMainSha256')}
    red_api={k:api[k]for k in('originalActualExit','originalSource','productionMainSource','originalManifestSha256','purposefulApiRedEstablished','wholeRedEstablished','webTestsNotRun','actualCompiledMainClasses','unbuiltMainClasses','all849MainSourceUnchanged')}
    red_api.update(assessmentSha256=sha(ap),redPurposeTests=2,passedAddedToGreen=0)
    red_web={k:web[k]for k in('source','actualExit','startedUTC','completedUTC','archiveSha256','tests','suites','failedOrSkipped','purposefulRedEstablished')};red_web.update(manifestSha256=sha(wp),redPurposeTests=1,passedAddedToGreen=0)
    value.update(branch='dev-foundation',run='pg5774-jms-primary-green-v1',hostOS=platform.platform(),jdk='25.0.4',maven='3.9.12',jacoco='0.8.15',spotbugsPlugin='4.10.4.0',commands=begin['commands'],actualMainClasses=1664,actualTestCases=cases,newDesignTestIdTrace=trace,coverageXmlHashes={m:c['sha256']for m,c in v['coverage'].items()},privateManifestSha256=sha(path),independentStaticManifestSha256=sha(sp),purposefulApiRed=red_api,purposefulWebRed=red_web,oracleRef='1200_JMS原例外自己抑制_単体テスト仕様書.md',bugRefs=['BUG1485','BUG1486'],yktRefs=['YKT1245','YKT1246'],newGuardsActualCoverage=static['newGuardsActualCoverage'],coverageExclusionsAdded=0,executionKind='NORMAL_EXECUTED_PT_NOT_ALTERNATIVE',fullCurrentSourceAcceptance=False,liveResourcesVerified=False,refusalScope='PTALT001/002 unresolved; dependent operations held')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5778-jms-primary14';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':v['source'],'tests':14,'suites':7,'newTestIds':sorted(r['designTestId']for r in trace),'sha256':sha(out/'manifest.json'),'formalAccepted':False,'targetFour100':v['targetFour100']}))


if __name__=='__main__':main()
