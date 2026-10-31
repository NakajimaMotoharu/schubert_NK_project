"""Public legacy purpose references only; exact whole Source and coordinates, never runtime reuse."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16210-concurrency-saved50-reference-v1','ee373a1f88e011a7b94970e0c95f70b7387181d8066508717e888bc86ad99de2')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16248-legacy-fourteen-133-reference-v1'
COORDS=('beginline','endline','begincolumn','endcolumn','priority')
BASIS='LEGACY_SOURCE_RULE_COORDINATES_PRIORITY_DIAGNOSTIC_REFERENCE_NOT_FULL_OLD_ATTRS_OR_RUNTIME'
# name, public manifest SHA, original decisions SHA, all old rows, selected rows.
FAMILIES=[
 ('PG6284-web-owned-static-review-v1','38fb05f2ed00f927007b1ce1b7093e096838aee5ffbbfeb6694622ffe9ecfb10','db7c941d0ab16ae7abb639e6e8b1d8a77fe637a73de6fc2f4d7c16084ea73261',33,9),
 ('PG6288-group-lookup-static-review-v1','11a530449d3c3f1967a63be5c3a0ca090363555225dbf32aef72c08250e47d32','84895bdf544468a94359f7b509f91d38ac55be5c2d5417dd5a2dec944f195c1f',18,4),
 ('PG6314-web-session-static-review-v1','39c0e2d43b3eb5c3c22fc5508a4e275da8e4d6ba0aef8651982adb87658db2fb','282229aae4de56a605d2db4346c40ddfcf9ec3052bb81bc4319cdebe3c7170ef',14,4),
 ('PG6338-outbox-graph-static-review-v1','913d5fb156d4e7c99a679f4699b829bed01cab175fa06427c1769f871929499a','f6546692123333e3b8b22d492917aa78536879520d54e329fd563f5ffb39fe8a',44,3),
 ('PG6344-question-storage-static-review-v1','05336045ed9b0df5eb0472cd30e86e3cf46e827ab52f944de5446c543f51cb82','21e60816852655c75652a509880da8faa6b58719b2e559b9d0313ebaf883c4f3',15,2),
 ('PG6352-ordinary-boundary-static-review-v1','24fc1a1ac1503d1f2ff19751b9154a0561c15ad0392e40c6f9ac533cba12a9b6','1d4f18ce8931b19d31f46cf16d7249ae1ceab5c886d0db79329ff26d7367b084',21,7),
 ('PG6354-batch-database-static-review-v1','33d467098f3881a2a92b4de30992f921c51f312eddd572a2bad2c8e2b231805a','38c60283328126fb4ee808d1566ce395c5083bbb8a2006a0af8733f471967bb9',35,7),
 ('PG6356-shared-boundary-static-review-v1','0bb79cb5ff97ba4e376708e9e3f0ec0320aae833d496a74641a66ef2209114a9','534d50e3fce470eb076aca3fbcca873f7463bb3ede75f680724cdc52abd36f3f',35,24),
 ('PG6362-systemd-cgroup-static-review-v1','558673dec3399b54cd6525aa777867fe1a84dac93dac3c88c4cf7fa56dc8acc3','7e912e9e534c0a375e19d21cd4eb4e6dbd012f2f589a2bed63742146fabda5ae',27,6),
 ('PG6394-startup-static-review-v1','36d0f91a905a865b9ba45da550c9c56acdfe2b1652f8478a1c595f8852cfabfd','8d7b9a32f33ac9c8c87ad7ad7ea1a98b912dca3f07fa4f591a3acf26fc4f112d',19,12),
 ('PG6404-runtime-boundary-static-review-v1','5c32e4d5d2203baabfabc5a590439a7a22c2fbdedb6478de0effff48c1633ea9','b181f38490d02f9a2e8275173bf5321503e255ca5d09f3de0bca99cf0e5f7a7b',25,13),
 ('PG6422-web-frame-static-review-v1','98f22c7c7045c9a6c7674b6329d87448098e8a7ec3aeb8b9ffd3b79844c7539e','d158dcc4f43a7547422756533d55a4cce5e6c56d88e8018d942eb534581c1ea9',5,4),
 ('PG6428-backup-normal-static-review-v1','2da516f19954d662b9cec1d2db70cbc0a1a8c0d7b31f09da22737158102f42bf','ebf8354e6ce2c4917b7659614d082fa2f4525790bb884f1aabf1558eadd77da9',15,10),
 ('PG6432-control-client-static-review-v1','117fd6ab8314b631e762bb7a775b43f0f4ac0860f6a85ad775310676a395ae71','12006f276c372707478399dac9e3a3d7610db0d930ca31a8c6d3d1fc2f652e50',41,28)]

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def match(current,old):
    return old['sourcePath']==current['path'] and old['sourceSha256']==current['sourceSha256'] and old['rule']==current['rule'] and all(old[k]==current['attributes'][k] for k in COORDS)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current qualified metadata')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==361 and prior['combinedSelectedReferences']==1011 and prior['combinedPurposeReviewed']==119,'fixed prior domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW)
    links=[];hashes={};extra=Counter();family_refs=[]
    required={'sourcePath','sourceSha256','rule','priority','beginline','endline','begincolumn','endcolumn','diagnosticFragment','diagnosticTextSha256','reason','findingId','owningPhysicalClassHashes','identitySchema','actualRuntimeProven','rawWarningRetained','ptAlternativeCompleted','F03Accepted','formalAccepted','status','currentWholeCaseRefs','currentWholeJoinPending'}
    for name,pin,dec_pin,count,selected in FAMILIES:
        old=read((name,pin));rows=data.read_checked(data.BASE/name/'decisions.json',dec_pin)
        require(type(old['actualExit']) is int and old['actualExit']==old['testsExecuted']==old['pmdRawRemoved']==old['ptAlternativeCompleted']==0
                and old['F03Accepted'] is old['formalAccepted'] is False and 'invocation' not in old
                and old['decisionsSha256']==dec_pin and len(rows)==count and old['reviewed']==count,'fixed legacy reported-success scope without invocation')
        require(all(required<=set(v) and 'attributes' not in v for v in rows),'legacy schema preflight, no invented full attrs')
        local=[]
        for current in queue:
            if current['path'].endswith('/RootFailedStartRecovery.java'):continue
            saved=[(i,v) for i,v in enumerate(rows) if match(current,v)]
            if not saved:continue
            require(len(saved)==1,'one exact old row');ordinal,row=saved[0];actual=observed[current['id']]
            require(row['source']==old['source'] and row['identitySchema']==2 and row['reason'] and row['status']=='REQUIRED_CONTRACT'
                    and row['actualRuntimeProven'] is row['F03Accepted'] is row['formalAccepted'] is False
                    and row['rawWarningRetained'] is True and row['ptAlternativeCompleted']==0,'old finite purpose, not actual runtime')
            require(actual['currentSource']==SOURCE and actual['path']==current['path'] and actual['sourceSha256']==current['sourceSha256']
                    and actual['attributes']==current['attributes'] and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'current exact fullattrs and diagnostic')
            original=[v for v in raw if v['path']==current['path'] and v['attributes']==current['attributes']]
            require(len(original)==1 and original[0]['message']==actual['message'],'fixed original current diagnostic reference')
            path=current['path'];blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==row['sourceSha256'],'full Source byte equality')
            hashes[path]=row['sourceSha256'];body=blob.decode();lines=body.splitlines(keepends=True);a=current['attributes']
            i,j=int(a['beginline'])-1,int(a['endline'])-1;s,e=int(a['begincolumn'])-1,int(a['endcolumn'])-1
            require(0<=i<=j<len(lines) and all(v.isascii() and '\t' not in v and '\\u' not in v for v in lines[i:j+1]),'explicit ASCII reporting line domain only')
            start=sum(map(len,lines[:i]))+s;stop=sum(map(len,lines[:j]))+e
            require(body[start:stop+1]==row['diagnosticFragment'] and body[stop:stop+1] in (' ','\n'),'original extra-one fragment retained not redefined')
            extra[body[stop:stop+1]]+=1
            local.append(dict(**current,currentSource=SOURCE,staticReviewSource=old['source'],matchingBasis=BASIS,
                oldManifestName=name,oldManifestSha256=pin,oldDecisionsSha256=dec_pin,oldRowOrdinal=ordinal,
                oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),legacyReviewRow=row,
                originalDiagnosticRowSha256=original[0]['rowSha256'],originalRawInputSha256=original[0]['inputSha256'],
                diagnosticMessageSha256=row['diagnosticTextSha256'],oldFullAttributesAvailable=False,
                legacyToolInvocationAvailable=False,legacyRunReauthenticated=False,historicalPhysicalHashesUsedAsCurrent=False,
                legacyReportedCharacterStart=start,legacyReportedCharacterEndExclusive=stop+1,legacyExtraCharacter=body[stop:stop+1],
                legacyFragmentIsCanonicalPmdToken=False,legacyCharacterOffsetsAreByteOffsets=False,
                currentRuntimeQualification=False,currentDesignApplicabilityReaccepted=False,
                meaning='EXACT_SOURCE_LEGACY_PURPOSE_REFERENCE_NOT_NEW_REVIEW_OR_EXECUTION_ACCEPTANCE'))
        require(len(local)==selected,'fixed per-family selected count');links.extend(local)
        family_refs.append(dict(name=name,manifestSha256=pin,decisionsSha256=dec_pin,source=old['source'],oldRows=count,selectedRows=selected,legacyInvocationAvailable=False))
    require(len(links)==len({v['id'] for v in links})==133 and len(hashes)==35 and extra=={' ':132,'\n':1},'fixed 133/35Source/fragment domains')
    require(Counter(v['rule'] for v in links)=={'AvoidCatchingGenericException':128,'CloseResource':4,'DoNotThrowExceptionInFinally':1},'exact rule counts')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    verify(prior['invocation']);verify(obs['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        originalRawJsonSha256=RAW,oldFamilies=family_refs,sourceHashes=hashes,matchingBasis=BASIS,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        oldReviewed=sum(v[3] for v in FAMILIES),currentSelected=133,newReferenceConnections=133,
        combinedSelectedReferences=1144,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1263,remainingSelectedUnreferenced=228,
        legacyExtraCharacterCounts=dict(extra),legacyFullAttrsAvailable=False,legacyInvocationAvailable=False,legacyRunReauthenticated=False,
        currentDesignApplicabilityReaccepted=False,newManualReviews=0,productTestsExecuted=0,oldProductToolsReexecuted=0,
        oldRuntimeTransferred=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,ptExecutionExempt=False,
        wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
