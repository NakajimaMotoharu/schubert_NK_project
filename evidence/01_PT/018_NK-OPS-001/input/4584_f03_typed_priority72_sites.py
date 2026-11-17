"""Review all72 exact type-priority guards; not a blanket waiver of arbitrary caught-type branching."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
leftp=b/'evidence/PG37048-f03-retention-erasure24-applicability-v1/remaining-unmatched.json';rows=load(leftp);selected=[x for x in rows if x['raw']['rule']=='AvoidInstanceofChecksInCatchClause'];assert len(selected)==72
reasons={
 'BackupCommitService.java':'SS332/341 recovery compares both original failure and rollback cleanup, preserving an unknown original identity or stronger unknown cleanup before fixed known-catalog failure. Branches inspect two exception objects, not a downcast that could be replaced by a single narrower catch.',
 'StepCleanupService.java':'Same approved transaction recovery matrix additionally recognizes CleanupStoppedException as a known stop. Original Runtime/Error stays identical with fixed safe suppression; unknown cleanup has explicit priority over known primary. Normal success is never produced.',
 'BackupArtifactVerifier.java':'Fixed IO/iterator/unsupported boundary classifies Runtime provider fatal graphs before emitting value-free unavailable. Known IO follows existing IO normalization; force scope retains only explicit StorageIoException reason. No raw provider detail or normal NPE recovery.',
 'BackupManifestReader.java':'Fixed checked IO/crypto and iterator/unsupported boundary distinguishes Runtime provider graphs solely to preserve fatal before the fixed unavailable catalog. Original known IO redaction remains unchanged, buffers and locks retain their explicit finally obligations.',
 'CleanupBackupAdmission.java':'Recovery checks cleanup known BatchRepositoryException only after separately considering unknown primary; fixed-catalog conversion occurs after both fatal graph checks. Otherwise original cleanup is rethrown. This compares primary/secondary precedence across nested recovery.',
 'CleanupProcessMain.java':'Two entry catches list only explicit known IO/domain errors. Non-IO domain wrappers are fatal-graph checked before fixed non-success exit30. Ordinary known IO follows approved IO catalog, and unrelated unknown Runtime/Error is not caught as success.',
 'MorningProcessMain.java':'Completed-entry catch retains fixed IOException/StopGate/known cleanup exit30 catalog; non-IO wrapper fatal graphs propagate before that fixed non-success. No catch converts unknown NPE/Error into successful completion.',
 'ConfigurationGroupResolver.java':'Shared scope compares known IO/Interrupted primary with cleanup type to implement original secondary-priority contract; interruption is restored even when unknown cleanup wins. Replacing it with independent caught-type-only handlers would omit the original-primary context.',
 'ProcessResourceScope.java':'Acquire/use share exact known IO/Interrupted/StopGate versus unknown cleanup matrix, preserve interrupted status before higher-priority cleanup, otherwise attach fixed safe diagnostic to identical primary. Checks are explicitly on primary and cleanup, not ordinary exception recovery.',
 'CleanupDatabaseSession.java':'Typed SQL/domain primary must preserve fatal graph before fixed unavailable. If classification finds Error, the pending primary is updated to that exact fatal before rethrow so owned finally applies correct precedence; known IO remains original fixed IO semantics.',
 'InspectorCredentialLoader.java':'Four fixed credential parsing/IO boundaries distinguish parser Runtime wrappers from known IOException solely for fatal-graph preservation before fixed InspectorCredentialException and buffer erasure. This is source-only redaction policy; no credential/key input or actual file/native load is executed.'}
assert set(reasons)=={Path(x['raw']['path']).name for x in selected}
fp=b/'evidence/PG37042-current287-catch-facts-v1/manifest.json';typed=load(fp);owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[]
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();lines=text.splitlines();n=int(raw['beginline']);assert sha(path)==x['sourceSha256']==typed['sourceInputs'][raw['path']] and lines[n-1]==x['actualSourceLine'] and 'instanceof' in x['actualSourceLine']
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=n,column=int(raw['begincolumn']),rule=raw['rule'],method=raw.get('method'),actualSourceLine=x['actualSourceLine'],sourceContext=lines[max(0,n-5):n+8],owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_REQUIRED_TYPED_FAILURE_PRIORITY',reason=reasons[path.name],functionalNativeOrNpeNegativeTestsReplaced=False))
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==72;remaining=[x for x in rows if x['rawFindingIndex'] not in indices];assert len(remaining)==293
commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();docs=[]
for prefix in ['332','333','341','343']:
 path=next((r/'documents/300_SS').rglob(prefix+'_*.md'));relative=str(path.relative_to(r));content=subprocess.check_output(['git','show',commit+':'+relative]);docs.append(dict(path=relative,commit=commit,sha256=hashlib.sha256(content).hexdigest()))
assert 'bodyが未知Runtime/Error' in subprocess.check_output(['git','show',commit+':'+next(x['path'] for x in docs if Path(x['path']).name.startswith('333_'))],text=True)
out=b/'evidence/PG37064-f03-typed-priority72-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=typed['sourceCore'],reviewOnly=True,newFinalDispositions=72,sourceClasses=11,finalWithPrior=678,remainingUnmatched=293,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=678+293==971,originalRemaining=ref(leftp),typedFacts=ref(fp),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),canonicalSpecPins=docs,sourceRuleSuppressionChanges=0,productTestsExecuted=0,credentialKeyFileOrNativeLoadExecuted=False,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,typedPriority72=True,sourceClasses=11,final=678,remaining=293,newAcceptance=0)))
