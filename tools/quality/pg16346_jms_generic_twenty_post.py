"""Independent exact XML/UTF8 byte/twenty-row Source-purpose check; no JMS or Graph execution."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16345-jms-generic-twenty-purpose-v2','516fd56986dae16a471bebbec54e7f0cc2e6a94b8196a8578728a0456202991a')
PRIOR=('PG16291-thread-five-gonefd-two-purpose-v2','657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
OUT=data.BASE/'PG16346-jms-generic-twenty-post-v1'

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
    xml_blob=(data.BASE/BASE[0]/'pmd.xml').read_bytes();require(data.sha(xml_blob)==base['reports']['pmd']['sha256']==m['baselinePmdXmlSha256'] and base['processingErrors']==[],'original complete XML')
    xml_rows={}
    for node in ET.fromstring(xml_blob):
        tag=node.tag.rpartition('}')[2];require(tag not in {'error','configerror'},'no hidden analyzer error')
        if tag!='file':continue
        name=node.get('name');path='src/schubert-nk-'+name.split('/src/schubert-nk-',1)[1]
        if path not in m['sourceHashes']:continue
        for item in node:
            attrs=dict(item.attrib);xml_rows[path,wire(attrs)]=''.join(item.itertext()).strip()
    ids={v['id'] for v in rows};require(len(rows)==len(ids)==20,'twenty unique warnings')
    expected_kinds={'ApiBrokerContexts.java':{126:'ASSEMBLY_PRIMARY',131:'ASSEMBLY_SECONDARY_CLOSE',213:'PASSWORD_SOURCE_FAILURE',223:'CONTEXT_CREATE_FAILURE',246:'OWNER_CLOSE_FAILURE'},
        'WebBrokerContexts.java':{121:'SETUP_PRIMARY',124:'SETUP_SECONDARY_CLOSE',164:'PASSWORD_SOURCE_FAILURE',174:'CONTEXT_CREATE_FAILURE',193:'OWNER_CLOSE_FAILURE'},
        'ArtemisConnectionFactoryProvider.java':{99:'SETUP_PRIMARY',102:'SETUP_SECONDARY_CLOSE'}}
    def purpose(v):
        path=v['path'];attrs=v['attributes'];key=path,wire(attrs);require(key in original_index and key in xml_rows,'exact diagnostic coordinate, never erase attrs')
        old=original_index[key];kind=expected_kinds[path.rsplit('/',1)[-1]][int(attrs['beginline'])]
        require(v['purposeKind']==kind and v['currentSource']==SOURCE and v['sourceSha256']==old['sourceSha256']==m['sourceHashes'][path],'purpose and whole Source')
        require(v['baselineManifestSha256']==BASE[1] and v['baselineDiagnostic']==old and v['baselineDiagnosticRowSha256']==data.sha(wire(old))
                and v['originalDiagnosticSha256']==data.sha(old['message'].encode()) and old['message']==xml_rows[key],'full original row and XML message')
        blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==m['sourceHashes'][path],'actual whole UTF8 source')
        lines=blob.decode().splitlines(keepends=True);a,b=int(attrs['beginline'])-1,int(attrs['endline'])-1;c,e=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
        start=len((''.join(lines[:a])+lines[a][:c]).encode());end=len((''.join(lines[:b])+lines[b][:e]).encode());token=blob[start:end]
        require(v['canonicalSpanStart']==start and v['canonicalSpanEndExclusive']==end and v['canonicalSpanSha256']==data.sha(token)
                and token in {b'RuntimeException',b'Exception',b'Error'},'independent UTF8 byte conversion from halfopen columns')
        require(v['spanBasis']=='QUALIFIED_PMD_CHARACTER_TO_UTF8_BYTE_HALFOPEN_SPAN' and v['dynamicGraphDependencyUnresolved'] is True
                and v['observerReturnProven'] is v['immutableStringPhysicalErasureProven'] is False,'unproven dynamic dependencies retained')
        require(v['productTestsExecuted']==0 and v['ptExecutionExempt'] is False and v['currentWholeCaseRefs']==[] and v['manualPurpose'] and v['residualRisk'],'not runtime/waiver')
    for v in rows:purpose(v)
    require(remaining==[v for v in queue if v['id'] not in ids] and len(remaining)==172
            and len({(v['path'],v['attributes']['beginline']) for v in rows})==12,'exact remaining order/twelve clauses')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['priorManifestSha256']==PRIOR[1] and v['priorQueueSha256']==prior['queueSha256'],'actual source/prior')
        require(v['sourceHashes']==m['sourceHashes'] and v['purposesSha256']==m['purposesSha256'] and v['queueSha256']==m['queueSha256']
                and v['baselineManifestSha256']==BASE[1] and v['baselineFindingsSha256']==base['findingsSha256'],'all public bindings')
        require((v['newManualReviews'],v['newReferenceConnections'],v['combinedSelectedReferences'],v['combinedPurposeReviewed'],v['combinedPurposeOrReferenceRows'],v['remainingSelectedUnreferenced'],v['sourceCatchClauses'],v['directContractMetadataNegativeVectors'],v['utf8PrefixPositiveVectors'])==(20,0,1171,148,1319,172,12,9,2),'warning/clauses/metadata not PT counts')
        require(v['productTestsExecuted']==v['externalActions']==v['rawSuppressed']==v['newAccepted']==0 and v['actualViolationCount'] is v['firstEverSemanticReasons'] is v['effortPercent'] is None,'no invented result/novelty/cost')
        require(all(v[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']),'no silent qualification')
    contract(m);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('sourceHashes',{}),('purposesSha256','0'*64),('queueSha256','0'*64),('baselineManifestSha256','0'*64),('baselineFindingsSha256','0'*64),('newManualReviews',0),('newReferenceConnections',20),('combinedSelectedReferences',1191),('combinedPurposeReviewed',128),('combinedPurposeOrReferenceRows',1299),('remainingSelectedUnreferenced',0),('sourceCatchClauses',20),('directContractMetadataNegativeVectors',0),('utf8PrefixPositiveVectors',0),('productTestsExecuted',20),('externalActions',1),('rawSuppressed',20),('newAccepted',1),('actualViolationCount',0),('ptExecutionExempt',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Source purpose manifest '+key)
    sample=rows[0];text=(data.ROOT/sample['path']).read_text();attrs=sample['attributes'];lines=text.splitlines(keepends=True)
    char_start=len(''.join(lines[:int(attrs['beginline'])-1]))+int(attrs['begincolumn'])-1
    require(char_start!=sample['canonicalSpanStart'],'Unicode prefix makes old character-as-byte counterexample nondegenerate')
    byte_neg=[]
    for key,value in [('canonicalSpanStart',char_start),('canonicalSpanStart',sample['canonicalSpanStart']-1),('canonicalSpanEndExclusive',sample['canonicalSpanEndExclusive']+1),('spanBasis','FULL_ASCII_ASSUMPTION')]:
        bad=copy.deepcopy(sample);bad[key]=value
        try:purpose(bad)
        except ValueError:byte_neg.append(key)
        else:raise ValueError('false UTF8 byte binding')
    for v in (m,prior,base):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],independentMetadataNegativeVectors=len(labels),negativeLabels=labels,
        utf8ByteNegativeVectors=len(byte_neg),utf8ByteNegativeLabels=byte_neg,sourceFiles=3,purposeRows=20,sourceCatchClauses=12,remaining=172,
        productTestsExecuted=0,sourceChanged=False,wholeF03Accepted=False,whole451Accepted=False,actualViolationCount=None,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
