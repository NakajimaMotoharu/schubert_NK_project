"""Independent original reader4 literal wire/hash oracle and typed full-denominator post."""
import copy
import hashlib
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15854_scenario_record_reader_four_pt as original
import pg15856_scenario_record_reader_four_post as post

PIN='d6f4922e2f6096a34a4e0dbe0a533c029960978dcf5e11c18ceb4a5fc40f8913'
OUT=data.BASE/'PG15858-scenario-record-reader-four-independent-v1'
P='dev/codex/schubert/nk/web/storage/'
TOTALS={k:dict(covered=c,missed=0) for k,c in [('LINE',31),('METHOD',4),('CLASS',2),('BRANCH',14)]}
TRUE=['singleSession','officialGeneratedFiltersUnchanged','targetUnitFour100','allMeasuredApplicableCountersCovered','cryptoOrKeyOperationsInvoked','testOwnedTemporaryFileIo','testOwnedTempFilesCleanupByJunit','independentPublicFixtureOffsets','previousHelpersNotReaccepted']
FALSE=['actualFilesOpenedByProduct','actualPrivateFilesOpened','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused','rootMainInvoked','systemLoggerFactoryUsed']
ZERO=['failures','errors','skipped','reruns','newAccepted','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']
def require(ok,message):
    if not ok:raise ValueError(message)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==4 and p['suites']==1,'same source original four')
    require(all(p[k] is True for k in TRUE) and all(p[k] is False for k in FALSE) and all(type(p[k]) is int and p[k]==0 for k in ZERO) and p['effortPercent'] is None,'typed reviewed effects, no formal/external promotion')
    require(p['strictFour100GateExit']==p['crcMismatch']==0 and p['sessionIdentity']==original.SESSION and p['totals']==TOTALS,'full current source counters/CRC/session')
    names={P+'ScenarioRecordReader',P+'FileIntegrityException'};expected={n:[n] for n in names}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==names,'two whole Source/two Code only')
    require(p['metadataClasses']==p['manualCounterExclusions']==p['unexecutedCodeClasses']==[] and all(any(m['hasCode'] for m in row['methods']) for row in p['sourcePhysicalInventory'].values()),'no Code exclusion/NoCode substitution')
    require(all(type(v) is int for row in p['executable'].values() for c in row['counters'].values() for v in c.values()),'typed actual counters')
    require({k:{role:sum(r['counters'][k][role] for r in p['executable'].values()) for role in ['covered','missed']} for k in TOTALS}==TOTALS,'independent physical sums')
    reader=p['fullSourceUnits'][P+'ScenarioRecordReader'];error=p['fullSourceUnits'][P+'FileIntegrityException']
    require(reader['four100'] is True and reader['branchNaturallyZero'] is False and error['four100'] is False and error['branchNaturallyZero'] is error['threeCounter100'] is True,'one strict four/one natural B0, not two strict four')
    require(p['cryptoOperationKind']=='SHA256_PUBLIC_SYNTHETIC_TEMPORARY_FILE_BYTES_NO_KEYS' and p['publicSyntheticTestKeysUsed'] is False,'digest not key authority')
    require(len(p['owners'])==4 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==2,'two existing Main and two unknown Tests preserved')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive held/native absence terminals')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15854-scenario-record-reader-four-pt-v1/manifest.json',post.RAW);post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(r['classname'],r['name']) for r in p['cases']})==4,'original cases exactly once, no independent execution')
    fixture=original.FIXTURE_SOURCE.read_text();test=original.TESTS['ScenarioRecordReaderTest'].read_text()
    require('PayloadCodec' not in fixture and '50001 - sequence' in fixture and all(v in fixture for v in ['put(bytes, 0,','put(bytes, 12,','put(bytes, 18,','put(bytes, 26,','put(bytes, 164,','put(bytes, 4260,','4800L * count','MessageDigest.getInstance("SHA-256")']),'independent fixture offset/size/hash provenance')
    golden=bytearray(b' '*4800)
    for offset,value in [(0,b'000000050000'),(12,b'000001'),(18,b'00000042'),(26,b'narration'),(164,'本文'.encode('utf-8')),(4260,b'000')]:golden[offset:offset+len(value)]=value
    require(hashlib.sha256(golden).hexdigest()=='7ea8809736f14c427cb1561c79ebfd62eb3c4ecd82b17488bdf9fb474cd7caa5' and golden[4787:]==b' '*13,'independent literal full golden vector/hash/reserved')
    require(test.count('@Test')==4 and all(v in test for v in ['new int[] {1, 201, 10000}','new int[] {0, 4799, 4801}','index < 32','maximumRead = 7','2 * 4800L * count','new String[] {"ZERO", "IO", "EOF_ZERO", "SEEK", "SECOND_IO", "MUTATE"}','reserved[4799]','utf8[164]','nfc, 164','assertEquals(9600, channel.bytesRead)']),'normal/boundary/null/digest32/partial/sequencing/change oracle')
    path='documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md';ui=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)
    require(all(v.encode() in ui for v in ['| Entry ID | 1 | 12 |','| Entry sequence | 13 | 6 |','| 本文 | 165 | 4,096 |','| Audio sequence | 4,261 | 3 |','| Reserved | 4,788 | 13 |']),'approved main UI offset oracle')
    vectors=[('source','source','OLD'),('tests','tests',True),('totals','totals',{}),('closure','completeSourceUnitClosure',{}),('classes','physicalClasses',{}),('Code','sourcePhysicalInventory',{}),('executable','executable',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('unexecuted','unexecutedCodeClasses',['X']),('crc','crcMismatch',1),('owners','owners',{}),('cryptoKind','cryptoOperationKind','NONE'),('effort','effortPercent',100)]
    vectors.extend((k,k,False) for k in TRUE);vectors.extend((k,k,True) for k in FALSE);vectors.extend((k,k,1) for k in ['newAccepted','actualVmActions'])
    labels=[]
    for label,key,value in vectors:
        require(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True),'nondegenerate vector')
        changed=copy.deepcopy(p);changed[key]=value
        try:assess(changed)
        except ValueError:labels.append(label)
        else:raise ValueError('false reader qualification: '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=4,suites=1,sourcePrograms=2,newSourcePrograms=2,physicalClasses=2,executablePhysicalClasses=2,metadataPhysicalClasses=0,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,semanticNegativeVectors=len(labels),negativeLabels=labels,independentGoldenRecordBytes=4800,independentGoldenRecordSha256=hashlib.sha256(golden).hexdigest(),approvedMainUiPath=path,approvedMainUiSha256=data.sha(ui),cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],testOwnedTemporaryFileIo=True,actualSecretKeysLoaded=False,actualPrivateFilesOpened=False,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=4,semanticNegativeVectors=len(labels),newSourcePrograms=2)))
if __name__=='__main__':main()
