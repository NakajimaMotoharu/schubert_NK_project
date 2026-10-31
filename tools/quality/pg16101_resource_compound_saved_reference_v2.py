"""Reuse exact historical static purposes with explicit span/multiplicity schemas; no Product."""
from collections import Counter, defaultdict
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='1be156b6ebb139713db31a561b8b024972975471'
OLD=('PG12432-resource-compound-context-v1','20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de')
OLD_POST=('PG12434-resource-compound-context-post-v1','7457fb8e17f085e7022cca8aad1953eb61c5f3ae128d137cde2be6ba03f30ce3')
PRIOR=('PG16075-four-repository-saved-reference-join-v2','44b10dd7416d940b650c77325dd48e195fdf2dacc749fa98e75b063464bc874d')
OUT=data.BASE/'PG16101-resource-compound-saved-reference-v2'
EXPORTER='tools/quality/pg12432_resource_compound_context.py'
EXPORTER_SHA='7707736ffe8dd37399377797faf20fe233c8ce258d336367f8d90b610768b147'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(row):
    return json.dumps([row['path'],row['sourceSha256'],row['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    require(data.sha((data.ROOT/'tools/quality/pg16100_resource_compound_saved_reference.py').read_bytes())=='b5a4af8ba6e4fcacc9704fab52afc7c029e12cb4a232de937506840039865b45','old failed consumer frozen')
    old,post,prior=[read(p) for p in (OLD,OLD_POST,PRIOR)]
    require(old['actualExit']==post['actualExit']==prior['actualExit']==0
            and old['source']==post['source']==OLD_SOURCE and prior['source']==SOURCE
            and post['reviewManifestSha256']==OLD[1] and post['metadataNegativeVectors']==25,'same historical static proof')
    require(data.sha((data.ROOT/EXPORTER).read_bytes())==EXPORTER_SHA,'frozen exporter plus-one convention')
    require(old['productTestsExecuted']==0 and old['coverage'] is None and old['sourceCodeChanged'] is False,'not old runtime')
    review=data.read_checked(data.BASE/OLD[0]/'review.json',old['reviewSha256'])
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(review['rows'])==46 and review['source']==OLD_SOURCE
            and len(queue)==785 and prior['combinedSelectedReferences']==610 and prior['previousPurposeReviewed']==96,'existing complete domains')
    source_hashes=old['closureSourceHashes']
    require(len(source_hashes)==5 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in source_hashes.items()),'all five Main/helper exact current bytes')
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_raw={v['id']:v for v in raw}
    current_manifest=read(('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983'))
    current=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',current_manifest['observationsSha256'])
    require(all({'sourceSha256','currentSource','path','attributes','message','staticObservationId'} <= set(v) for v in current), 'explicit current observation schema before use')
    current_by_id={v['staticObservationId']:v for v in current}
    groups=defaultdict(list);selected=defaultdict(list)
    for index,row in enumerate(review['rows']):groups[signature(row)].append((index,row))
    for row in queue:
        if signature(row) in groups:selected[signature(row)].append(row)
    require(len(groups)==len(selected)==32 and sum(map(len,selected.values()))==46
            and all(len(selected[key])==len(values) for key,values in groups.items()),'exact multiplicity, not invented individual bijection')
    links=[];extensions=Counter()
    for key,occurrences in selected.items():
        saved=groups[key];first=saved[0][1]
        common=('kind','reason','disposition','methodTokenSha256','catchTokenSha256','controls','sourceSpanSha256')
        require(all({k:r[k] for k in common}=={k:first[k] for k in common} for i,r in saved),'all duplicate purposes genuinely identical')
        witnesses=[]
        for index,row in saved:
            original=old_raw[row['id']]
            require(original['rowSha256']==row['originalRowSha256']
                    and original['inputSha256']==row['sourceSha256']
                    and original['attributes']==row['attributes'] and original['path']==row['path']
                    and original['rule']==row['rule']==row['attributes']['rule'],'exact original raw row')
            require(row['source']==OLD_SOURCE and row['oldRuntimeReassigned'] is False and row['newAccepted']==row['productTestsExecutedByReview']==0
                    and row['dynamicPtStatus']=='NOT_EXECUTED' and row['reason'] and row['currentWholeJoinPending'] is True,'retained reasons only')
            witnesses.append(dict(ordinal=index,id=row['id'],rowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),originalRawRowSha256=row['originalRowSha256']))
        for row in occurrences:
            text=(data.ROOT/row['path']).read_text();start,stop,token=span(text,row['attributes'])
            require(stop<len(text) and text[stop] in ' \n)' and data.sha(text[start:stop+1].encode())==first['sourceSpanSha256'],'explicit exact plus-one extent, never canonical normalization')
            actual=current_by_id[row['id']]
            require(actual['message']==old_raw[first['id']]['message']
                    and actual['attributes']==row['attributes'] and actual['sourceSha256']==row['sourceSha256'] and actual['currentSource']==SOURCE and actual['path']==row['path'],'same whole diagnostic semantics')
            extensions[repr(text[stop])]+=1
            links.append(dict(**row,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
                canonicalStart=start,canonicalEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
                legacyExtentSha256=first['sourceSpanSha256'],legacyExtraCharacter=repr(text[stop]),
                legacyExtentIsCanonicalPmdToken=False,spanSchema='CANONICAL_EXCLUSIVE_AND_FIXED_EXPORTER_PLUS_ONE_CHARACTER',
                individualOccurrenceIdentity='SIGNATURE_GROUP_ONLY_NO_ARBITRARY_BIJECTION',
                oldSignatureOccurrences=len(saved),currentSignatureOccurrences=len(occurrences),
                oldRowWitnesses=witnesses,oldReason=first['reason'],oldKind=first['kind'],
                diagnosticMessageSha256=data.sha(actual['message'].encode()),
                meaning='EXISTING_STATIC_REFERENCE_ONLY_NOT_NEW_REVIEW_OR_RUNTIME'))
    require(len(links)==len({r['id'] for r in links})==46
            and extensions==Counter({"' '":22,"'\\n'":8,"')'":16}),'all exact occurrence extent suffixes')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    authority=old['upperAuthority'];path=authority['path'];body=(data.ROOT/path).read_bytes()
    require(subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)==body
            and data.sha(body)==authority['sha256'],'current approved authority exact old public design')
    for v in (old,post,prior):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,staticReviewSource=OLD_SOURCE,invocation=invocation,
        oldReviewManifestSha256=OLD[1],oldPostManifestSha256=OLD_POST[1],oldReviewSha256=old['reviewSha256'],
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=source_hashes,authority=authority,
        exporterSha256=EXPORTER_SHA,exporterReexecuted=False,signatureGroups=32,occurrences=46,
        individualIdentityInvented=False,legacyExtentIsCanonicalPmdToken=False,extraCharacters={'SPACE':22,'LF':8,'RIGHT_PAREN':16},
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=46,combinedSelectedReferences=656,combinedPurposeReviewed=96,
        combinedPurposeOrReferenceRows=752,remainingSelectedUnreferenced=739,newManualReviews=0,
        rawSuppressed=0,actualViolationCount=None,productTestsExecuted=0,oldProductToolsReexecuted=0,
        oldRuntimeTransferred=False,sourceChanged=False,externalActions=0,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
