"""Publish original finite enum PT and independent current-source ABI/static evidence."""
import hashlib
import json
import os
import platform
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5732_enum48_selected import SLOT as SELECTED
from pg5058_whole_case_projection import project_xml


def main():
    path=ROOT.parent/'pgpt-runs/PG379'/SELECTED/'manifest.safe.json';v=json.loads(path.read_bytes())
    sp=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5734-enum48-static-v1/manifest.json';s=json.loads(sp.read_bytes())
    if not(v['actualExit']==0 and v['selectedQualified']and v['targetFour100']and(v['tests'],v['suites'])==(12,7)and s['actualExit']==0 and s['source']==v['source']and s['target48StaticAndAbiQualified']):raise ValueError('original same-source selected and independent static first')
    source=path.parent/'source';cases=[]
    for name,row in sorted(v['xmlHashes'].items()):
        filename='TEST-'+name+'.xml';xml=source/('src/schubert-nk-'+row['module']+'/target/surefire-reports')/filename
        cases.extend(project_xml(row['module'],filename,xml.read_bytes(),row['sha256']))
    if len(cases)!=12 or len({r['testId']for r in cases})!=12:raise ValueError('all12 actual case identities')
    begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    if begin['source']!=v['source']or begin['archiveSha256']!=v['archiveSha256']:raise ValueError('original archive correspondence')
    value={k:val for k,val in v.items()if k not in('allPhysicalMainSha256','coverage')}
    value.update(branch='dev-foundation',run=SELECTED,commands=begin['commands'],hostOS=platform.platform(),jdk='25.0.4',maven='3.9.12',jacoco='0.8.15',spotbugsPlugin='4.10.4.0',actualMainClasses=1664,
      actualTestCases=cases,coverageXmlHashes={m:r['sha256']for m,r in v['coverage'].items()},
      privateManifestSha256=sha(path),independentStaticSha256=sha(sp),oracleRef='1185_F03残enum21内部命名・独立値catalog仕様.md',
      bugRefs=['BUG1478','BUG1479'],yktRefs=['YKT1237','YKT1240'],coverageExclusionsAdded=0,executionKind='NORMAL_EXECUTED_PT_NOT_ALTERNATIVE',
      fullCurrentSourceAcceptance=False,liveResourcesVerified=False,ptRefusalScope='PTALT001/002 unresolved, runtime operations held',
      testSourceHashes={p.relative_to(source).as_posix():sha(p)for p in source.glob('src/*/src/test/java/**/EnumValueCatalogCompatibilityTest.java')})
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5736-enum48-catalog12';os.umask(0o077);out.mkdir(parents=True)
    target=out/'manifest.json'
    with target.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':v['source'],'tests':12,'suites':7,'targetEnums':14,'targetFour100':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
