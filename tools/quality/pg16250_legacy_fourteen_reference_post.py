"""Independent original-row/line-coordinate/reference proof; legacy limits never promoted."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16248_legacy_fourteen_133_reference import SOURCE,PRIOR,OBS,RAW,FAMILIES,COORDS,BASIS,read

PIN='013bfd3e905d613397592e307aa45b4d5014862b32da1bf484a10d953762fa4b'
OUT=data.BASE/'PG16250-legacy-fourteen-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    current,prior,obs=[read(v) for v in [('PG16248-legacy-fourteen-133-reference-v1',PIN),PRIOR,OBS]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (current,prior,obs)),'current exact metadata source')
    before=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256']);by_id={v['id']:v for v in before}
    observations=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observations={v['staticObservationId']:v for v in observations}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW)
    links=data.read_checked(data.BASE/'PG16248-legacy-fourteen-133-reference-v1/references.json',current['referencesSha256'])
    after=data.read_checked(data.BASE/'PG16248-legacy-fourteen-133-reference-v1/remaining-selected-review-queue.json',current['queueSha256'])
    require(len(links)==len({v['id'] for v in links})==133 and len(before)==361,'133 unique of original361')
    families={};selected=Counter();source_hashes={};extras=Counter();schemas=Counter()
    for name,pin,dec_pin,count,n in FAMILIES:
        m=read((name,pin));rows=data.read_checked(data.BASE/name/'decisions.json',dec_pin)
        require(m['decisionsSha256']==dec_pin and m['actualExit']==m['testsExecuted']==0 and len(rows)==count and 'invocation' not in m,'old public record only not new invocation authentication')
        families[name]=(m,rows,pin,dec_pin,n)
    for link in links:
        original=by_id[link['id']];require(not original['path'].endswith('/RootFailedStartRecovery.java'),'exclude before Source access')
        require(all(link[k]==v for k,v in original.items()),'entire current original row/fullattrs unchanged')
        m,rows,pin,dec_pin,n=families[link['oldManifestName']];old=rows[link['oldRowOrdinal']]
        require(wire(link['legacyReviewRow'])==wire(old) and link['oldRowSha256']==data.sha(wire(old).encode()),'all original reason/status/oldphysical/case/pending fields retained')
        require(link['oldManifestSha256']==pin and link['oldDecisionsSha256']==dec_pin and link['staticReviewSource']==old['source']==m['source'],'exact old public Source')
        require(old['sourcePath']==original['path'] and old['sourceSha256']==original['sourceSha256'] and old['rule']==original['rule']
                and all(old[k]==original['attributes'][k] for k in COORDS),'independent flat five coordinates/rule/wholeSource')
        require(old['reason'] and old['status']=='REQUIRED_CONTRACT' and old['actualRuntimeProven'] is old['F03Accepted'] is old['formalAccepted'] is False
                and old['rawWarningRetained'] is True and old['ptAlternativeCompleted']==0 and 'attributes' not in old,'old limits preserved')
        observed=observations[link['id']]
        require(observed['currentSource']==SOURCE and observed['path']==original['path'] and observed['attributes']==original['attributes']
                and observed['sourceSha256']==original['sourceSha256'] and data.sha(observed['message'].encode())==old['diagnosticTextSha256']==link['diagnosticMessageSha256'],'whole current diagnostic binding')
        candidates=[v for v in raw if v['path']==original['path'] and v['attributes']==original['attributes']]
        require(len(candidates)==1 and candidates[0]['rowSha256']==link['originalDiagnosticRowSha256'] and candidates[0]['inputSha256']==link['originalRawInputSha256']
                and candidates[0]['message']==observed['message'],'original raw manifest trace')
        blob=(data.ROOT/original['path']).read_bytes();require(data.sha(blob)==original['sourceSha256'],'whole Source actual equality')
        source_hashes[original['path']]=original['sourceSha256'];lines=blob.decode().splitlines(keepends=True);a=original['attributes']
        i,j=int(a['beginline'])-1,int(a['endline'])-1;first,last=int(a['begincolumn'])-1,int(a['endcolumn'])-1
        if i==j:fragment=lines[i][first:last+1]
        else:fragment=lines[i][first:]+''.join(lines[i+1:j])+lines[j][:last+1]
        require(fragment==old['diagnosticFragment'] and all(v.isascii() and '\t' not in v and '\\u' not in v for v in lines[i:j+1]),'independent direct row slices and ASCII domain')
        start=len(''.join(lines[:i]))+first;end=len(''.join(lines[:j]))+last+1
        require(link['legacyReportedCharacterStart']==start and link['legacyReportedCharacterEndExclusive']==end
                and fragment[-1:]==link['legacyExtraCharacter'] and fragment[-1:] in (' ','\n'),'extra old character not canonical/byte offset')
        require(link['matchingBasis']==BASIS and link['currentSource']==SOURCE and all(link[k] is False for k in ['oldFullAttributesAvailable','legacyToolInvocationAvailable',
                'legacyRunReauthenticated','historicalPhysicalHashesUsedAsCurrent','legacyFragmentIsCanonicalPmdToken',
                'legacyCharacterOffsetsAreByteOffsets','currentRuntimeQualification','currentDesignApplicabilityReaccepted']),'no missing-field or runtime invention')
        selected[link['oldManifestName']]+=1;extras[fragment[-1:]]+=1
        schemas['PLANNED_AND_CASE_REFS' if 'plannedCurrentWholeCaseClasses' in old else 'CASE_REFS_ONLY']+=1
    require(all(selected[name]==n for name,(_,_,_,_,n) in families.items()) and len(source_hashes)==35 and extras=={' ':132,'\n':1}
            and schemas=={'PLANNED_AND_CASE_REFS':89,'CASE_REFS_ONLY':44},'all fixed families/Source/old schemas')
    ids={v['id'] for v in links};remaining=[v for v in before if v['id'] not in ids]
    require(wire(after)==wire(remaining) and len(after)==228 and source_hashes==current['sourceHashes'],'all remaining original rows unchanged')
    counts=Counter(v['rule'] for v in links)
    require(counts=={'AvoidCatchingGenericException':128,'CloseResource':4,'DoNotThrowExceptionInFinally':1},'all selected rule counts')
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['priorManifestSha256']==PRIOR[1]
                and value['priorQueueSha256']==prior['queueSha256'] and value['originalRawJsonSha256']==RAW,'same current fixed inputs')
        require(value['referencesSha256']==data.sha((data.BASE/'PG16248-legacy-fourteen-133-reference-v1/references.json').read_bytes())
                and value['queueSha256']==data.sha((data.BASE/'PG16248-legacy-fourteen-133-reference-v1/remaining-selected-review-queue.json').read_bytes()),'actual saved files')
        require((value['oldReviewed'],value['currentSelected'],value['newReferenceConnections'],value['combinedSelectedReferences'],value['combinedPurposeReviewed'],
                value['combinedPurposeOrReferenceRows'],value['remainingSelectedUnreferenced'])==(347,133,133,1144,119,1263,228),'derived exact domains')
        require(value['sourceHashes']==source_hashes and value['matchingBasis']==BASIS and value['legacyExtraCharacterCounts']==dict(extras)
                and len(value['oldFamilies'])==14,'all legacy fields/limits')
        require(all(value[k] is False for k in ['legacyFullAttrsAvailable','legacyInvocationAvailable','legacyRunReauthenticated','currentDesignApplicabilityReaccepted',
                'oldRuntimeTransferred','sourceChanged','ptExecutionExempt','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and value['newManualReviews']==value['productTestsExecuted']==value['oldProductToolsReexecuted']==value['rawSuppressed']==value['externalActions']==value['newAccepted']==0
                and value['actualViolationCount'] is value['effortPercent'] is None,'not new manual/runtime/PT/acceptance')
    contract(current);labels=[]
    vectors=[('source','OLD'),('priorManifestSha256','0'*64),('priorQueueSha256','0'*64),('originalRawJsonSha256','0'*64),
        ('referencesSha256','0'*64),('queueSha256','0'*64),('oldReviewed',133),('currentSelected',134),('newReferenceConnections',0),
        ('combinedSelectedReferences',1011),('combinedPurposeReviewed',252),('combinedPurposeOrReferenceRows',1130),('remainingSelectedUnreferenced',361),
        ('sourceHashes',{}),('matchingBasis','FULL_OLD_ATTRIBUTES'),('legacyExtraCharacterCounts',{}),('oldFamilies',[]),('legacyFullAttrsAvailable',True),
        ('legacyInvocationAvailable',True),('legacyRunReauthenticated',True),('currentDesignApplicabilityReaccepted',True),('newManualReviews',133),
        ('productTestsExecuted',133),('oldRuntimeTransferred',True),('formalUpdated',True),('effortPercent',100)]
    for key,value in vectors:
        require(wire(current[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(current);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false legacy qualification '+key)
    require(len(labels)==26,'finite26')
    for v in (current,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        metadataNegativeVectors=26,negativeLabels=labels,referenceRows=133,sourcePrograms=35,families=14,oldSchemaCounts=dict(schemas),
        combinedSelectedReferences=1144,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1263,remainingSelectedUnreferenced=228,
        legacyFullAttrsAvailable=False,legacyInvocationAvailable=False,legacyRunReauthenticated=False,currentDesignApplicabilityReaccepted=False,
        productTestsExecuted=0,newManualReviews=0,oldRuntimeTransferred=False,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
