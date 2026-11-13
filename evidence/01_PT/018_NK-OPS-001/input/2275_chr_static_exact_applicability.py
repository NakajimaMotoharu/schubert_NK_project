"""Per-site applicability for actual Root rules; no suppression/exclusion or raw report rewrite."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];E=R/'evidence/01_PT/018_NK-OPS-001/evidence';S=E/'PG29256-chr-tool-full-static-v1';O=E/'PG29260-chr-static-exact-applicability-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not O.exists();m=json.loads((S/'manifest.json').read_text());assert m['source']=='029c35c032291a2f93894713de37ef0387071ea9' and not m['processingErrors'] and m['checkstyleErrors']==0
 assert m['stages']['pmd']['actualExitCode']==4 and m['stages']['checkstyle']['actualExitCode']==0
 policy=R/'tools/quality/static/pmd.xml';assert policy.read_bytes()==subprocess.check_output(['git','show','1634e3884a7b645f50b3552642ed4a1844736ab5:tools/quality/static/pmd.xml'],cwd=R)
 # Exact sites frozen from source ownership review, not a file/rule-wide exception.
 entries=[
 ('ArtifactComparator.java',74,'currentByCase','Invocation-local Current JSON catalog, constructed and consumed synchronously; no mutable reference shared across calls.'),
 ('ArtifactComparator.java',75,'nkByCase','Invocation-local NK JSON catalog distinct from Current; no concurrent mutation or static reference.'),
 ('ArtifactComparator.java',103,'rules','Invocation-local immutable-input rules index, filled before the same synchronous observation loop.'),
 ('ArtifactComparator.java',253,'files','Private artifactFiles method builds a new sorted path map per call; callers consume after stream close, no sharing.'),
 ('CorrelatedLogEvidenceValidator.java',100,'events','expectations returns a fresh map only to the current validate call; each concurrent validation owns separate maps.'),
 ('CorrelatedLogEvidenceValidator.java',167,'addedEvents','compareSide allocates this map for one before/after comparison; no caller receives mutable shared storage.'),
 ('CorrelatedLogEvidenceValidator.java',188,'rows','rows allocates one fresh index per snapshot; no persistent map or concurrent write exists.'),
 ('GateCli.java',128,'actual','Source verification method-local metadata populated before synchronous JSON serialization; not shared with another invocation.'),
 ('GateCli.java',214,'result','Preflight method-local JSON report with no worker or concurrent writer; map order preserves report determinism.'),
 ('GateCli.java',265,'result','Repeat-comparison method-local report created after file comparison; serialization is synchronous and no map escapes mutable.'),
 ('GateCli.java',336,'result','Gate report method-local metadata, fully populated before synchronous owned output publication; no shared mutation.'),
 ('GateCli.java',496,'manifest','Baseline metadata construction local to invocation; this static scan grants no baseline-publication authority.'),
 ('GateCli.java',560,'result','prefixed creates a new TreeMap owned by its caller; source entries copied synchronously and no concurrent mutation.'),
 ('GateCli.java',566,'result','fileHashes creates a fresh per-call index; only the synchronous caller owns returned map, no global sharing.'),
 ('GateContractValidator.java',124,'metrics','Validator invocation-local metadata; copied into immutable result after validation, not a concurrent collector.'),
 ('ArtifactComparatorTest.java',762,'currentArtifacts','TempDir fixture Current map owned by one test call; synchronous JSON writes only, no shared mutable test state.'),
 ('ArtifactComparatorTest.java',763,'nkArtifacts','Separate TempDir fixture NK map owned by one test call; synchronous writes complete before tool comparison.'),
 ]
 raw=m['rawFindings'];assert len(raw)==22;classified=[]
 for filename,line,anchor,reason in entries:
  matches=[x for x in raw if Path(x['path']).name==filename and int(x['beginline'])==line and x['rule']=='UseConcurrentHashMap'];assert len(matches)==1
  x=matches[0];text=Path(x['path']).read_text().splitlines()[line-1];assert anchor in text and 'new ' in text
  classified.append(dict(**x,sourceAnchor=text.strip(),reason=reason,disposition='NOT_APPLICABLE_PRECONDITION_NO_CONCURRENT_ACCESS'))
 extras=[
 ('CorrelatedLogEvidenceValidatorTest.java',326,'DoNotUseThreads','Executors.newFixedThreadPool(2)','J2EE-container prohibition has no applicable container here: plain JUnit two finite pure-JSON validators with independent inputs and owned executor; no Web/service process.'),
 ('CorrelatedLogEvidenceValidatorTest.java',327,'DoNotUseThreads','workers.submit','Plain JUnit isolated healthy JSON validation task; no application-managed thread, credential, transport or container lifecycle.'),
 ('CorrelatedLogEvidenceValidatorTest.java',328,'DoNotUseThreads','workers.submit','Plain JUnit isolated faulty JSON validation task, distinct snapshot; J2EE application/container condition is absent.'),
 ('GateContractTest.java',30,'AvoidLiteralsInIfCondition','"NK_ONLY"','Literal is independent schema oracle for the sole approved NK-only case, not an unexplained business algorithm threshold or runtime config; keeping expected separate from production constant is required.'),
 ('GateContractTest.java',None,'UseProperClassLoader','GateContractTest.class.getClassLoader()','Explicit defining loader reads bundled test resource in plain JUnit; no J2EE delegated loader. TCCL substitution could select unrelated resources and weaken oracle provenance.'),
 ]
 for filename,line,rule,anchor,reason in extras:
  matches=[x for x in raw if Path(x['path']).name==filename and (line is None or int(x['beginline'])==line) and x['rule']==rule];assert len(matches)==1;x=matches[0];text=Path(x['path']).read_text().splitlines()[int(x['beginline'])-1];assert anchor in text
  classified.append(dict(**x,sourceAnchor=text.strip(),reason=reason,disposition='NOT_APPLICABLE_CONTEXT_OR_INDEPENDENT_ORACLE'))
 identity=lambda x:(x['path'],x['beginline'],x['rule'],x['message']);assert len(classified)==len(raw) and {identity(x) for x in classified}=={identity(x) for x in raw}
 assert all(sha(R/p)==v for p,v in m['inputHashes'].items())
 O.mkdir();v=dict(source=m['source'],actualExitCode=0,rawFindings=22,classified=classified,applicable=0,unclassified=0,processingErrors=0,checkstyle=0,rootRulesUnchanged=True,rootPolicySha256=sha(policy),staticRef=dict(path=str((S/'manifest.json').relative_to(R)),sha256=sha(S/'manifest.json')),productTestsExecuted=0,fullBundleAccepted=False,formalAcceptanceAdded=0,verifierSha256=sha(Path(__file__)))
 (O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print('actualExit0 raw22 individually classified; no rule exclusions/suppression; full bundle not accepted')
if __name__=='__main__':main()
