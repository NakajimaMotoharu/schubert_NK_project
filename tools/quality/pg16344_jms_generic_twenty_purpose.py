"""Twenty generic-catch Source purposes; no provider, credential, Graph or cleanup execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16291-thread-five-gonefd-two-purpose-v2','657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASELINE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
OUT=data.BASE/'PG16344-jms-generic-twenty-purpose-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts.java'
WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java'
FACTORY='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ArtemisConnectionFactoryProvider.java'
PINS={API:'af4602cd8c0906045e5985cba6a4e7e32d43b74e59a060f207705b3166f10330',WEB:'093e19a0dab933309178946242efbd01c3dc4a47c0f97e1cf0fb1d5807be5c1c',FACTORY:'e34f85fb6c359595962afb863089e0f4c874dd78a4108981e1d623ec03b2d6e8'}
KINDS={API:{126:'ASSEMBLY_PRIMARY',131:'ASSEMBLY_SECONDARY_CLOSE',213:'PASSWORD_SOURCE_FAILURE',223:'CONTEXT_CREATE_FAILURE',246:'OWNER_CLOSE_FAILURE'},
       WEB:{121:'SETUP_PRIMARY',124:'SETUP_SECONDARY_CLOSE',164:'PASSWORD_SOURCE_FAILURE',174:'CONTEXT_CREATE_FAILURE',193:'OWNER_CLOSE_FAILURE'},
       FACTORY:{99:'SETUP_PRIMARY',102:'SETUP_SECONDARY_CLOSE'}}
PURPOSES={
    'ASSEMBLY_PRIMARY':'Broad runtime/fatal assembly boundary protects already captured factories in reverse index order and rethrows the same primary when cleanup/observers/attachment return. No successful owner is published on this source path.',
    'ASSEMBLY_SECONDARY_CLOSE':'Captures the per-owner secondary, notifies the declared UNKNOWN policy and retains non-self primary suppression/fallback. The observer is inside the constructor loop and may not return; this does not prove all later closes occur.',
    'PASSWORD_SOURCE_FAILURE':'A failing borrowed password supplier goes through the declared fatal-graph check then fixed unavailable error if that check returns; never a successful JMS context. Graph semantics are outside this Source review.',
    'CONTEXT_CREATE_FAILURE':'A createContext/length/null-result runtime failure goes through the declared fatal check and fixed unavailable error; the mutable char copy is filled in finally. Immutable String/provider erasure is not promised.',
    'OWNER_CLOSE_FAILURE':'Close uncertainty is recorded/observed and either fatal or fixed redacted error is propagated if the observer/graph calls return. Only normal owner close paths mark success; UNKNOWN retention is not normal release.',
    'SETUP_PRIMARY':'Configuration failure owns one close attempt before secondary priority/attachment and eventual primary rethrow; no configured factory is returned by this failure source path.',
    'SETUP_SECONDARY_CLOSE':'After the owned close failure the observer is notified; a secondary Error outranks a non-Error primary, otherwise attachment is delegated before primary rethrow. Nonreturn/Graph behavior is not dynamically proven.'}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def controls(path,text):
    compact=''.join(text.split());require(text.isascii(),'whole raw ASCII makes character and byte offsets equal')
    if path==API:
        required=['catch(RuntimeException|Errorfailure){','closeFailures[index]=closing;onUnconfirmed.accept(closing);',
            'if(closing!=failure)failure.addSuppressed(closing);','if(failure.getSuppressed().length==0){',
            'owners.get(index).close();ownerClosed[index]=true;',
            'if(failure!=null)onUnconfirmed.accept(failure);if(failureinstanceofErrorfatal)throwfatal;',
            'thrownewIllegalStateException("APIbrokerfactoryclosefailed");}closed=true;']
    else:
        helper='WebStartupException' if path==WEB else 'TemporaryInfrastructureException'
        required=['catch(RuntimeException|Errorprimary){','catch(RuntimeException|Errorsecondary){',
            'factory.close();','onUnconfirmed.accept(secondary);',
            'if(secondaryinstanceofError&&!(primaryinstanceofError)){secondary.addSuppressed(primary);throwsecondary;}',
            helper+'.attachSecondary(primary,secondary);','throwprimary;']
        ordered=['factory.close();','onUnconfirmed.accept(secondary);','if(secondaryinstanceofError',helper+'.attachSecondary(primary,secondary);','throwprimary;']
        require([compact.index(x) for x in ordered]==sorted(compact.index(x) for x in ordered),'source close/observer/priority/attachment order')
        if path==WEB:required+=['owner.close();}catch(Exception|Errorfailure){','thrownewIllegalStateException("Webbrokerfactoryclosefailed");}closed=true;']
    require(all(x in compact for x in required),'explicit source ownership/error controls')
    if path!=FACTORY:
        helper='TemporaryInfrastructureException' if path==API else 'WebStartupException'
        require(compact.count(helper+'.preserveFatal(failure);thrownewIllegalStateException(UNAVAILABLE);')==2
                and r"Arrays.fill(copy,'\0');" in compact and 'newString(copy)' in compact,'two fixed redactions and mutable-only wipe')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,baseline=[read(v) for v in (PRIOR,OBS,BASELINE)]
    require(prior['actualExit']==obs['actualExit']==baseline['actualExit']==0 and prior['source']==obs['source']==SOURCE,'actual saved static chain')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==192 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==128,'prior exact domains')
    original=data.read_checked(data.BASE/BASELINE[0]/'findings.json',baseline['findingsSha256'])
    observed={v['staticObservationId']:v for v in data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])}
    xml=(data.BASE/BASELINE[0]/'pmd.xml').read_bytes();require(data.sha(xml)==baseline['reports']['pmd']['sha256'],'original analyzer XML retained')
    selected=[v for v in queue if v['path'] in PINS]
    require(len(selected)==20 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'only twenty generic rows')
    texts={p:(data.ROOT/p).read_text() for p in PINS};negative=[]
    for path,text in texts.items():
        require(data.sha(text.encode())==PINS[path],'whole current Source hash');controls(path,text)
        changes=[('ownerClosed[index] = true;','ownerClosed[index] = false;'),('closeFailures[index] = closing;','closeFailures[index] = null;'),('Arrays.fill(copy,','REMOVED(copy,')] if path==API else [('factory.close();','OMITTED();'),('throw secondary;','return factory;'),('throw primary;','return factory;')]
        for number,(a,b) in enumerate(changes):
            require(a in text,'nondegenerate source metadata variant');bad=text.replace(a,b)
            try:controls(path,bad)
            except (ValueError,IndexError):negative.append(path+':'+str(number))
            else:raise ValueError('false source control accepted')
    purposes=[]
    for row in selected:
        path=row['path'];o=observed[row['id']];matches=[v for v in original if v['path']==path and v['attributes']==row['attributes'] and v['sourceSha256']==row['sourceSha256']]
        require(len(matches)==1,'one same-byte original diagnostic');raw=matches[0]
        require(o['currentSource']==SOURCE and o['measurementDomain']=='UNCHANGED_MAIN_INPUT_PG13253' and o['sourceSha256']==row['sourceSha256']==PINS[path]
                and o['attributes']==raw['attributes'] and o['message']==raw['message'],'correct current diagnostic origin, not old coordinate assumption')
        line=int(row['attributes']['beginline']);kind=KINDS[path][line];a,b,token=span(texts[path],row['attributes'])
        require(token in {'RuntimeException','Exception','Error'} and texts[path].encode()[a:b]==token.encode(),'raw ASCII type token')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_GENERIC_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Source-shape and manual policy only: no type/CFG/transitive Graph/provided Throwable cycle behavior, real provider/credential/close/observer return, UNKNOWN retention recovery/deadline or actual JMS/runtime assurance.',
            baselineManifestSha256=BASELINE[1],baselineDiagnosticRowSha256=data.sha(wire(raw)),baselineDiagnostic=raw,originalDiagnosticSha256=data.sha(raw['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='QUALIFIED_PMD_HALFOPEN_FULL_ASCII_SOURCE',
            dynamicGraphDependencyUnresolved=True,immutableStringPhysicalErasureProven=False,observerReturnProven=False,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    require(len(remaining)==172 and len({(v['path'],v['attributes']['beginline']) for v in purposes})==12,'twenty rows/twelve source catch clauses, not test cases')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    for v in (prior,obs,baseline):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASELINE[1],baselineFindingsSha256=baseline['findingsSha256'],baselinePmdXmlSha256=data.sha(xml),approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=20,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=148,combinedPurposeOrReferenceRows=1319,remainingSelectedUnreferenced=172,sourceCatchClauses=12,directContractMetadataNegativeVectors=len(negative),directContractNegativeLabels=negative,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
