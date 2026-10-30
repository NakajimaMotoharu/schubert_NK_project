"""Independent public golden bytes/schema and original whole8/one-codec Source proof, no Product replay."""
import copy
import json
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

PIN='bf31dcc65b69da33f948f7af4e4ddc35871c7339e7e1433bdc1ce22b56ff7048'
POST=data.BASE/'PG14888-backup-manifest-codec-eight-post-v1'
OUT=data.BASE/'PG14890-backup-manifest-codec-independent-v1'
NAME='dev/codex/schubert/nk/batch/file/BackupManifestCodec'
GOLDEN='733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only codec independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14886-backup-manifest-codec-eight-pt-v1/manifest.json','2ac97c21726f3a44d77919e7b7aaa80c9ebf3642ed6b10ee167694a2cf38cb92')
    registry=data.read_checked(data.BASE/'PG14876-current914-carrier-registry-v1/manifest.json','f75bcddfec1b33a972f607881b2de07a129ac5bb0d01f344bb5ce0f5cf74979b')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG14886-ORIGINAL-BACKUP-MANIFEST-CODEC8','same actual source/new own exec')
    methods=set()
    for name,h in p['xmlHashes'].items():
        content=(POST/name).read_bytes();require(data.sha(content)==h==raw['xmlHashes'][name],'whole original XML hash');root=ET.fromstring(content)
        require(int(root.get('tests'))==8 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all8 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'all genuine PASS');pair=(c.get('classname'),c.get('name'));require(pair not in methods,'unique8 original methods');methods.add(pair)
    require(len(methods)==8 and not methods&{(c['classname'],c['name']) for c in registry['cases']} and {n for c,n in methods}=={'independentCanonicalGolden','allFieldsAndMaximumLengths','structuralByteMutation','noncanonicalScalarsAndDates','missingUnknownDuplicateAndOrder','sizeAndNullBoundaries','inputOutputOwnership','concurrentCanonicalRoundTrips'},'original whole8 distinct from current914')
    golden=data.ROOT/'src/schubert-nk-batch/src/test/resources/backup/manifest-golden.json';content=golden.read_bytes()
    require(data.sha(content)==GOLDEN and len(content)==965 and (POST/'PT-BAT-186-manifest.json').read_bytes()==content,'independent fixed965byte golden/own synthetic trace')
    literal=json.loads(content);require(list(literal)==['format','database','runId','cutoff','startedAt','contentFinishedAt','databaseStep','configurationStep','versions','recipientSha256','files'],'independent fixed schema order')
    require(json.dumps(literal,separators=(',',':'),ensure_ascii=True).encode()+b'\n'==content and literal['format']=='NKBACKUP1' and literal['database']=='schubert_nk' and literal['runId']=='12345678-9abc-def0-8123-456789abcdef','independent canonical ASCII/LF and public claims identity')
    require(literal['databaseStep']['id']==90000 and literal['configurationStep']['id']==90001 and literal['databaseStep']['attempt']==literal['configurationStep']['attempt']==1 and [v['size'] for v in literal['files'].values()]==[1,512,200] and sum(v['size'] for v in literal['files'].values())==713,'independent fixed claim sizes/step identity')
    require(list(literal['files'])==['schubert_nk.dump','config.tar','credentials.tar.age'] and [v['sha256'] for v in literal['files'].values()]==['a'*64,'b'*64,'c'*64] and literal['recipientSha256']=='0'*64,'public synthetic digest values, not actual files/keys')
    require(NAME not in registry['fullSourceUnits'] and p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and p['metadataClasses']==[],'new complete one codec Source/class, no hidden filter')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    path='src/schubert-nk-batch/src/main/java/'+NAME+'.java';require(data.sha((data.ROOT/path).read_bytes())==normal['begin']['inputHashes'][path]=='7e9fdc5ea08e7616d3a8b5e77c5d3d194fbe61872d738ff5281419bcb6eb1d12','actual same Main byte pin')
    physical=(snapshot/'src/schubert-nk-batch/target/classes'/(NAME+'.class')).read_bytes();parsed=code.decode(physical,NAME+'.class')
    require(data.sha(physical)==p['physicalClasses'][NAME] and parsed['methods']==p['sourcePhysicalInventory'][NAME]['methods'] and parsed['sourceFile']=='BackupManifestCodec.java' and {'encode','decode','field','digest','invalid'}<={m['name'] for m in parsed['methods']},'independent complete executable Code inventory')
    counters=dict(LINE=dict(missed=0,covered=77),METHOD=dict(missed=0,covered=6),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=12))
    require(p['totals']==p['executable'][NAME]['counters']==p['fullSourceUnits'][NAME]['totals']==counters and p['fullSourceUnits'][NAME]['four100'] is True and p['missedLines']==[],'all actual nonempty four100, not partial helper coverage')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','executable','fullSourceUnits','totals','owners','ownedSyntheticTrace','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual byte/whole source/oracle values immutable')
        require(v['tests']==8 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'whole original8 unexcluded four100')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no old/helper/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',7),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',[NAME]),('totals',{}),('fullSourceUnits',{}),('ownedSyntheticTrace',{}),('fixtureHashes',{}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false codec proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=8,suites=1,newUniqueMethods=8,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,totals=counters,semanticNegativeVectors=len(negative),negativeLabels=negative,independentGoldenSha256=GOLDEN,independentGoldenBytes=965,publicSyntheticClaimsOnly=True,actualBackupOrKeyVerification=False,originalMethodsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
