"""Independent Scenario stream5 full-byte oracle and BUG2151 disclosure metadata, no Product replay."""
import copy
import hashlib
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15886_scenario_record_stream_five_pt as original
import pg15888_scenario_record_stream_five_post as post
import pg15889_reader_temporary_fixture_disclosure_erratum as erratum

PIN='221c4b68ed3f128cf26e43510f9d73c96bf4e031f9844b953a24b0b332aa6477'
CORR_PIN='4f9439fb32a5f5876e07bbe731a4864e3c9b46da3e946b18428b46df2f54773f'
OUT=data.BASE/'PG15890-scenario-record-stream-five-independent-v1'
NAME='dev/codex/schubert/nk/api/storage/ScenarioRecordStream'
TOTALS={k:dict(covered=c,missed=0) for k,c in [('LINE',30),('METHOD',6),('CLASS',1),('BRANCH',16)]}
TRUE=['singleSession','officialGeneratedFiltersUnchanged','targetUnitFour100','allMeasuredApplicableCountersCovered','cryptoOrKeyOperationsInvoked','onlyPublicScenarioStreamContracts','testOwnedTemporaryFileIo','testOwnedTemporaryFixtureWrites','testOwnedTempFilesCleanupByJunit','independentPublicFixtureOffsets','actualJdkFileForceOnOwnTemporaryFiles','ownEightThreadPoolUsed']
FALSE=['testOwnNewSlotPublicEvidenceWrites','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused','rootMainInvoked']
def require(ok,message):
    if not ok:raise ValueError(message)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==5 and p['suites']==1,'genuine current whole5')
    require(all(p[k] is True for k in TRUE) and all(p[k] is False for k in FALSE) and all(type(p[k]) is int and p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']) and p['effortPercent'] is None,'typed real temporary-file/force/digest scope, no actual lifecycle')
    require(p['strictFour100GateExit']==p['crcMismatch']==0 and p['sessionIdentity']==original.SESSION and p['totals']==TOTALS,'actual strict whole four/session/CRC')
    require(p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['fullSourceUnits'])==set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])=={NAME},'one whole Source/one Code only')
    require(p['metadataClasses']==p['manualCounterExclusions']==p['unexecutedCodeClasses']==[] and any(m['hasCode'] for m in p['sourcePhysicalInventory'][NAME]['methods']),'no Code exclusion/metadata conversion')
    u=p['fullSourceUnits'][NAME];require(u['totals']==p['executable'][NAME]['counters']==TOTALS and u['four100'] is u['threeCounter100'] is True and u['branchNaturallyZero'] is False,'complete Source not artificial branch-zero')
    require(all(type(v) is int for c in p['executable'][NAME]['counters'].values() for v in c.values()) and p['independentParallelChannels']==16,'typed counters/parallel16')
    require(p['cryptoOperationKind']=='SHA256_PUBLIC_SYNTHETIC_TEMPORARY_FILE_BYTES_NO_KEYS' and len(p['owners'])==2 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==1 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'public digest only, Test UNKNOWN remains')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual held/native boundary absence')
