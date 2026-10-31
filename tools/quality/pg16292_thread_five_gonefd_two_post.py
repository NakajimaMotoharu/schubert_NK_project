"""Independent saved XML/current raw coordinate seven-purpose check, no product execution."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16291-thread-five-gonefd-two-purpose-v2','657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1')
PRIOR=('PG16266-release-interrupt-two-purpose-v1','9afbe28a7e0fb0197b81c4a2da781a55b9d81dbccf41577ec0f60bc448434cd7')
REPORTS={'PG13505-main-assignment-seven-v1':'aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf',
         'PG13534-main-assignment-final-four-v1':'36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda'}
PREFIX='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/'
OUT=data.BASE/'PG16292-thread-five-gonefd-two-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,prior=[read(v) for v in (RAW,PRIOR)]
    purposes=data.read_checked(data.BASE/RAW[0]/'purposes.json',m['purposesSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    remaining=data.read_checked(data.BASE/RAW[0]/'remaining-selected-review-queue.json',m['queueSha256'])
    records={v['id']:v for v in purposes};require(len(purposes)==len(records)==7,'seven unique')
    expected_sites={('platform/FixedUnitCgroupNamespace.java',50):'INTERRUPTION_READ_BEFORE_CONTEXT',('platform/FixedUnitCgroupNamespace.java',53):'INTERRUPTION_READ_AFTER_CONTEXT_AND_UID',
                    ('file/MorningPermitPublication.java',75):'CAPTURE_CONSTRUCTION_THREAD_ID',('file/MorningPermitPublication.java',242):'COMPARE_OWNER_THREAD_ID',('file/MorningPermitPublication.java',309):'CLEAR_INTERRUPTION_INSIDE_INDEFINITE_RETENTION',
                    ('platform/MorningCaddyReadiness.java',404):'DISAPPEARED_FD_NOT_OWNED_EVIDENCE',('platform/MorningServiceReadiness.java',243):'DISAPPEARED_FD_NOT_OWNED_EVIDENCE'}
    require({(v['path'].removeprefix(PREFIX),int(v['attributes']['beginline'])) for v in purposes}==set(expected_sites),'independent seven selected sites')
    reports={k:read((k,v)) for k,v in REPORTS.items()};xml_rows={}
    for folder,witness in reports.items():
        blob=(data.BASE/folder/'pmd.xml').read_bytes();require(data.sha(blob)==witness['reports']['pmd'] and witness['actualExit']==witness['productTestsExecuted']==0,'original saved XML and static only')
        found=[]
        for node in ET.fromstring(blob):
            if node.tag.rpartition('}')[2]!='file':continue
            name=node.get('name');path='src/schubert-nk-'+name.split('/src/schubert-nk-',1)[1]
            if path not in m['sourceHashes']:continue
            for item in node:found.append(dict(path=path,attributes=dict(item.attrib),message=''.join(item.itertext()).strip()))
        xml_rows[folder]=found;verify(witness['invocation'])
    def purpose_contract(v):
        path=v['path'];attrs=v['attributes'];short=path.removeprefix(PREFIX);kind=expected_sites[short,int(attrs['beginline'])]
        require(v['purposeKind']==kind and v['currentSource']==SOURCE and v['rawReportManifest'] in REPORTS,'explicit purpose/current source/origin')
        folder=v['rawReportManifest'];witness=reports[folder]
        require(v['rawReportManifestSha256']==REPORTS[folder] and v['rawReportSha256']==witness['reports']['pmd']
                and v['rawCandidateSourceSha256']==witness['candidateSourceHashes'][path]==v['sourceSha256']==m['sourceHashes'][path],'exact selected candidate bytes, not legacy run qualification')
        matching=[r for r in xml_rows[folder] if r['path']==path and r['attributes']==attrs]
        require(len(matching)==1,'current XML exact attrs, no coordinate erasure');r=matching[0]
        require(v['originalDiagnosticSha256']==data.sha(r['message'].encode()) and v['savedXmlDiagnosticRowSha256']==data.sha(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),'raw diagnostic metadata retained')
        body=(data.ROOT/path).read_bytes();require(data.sha(body)==m['sourceHashes'][path],'whole current Source hash')
        lines=body.decode().splitlines(keepends=True);first,last=int(attrs['beginline'])-1,int(attrs['endline'])-1
        left,right=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
        a=len((''.join(lines[:first])+lines[first][:left]).encode());b=len((''.join(lines[:last])+lines[last][:right]).encode())
        require(v['canonicalSpanStart']==a and v['canonicalSpanEndExclusive']==b and v['canonicalSpanSha256']==data.sha(body[a:b]),'independent raw halfopen byte conversion')
        token=body[a:b].decode();require(token=='Thread' if attrs['rule']=='DoNotUseThreads' else token.startswith('catch (NoSuchFileException gone) {') and token.endswith('}'),'reported six-byte Thread or exact missing-only catch')
        retained=kind.startswith('CLEAR_')
        require(v['interruptStateClearingAtSite'] is retained and v['indefiniteRetention'] is retained and v['externalDeadlineProven'] is False,'retention/clear must not be called read-only or complete')
        require(v['productTestsExecuted']==0 and v['ptExecutionExempt'] is False and v['currentWholeCaseRefs']==[] and bool(v['manualPurpose']) and bool(v['residualRisk']),'no runtime/omitted risk')
    for v in purposes:purpose_contract(v)
    require(remaining==[v for v in queue if v['id'] not in records] and len(remaining)==192 and all(v['rule']=='AvoidCatchingGenericException' for v in remaining),'exact remaining ordered queue')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['priorManifestSha256']==PRIOR[1] and v['priorQueueSha256']==prior['queueSha256'],'genuine current source and prior')
        require(v['purposesSha256']==m['purposesSha256'] and v['queueSha256']==m['queueSha256'] and v['sourceHashes']==m['sourceHashes'] and v['savedCurrentCoordinateReportReferences']==m['savedCurrentCoordinateReportReferences'],'all public bindings')
        require((v['newManualReviews'],v['newReferenceConnections'],v['combinedSelectedReferences'],v['combinedPurposeReviewed'],v['combinedPurposeOrReferenceRows'],v['remainingSelectedUnreferenced'],v['directContractMetadataNegativeVectors'])==(7,0,1171,128,1299,192,8),'separate exact manual/ref/metadata counts')
        require(v['productTestsExecuted']==v['externalActions']==v['rawSuppressed']==v['newAccepted']==0 and v['actualViolationCount'] is None and v['effortPercent'] is None,'not PT or actual violation resolution')
        require(all(v[k] is False for k in ['ptExecutionExempt','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']),'no unstated qualification')
    contract(m);labels=[]
    vectors=[('actualExit',True),('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('purposesSha256','0'*64),('queueSha256','0'*64),('sourceHashes',{}),('savedCurrentCoordinateReportReferences',[]),('newManualReviews',0),('newReferenceConnections',7),('combinedSelectedReferences',1178),('combinedPurposeReviewed',121),('combinedPurposeOrReferenceRows',1292),('remainingSelectedUnreferenced',0),('directContractMetadataNegativeVectors',0),('productTestsExecuted',7),('externalActions',1),('rawSuppressed',7),('newAccepted',1),('actualViolationCount',0),('effortPercent',100),('ptExecutionExempt',True),('sourceChanged',True),('wholeF03Accepted',True),('whole451Accepted',True),('formalUpdated',True)]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false purpose manifest '+key)
    row_neg=[]
    for key,value in [('rawReportManifestSha256','0'*64),('rawReportSha256','0'*64),('rawCandidateSourceSha256','0'*64),('canonicalSpanEndExclusive',0)]:
        bad=copy.deepcopy(purposes[0]);bad[key]=value
        try:purpose_contract(bad)
        except ValueError:row_neg.append(key)
        else:raise ValueError('false raw XML/coordinate binding')
    for v in (m,prior):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],independentMetadataNegativeVectors=len(labels),negativeLabels=labels,
        rawOriginAndCoordinateNegativeVectors=len(row_neg),rawOriginAndCoordinateNegativeLabels=row_neg,sourceFiles=4,purposeRows=7,remaining=192,newManualReviews=7,
        productTestsExecuted=0,sourceChanged=False,wholeF03Accepted=False,whole451Accepted=False,actualViolationCount=None,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
