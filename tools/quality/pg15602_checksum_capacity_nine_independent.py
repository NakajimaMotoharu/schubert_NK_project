"""Independent fixed checksum/decimal-capacity oracles and exact whole-source metadata; no product run."""
import copy
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15598_checksum_capacity_nine_pt as original
import pg15600_checksum_capacity_nine_post as post

PIN='1279bca0c949f4aaa26ce5913fef4bfb6a1add3c072c213a3e1a273e80e88b0d'
OUT=data.BASE/'PG15602-checksum-capacity-nine-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in values) for n,values in original.CLOSURES.items()}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(9,2,9,2) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'genuine nine')
    require(len({(c['classname'],c['name']) for c in p['cases']})==9 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'whole four Source/seven Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no exclusion')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(missed=0,covered=v) for k,v in [('LINE',121),('METHOD',19),('CLASS',7),('BRANCH',60)]},'independent exact sums')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==ns and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)) and u['threeCounter100'] is True,'actual per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['allMeasuredApplicableCountersCovered'] is True and sum(u['four100'] for u in p['fullSourceUnits'].values())==2,'two branchless not fake four100')
    require(p['cryptoOrKeyOperationsInvoked'] is True and p['cryptoOperationKind']=='MESSAGEDIGEST_ISEQUAL_PUBLIC_LITERAL_SHA_TEXT_ONLY' and p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is False and p['ownedJcaProviderOrderRestored'] is None,'truthful SHA comparison only')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is False,'no live/private IO')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no transfer/acceptance')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==6 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==4 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==2,'actual owners')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual stage terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15598-checksum-capacity-nine-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15588-current1894-public-inbox-values-registry-v1/manifest.json','326d30d61ad5da5149c91af3b8687ef954180f0487925857e3158ed85699b9b1')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new four Source, no old helper reacceptance')
    texts={k:path.read_text() for k,path in original.TESTS.items()};expected=set()
    for key,text in texts.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(names)==original.COUNTS[key],'whole original counts')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every whole original once')
    checksum=texts['AssetChecksumManifestTest'];capacity=texts['TransferCapacityTest']
    abc=hashlib.sha256(b'abc').hexdigest();require(abc=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad' and abc in checksum,'independent published SHA256 abc')
    longest='music/'+'a'*250+'/'+'b'*251+'.ogg'
    require(len(longest.encode())==512 and len((abc+'  '+longest).encode())==578 and len((longest+'x').encode())==513,'independent exact byte boundaries')
    require(unicodedata.normalize('NFC','e\u0301')=='é' and 'music/e\\u0301.ogg' in checksum and '"あ".repeat(23)' in checksum,'independent NFC and character-vs-byte negative')
    require(all(v in checksum for v in ['59_627','59_628','music/59626.ogg','new int[] {1, 13, 65_536}','new int[] {0, 3}','failAfter + 1','i < 64','i < 100','assertTrue(source.isOpen())','assertEquals(0, source.reads)']),'original complete fixed input matrix/borrowed ownership')
    byte_inputs=[0,3499999999,3500000000,3500000001,4499999999,4500000000,4500000001,2**63-1]
    file_inputs=[0,4999,5000,5001,8999,9000,9001,2**63-1]
    byte_levels=['NORMAL','NORMAL','WARNING','WARNING','WARNING','CRITICAL','CRITICAL','CRITICAL']
    file_levels=['NORMAL','NORMAL','WARNING','WARNING','WARNING','CRITICAL','CRITICAL','CRITICAL']
    require([('CRITICAL' if b>=4500000000 else 'WARNING' if b>=3500000000 else 'NORMAL') for b in byte_inputs]==byte_levels and [('CRITICAL' if f>=9000 else 'WARNING' if f>=5000 else 'NORMAL') for f in file_inputs]==file_levels,'independent decimal boundary matrix')
    require(4499999999+48000000==4547999999<5000000000 and 4800+9600+4800==19200 and 4800+9600==14400,'independent admission and retention arithmetic')
    require(all(v in capacity for v in ['4_547_999_999L','48_000_001','new TransferCapacity(0, 8999)','new TransferCapacity(4_499_999_999L, 100)','assertEquals(1, accepted)','synchronized (capacity)','synchronized (reservation)','first::retain','second::retain','second.close();','assertEquals(14400, snapshot.bytes())']),'independent null/size/idempotence/concurrency assertions')
    docs=['documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md','documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(b==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,b in documents.items()),'approved design exact main bytes')
    require('512' in documents[docs[0]].decode() and '>=3.5GBまたは5,000' in documents[docs[1]].decode() and '>=4.5GBまたは9,000' in documents[docs[1]].decode(),'approved independent byte/alert values')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('sources','fullSourceUnits',{}),('tests','tests',10),('suites','suites',3),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic-key','publicSyntheticTestKeysUsed',True),('jca','childLocalJcaRegistryRestorationTested',True),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=9,suites=2,sourcePrograms=4,physicalClasses=7,four100SourcePrograms=2,naturallyBranchZeroSourcePrograms=2,incompleteSourcePrograms=0,baselineMainOwnerRows=4,unknownTestOwnerRows=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentAbcSha256=abc,maximumPathBytes=512,maximumManifestLineBytes=578,independentByteBoundaryLevels=byte_levels,independentFileBoundaryLevels=file_levels,pythonVersion=sys.version,approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticTestKeysUsed=False,childLocalJcaRegistryRestorationTested=False,ownFreshJvmProviderStateOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=9,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
