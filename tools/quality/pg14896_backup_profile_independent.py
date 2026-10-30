"""Independent original literal profile4/full Source counters and baseline ownership correction."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14895_backup_profile_four_post_v2 import owner_preflight

PIN='d32a7fc98d46a964b318402cbe5bd09e671c8e2bd5409d142c3d0206eecfd8b3'
POST=data.BASE/'PG14895-backup-profile-four-post-v2'
OUT=data.BASE/'PG14896-backup-profile-independent-v1'
NAME='dev/codex/schubert/nk/batch/backup/BackupProfile'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only profile independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14892-backup-profile-four-pt-v1/manifest.json','a36a4d313f3f6c858a7d89320ef5cc503024b187f03cad855c5255a267b50197')
    registry=data.read_checked(data.BASE/'PG14876-current914-carrier-registry-v1/manifest.json','f75bcddfec1b33a972f607881b2de07a129ac5bb0d01f344bb5ce0f5cf74979b')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG14892-ORIGINAL-BACKUP-PROFILE4','same actual source/one new own exec')
    cases=[]
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original4 XML bytes');tree=ET.fromstring(value)
        require(int(tree.get('tests'))==4 and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'whole4 FES0')
        for c in tree.findall('testcase'):
            require(not list(c),'genuine PASS');cases.append((c.get('classname'),c.get('name')))
    require(len(cases)==len(set(cases))==4 and not set(cases)&{(c['classname'],c['name']) for c in registry['cases']} and {n for c,n in cases}=={'positiveDelByteIsRejectedAndOwnedInputIsWiped','literalGoldenAndImmutableNonsecretClaims','strictByteAndCanonicalNegativeMatrixWipesEveryInput','constructorRejectsMissingUnknownNullAndMalformedHashes'},'all original four, no repeated methods')
    test=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupProfileTest.java';require(data.sha(test.read_bytes())=='4a963ac811d3f30f957310ae72755277cbc000f53a26af0da65e1cc822a20fdc','original literal Test pin')
    match=re.search(r'private static final String GOLDEN =\s*"""\n\s*(\{[^\n]+\})\n\s*""";',test.read_text());require(match is not None,'independent Java public textblock golden')
    literal=(match.group(1)+'\n').encode('ascii');value=json.loads(literal)
    versions=['host','app','schema','os','jdk','postgresql','artemis','age'];tools=['pgDumpWrapperSha256','pgRestoreWrapperSha256','pgDumpSha256','pgRestoreSha256','tarSha256','ageSha256','artemisArtifactSha256']
    require(list(value)==['profile',*versions,*tools] and value['profile']=='NKBACKUPPROFILE1' and [value[k] for k in versions]==['pgpt-host','0.1.0-PG381','023','ubuntu-26.04','25.0.4+6','18.6','2.56.0','1.2.1'] and all(value[k]=='1'*64 for k in tools),'independent version and seven synthetic hash claims')
    require(json.dumps(value,separators=(',',':')).encode()+b'\n'==literal,'independent canonical ASCII JSON/LF, no production expected generator')
    require(NAME not in registry['fullSourceUnits'] and p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and p['metadataClasses']==[],'entire new record Source/class, no metadata omission')
    snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot';physical=(snapshot/'src/schubert-nk-batch/target/classes'/(NAME+'.class')).read_bytes();parsed=code.decode(physical,NAME+'.class')
    require(data.sha(physical)==p['physicalClasses'][NAME] and parsed['methods']==p['sourcePhysicalInventory'][NAME]['methods'] and parsed['sourceFile']=='BackupProfile.java' and {'consume','encode','toolHashes','grammar','invalid','toString'}<={m['name'] for m in parsed['methods']},'independent full executable record inventory')
    counters=dict(LINE=dict(missed=0,covered=56),METHOD=dict(missed=0,covered=10),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=30));require(p['totals']==p['fullSourceUnits'][NAME]['totals']==p['executable'][NAME]['counters']==counters and p['targetUnitFour100'] is True and p['missedLines']==[],'all nonempty four100, no helper union')
    path='src/schubert-nk-batch/src/main/java/'+NAME+'.java';logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(owner_preflight('WBS-P017-06',logical)['canonicalCostOwner']==p['owners'][path]['canonicalOwner']==p['owners'][path]['canonicalCostOwner']=='WBS-P017-06' and p['owners'][path]['sha256']==data.sha((data.ROOT/path).read_bytes())=='4b9b04b202f3cafb60dfd69f420ea5e8e688ecf9db9d795998e55929e21ccdd6','actual baseline owner pair not neighbouring codec owner')
    owner_negative=[]
    for wrong in ['WBS-P017-05',None,'WBS-UNKNOWN']:
        try:owner_preflight(wrong,logical)
        except ValueError:owner_negative.append(wrong)
        else:raise ValueError('inferred owner accepted')
    codec=data.read_checked(data.BASE/'PG14888-backup-manifest-codec-eight-post-v1/manifest.json','bf31dcc65b69da33f948f7af4e4ddc35871c7339e7e1433bdc1ce22b56ff7048');codec_path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupManifestCodec.java'
    require(codec['owners'][codec_path]['canonicalOwner']==codec['owners'][codec_path]['canonicalCostOwner']==logical[codec_path]['owner']==logical[codec_path]['costOwner']=='WBS-P017-05','other codec actual canonical row non-applicable')
    require(p['invocation']['loadedProjectPythonSources']['tools/quality/reviewed_whole_pure_source_post_v2.py']==data.sha((data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v2.py').read_bytes())=='e03f87b04fc7b889aafaf6bf68754b1d85f5896c93b419f3decd8d7b35adb407','frozen qualified shared v2 unchanged')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','profile','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual original proof/owner values immutable')
        require(v['tests']==4 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'actual whole four100, no fake noCode')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['currentSourceExistingExecReanalyzed'] is v['originalTestsCountedElsewhere'] is False and v['effortPercent'] is None,'actual new method role/no old/formal transfer')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',3),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',[NAME]),('totals',{}),('fullSourceUnits',{}),('profile',{}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('oldCoverageTransferred',True),('currentSourceExistingExecReanalyzed',True),('originalTestsCountedElsewhere',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Profile proof accepted '+key)
    for v in [p,registry,codec]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=4,suites=1,newUniqueMethods=4,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,totals=counters,independentGoldenSha256=data.sha(literal),independentGoldenBytes=len(literal),semanticNegativeVectors=len(negative),negativeLabels=negative,ownerNamespacePositiveVectors=1,ownerNamespaceNegativeVectors=len(owner_negative),owner='WBS-P017-06',relatedCodecOwner='WBS-P017-05',historicalCostsReallocated=False,publicSyntheticClaimsOnly=True,actualToolAuthorityVerified=False,originalMethodsReexecuted=0,bug='BUG-2116',horizontal='YKT-1863',newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
