"""Public-source oracle candidates and existing exact-source proof joins only; no class loading or PT."""
from pathlib import Path
import hashlib,json,re,datetime,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';base=b/'evidence/PG37334-p01810-source-inventory-v1';out=b/'evidence/PG37450-p01810-vector-negative-catalog-v1';assert not out.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(r)),sha256=sha(p))
inv=json.loads((base/'boundary-inventory.json').read_text());eight=json.loads((base/'source-test-expected-matrix.json').read_text());assert len(inv)==93 and len(eight)==8
sources=[p for p in (r/'src').glob('schubert-nk-*/src/test/java/**/*.java')]
blocked=('RootFailedStartRecovery','SnapshotKeyCloseWitness')
index={};testrefs={}
for item in inv:
 name=Path(item['path']).stem;index[name]=[]
for p in sources:
 if any(x in p.name for x in blocked):continue
 # These are public Java Test sources only, not classfiles, logs or credentials.
 text=p.read_text();names=[name for name in index if re.search(r'\b'+re.escape(name)+r'\b',text)]
 if not names:continue
 methods=re.findall(r'@Test\b(?:(?!@Test).){0,700}?\bvoid\s+(\w+)\s*\(',text,re.S)
 lines=text.splitlines();assertions=[]
 for n,line in enumerate(lines,1):
  calls=re.findall(r'\b(assert\w+)\s*\(',line)
  if calls:assertions.append(dict(line=n,calls=calls,negative=any(x in line.lower() for x in ['throw','null','false','empty','absent','redact','denied','missing','invalid','cause','suppress'])))
 fixed=[]
 for n,line in enumerate(lines,1):
  m=re.search(r'\bassertEquals\s*\(\s*("(?:[^"\\]|\\.){0,96}"|-?\d+(?:L)?)\s*,',line)
  if m:fixed.append(dict(line=n,literal=m.group(1)))
 entry=dict(path=str(p.relative_to(r)),sha256=sha(p),testMethods=methods,assertionLocations=assertions,independentLiteralExpectedCandidates=fixed,testExecutionClaim=False,relation='LEXICAL_REFERENCE_ONLY_REQUIRES_CASE_ORACLE_REVIEW')
 testrefs[entry['path']]=entry
 for name in names:index[name].append(entry['path'])
rows=[]
for x in inv:
 p=r/x['path'];same=sha(p)==x['sourceSha256'];name=p.stem;held=any(w in name for w in ['Root','Intent','Permit','Credential','Backup','Native','Linux','Nio','Unit','Systemctl','Recovery','Signing','Infrastructure'])
 candidates=index[name]
 negative=sum(sum(1 for a in testrefs[c]['assertionLocations'] if a['negative']) for c in candidates)
 fixed=sum(len(testrefs[c]['independentLiteralExpectedCandidates']) for c in candidates)
 rows.append(dict(path=x['path'],sourceSha256=sha(p),originalInventorySameSource=same,logicalOwners=x['logicalOwners'],boundaryAnchors=x['hits'],candidateTests=candidates,negativeAssertionLineCandidates=negative,fixedExpectedLineCandidates=fixed,fixtureQualification='HOLD_SOURCE_ONLY_NO_DYNAMIC_ADMISSION' if held else 'CANDIDATE_SOURCE_ONLY_NOT_EXECUTION_OR_COVERAGE',remaining='Need exact per-case independent oracle, fixture/authority admission and current single-source raw proof; lexical relation is not PASS.',formalAccepted=False))
