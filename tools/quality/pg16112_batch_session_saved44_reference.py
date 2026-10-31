"""Saved two-session reason-schema reference, exact bytes/diagnostics/dual spans only."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OLD=('PG11580-batch-session-source-review-v1','198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc')
OLD_POST=('PG11582-batch-session-source-review-post-v1','7f2130d91fa6fe4e4b1b3846455218702099d19effb32b6e6d361219300c57a3')
PRIOR=('PG16106-jms-three-saved-purpose-reference-v1','4dccb138c4c39be4fd57e1f14b07d08fe0ab5f228a5894adb9b0f6b121c6ee0b')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16112-batch-session-saved44-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def key(v):
    return json.dumps([v['path'],v['sourceSha256'],v['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,post,prior,obs=[read(v) for v in (OLD,OLD_POST,PRIOR,OBS)]
    require(all(v['actualExit']==0 for v in (old,post,prior,obs))
            and old['source']==post['source']==OLD_SOURCE and prior['source']==obs['source']==SOURCE
            and post['primaryManifestSha256']==OLD[1] and post['metadataNegativeVectors']==15,'qualified historical source-only proof')
    require(old['reviewed']==44 and old['reauthenticatedHistoricalReasons']==42 and old['newIndividualDispositions']==2
            and old['productTestsExecuted']==0 and old['historicalRuntimeImportedAsCurrent'] is False and old['coverage'] is None,'old judgments remain old')
    review=data.read_checked(data.BASE/OLD[0]/'review.json',old['reviewSha256']);rows=review['rows']
    required={'attributes','coverage','currentSourceFacts','currentSpanSha256','diagnosticTextSha256','disposition','id',
              'oldRuntimeReassigned','originalRowSha256','path','productTestsExecuted','ptExecutionExempt','rawWarningRetained','reason','source','sourceSha256'}
    require(len(rows)==44 and all(required<=set(v) for v in rows),'explicit saved reason schema')
    require(len(review['mainSourceHashes'])==5 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['mainSourceHashes'].items()),'reuse prior full review of unchanged five sources, not new fulltext review')
    require(data.sha((data.ROOT/'tools/quality/pg11579_session_recheck_source_facts.py').read_bytes())==old['factExtractorSha256']=='fc31c38e0d4f7e6d5ad405ba73948347f003ecd86081ce09f9bbe406d543ce34'
            and data.sha((data.ROOT/'tools/quality/pg11569_four_repository_scope_facts.py').read_bytes())=='372375bf808bf1662391d1658aab99ef6886895d75db882dca812fa228964268','frozen historical fact/span schema')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==667 and prior['combinedSelectedReferences']==728 and prior['combinedPurposeReviewed']==96,'prior current domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    require(all({'sourceSha256','currentSource','path','attributes','message','staticObservationId'}<=set(v) for v in observed),'current observation schema')
    observed={v['staticObservationId']:v for v in observed}
    saved={key(v):(i,v) for i,v in enumerate(rows)}
    require(len(saved)==44,'all44 signatures unique')
    selected=[v for v in queue if key(v) in saved]
    require(len(selected)==len({v['id'] for v in selected})==44,'all complete occurrences')
    links=[];extras=Counter()
    for current in selected:
        ordinal,row=saved[key(current)];actual=observed[current['id']]
        require(row['source']==OLD_SOURCE and row['rawWarningRetained'] is True and row['oldRuntimeReassigned'] is row['ptExecutionExempt'] is False
                and row['productTestsExecuted']==0 and row['coverage'] is None and row['reason'] and row['disposition']=='REQUIRED_CONTRACT','original static-only row unchanged')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['path']==current['path'] and actual['attributes']==current['attributes']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'whole diagnostic source/message')
        text=(data.ROOT/current['path']).read_text();start,stop,token=span(text,current['attributes'])
        require(stop<len(text) and text[stop] in ' \n;' and data.sha(text[start:stop+1].encode())==row['currentSpanSha256'],'explicit legacy plus-one extent')
        extras[repr(text[stop])]+=1
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            legacyExtentSha256=row['currentSpanSha256'],legacyExtraCharacter=repr(text[stop]),
            legacyExtentIsCanonicalPmdToken=False,spanSchema='CANONICAL_EXCLUSIVE_AND_PRESERVED_FIXED_EXPORTER_PLUS_ONE',
            oldFindingId=row['id'],oldRowOrdinal=ordinal,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),
            oldReason=row['reason'],oldDisposition=row['disposition'],oldCurrentSourceFacts=row['currentSourceFacts'],
            diagnosticMessageSha256=row['diagnosticTextSha256'],
            meaning='EXISTING_STATIC_REASON_REFERENCE_ONLY_NOT_NEW_DISPOSITION_OR_RUNTIME'))
    require(extras==Counter({"' '":31,"'\\n'":7,"';'":6}),'all exact legacy suffixes')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    authority=review['approvedDesign'];path=authority['path'];body=(data.ROOT/path).read_bytes()
    require(data.sha(body)==authority['sha256'] and subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)==body,'current approved design same as saved static authority')
    for v in (old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,staticReviewSource=OLD_SOURCE,invocation=invocation,
        oldReviewManifestSha256=OLD[1],oldPostManifestSha256=OLD_POST[1],oldReviewSha256=old['reviewSha256'],
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=review['mainSourceHashes'],approvedDesign=authority,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=44,combinedSelectedReferences=772,combinedPurposeReviewed=96,
        combinedPurposeOrReferenceRows=868,remainingSelectedUnreferenced=623,
        oldReauthenticatedReasons=42,oldIndividualDispositions=2,newManualReviews=0,newIndividualDispositions=0,
        priorFullSourceReviewReused=True,newWholeSourceTextReviewClaimed=False,legacyExtentIsCanonicalPmdToken=False,
        legacyExtraCharacters={'SPACE':31,'LF':7,'SEMICOLON':6},rawSuppressed=0,actualViolationCount=None,
        productTestsExecuted=0,oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,
        externalActions=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
