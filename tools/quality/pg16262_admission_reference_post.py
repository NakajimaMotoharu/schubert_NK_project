"""Independent inherited-reason-only/None contract; no fabricated facts or DB execution."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16261_admission_saved12_reference_v2 import SOURCE,OLD_SOURCE,REVIEW,POST,PRIOR,OBS,RAW,FIELDS,read

PIN='17e8fc659e467506b6bbb5b7c01eb773f7f7d0166f9182326323df0de2845b31'
OUT=data.BASE/'PG16262-admission-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,old,post,prior,obs=[read(v) for v in [('PG16261-admission-saved12-reference-v2',PIN),REVIEW,POST,PRIOR,OBS]]
    require(all(v['actualExit']==0 for v in (m,old,post,prior,obs)) and m['source']==prior['source']==obs['source']==SOURCE
            and old['source']==post['source']==OLD_SOURCE and post['primaryManifestSha256']==REVIEW[1] and post['metadataNegativeVectors']==14,'fixed original and current qualification')
    review=data.read_checked(data.BASE/REVIEW[0]/'review.json',old['reviewSha256']);rows=review['rows'];require(len(rows)==19 and all(set(v)==FIELDS for v in rows),'actual old schema')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256']);by_id={v['id']:v for v in queue}
    links=data.read_checked(data.BASE/'PG16261-admission-saved12-reference-v2/references.json',m['referencesSha256'])
    after=data.read_checked(data.BASE/'PG16261-admission-saved12-reference-v2/remaining-selected-review-queue.json',m['queueSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    actual=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);actual={v['staticObservationId']:v for v in actual}
    hashes={}
    def row_contract(v):
        current=by_id[v['id']];saved=rows[v['oldRowOrdinal']]
        require(wire(v['savedReviewRow'])==wire(saved) and v['oldRowSha256']==data.sha(wire(saved).encode())
                and all(v[k]==x for k,x in current.items()),'all original nested/current attrs preserved')
        require(saved['path']==current['path'] and saved['sourceSha256']==current['sourceSha256'] and saved['attributes']==current['attributes']
                and saved['source']==OLD_SOURCE and saved['historicalReasonWasBlank'] is False and saved['reasonOrigin']=='PG6048'
                and saved['reason'] and saved['currentSourceFacts'] is None and saved['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING','inherited existing reason, no additional facts')
        require(v['oldStandaloneRuleFieldAvailable'] is v['oldAdditionalSourceFactsAvailable'] is v['oldScopeFingerprintsReparsed'] is v['historicalDesignsReaccepted'] is v['currentRuntimeQualification'] is False,'explicit missing/None/old scope contracts')
    for v in links:
        row_contract(v);current=by_id[v['id']];saved=rows[v['oldRowOrdinal']];origin=raw[saved['id']];observed=actual[v['id']]
        require(v['oldManifestSha256']==REVIEW[1] and v['oldPostManifestSha256']==POST[1] and v['oldReviewSha256']==old['reviewSha256']
                and v['staticReviewSource']==OLD_SOURCE and v['currentSource']==SOURCE,'all source/provenance links')
        require(origin['rowSha256']==saved['originalRowSha256']==v['originalDiagnosticRowSha256'] and origin['path']==current['path']
                and origin['attributes']==current['attributes'] and origin['inputSha256']==current['sourceSha256']
                and observed['currentSource']==SOURCE and observed['attributes']==current['attributes'] and observed['message']==origin['message']
                and data.sha(origin['message'].encode())==saved['diagnosticTextSha256']==v['diagnosticMessageSha256'],'full raw/current diagnostic')
        require(data.sha((data.ROOT/current['path']).read_bytes())==current['sourceSha256'],'whole Source same bytes');hashes[current['path']]=current['sourceSha256']
    ids={v['id'] for v in links};expected=[v for v in queue if v['id'] not in ids]
    require(len(links)==len(ids)==12 and len(hashes)==2 and Counter(v['rule'] for v in links)=={'AvoidCatchingGenericException':8,'DoNotThrowExceptionInFinally':4}
            and wire(after)==wire(expected) and len(after)==201 and not any(v['rule']=='DoNotThrowExceptionInFinally' for v in after),'derived exact domains/remainder')
    row_labels=[]
    for key,value in [('currentSourceFacts',{'invented':True}),('reasonOrigin','INVENTED')]:
        bad=copy.deepcopy(links[0]);bad['savedReviewRow'][key]=value
        try:row_contract(bad)
        except ValueError:row_labels.append(key)
        else:raise ValueError('old facts fabricated')
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['staticReviewSource']==OLD_SOURCE
                and value['oldManifestSha256']==REVIEW[1] and value['oldPostManifestSha256']==POST[1] and value['oldReviewSha256']==old['reviewSha256']
                and value['priorManifestSha256']==PRIOR[1] and value['priorQueueSha256']==prior['queueSha256'],'same current and old chain')
        require(value['sourceHashes']==hashes and value['historicalApprovedDesigns']==review['approvedDesigns']
                and value['historicalCurrentSourceReviewFacts']==review['currentSourceReviewFacts'],'original historical design and root aggregate unchanged')
        require((value['oldReviewed'],value['oldOtherRowsOutsideCurrentQueue'],value['newReferenceConnections'],value['combinedSelectedReferences'],
                value['combinedPurposeReviewed'],value['combinedPurposeOrReferenceRows'],value['remainingSelectedUnreferenced'])==(19,7,12,1171,119,1290,201),'all counts')
        require(value['referencesSha256']==m['referencesSha256'] and value['queueSha256']==m['queueSha256'],'actual files')
        require(all(value[k] is False for k in ['oldStandaloneRuleFieldAvailable','oldAdditionalSourceFactsAvailable','oldScopeFingerprintsReparsed','historicalDesignsReaccepted',
                'currentRuntimeQualification','oldRuntimeTransferred','sourceChanged','ptExecutionExempt','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and value['newManualReviews']==value['productTestsExecuted']==value['oldProductToolsReexecuted']==value['rawSuppressed']==value['externalActions']==value['newAccepted']==0
                and value['actualViolationCount'] is value['effortPercent'] is None,'not current execution or acceptance')
    contract(m);labels=[]
    for key,value in [('source','OLD'),('staticReviewSource',SOURCE),('oldManifestSha256','0'*64),('oldPostManifestSha256','0'*64),
        ('oldReviewSha256','0'*64),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('sourceHashes',{}),('historicalApprovedDesigns',{}),
        ('oldReviewed',12),('oldOtherRowsOutsideCurrentQueue',0),('newReferenceConnections',13),('combinedSelectedReferences',1159),
        ('combinedPurposeReviewed',131),('combinedPurposeOrReferenceRows',1278),('remainingSelectedUnreferenced',213),
        ('oldStandaloneRuleFieldAvailable',True),('oldAdditionalSourceFactsAvailable',True),('oldScopeFingerprintsReparsed',True),
        ('historicalDesignsReaccepted',True),('currentRuntimeQualification',True),('newManualReviews',12),('productTestsExecuted',12),
        ('oldRuntimeTransferred',True),('formalUpdated',True),('effortPercent',100)]:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Admission reference '+key)
    require(len(labels)==26 and len(row_labels)==2,'finite26+2')
    for v in (m,old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        metadataNegativeVectors=26,negativeLabels=labels,rowSchemaNegativeVectors=2,rowSchemaNegativeLabels=row_labels,
        referenceRows=12,sourcePrograms=2,oldAdditionalSourceFactsAvailable=False,oldStandaloneRuleFieldAvailable=False,
        combinedSelectedReferences=1171,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1290,remainingSelectedUnreferenced=201,
        newManualReviews=0,productTestsExecuted=0,currentRuntimeQualification=False,historicalDesignsReaccepted=False,
        newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
