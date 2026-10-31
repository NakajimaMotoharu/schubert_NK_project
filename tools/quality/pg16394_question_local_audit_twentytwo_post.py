"""Independent XML/JLS zero-translation/Source binding for twenty-two question/local audit purposes."""
import copy
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16392-question-local-audit-twentytwo-purpose-v1','9c29b2aeddef946dcfcfc9b38b5d7afdbaf60a9f8f8631e51180bc728200947b')
PRIOR=('PG16380-batch-phase-eighteen-purpose-v1','db29b0860008a141a128ebe3dd6e97d7870dbd5a8c2cf91542cd57c18566bcae')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
QUAL=('PG16386-zero-unicode-span-qualification-v1','a867f250314fe3d1a670f09e85e15d3e82067a125bcd2e94e90dc1a746d568a0')
QUAL_POST=('PG16388-zero-unicode-span-independent-v1','8cb0a1383eb69550600464a4a2884e2bbc06071640623fc41c3fd3b29860ac1f')
OUT=data.BASE/'PG16394-question-local-audit-twentytwo-post-v1'

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
    ids={v['id'] for v in rows};require(len(rows)==len(ids)==22,'twenty-two unique warnings')
    expected_kinds={"QuestionSubmissionService.java":{"138":"SUBMISSION_OUTER_FAILURE","206":"SUBMISSION_ACCEPTANCE_TX","484":"SUBMISSION_SENT_TX","589":"SUBMISSION_RETAINED_AUDIT_TX","756":"SUBMISSION_ROLLBACK"},"QuestionWorkerService.java":{"139":"WORKER_PROVIDER_RUNTIME","153":"WORKER_OUTER_FAILURE","666":"WORKER_TX_FAILURE","669":"WORKER_TX_ROLLBACK"},"WebRequestLogProducer.java":{"202":"PROJECTION_FAILED_AUDIT","231":"LOCAL_LOGGER_RUNTIME","237":"LOCAL_TERMINAL_RUNTIME","282":"PROJECTION_TX_FAILURE","285":"PROJECTION_ROLLBACK_ORDINARY","287":"PROJECTION_ROLLBACK_ERROR"}}
    def purpose(v):
        path=v['path'];attrs=v['attributes'];key=path,wire(attrs);require(key in original_index and key in xml_rows,'exact diagnostic coordinate, never erase attrs')
        old=original_index[key];kind=expected_kinds[path.rsplit('/',1)[-1]][str(int(attrs['beginline']))]
        require(v['purposeKind']==kind and v['currentSource']==SOURCE and v['sourceSha256']==old['sourceSha256']==m['sourceHashes'][path],'purpose and whole Source')
        require(v['baselineManifestSha256']==BASE[1] and v['baselineDiagnostic']==old and v['baselineDiagnosticRowSha256']==data.sha(wire(old))
                and v['originalDiagnosticSha256']==data.sha(old['message'].encode()) and old['message']==xml_rows[key],'full original row and XML message')
        blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==m['sourceHashes'][path],'actual whole UTF8 source')
        lines=blob.decode().splitlines(keepends=True);a,b=int(attrs['beginline'])-1,int(attrs['endline'])-1;c,e=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
        text=blob.decode();runs=re.findall(r'(\\+)u',text)
        require(all(len(run)%2==0 for run in runs) and len(runs)==2 and not any(c in text for c in ('\r','\0','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029','\x1a')),'independent zero-translation/no ambiguous lines')
        start=len((''.join(lines[:a])+lines[a][:c]).encode());end=len((''.join(lines[:b])+lines[b][:e]).encode());token=blob[start:end]
        require(v['canonicalSpanStart']==start and v['canonicalSpanEndExclusive']==end and v['canonicalSpanSha256']==data.sha(token)
                and token in {b'RuntimeException',b'Exception',b'Error'},'independent UTF8 byte conversion from halfopen columns')
        require(v['spanBasis']=='JLS25_ZERO_ELIGIBLE_UNICODE_ESCAPE_UTF8_HALFOPEN' and v['dynamicGraphDependencyUnresolved'] is True
                and v['componentSpecificErrorPriorityRetained'] is True,'unproven dynamic dependencies retained')
        require(v['productTestsExecuted']==0 and v['ptExecutionExempt'] is False and v['currentWholeCaseRefs']==[] and v['manualPurpose'] and v['residualRisk'],'not runtime/waiver')
    for v in rows:purpose(v)
    require(remaining==[v for v in queue if v['id'] not in ids] and len(remaining)==10
            and len({(v['path'],v['attributes']['beginline']) for v in rows})==15,'exact remaining order/fifteen clauses')
    qualification,qualification_post=[read(v) for v in (QUAL,QUAL_POST)]
    helper_hash='5d0866d2f000218feda73ba52f8079c9834eeb8a101b4cb54bc60b7e76296df2'
    require(qualification['actualExit']==qualification_post['actualExit']==0 and qualification['source']==qualification_post['source']==SOURCE and qualification_post['parentManifestSha256']==QUAL[1] and qualification['helperSha256']==qualification_post['helperSha256']==helper_hash==data.sha((data.ROOT/qualification['helper']).read_bytes()),'same original zero-translation qualification')
    approved_hashes={}
    for design in ["documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md","documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md","documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md"]:
        blob=(data.ROOT/design).read_bytes()
        require(blob==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved three design Sources')
        approved_hashes[design]=data.sha(blob)
    def contract(v):
        require(v['approvedDesignHashes']==approved_hashes and v['spanQualificationSha256']==QUAL[1] and v['spanIndependentQualificationSha256']==QUAL_POST[1] and v['spanHelperSha256']==helper_hash,'exact design and zero-translation qualification bindings')
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['priorManifestSha256']==PRIOR[1] and v['priorQueueSha256']==prior['queueSha256'],'actual source/prior')
        require(v['sourceHashes']==m['sourceHashes'] and v['purposesSha256']==m['purposesSha256'] and v['queueSha256']==m['queueSha256']
                and v['baselineManifestSha256']==BASE[1] and v['baselineFindingsSha256']==base['findingsSha256'] and v['adapterPostSha256']=='9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814','all public bindings')
        require((v['newManualReviews'],v['newReferenceConnections'],v['combinedSelectedReferences'],v['combinedPurposeReviewed'],v['combinedPurposeOrReferenceRows'],v['remainingSelectedUnreferenced'],v['sourceCatchClauses'],v['directContractMetadataNegativeVectors'])==(22,0,1171,310,1481,10,15,9),'warning/clauses/metadata not PT counts')
        require(v['productTestsExecuted']==v['externalActions']==v['rawSuppressed']==v['newAccepted']==0 and v['actualViolationCount'] is v['firstEverSemanticReasons'] is v['effortPercent'] is None,'no invented result/novelty/cost')
        require(all(v[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']),'no silent qualification')
    contract(m);labels=[]
    for key,value in [('approvedDesignHashes',{}),('spanQualificationSha256','0'*64),('spanIndependentQualificationSha256','0'*64),('spanHelperSha256','0'*64),('actualExit',True),('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('sourceHashes',{}),('purposesSha256','0'*64),('queueSha256','0'*64),('baselineManifestSha256','0'*64),('baselineFindingsSha256','0'*64),('newManualReviews',0),('newReferenceConnections',13),('combinedSelectedReferences',1184),('combinedPurposeReviewed',288),('combinedPurposeOrReferenceRows',1459),('remainingSelectedUnreferenced',0),('sourceCatchClauses',13),('directContractMetadataNegativeVectors',0),('adapterPostSha256','0'*64),('productTestsExecuted',13),('externalActions',1),('rawSuppressed',13),('newAccepted',1),('actualViolationCount',0),('ptExecutionExempt',True),('formalUpdated',True),('effortPercent',100)]:
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
    for v in (m,prior,base,qualification,qualification_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],independentMetadataNegativeVectors=len(labels),negativeLabels=labels,
        utf8ByteNegativeVectors=len(byte_neg),utf8ByteNegativeLabels=byte_neg,sourceFiles=3,purposeRows=22,sourceCatchClauses=15,remaining=10,
        productTestsExecuted=0,sourceChanged=False,wholeF03Accepted=False,whole451Accepted=False,actualViolationCount=None,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
