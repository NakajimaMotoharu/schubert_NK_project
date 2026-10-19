"""Publish original exception green and separately labelled purposeful red; no PT or serializer calls."""
import json
import os
import platform
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5058_whole_case_projection import project_xml


def main():
    w=ROOT.parent/'pgpt-runs/PG379';path=w/'pg5748-exception-green-v1/manifest.safe.json';v=json.loads(path.read_bytes());source=path.parent/'source'
    rp=w/'pg5748-exception-red-v1/manifest.safe.json';r=json.loads(rp.read_bytes())
    sp=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5750-exception-static-v1/manifest.json';s=json.loads(sp.read_bytes())
    if not(v['actualExit']==0 and v['selectedQualified']and v['targetFour100']and(v['tests'],v['suites'])==(17,13)and s['actualExit']==0 and s['source']==v['source']and s['targetFour100']and s['remainingTargetFindings']==0 and r['actualExit']==1 and r['purposefulRedEstablished']):raise ValueError('original green/static and separately qualified red first')
    cases=[]
    for name,row in sorted(v['xmlHashes'].items()):
        filename='TEST-'+name+'.xml';xml=source/('src/schubert-nk-'+row['module']+'/target/surefire-reports')/filename
        cases.extend(project_xml(row['module'],filename,xml.read_bytes(),row['sha256']))
    if len(cases)!=17 or len({row['testId']for row in cases})!=17:raise ValueError('all17 actual green case identities')
    begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    if begin['source']!=v['source']or begin['archiveSha256']!=v['archiveSha256']:raise ValueError('same original source/archive/commands')
    value={k:val for k,val in v.items()if k not in('coverage','allPhysicalMainSha256')}
    red={k:r[k]for k in('source','actualExit','startedUTC','completedUTC','archiveSha256','tests','suites','failedOrSkipped','purposefulRedEstablished')}
    red.update(executionKind='EXPECTED_RED_NOT_PASS',manifestSha256=sha(rp),xmlHashes=r['xmlHashes'],passedAddedToGreen=0)
    value.update(branch='dev-foundation',run='pg5748-exception-green-v1',hostOS=platform.platform(),jdk='25.0.4',maven='3.9.12',jacoco='0.8.15',spotbugsPlugin='4.10.4.0',commands=begin['commands'],actualMainClasses=1664,actualTestCases=cases,
      coverageXmlHashes={m:c['sha256']for m,c in v['coverage'].items()},privateManifestSha256=sha(path),independentStaticManifestSha256=sha(sp),purposefulRed=red,
      oracleRef='1191_例外16内部命名・null不変条件仕様.md',decision='PG-D439',bugRefs=['BUG1482','BUG1483'],yktRefs=['YKT1237','YKT1243'],coverageExclusionsAdded=0,
      inheritedJavaSerializedSchemaCompatibilityClaimed=False,supportedSessionWireSchemaChanged=False,genericSerializableRenamerGuardChanged=False,
      executionKind='NORMAL_EXECUTED_PT_NOT_ALTERNATIVE',fullCurrentSourceAcceptance=False,liveResourcesVerified=False,refusalScope='PTALT001/002 unresolved, dependent runtime operations held')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5752-exception17';os.umask(0o077);out.mkdir(parents=True)
    target=out/'manifest.json'
    with target.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    totals={k:{part:sum(c[k][part]for c in v['targetCounters'].values())for part in('covered','missed')}for k in('LINE','METHOD','CLASS','BRANCH')}
    print(json.dumps({'actualExit':0,'source':v['source'],'tests':17,'suites':13,'targetExceptionClasses':16,'aggregateTargetCounters':totals,'sha256':sha(target),'formalAccepted':False}))


if __name__=='__main__':main()
