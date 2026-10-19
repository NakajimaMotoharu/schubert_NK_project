"""Allowlisted original revocation PT publication; no test/native/runtime execution."""
import json
import os
import platform
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5742_revocation_selected import SLOT as SELECTED
from pg5058_whole_case_projection import project_xml


def main():
    path=ROOT.parent/'pgpt-runs/PG379'/SELECTED/'manifest.safe.json';v=json.loads(path.read_bytes());source=path.parent/'source'
    sp=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5744-revocation-static-v1/manifest.json';s=json.loads(sp.read_bytes())
    if not(v['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(15,7)and s['actualExit']==0 and s['source']==v['source']and s['targetFour100']and s['remainingTargetFindings']==0):raise ValueError('original same-source actual PT/static first')
    begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    if begin['source']!=v['source']or begin['archiveSha256']!=v['archiveSha256']:raise ValueError('original source/archive binding')
    cases=[]
    for name,row in sorted(v['xmlHashes'].items()):
        filename='TEST-'+name+'.xml';xml=source/('src/schubert-nk-'+row['module']+'/target/surefire-reports')/filename
        cases.extend(project_xml(row['module'],filename,xml.read_bytes(),row['sha256']))
    if len(cases)!=15 or len({r['testId']for r in cases})!=15:raise ValueError('all15 original case identities')
    value={k:val for k,val in v.items()if k not in('coverage','allPhysicalMainSha256','targetCounters','targetFour100')}
    value.update(branch='dev-foundation',run=SELECTED,hostOS=platform.platform(),jdk='25.0.4',maven='3.9.12',jacoco='0.8.15',spotbugsPlugin='4.10.4.0',commands=begin['commands'],actualMainClasses=1664,actualTestCases=cases,
      coverageXmlHashes={m:r['sha256']for m,r in v['coverage'].items()},codecCounters=s['targetCounters'],codecFour100=True,
      privateManifestSha256=sha(path),staticManifestSha256=sha(sp),oracleRef='1189_Revocation版選択冗長条件_PG・PT仕様.md',bugRefs=['BUG1481'],yktRefs=['YKT1242'],coverageExclusionsAdded=0,
      executionKind='NORMAL_EXECUTED_PT_NOT_ALTERNATIVE',fullCurrentSourceAcceptance=False,liveResourcesVerified=False,refusalScope='PTALT001/002 unresolved; dependent runtime operations held')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5746-revocation15';os.umask(0o077);out.mkdir(parents=True)
    target=out/'manifest.json'
    with target.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':v['source'],'tests':15,'suites':7,'codecFour100':True,'sha256':sha(target),'formalAccepted':False}))


if __name__=='__main__':main()
