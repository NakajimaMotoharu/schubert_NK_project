"""Independent XML/UTF8/prefix binding for thirteen API catch purposes; no Product execution."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16356-api-borrowed-owned-thirteen-purpose-v1','e02c92bbc82d40711832235ad83f4d7377bbdfd1c27f31b549d863cf51ff9165')
PRIOR=('PG16350-jms-delivery-log-fortyseven-purpose-v1','5e9c475828e8139cfc66417a78cdb09f5d9cb119c21f3e2ef59ae94585a44a19')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
OUT=data.BASE/'PG16358-api-borrowed-owned-thirteen-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,prior,base=[read(v) for v in (RAW,PRIOR,BASE)]
    rows=data.read_checked(data.BASE/RAW[0]/'purposes.json',m['purposesSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    remaining=data.read_checked(data.BASE/RAW[0]/'remaining-selected-review-queue.json',m['queueSha256'])
    original=data.read_checked(data.BASE/BASE[0]/'findings.json',base['findingsSha256'])
    original_index={(v['path'],wire(v['attributes'])):v for v in original if v['path'] in m['sourceHashes']}
    xml_blob=(data.BASE/BASE[0]/'pmd.xml').read_bytes();require(data.sha(xml_blob)==base['reports']['pmd']['sha256'] and base['processingErrors']==[],'original complete XML')
    xml_rows={}
    for node in ET.fromstring(xml_blob):
        tag=node.tag.rpartition('}')[2];require(tag not in {'error','configerror'},'no hidden analyzer error')
        if tag!='file':continue
        name=node.get('name');path='src/schubert-nk-'+name.split('/src/schubert-nk-',1)[1]
        if path not in m['sourceHashes']:continue
        for item in node:
            attrs=dict(item.attrib);xml_rows[path,wire(attrs)]=''.join(item.itertext()).strip()
    ids={v['id'] for v in rows};require(len(rows)==len(ids)==13,'thirteen unique warnings')
    expected_kinds={"QuestionCommandService.java":{"196":"BORROWED_CANCEL","280":"BORROWED_DELETE"},"JdbcSyncRequestProcessor.java":{"44":"OWNED_SYNC_FAILURE","47":"OWNED_SYNC_ROLLBACK","57":"OWNED_SYNC_REDACT"},"WebLogIngestService.java":{"56":"OWNED_LOG_FAILURE","59":"OWNED_LOG_ROLLBACK"},"QuestionQueryRepository.java":{"313":"BORROWED_QUERY_PAGE","347":"BORROWED_QUERY_DETAIL"}}
    def purpose(v):
        path=v['path'];attrs=v['attributes'];key=path,wire(attrs);require(key in original_index and key in xml_rows,'exact diagnostic coordinate, never erase attrs')
        old=original_index[key];kind=expected_kinds[path.rsplit('/',1)[-1]][str(int(attrs['beginline']))]
        require(v['purposeKind']==kind and v['currentSource']==SOURCE and v['sourceSha256']==old['sourceSha256']==m['sourceHashes'][path],'purpose and whole Source')
        require(v['baselineManifestSha256']==BASE[1] and v['baselineDiagnostic']==old and v['baselineDiagnosticRowSha256']==data.sha(wire(old))
                and v['originalDiagnosticSha256']==data.sha(old['message'].encode()) and old['message']==xml_rows[key],'full original row and XML message')
        blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==m['sourceHashes'][path],'actual whole UTF8 source')
        lines=blob.decode().splitlines(keepends=True);a,b=int(attrs['beginline'])-1,int(attrs['endline'])-1;c,e=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
        prefix=''.join(lines[:b+1]);require('\\\\u' not in prefix and '\\r' not in prefix and '\\0' not in prefix,'untranslated prefix only before later escape')
        start=len((''.join(lines[:a])+lines[a][:c]).encode());end=len((''.join(lines[:b])+lines[b][:e]).encode());token=blob[start:end]
        require(v['canonicalSpanStart']==start and v['canonicalSpanEndExclusive']==end and v['canonicalSpanSha256']==data.sha(token)
                and token in {b'RuntimeException',b'Exception',b'Error'},'independent UTF8 byte conversion from halfopen columns')
        require(v['spanBasis']=='RAW_PREFIX_BEFORE_LATER_ESCAPE_QUALIFIED_UTF8_HALFOPEN' and v['dynamicGraphDependencyUnresolved'] is True
                and v['componentSpecificErrorPriorityRetained'] is True,'unproven dynamic dependencies retained')
        require(v['productTestsExecuted']==0 and v['ptExecutionExempt'] is False and v['currentWholeCaseRefs']==[] and v['manualPurpose'] and v['residualRisk'],'not runtime/waiver')
    for v in rows:purpose(v)
    require(remaining==[v for v in queue if v['id'] not in ids] and len(remaining)==112
            and len({(v['path'],v['attributes']['beginline']) for v in rows})==9,'exact remaining order/nine clauses')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['priorManifestSha256']==PRIOR[1] and v['priorQueueSha256']==prior['queueSha256'],'actual source/prior')
        require(v['sourceHashes']==m['sourceHashes'] and v['purposesSha256']==m['purposesSha256'] and v['queueSha256']==m['queueSha256']
                and v['baselineManifestSha256']==BASE[1] and v['baselineFindingsSha256']==base['findingsSha256'] and v['adapterPostSha256']=='9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814','all public bindings')
        require((v['newManualReviews'],v['newReferenceConnections'],v['combinedSelectedReferences'],v['combinedPurposeReviewed'],v['combinedPurposeOrReferenceRows'],v['remainingSelectedUnreferenced'],v['sourceCatchClauses'],v['directContractMetadataNegativeVectors'])==(13,0,1171,208,1379,112,9,12),'warning/clauses/metadata not PT counts')
        require(v['productTestsExecuted']==v['externalActions']==v['rawSuppressed']==v['newAccepted']==0 and v['actualViolationCount'] is v['firstEverSemanticReasons'] is v['effortPercent'] is None,'no invented result/novelty/cost')
        require(all(v[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']),'no silent qualification')
    contract(m);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('sourceHashes',{}),('purposesSha256','0'*64),('queueSha256','0'*64),('baselineManifestSha256','0'*64),('baselineFindingsSha256','0'*64),('newManualReviews',0),('newReferenceConnections',13),('combinedSelectedReferences',1184),('combinedPurposeReviewed',195),('combinedPurposeOrReferenceRows',1366),('remainingSelectedUnreferenced',0),('sourceCatchClauses',13),('directContractMetadataNegativeVectors',0),('adapterPostSha256','0'*64),('productTestsExecuted',13),('externalActions',1),('rawSuppressed',13),('newAccepted',1),('actualViolationCount',0),('ptExecutionExempt',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Source purpose manifest '+key)
    sample=rows[0]
    byte_neg=[]
    for key,value in [('canonicalSpanStart',sample['canonicalSpanStart']+1),('canonicalSpanStart',sample['canonicalSpanStart']-1),('canonicalSpanEndExclusive',sample['canonicalSpanEndExclusive']+1),('spanBasis','FULL_ASCII_ASSUMPTION')]:
        bad=copy.deepcopy(sample);bad[key]=value
        try:purpose(bad)
        except ValueError:byte_neg.append(key)
        else:raise ValueError('false UTF8 byte binding')
    for v in (m,prior,base):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],independentMetadataNegativeVectors=len(labels),negativeLabels=labels,
        utf8ByteNegativeVectors=len(byte_neg),utf8ByteNegativeLabels=byte_neg,sourceFiles=4,purposeRows=13,sourceCatchClauses=9,remaining=112,
        productTestsExecuted=0,sourceChanged=False,wholeF03Accepted=False,whole451Accepted=False,actualViolationCount=None,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
