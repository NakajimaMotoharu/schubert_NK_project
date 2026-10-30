"""Eighteen per-row ResourceScope reasons against approved design and real26 PT; raw gate stays1."""
from collections import Counter
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
ANALYSIS=('PG14664-storage-two-qualified-main-static-v1','4fb789834a8906d782f42acda3d8dc8a41cf403be5bb9938dbdfeacc025100a2')
POST=('PG14666-storage-two-static-post-v1','63a7b7f43111d1f4b71fb280b114302cc205f601cf9ea2dc6b65abf7d1a4af15')
PT=('PG14654-storage-resource-whole-twenty-six-post-v1','64716d82a4588387921fc49a0cdb423c79b661c22429a7a5662ab56edcac5a5f')
MAIN='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
MAIN_PIN='639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf'
DESIGN='documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md'
OUT=data.BASE/'PG14665-storage-resource-eighteen-context-review-v1'
G='AvoidCatchingGenericException'
I='AvoidInstanceofChecksInCatchClause'
SITES={
 (G,82,30):('RuntimeException','acquire','PRIMARY_RUNTIME'),
 (G,82,49):('Error','acquire','PRIMARY_ERROR'),
 (G,86,34):('RuntimeException','acquire','SECONDARY_RUNTIME'),
 (G,86,53):('Error','acquire','SECONDARY_ERROR'),
 (I,87,36):('IOException','acquire','PRIMARY_IO_PRIORITY'),
 (I,87,74):('IOException','acquire','SECONDARY_IO_PRIORITY'),
 (I,98,30):('StorageIoException','acquire','REASON_SANITIZATION'),
 (G,112,30):('RuntimeException','use','PRIMARY_RUNTIME'),
 (G,112,49):('Error','use','PRIMARY_ERROR'),
 (G,115,32):('RuntimeException','use','SECONDARY_RUNTIME'),
 (G,115,51):('Error','use','SECONDARY_ERROR'),
 (I,116,34):('IOException','use','PRIMARY_IO_PRIORITY'),
 (I,116,72):('IOException','use','SECONDARY_IO_PRIORITY'),
 (I,126,30):('StorageIoException','use','REASON_SANITIZATION')}
RATIONALES={
 'PRIMARY':'Unknown Runtime/Error is caught only to attempt owned release once, then rethrown with original identity; no normal return or NPE normalization. Main resource-null branch rejects without granting ownership.',
 'SECONDARY':'Release Runtime/Error cannot be hidden: after IO primary it wins, otherwise original unknown primary survives with bounded sanitized suppression. Success-body release failure propagates.',
 'IO_PRIORITY':'The exact primary-IO/secondary-IO distinctions implement approved SSC063/308 priority, not recovery by broad catch. Duplicated multi-catch diagnostics remain separate raw occurrences.',
 'REASON_SANITIZATION':'Known Storage reason survives only when prior suppression is absent; return uses new bounded exception and never exports raw cause/suppression. Other IO becomes UNAVAILABLE.'}
