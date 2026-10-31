"""Independent saved reason-schema/spans/source/remaining join, preserving historical dispositions."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
PARENT='PG16112-batch-session-saved44-reference-v1'
PIN='0425538b6334d0ae7be11ef628a76bbfaf4efcfe182c5a5536d56b0810114966'
OUT=data.BASE/'PG16114-batch-session-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    old=read('PG11580-batch-session-source-review-v1','198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc')
    old_post=read('PG11582-batch-session-source-review-post-v1','7f2130d91fa6fe4e4b1b3846455218702099d19effb32b6e6d361219300c57a3')
    prior=read('PG16106-jms-three-saved-purpose-reference-v1','4dccb138c4c39be4fd57e1f14b07d08fe0ab5f228a5894adb9b0f6b121c6ee0b')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    review=data.read_checked(data.BASE/'PG11580-batch-session-source-review-v1/review.json',old['reviewSha256'])
    rows=review['rows']
    queue=data.read_checked(data.BASE/'PG16106-jms-three-saved-purpose-reference-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observed=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    observations={v['staticObservationId']:v for v in observed}
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(old['source']==old_post['source']==OLD_SOURCE and prior['source']==SOURCE
            and all(v['actualExit']==0 for v in (old,old_post,prior,obs,p))
            and old_post['primaryManifestSha256']==p['oldReviewManifestSha256']=='198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc','all historical exact refs')
    require(p['sourceHashes']==review['mainSourceHashes'] and len(p['sourceHashes'])==5
            and all(data.sha((data.ROOT/f).read_bytes())==h for f,h in p['sourceHashes'].items()),'reuse five exact source bytes')
    expected=[];extras=Counter()
    for current in queue:
        matches=[(i,v) for i,v in enumerate(rows) if (v['path'],v['sourceSha256'],v['attributes'])==(current['path'],current['sourceSha256'],current['attributes'])]
        if not matches:continue
        require(len(matches)==1,'one historical signature')
        ordinal,oldrow=matches[0];actual=observations[current['id']]
        require(oldrow['source']==OLD_SOURCE and oldrow['rawWarningRetained'] is True
                and oldrow['oldRuntimeReassigned'] is oldrow['ptExecutionExempt'] is False
                and oldrow['productTestsExecuted']==0 and oldrow['coverage'] is None
                and oldrow['disposition']=='REQUIRED_CONTRACT' and oldrow['reason'],'retained reason schema not old runtime')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['path']==current['path'] and actual['attributes']==current['attributes']
                and data.sha(actual['message'].encode())==oldrow['diagnosticTextSha256'],'same current diagnostic, explicit schema')
        body=(data.ROOT/current['path']).read_text();a=current['attributes'];lines=body.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        require(start<stop<len(body) and data.sha(body[start:stop+1].encode())==oldrow['currentSpanSha256'],'independent full old extent')
        suffix=repr(body[stop]);extras[suffix]+=1
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            legacyExtentSha256=oldrow['currentSpanSha256'],legacyExtraCharacter=suffix,
            legacyExtentIsCanonicalPmdToken=False,spanSchema='CANONICAL_EXCLUSIVE_AND_PRESERVED_FIXED_EXPORTER_PLUS_ONE',
            oldFindingId=oldrow['id'],oldRowOrdinal=ordinal,oldRowSha256=data.sha(wire(oldrow).encode()),
            oldReason=oldrow['reason'],oldDisposition=oldrow['disposition'],oldCurrentSourceFacts=oldrow['currentSourceFacts'],
            diagnosticMessageSha256=oldrow['diagnosticTextSha256'],
            meaning='EXISTING_STATIC_REASON_REFERENCE_ONLY_NOT_NEW_DISPOSITION_OR_RUNTIME'))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==44 and len(remaining)==623
            and extras==Counter({"' '":31,"'\\n'":7,"';'":6}),'complete44/623 exact known suffixes')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['staticReviewSource']==OLD_SOURCE,'source and exit')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],
                 m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'],m['oldReauthenticatedReasons'],m['oldIndividualDispositions'])==
                 (44,772,96,868,623,42,2),'historical and current count domains')
        require(m['priorFullSourceReviewReused'] is True and m['newWholeSourceTextReviewClaimed'] is False
                and m['legacyExtentIsCanonicalPmdToken'] is False
                and m['legacyExtraCharacters']=={'SPACE':31,'LF':7,'SEMICOLON':6},'no invented new review or token')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','newIndividualDispositions','rawSuppressed','productTestsExecuted','oldProductToolsReexecuted','externalActions','newAccepted'))
                and all(m[k] is False for k in ('oldRuntimeTransferred','sourceChanged','formalUpdated','wholeF03Accepted','whole451Accepted'))
                and m['actualViolationCount'] is m['effortPercent'] is None,'no inferred quality/runtime')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'all old fields/facts/extent and current remaining rows')
    contract(p,refs,rest);labels=[]
    vectors=[('source','source',OLD_SOURCE),('old-source','staticReviewSource',SOURCE),
        ('refs','newReferenceConnections',42),('sum','combinedSelectedReferences',770),('purpose','combinedPurposeReviewed',140),
        ('remaining','remainingSelectedUnreferenced',0),('old-judgments','oldIndividualDispositions',0),
        ('new-judgments','newIndividualDispositions',2),('new-review','newWholeSourceTextReviewClaimed',True),
        ('canonical','legacyExtentIsCanonicalPmdToken',True),('manual','newManualReviews',44),
        ('suppress','rawSuppressed',44),('PT','productTestsExecuted',1),('replay','oldProductToolsReexecuted',1),
        ('runtime','oldRuntimeTransferred',True),('formal','formalUpdated',True),('accepted','newAccepted',1),
        ('effort','effortPercent',100),('violation','actualViolationCount',0),('reuse','priorFullSourceReviewReused',False)]
    for label,k,v in vectors:
        bad=copy.deepcopy(p);bad[k]=v
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false session reference '+label)
    for label,k,v in [('witness','oldRowSha256','0'*64),('reason','oldReason','changed'),
                      ('span','canonicalSpanSha256','0'*64),('oldextent','legacyExtentSha256','0'*64),
                      ('facts','oldCurrentSourceFacts',{'forged':True})]:
        bad=copy.deepcopy(refs);bad[0][k]=v
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false row '+label)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26 independent metadata checks')
    for v in (old,old_post,prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,
        negativeLabels=labels,occurrences=44,combinedPurposeOrReferenceRows=868,remainingSelectedUnreferenced=623,
        newManualReviews=0,newIndividualDispositions=0,oldIndividualDispositions=2,productTestsExecuted=0,
        oldRuntimeTransferred=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
