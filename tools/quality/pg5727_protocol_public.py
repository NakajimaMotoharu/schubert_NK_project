"""Allowlisted actual protocol88 XML/counter publication; never re-executes test bodies."""
import hashlib
import json
import os
import platform
from pg5724_semantic_enum_protocol import ROOT,SLOT as PROTOCOL
from pg5058_whole_case_projection import project_xml


def main():
    base=ROOT.parent/'pgpt-runs/PG379';path=base/PROTOCOL/'manifest.safe.json';raw=path.read_bytes();value=json.loads(raw)
    static_path=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5726-enum-static-v1/manifest.json';static=json.loads(static_path.read_bytes())
    if not(value['actualExit']==0 and value['protocolFour100Qualified']and static['actualExit']==0 and static['source']==value['source']and static['target18StaticAndAbiQualified']and(value['tests'],value['suites'])==(88,18)):raise ValueError('actual independent protocol PT/static first')
    source=path.parent/'source';cases=[]
    for name,digest in sorted(value['xmlHashes'].items()):
        filename='TEST-'+name+'.xml'
        xml=source/'src/schubert-nk-protocol/target/surefire-reports'/filename
        cases.extend(project_xml('protocol',filename,xml.read_bytes(),digest))
    if len(cases)!=88 or len({r['testId']for r in cases})!=88:raise ValueError('all original88 case identities, no synthetic pass')
    begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    if begin['source']!=value['source']or begin['archiveSha256']!=value['archiveSha256']:raise ValueError('original source/archive/command correspondence')
    projected={k:v for k,v in value.items()if k!='allPhysicalProtocolMainSha256'}
    projected.update(run=PROTOCOL,branch='dev-foundation',executionKind='NORMAL_EXECUTED_PT_NOT_ALTERNATIVE',
      hostOS=platform.platform(),jdk='25.0.4',maven='3.9.12',jacoco='0.8.15',spotbugsPlugin='4.10.4.0',commands=begin['commands'],
      actualPhysicalMain=174,actualTestCases=cases,privateManifestSha256=hashlib.sha256(raw).hexdigest(),
      staticManifestSha256=hashlib.sha256(static_path.read_bytes()).hexdigest(),
      oracleRefs=['1181_semantic_enum内部命名是正・互換単体テスト仕様.md','ProtocolSemanticTypeTest.approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables','EnumWireCompatibilityTest.enum001SerializedAnswerStateMatchesIndependentProtocolVector','EnumWireCompatibilityTest.enum002EverySemanticEnumRetainsItsFieldIndependentSerialDescriptor'],
      bugs=['BUG1474','BUG1475'],crossCheck='YKT1237/YKT1238',coverageExclusionsAdded=0,
      coverageMissingByCounter={k:value['coverage'][k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')},
      fullCurrentSourceAcceptance=False,liveResourcesVerified=False,refusalException='PTALT-001 remains unresolved and unrelated to this executed subset')
    out=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5727-protocol88-enum18';os.umask(0o077);out.mkdir(parents=True)
    target=out/'manifest.json'
    with target.open('x')as f:json.dump(projected,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':value['source'],'tests':88,'suites':18,'fourCountersMissed0':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