TESTS={
 'acquire':['factory006BodyIoReasonsAreRedactedAndExistingSuppressionIsNotExported','factory007BodyAndCloseIoAlwaysBecomeUnavailableWithoutRawSuppression','factory008UnknownCloseTakesPriorityOverBodyIo','factory009UnknownBodyKeepsIdentityAfterSuccessfulClose','factory010UnknownCompoundAndSelfFailureHaveSanitizedOrderedSuppression','factory011SuccessfulBodyCannotHideAnyCloseFailure','factory015IncompleteAssemblyMatchesIndependentThreeByFourGolden','factory016NullCompleteOwnerIsReleasedWithSanitizedCompoundFailure','factory017RepeatedAndAlreadySuppressedFailuresKeepIndependentPriority'],
 'use':['knownIoFailures','unknownBodyFailures','knownBodyUnknownCleanup','unknownCompoundFailures','nullAndNullableContracts','nestedScopes']}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    a,p,pt=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in (ANALYSIS,POST,PT)]
    assert all(v['source']==SOURCE and v['actualExit']==0 for v in (a,p,pt))
    assert p['analysisManifestSha256']==ANALYSIS[1] and p['metadataNegativeVectors']==10 and a['qualityGateExit']==p['qualityGateExit']==1 and p['unclassifiedRows']==18
    assert pt['tests']==26 and pt['suites']==2 and pt['singleSession'] and pt['crcMismatch']==0 and pt['targetUnitFour100'] and pt['productTestsReexecutedByPost']==0
    assert data.sha((data.ROOT/MAIN).read_bytes())==MAIN_PIN
    source=(data.ROOT/MAIN).read_text().splitlines()
    design=subprocess.check_output(['git','show','origin/main:'+DESIGN],cwd=data.ROOT);head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    assert head=='8b91944df5820535e23ba2469740f1c0aa94c447' and design==(data.ROOT/DESIGN).read_bytes()
    text=design.decode();assert all(v in text for v in ['primary IOにsecondary Runtime/Errorならsecondaryを優先','catch NPEによる正常復帰','unknown例外優先順位'])
    actual_methods={v['name'].split('(',1)[0]:v['classname'] for v in pt['cases']}
    assert all(n in actual_methods for names in TESTS.values() for n in names)
    raw=data.read_checked(data.BASE/ANALYSIS[0]/'findings.json',a['findingsSha256'])
    assert len(raw)==18 and Counter(v['rule'] for v in raw)=={G:8,I:10} and all(v['path']==MAIN and v['sourceSha256']==MAIN_PIN for v in raw)
    occurrences=Counter();review=[]
    for index,row in enumerate(raw,1):
        attrs=row['attributes'];key=(row['rule'],int(attrs['beginline']),int(attrs['begincolumn']))
        token,method,role=SITES[key];assert method==attrs['method'] and attrs['beginline']==attrs['endline']
        line=source[key[1]-1];assert line[key[2]-1:int(attrs['endcolumn'])-1]==token
        family='IO_PRIORITY' if role.endswith('_IO_PRIORITY') else 'REASON_SANITIZATION' if role=='REASON_SANITIZATION' else role.split('_',1)[0]
        occurrences[key]+=1
        review.append(dict(id=f'STO14664-{index:03d}',raw=row,rawOccurrence=occurrences[key],sourceToken=token,sourceMethod=method,semanticRole=role,contextLines=source[max(0,key[1]-4):key[1]+3],rationale=RATIONALES[family],designReference=dict(path=DESIGN,originMain=head,sha256=data.sha(design),sections=['SSC063','SSC308']),testReferences=[dict(classname=actual_methods[n],method=n,post=PT[0],postSha256=PT[1]) for n in TESTS[method]],proposedDisposition='REVIEWED_DESIGN_REQUIRED_BOUNDARY_RAW_RETAINED',rawRetained=True,qualityGatePass=False,currentWholeJoinPending=True,applicabilityAcceptedByWholeGate=False,productionChanged=False,rulesOrSuppressionChanged=False,productTestsExecutedByReview=0))
    assert set(occurrences)==set(SITES) and len(occurrences)==14 and sum(occurrences.values())==18 and sum(v-1 for v in occurrences.values())==4
    assert all(count==(2 if key[0]==I and key[1] in [87,116] else 1) for key,count in occurrences.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',review)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,analysis=ANALYSIS,analysisPost=POST,ptReference=PT,mainPath=MAIN,mainSha256=MAIN_PIN,designPath=DESIGN,designOriginMain=head,designSha256=data.sha(design),reviewSha256=data.sha((OUT/'review.json').read_bytes()),rawFindingRows=18,uniqueFindingSignatures=14,duplicateRawOccurrencesRetained=4,sourceProgramsWithFindings=1,reviewedRows=18,rawQualityGateExit=1,actualApplicableViolations=None,qualityGatePass=False,currentWholeJoinPending=True,wholeF03Accepted=False,whole451Accepted=False,productionChanged=False,rulesOrSuppressionChanged=False,productTestsExecuted=0,analyzersReexecuted=False,newAccepted=0,formalUpdated=False,effortPercent=None,reviewSemantics='SOURCE_REASONS_AND_TRUE_PT_REFERENCES_NOT_WARNING_SUPPRESSION_OR_WHOLE_GATE_ACCEPTANCE'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