# Reuse selected public proof hashes; no binaries/classfiles are read or regenerated.
joins=[]
for prefix,sourcefile,testfile in [
 ('PG34652-security-audit11-independent-v1','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebSecurityAudit.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebSecurityAuditPortTest.java'),
 ('PG34812-principal-topbar6-independent-v1','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java',None)]:
 p=b/'evidence'/prefix/'manifest.json';j=json.loads(p.read_text());assert j['actualExit']==0
 inputs=j['inputHashes'];assert inputs[sourcefile]==sha(r/sourcefile)
 if testfile:assert inputs[testfile]==sha(r/testfile)
 rel=[dict(path=k,sameCurrentSource=sha(r/k)==v,oldSha256=v,currentSha256=sha(r/k)) for k,v in inputs.items() if k.endswith('.java') and '/src/main/java/' in k and '/web/' in k]
 all_historical_web_inputs_same=all(x['sameCurrentSource'] for x in rel)
 rawname=prefix.replace('52-security','54-security').replace('12-principal','14-principal').replace('-independent-v1','-unfiltered-same-exec-v1');rawp=b/'evidence'/rawname/'manifest.json';raw=json.loads(rawp.read_text());assert raw['actualExit']==0
 targets=raw['declaredTargets'];counts={c:raw['classes'][c]['counters'] for c in targets};assert all(all(v['missed']==0 for v in cs.values()) for cs in counts.values())
 joins.append(dict(proof=ref(p),rawProof=ref(rawp),originalSource=j['source'],originalRun=j.get('run'),actualTests=j.get('tests'),currentSameJavaSourceBindings=rel,originalSingleExec=raw['originalSingleExec'],targetCounters=counts,targetAllCodeCounters100=True,wholeUnrelatedDependenciesAccepted=False,classfileReadOrNewTestExecuted=False,allHistoricalWebInputsUnchanged=all_historical_web_inputs_same,currentWholeClosureRuntimeQualified=all_historical_web_inputs_same,qualification='EXACT_TARGET_JAVA_HISTORICAL_RAW_ONLY_CURRENT_DEPENDENCY_CLOSURE_NOT_ASSUMED'))
# Request Details has a genuinely changed source and current five-test proof, kept separate.
p=b/'evidence/PG37350-request-details5-criteria-return-v1/manifest.json'
if p.exists():joins.append(dict(proof=ref(p),qualification='CURRENT_CHANGED_PARSER5_SEPARATE_RUN_NOT_ADDED_TO_WEB_RUN'))
else:raise AssertionError('exact parser5 criteria path must be independently located before completion')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();out.mkdir()
for name,val in [('boundary-fixture-negative-matrix.json',rows),('public-test-expected-candidates.json',list(testrefs.values())),('exact-source-existing-proof-joins.json',joins)]:
 (out/name).write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n')
manifest=dict(actualExit=0,terminalAtUTC=now,source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionSourceCore=subprocess.check_output(['git','log','-1','--format=%H','--',*[f'src/schubert-nk-{m}/src/main/java' for m in ['protocol','storage','bootstrap','api','web','batch']]],text=True).strip(),inventory=ref(base/'manifest.json'),boundaryRows=len(rows),rowsCurrentSourceSame=sum(x['originalInventorySameSource'] for x in rows),candidatePublicTestFiles=len(testrefs),rowsWithCandidateTests=sum(bool(x['candidateTests']) for x in rows),rowsWithoutCandidateTests=sum(not x['candidateTests'] for x in rows),explicitHeldSourceRows=sum(x['fixtureQualification'].startswith('HOLD') for x in rows),negativeAssertionCandidateRows=sum(x['negativeAssertionLineCandidates']>0 for x in rows),fixedExpectedCandidateRows=sum(x['fixedExpectedLineCandidates']>0 for x in rows),publicExistingProofJoins=joins,newProductTestsExecuted=0,heldFourClassfilesReadOrGenerated=0,actualRootVmDbNativeAuthorityOperations=0,candidateSourceRelationsAreNotPass=True,completedOriginalRowPricePp=0,completedAdditionalPricePp=0,completionPendingIndependentReview=True,formalUpdated=False,newAcceptance=0,effortCompletionRate=None,files={p.name:sha(p) for p in out.iterdir()})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:manifest[k] for k in ['actualExit','boundaryRows','rowsWithCandidateTests','rowsWithoutCandidateTests','negativeAssertionCandidateRows','fixedExpectedCandidateRows','explicitHeldSourceRows']}))