def assess_correction(c,audit):
    require(c['actualExit']==0 and c['source']==original.SOURCE and c['originalPostSha256']==erratum.READER_SHA and c['reportedOriginalFieldValue'] is True,'exact original reader report')
    e=c['effectiveDisclosure'];require(e['effectiveTestOwnNewSlotPublicEvidenceWrites'] is False and e['effectiveTestOwnedTemporaryFixtureWrites'] is e['effectiveTestOwnedTemporaryFileIo'] is e['effectiveTestOwnedTempFilesCleanupByJunit'] is True and e['actualTemporaryPathRecorded'] is False,'temporary fixtures not explicit slot evidence output')
    require((c['checkedPublicReferenceCount'],c['positiveReferenceCount'],c['affectedReferenceCount'])==(128,3,1) and len(audit)==len({r['name'] for r in audit})==128 and c['unreviewedPositiveReferences']==[],'all original/unit/additional/joint/resource references audited')
    require({r['name'] for r in audit if r['reportedOwnSlotOutput'] is True}=={erratum.READER,'PG15460-public-value-eighteen-post-v1','PG15872-maintenance-records-eight-post-v1'},'exact three positive reports')
    require(c['originalCountersSourceRunCasesAndCryptoUnchanged'] is c['originalManifestAndToolUnchanged'] is True and c['actualTemporaryPathInferred'] is False and c['productTestsExecuted']==c['newAccepted']==0 and c['formalUpdated'] is False and c['effortPercent'] is None,'no runtime rerun/counter mutation or path inference')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15886-scenario-record-stream-five-pt-v1/manifest.json',post.RAW);post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(c['classname'],c['name']) for c in p['cases']})==5,'five genuine original cases unchanged')
    text=original.TESTS['ScenarioRecordStreamTest'].read_text()
    require(text.count('@Test')==5 and all(v in text for v in ['new int[] {1, 201, 10000}','records(10001)','records(201)','input.set(200, record(200, invalid))','input.readNBytes(4800)','assertEquals(-1, input.read())','MessageDigest.getInstance("SHA-256")','actual.force(metadata)','assertTrue(channel.writes > 600)','mode <= 4','i < 16','assertEquals(0, entries.count())']),'original independent bytes/finite faults/preflight-before-IO/force/parallel oracle')
    golden=bytearray(b' '*4800)
    for offset,value in [(0,b'000000000071'),(12,b'000001'),(18,b'00000042'),(26,b'narration'),(164,'本文 0'.encode()),(4260,b'000')]:golden[offset:offset+len(value)]=value
    require(data.sha(golden)=='49f72d58dfc197bcc94a857e8292e86191a84b07ca7d80c6e8d8b6b56c6f3196' and golden[4787:]==b' '*13,'independent literal UI record1/hash/reserved')
    vectors=[]
    for count in [1,201,10000]:
        digest=hashlib.sha256()
        for i in range(count):
            value=bytearray(b' '*4800)
            for offset,part in [(0,f'{71+i:012d}'),(12,f'{i+1:06d}'),(18,f'{42+i:08d}'),(26,'narration'),(164,'本文 '+str(i)),(4260,'000')]:
                encoded=part.encode('utf-8');value[offset:offset+len(encoded)]=encoded
            digest.update(value)
        vectors.append(dict(records=count,expectedBytes=count*4800,independentExpectedSha256=digest.hexdigest(),basis='UI234_OFFSETS_NO_PRODUCTION_METHOD_USED; ORIGINAL_TEST_ASSERTS_ALL_BYTES_AND_INDEPENDENT_JDK_DIGEST'))
    ui='documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md';ui_raw=subprocess.check_output(['git','show','origin/main:'+ui],cwd=data.ROOT)
    require(all(v.encode() in ui_raw for v in ['| Entry ID | 1 | 12 |','| Entry sequence | 13 | 6 |','| 本文 | 165 | 4,096 |','| Audio sequence | 4,261 | 3 |','| Reserved | 4,788 | 13 |']),'approved main layout oracle')
    c=data.read_checked(erratum.OUT/'manifest.json',CORR_PIN);audit=data.read_checked(erratum.OUT/'reference-field-audit.json',c['fieldAuditSha256']);assess_correction(c,audit)
    for row in audit:
        value=data.read_checked(data.BASE/row['name']/'manifest.json',row['sha256'])
        require(value.get('testOwnNewSlotPublicEvidenceWrites') is row['reportedOwnSlotOutput'] and value['source']==row['source'],'each original public report retained, absence not zero inferred')
    negatives=[]
    values=[('source','source','OLD'),('tests','tests',True),('totals','totals',{}),('closure','completeSourceUnitClosure',{}),('physical','physicalClasses',{}),('inventory','sourcePhysicalInventory',{}),('metadata','metadataClasses',['X']),('exclusion','manualCounterExclusions',['X']),('unexecuted','unexecutedCodeClasses',['X']),('strict','strictFour100GateExit',1),('crc','crcMismatch',1),('parallel','independentParallelChannels',0),('owners','owners',{}),('effort','effortPercent',100)]
    values.extend((k,k,False) for k in TRUE);values.extend((k,k,True) for k in FALSE)
    for label,key,value in values:
        require(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True),'nondegenerate negative')
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:negatives.append(label)
        else:raise ValueError('false stream qualification '+label)
    correction_negatives=[]
    for label,change in [('slot-output-conflated',lambda v:v['effectiveDisclosure'].update(effectiveTestOwnNewSlotPublicEvidenceWrites=True)),('fixture-denied',lambda v:v['effectiveDisclosure'].update(effectiveTestOwnedTemporaryFixtureWrites=False)),('path-inferred',lambda v:v.update(actualTemporaryPathInferred=True)),('counter-modified',lambda v:v.update(originalCountersSourceRunCasesAndCryptoUnchanged=False)),('unreviewed-hidden',lambda v:v.update(unreviewedPositiveReferences=['PUBLIC_UNREVIEWED']))]:
        bad=copy.deepcopy(c);change(bad)
        try:assess_correction(bad,audit)
        except ValueError:correction_negatives.append(label)
        else:raise ValueError('false disclosure correction '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(c['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'independent-golden-record-vectors.json',vectors)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=5,suites=1,sourcePrograms=1,newSourcePrograms=1,physicalClasses=1,executablePhysicalClasses=1,metadataPhysicalClasses=0,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,semanticNegativeVectors=len(negatives),negativeLabels=negatives,independentGoldenVectorsSha256=data.sha((OUT/'independent-golden-record-vectors.json').read_bytes()),cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],onlyPublicScenarioStreamContracts=True,testOwnedTemporaryFixtureWrites=True,testOwnNewSlotPublicEvidenceWrites=False,actualJdkFileForceOnOwnTemporaryFiles=True,actualSecretKeysLoaded=False,actualPrivateFilesOpened=False,disclosureErratumSha256=CORR_PIN,disclosureCorrectionNegativeVectors=len(correction_negatives),disclosureCorrectionNegativeLabels=correction_negatives,all128PublicReferencesVerified=True,originalReaderFourReexecuted=False,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=5,semanticNegativeVectors=len(negatives),disclosureCorrectionNegativeVectors=len(correction_negatives))))
if __name__=='__main__':main()
