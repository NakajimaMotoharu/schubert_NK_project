"""Independent exact fullattrs/original row and historical controls proof, without Product execution."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16254_monitor_saved15_reference import SOURCE,PRIOR,OBS,RAW,FAMILIES,FIELDS,read

PIN='11de0e98f6d03ac9bf4e6f7bf9871f956f4a987371c8279e3f0657bc301ed7f3'
OUT=data.BASE/'PG16256-monitor-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,prior,obs=[read(v) for v in [('PG16254-monitor-saved15-reference-v1',PIN),PRIOR,OBS]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (m,prior,obs)),'genuine current source')
    links=data.read_checked(data.BASE/'PG16254-monitor-saved15-reference-v1/references.json',m['referencesSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256']);current={v['id']:v for v in queue}
    after=data.read_checked(data.BASE/'PG16254-monitor-saved15-reference-v1/remaining-selected-review-queue.json',m['queueSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    actual=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);actual={v['staticObservationId']:v for v in actual}
    old={};selected=Counter();hashes={}
    for name,pin,post_name,post_pin,count,n,neg in FAMILIES:
        a,b=[read(v) for v in [(name,pin),(post_name,post_pin)]]
        require(a['actualExit']==b['actualExit']==0 and a['source']==b['source'] and b['reviewManifestSha256']==pin and b['metadataNegativeVectors']==neg,'fixed original post chain')
        review=data.read_checked(data.BASE/name/'review.json',a['reviewSha256']);require(len(review['rows'])==count and all(set(v)==FIELDS for v in review['rows']),'all original actual fields')
        old[name]=(a,b,review['rows'],pin,post_pin,n);verify(a['invocation']);verify(b['invocation'])
    for v in links:
        cur=current[v['id']];a,b,rows,pin,post_pin,n=old[v['oldManifestName']];row=rows[v['oldRowOrdinal']]
        require(all(v[k]==x for k,x in cur.items()) and wire(v['savedReviewRow'])==wire(row)
                and v['oldRowSha256']==data.sha(wire(row).encode()),'all current and saved nested fields exact')
        require(v['oldManifestSha256']==pin and v['oldPostManifestSha256']==post_pin and v['oldReviewSha256']==a['reviewSha256']
                and v['staticReviewSource']==row['source']==a['source'],'exact old references')
        require(row['path']==cur['path'] and row['sourceSha256']==cur['sourceSha256'] and row['attributes']==cur['attributes']
                and row['rule']==cur['rule'] and row['currentWholeJoinPending'] is True and row['oldRuntimeReassigned'] is False
                and row['productTestsExecutedByReview']==row['newAccepted']==0 and row['reason'] and row['controls'],'whole source context, not old runtime')
        original=raw[row['id']];observation=actual[v['id']]
        require(original['path']==cur['path'] and original['attributes']==cur['attributes'] and original['inputSha256']==cur['sourceSha256']
                and original['rowSha256']==row['originalRowSha256']==v['originalDiagnosticRowSha256']
                and observation['attributes']==cur['attributes'] and observation['currentSource']==SOURCE and observation['message']==original['message']
                and data.sha(original['message'].encode())==v['diagnosticMessageSha256'],'all raw/current diagnostics')
        require(data.sha((data.ROOT/cur['path']).read_bytes())==cur['sourceSha256'],'whole Source bytes')
        require(v['oldFullAttributesAvailable'] is True and all(v[k] is False for k in ['oldDiagnosticMessageFieldAvailable','oldScopeFingerprintsReparsed',
                'currentRuntimeQualification','currentDesignApplicabilityReaccepted','scopeGeneralized']),'old scope/limit not promoted')
        selected[v['oldManifestName']]+=1;hashes[cur['path']]=cur['sourceSha256']
    ids={v['id'] for v in links};expected=[v for v in queue if v['id'] not in ids]
    require(len(links)==len(ids)==15 and len(hashes)==6 and all(selected[name]==v[5] for name,v in old.items()),'all fixed three family 2+8+5')
    require(Counter(v['rule'] for v in links)=={'AvoidSynchronizedStatement':11,'AvoidCatchingGenericException':4}
            and wire(after)==wire(expected) and len(after)==213 and not any(v['rule']=='AvoidSynchronizedStatement' for v in after),'exact remainder, not whole gate')
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['priorManifestSha256']==PRIOR[1]
                and value['priorQueueSha256']==prior['queueSha256'] and value['originalRawJsonSha256']==RAW,'same source inputs')
        require((value['newReferenceConnections'],value['combinedSelectedReferences'],value['combinedPurposeReviewed'],value['combinedPurposeOrReferenceRows'],
                value['remainingSelectedUnreferenced'],value['oldReviewed'],value['oldOtherRowsOutsideCurrentQueue'])==(15,1159,119,1278,213,48,33),'derived exact domains')
        require(value['sourceHashes']==hashes and len(value['oldFamilies'])==3 and value['oldFullAttributesAvailable'] is True,'all full Source contexts')
        require(value['referencesSha256']==m['referencesSha256'] and value['queueSha256']==m['queueSha256'],'actual file hashes')
        require(all(value[k] is False for k in ['oldScopeFingerprintsReparsed','currentRuntimeQualification','currentDesignApplicabilityReaccepted','scopeGeneralized',
                'oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and value['newManualReviews']==value['productTestsExecuted']==value['oldProductToolsReexecuted']==value['rawSuppressed']==value['externalActions']==value['newAccepted']==0
                and value['actualViolationCount'] is value['effortPercent'] is None,'not new manual/runtime/gate acceptance')
    contract(m);labels=[]
    vectors=[('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('originalRawJsonSha256','0'*64),
        ('newReferenceConnections',16),('combinedSelectedReferences',1144),('combinedPurposeReviewed',134),('combinedPurposeOrReferenceRows',1263),
        ('remainingSelectedUnreferenced',228),('oldReviewed',15),('oldOtherRowsOutsideCurrentQueue',0),('sourceHashes',{}),('oldFamilies',[]),
        ('oldFullAttributesAvailable',False),('referencesSha256','0'*64),('queueSha256','0'*64),('oldScopeFingerprintsReparsed',True),
        ('currentRuntimeQualification',True),('currentDesignApplicabilityReaccepted',True),('scopeGeneralized',True),('newManualReviews',15),
        ('productTestsExecuted',15),('oldRuntimeTransferred',True),('wholeF03Accepted',True),('formalUpdated',True),('effortPercent',100)]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false monitor reference '+key)
    require(len(labels)==26,'finite26')
    for v in (m,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        metadataNegativeVectors=26,negativeLabels=labels,referenceRows=15,sourcePrograms=6,fullAttributes=True,
        combinedSelectedReferences=1159,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1278,remainingSelectedUnreferenced=213,
        newManualReviews=0,productTestsExecuted=0,oldScopeFingerprintsReparsed=False,currentRuntimeQualification=False,
        currentDesignApplicabilityReaccepted=False,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
