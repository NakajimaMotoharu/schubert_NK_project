"""Independent original two XML/current Source byte/purpose binding, no native execution."""
import copy
import json
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16380-batch-phase-eighteen-purpose-v1','db29b0860008a141a128ebe3dd6e97d7870dbd5a8c2cf91542cd57c18566bcae')
PRIOR=('PG16374-maintenance-jdbc-nineteen-purpose-v1','5a07285c8e9198df00f7cb8825127a68f3836518590cfdfdcad78db135ec8e2e')
REPORTS=[('PG13505-main-assignment-seven-v1','aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf'),('PG13534-main-assignment-final-four-v1','36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda')]
OUT=data.BASE/'PG16382-batch-phase-eighteen-post-v1'
KINDS={"StartupAdmissionFile.java":{"287":"REVERSE_UNKNOWN","303":"REVERSE_UNKNOWN_AFTER_IO","320":"REVERSE_DRAIN_SECONDARY"},"FixedUnitCgroupNamespace.java":{"178":"FORWARD_UNKNOWN","193":"FORWARD_UNKNOWN_AFTER_IO","209":"FORWARD_DRAIN_SECONDARY"},"MorningBackupArtifacts.java":{"548":"BACKUP_BYTES_FAILURE"},"MorningPermitPublication.java":{"209":"PUBLICATION_UNSTARTED_CLOSE","236":"PUBLICATION_ABORT_UNCONFIRMED"}}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,prior=[read(v) for v in (RAW,PRIOR)]
    rows=data.read_checked(data.BASE/RAW[0]/'purposes.json',m['purposesSha256'])
    remaining=data.read_checked(data.BASE/RAW[0]/'remaining-selected-review-queue.json',m['queueSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    diagnostics={};refs=[]
    for pair in REPORTS:
        report=read(pair);blob=(data.BASE/pair[0]/'pmd.xml').read_bytes()
        require(report['actualExit']==report['productTestsExecuted']==0 and data.sha(blob)==report['reports']['pmd'],'saved current XML and exit')
        refs.append(dict(manifest=pair[0],sha256=pair[1],pmdSha256=data.sha(blob),candidateSourceHashes={p:h for p,h in report['candidateSourceHashes'].items() if p in m['sourceHashes']}))
        for node in ET.fromstring(blob):
            tag=node.tag.rpartition('}')[2];require(tag not in {'error','configerror'},'no hidden XML analyzer error')
            if tag!='file':continue
            path='src/schubert-nk-'+node.get('name').split('/src/schubert-nk-',1)[1]
            if path not in m['sourceHashes']:continue
            require(report['candidateSourceHashes'][path]==m['sourceHashes'][path],'same current full Source')
            for item in node:
                require(item.tag.rpartition('}')[2]=='violation','only violation row')
                attrs=dict(item.attrib);key=path,wire(attrs);require(key not in diagnostics,'nonduplicate current diagnostic')
                d=dict(path=path,attributes=attrs,message=''.join(item.itertext()).strip())
                diagnostics[key]=dict(**d,rawDiagnosticRowSha256=data.sha(wire(d)),rawReportManifest=pair[0],rawReportManifestSha256=pair[1],rawReportSha256=data.sha(blob),rawReportSource=report['source'],rawCandidateSourceSha256=report['candidateSourceHashes'][path])
        verify(report['invocation'])
    def purpose(v):
        p=v['path'];a=v['attributes'];key=p,wire(a);require(key in diagnostics and v['rawDiagnostic']==diagnostics[key],'entire original XML diagnostic origin')
        require(v['currentSource']==SOURCE and v['sourceSha256']==m['sourceHashes'][p] and v['purposeKind']==KINDS[p.rsplit('/',1)[-1]][a['beginline']],'whole Source/current purpose')
        blob=(data.ROOT/p).read_bytes();require(data.sha(blob)==m['sourceHashes'][p],'actual Source byte')
        lines=blob.decode().splitlines(keepends=True);i,j=int(a['beginline'])-1,int(a['endline'])-1;c,e=int(a['begincolumn'])-1,int(a['endcolumn'])-1
        start=len((''.join(lines[:i])+lines[i][:c]).encode());end=len((''.join(lines[:j])+lines[j][:e]).encode());token=blob[start:end]
        require(v['canonicalSpanStart']==start and v['canonicalSpanEndExclusive']==end and token in {b'RuntimeException',b'Error'} and v['canonicalSpanSha256']==data.sha(token),'independent byte halfopen span')
        require(v['spanBasis']=='QUALIFIED_PMD_CHARACTER_TO_UTF8_BYTE_HALFOPEN_SPAN' and v['manualPurpose'] and v['residualRisk'],'explicit manual purpose and unresolved risk')
        require(v['productTestsExecuted']==0 and v['ptExecutionExempt'] is False and v['currentWholeCaseRefs']==[],'no PT invention')
    ids={v['id'] for v in rows};require(len(rows)==len(ids)==18,'18 unique warning rows')
    for v in rows:purpose(v)
    require(remaining==[v for v in queue if v['id'] not in ids] and len(remaining)==32 and len({(v['path'],v['attributes']['beginline']) for v in rows})==9,'exact queue and9catch')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    approved=(data.ROOT/design).read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['priorManifestSha256']==PRIOR[1] and v['priorQueueSha256']==prior['queueSha256'],'actual source/prior')
        require(v['sourceHashes']==m['sourceHashes'] and len(v['sourceHashes'])==4 and v['purposesSha256']==m['purposesSha256'] and v['queueSha256']==m['queueSha256'],'current four Source/artifact bindings')
        require(v['savedCurrentCoordinateReportReferences']==refs and v['coordinateToolManifestSha256']=='657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1' and v['approvedDesignSha256']==data.sha(approved),'current XML/tool/design bindings')
        require((v['newManualReviews'],v['newReferenceConnections'],v['combinedSelectedReferences'],v['combinedPurposeReviewed'],v['combinedPurposeOrReferenceRows'],v['remainingSelectedUnreferenced'],v['sourceCatchClauses'],v['directContractMetadataNegativeVectors'])==(18,0,1171,288,1459,32,9,12),'reviewed rows not runtime counts')
        require(v['productTestsExecuted']==v['externalActions']==v['rawSuppressed']==v['newAccepted']==0 and v['actualViolationCount'] is v['firstEverSemanticReasons'] is v['effortPercent'] is None,'no invented execution/violations/novelty/cost')
        require(all(v[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']),'no silent qualification')
    contract(m);negative=[]
    for key,value in [('actualExit',True),('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('sourceHashes',{}),('purposesSha256','0'*64),('queueSha256','0'*64),('savedCurrentCoordinateReportReferences',[]),('coordinateToolManifestSha256','0'*64),('approvedDesignSha256','0'*64),('newManualReviews',0),('newReferenceConnections',18),('combinedSelectedReferences',1189),('combinedPurposeReviewed',270),('combinedPurposeOrReferenceRows',1441),('remainingSelectedUnreferenced',0),('sourceCatchClauses',18),('directContractMetadataNegativeVectors',0),('productTestsExecuted',18),('externalActions',1),('rawSuppressed',18),('newAccepted',1),('actualViolationCount',0),('ptExecutionExempt',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false manifest '+key)
    byte_negative=[]
    for key,value in [('canonicalSpanStart',rows[0]['canonicalSpanStart']+1),('canonicalSpanStart',rows[0]['canonicalSpanStart']-1),('canonicalSpanEndExclusive',rows[0]['canonicalSpanEndExclusive']+1),('spanBasis','OLD_RAW_COORDINATE')]:
        bad=copy.deepcopy(rows[0]);bad[key]=value
        try:purpose(bad)
        except ValueError:byte_negative.append(key)
        else:raise ValueError('false byte span')
    for v in (m,prior):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],
        independentMetadataNegativeVectors=len(negative),negativeLabels=negative,utf8ByteNegativeVectors=len(byte_negative),utf8ByteNegativeLabels=byte_negative,
        sourceFiles=4,purposeRows=18,sourceCatchClauses=9,remaining=32,currentCoordinateXmlReports=2,productTestsExecuted=0,sourceChanged=False,
        actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
