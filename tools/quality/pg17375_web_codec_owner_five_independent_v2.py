"""Independent public key/AAD and ownership literal assertions, passive original Test CRC."""
import copy
import hashlib
import os
from pathlib import Path
import re
import shutil
import struct
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17370_web_codec_owner_five_pt as original
SOURCE=original.SOURCE
POST=('PG17372-web-codec-owner-five-post-v1','051fd03a1c42796a098795a2ab7ec283e486c872c7b1ee6cb47786a35e97b15c')
RAW='6cb044f9c143c9ae44a5c62e6f653743d8c321ad5da52b3fa1f019771d0abd76'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17370-web-codec-owner-five-pt-v1'
OUT=data.BASE/'PG17375-web-codec-owner-five-independent-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17374-web-codec-owner-five-independent-v1'
METHODS={'dev.codex.schubert.nk.web.bootstrap.WebNativeCodecsTest':['nkey005ThirdPurposeCopyNullFaultAndIndependentCipher','nkey001CopiesErasedButBorrowedCodecsSurviveUntilOwnerClose','nkey002NullMissingSecondCopyAndInvalidLengthFailClosed','nkey003PurposeOrderAndVersionFailureNeverUseFallback','nkey004ConcurrentBorrowAndCloseHaveOnlyOwnedOrClosedOutcome']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17370-web-codec-owner-five-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(5,1,1,3),'whole Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[original.NAME+'$1'],'NoCode SAM and unexecuted credential adapter retained')
        require(len(v['cases'])==5 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original5 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':5,'covered':57},'METHOD':{'missed':4,'covered':7},'CLASS':{'missed':1,'covered':1},'BRANCH':{'missed':0,'covered':14}},'complete partial counters')
        require(set(v['fullSourceUnits'])=={original.NAME} and set(v['fullSourceUnits'][original.NAME]['physical'])==set(original.CLOSURES[original.NAME]) and v['fullSourceUnits'][original.NAME]['four100'] is False,'whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['syntheticPublicKeyBuffersOnly'] is v['productOwnSecureRandomNonceGenerated'] is v['publicRandomUuidFixtureGenerated'] is v['cryptoOrKeyOperationsInvoked'] is True and v['actualSecretKeysLoaded'] is v['actualNativeHookOrProviderOperation'] is False,'disclosed synthetic JCA/entropy no real key')
        require(v['declaredOwnPlatformThreadCount']==2 and v['declaredOwnExecutorInstances']==v['declaredOwnTaskCount']==1 and v['ownThreadCount'] is None,'declared pool bound not actual observed thread count')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native and credential reader absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no backend')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',6),('suites',2),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',[]),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('syntheticPublicKeyBuffersOnly',False),('productOwnSecureRandomNonceGenerated',False),('publicRandomUuidFixtureGenerated',False),('cryptoOrKeyOperationsInvoked',False),('actualSecretKeysLoaded',True),('declaredOwnPlatformThreadCount',0),('ownThreadCount',2),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['sourceHashes'][str(path.relative_to(data.ROOT))]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    for token in ['List.of("copy", "null", "short", "version", "version-null", "fatal")','"web-revoke"','"schubert_web_session.pending_context_revocations"','new byte[] {1}','"v1"','"NKENC1"','assertEquals(102, actual.length)','new javax.crypto.spec.GCMParameterSpec(128, actual, 10, 12)','cipher.doFinal(actual, 22, 80)','new javax.crypto.spec.SecretKeySpec(bytes(129), "AES")','out.writeInt(field.length)','new byte[32], source.revoke','owner.close();','Executors.newFixedThreadPool(2)','for (int i = 0; i < 100; i++)','reader.get(5, TimeUnit.SECONDS)','((Source) source).requests']:
        require(token in text,'independent literal/JCA/ownership oracle '+token)
    fields=[b'web-revoke',b'schubert_web_session.pending_context_revocations',uuid.UUID('00112233-4455-6677-8899-aabbccddeeff').bytes,struct.pack('>qI',1788825600,0),bytes([1]),b'v1']
    aad=b''.join(struct.pack('>I',len(v))+v for v in fields)
    require([len(v) for v in fields]==[10,48,16,12,1,2] and len(aad)==113,'six literal public AAD fields/LP total')
    def aad_contract(value):
        offset=0
        for field in fields:
            require(len(value)>=offset+4,'complete public LP header')
            n=int.from_bytes(value[offset:offset+4],'big');offset+=4
            require(n==len(field) and value[offset:offset+n]==field,'exact public LP field')
            offset+=n
        require(offset==len(value)==113,'no trailing public AAD bytes')
    aad_contract(aad);aad_labels=[];offset=0
    for i,field in enumerate(fields):
        bad=aad[:offset]+struct.pack('>I',len(field)+1)+aad[offset+4:]
        require(bad!=aad,'nondegenerate public LP length')
        try:aad_contract(bad)
        except ValueError:aad_labels.append('length-'+str(i))
        else:raise ValueError('altered public LP accepted')
        offset+=4+len(field)
    try:aad_contract(aad+b'x')
    except ValueError:aad_labels.append('trailing')
    else:raise ValueError('trailing public AAD accepted')
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    base=next(iter(METHODS)).replace('.','/');names=[base]+[base+'$'+s for s in ['1','2','3','4','Source']]
    for name in names:
        src=RUN/'fresh-test-classes'/(name+'.class');dst=component/(name+'.class');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);physical[name]=data.sha(src.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','qualified passive class')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(k).read_bytes())==v for k,v in runtime['toolAndDependencyHashes'].items()),'same reader SDK')
    stage=runner.step('passive-original-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*names],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'same original Test CRC')
    lines=(SLOT/'passive-original-test-crc.stdout').read_text().splitlines();crc=[v.split(chr(9)) for v in lines if v.startswith('CLASS'+chr(9))]
    require(len(crc)==6 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=5,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=5,independentPublicAadSha256=hashlib.sha256(aad).hexdigest(),independentPublicAadLength=len(aad),independentPublicAadNegativeVectors=len(aad_labels),independentPublicAadNegativeLabels=aad_labels,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=3,metadataPhysicalClasses=1,partialSourcePrograms=1,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
