"""Six source connections only; runtime/compile/coverage not performed or substituted."""
from pathlib import Path
import hashlib,json,re,subprocess
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG26846-scenario-fatal-source-static-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists();O.mkdir();c.SLOT=O
p=R/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/scenario/ScenarioReplayService.java';old=subprocess.check_output(['git','show','62960fc3b5d4a67cf7bd9df887b668169d10f87f:'+str(p.relative_to(R))],text=True);s=p.read_text();added='      TemporaryInfrastructureException.preserveFatal(failure);\n';assert s.count(added)==6 and s.replace(added,'')==old
pattern=r'catch\s*\(([^)]*)\)\s*\{\s*TemporaryInfrastructureException.preserveFatal\(failure\);\s*throw new TemporaryInfrastructureException\(\);\s*\}'
assert len(re.findall(pattern,s))==6
stages={};jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';cs=sg/'checkstyle-14.3.0-all.jar';gf=TC/'google-java-format-1.36.1-all-deps.jar';rules=R/'tools/quality/static/checkstyle.xml'
stages['format']=c.step('format',[str(jdk/'java'),'-jar',str(gf),'--dry-run','--set-exit-if-changed',str(p)],R)
stages['checkstyle']=c.step('checkstyle',[str(jdk/'java'),'-jar',str(cs),'-c',str(rules),'-f','xml','-o',str(O/'checkstyle.xml'),str(p)],R)
import xml.etree.ElementTree as ET
errors=ET.parse(O/'checkstyle.xml').findall('.//error');passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not errors
v=dict(actualExit=0 if passed else 1,sourceBefore='62960fc3b5d4a67cf7bd9df887b668169d10f87f',inputHashes={str(p.relative_to(R)):sha(p)},toolHashes={str(x):sha(x) for x in [cs,gf,rules]},stages=stages,checkstyleIssues=len(errors),sourceOnlyIndependentReview=dict(exactAddedCalls=6,oldSourceRecoveredByRemovingOnlySixCalls=True,oldExceptionTypesAndRedactedCatalogAndBuffersUnchanged=True,allSameSixMethodsPreserved=True,sharedFatalGraphImplementationUnchanged=True),productTestsExecuted=0,MainCompiled=False,actualHeldClassBinaryReadHashParseInit=False,coverage=None,nullAway=None,spotBugs=None,pmd=None,ptStatus='NOT_RUN_HOLD_NOT_PASS',bugState='OPEN_PENDING_PERMITTED_INDEPENDENT_RUNTIME_QUALIFICATION',alternativeIsNotProductPT=True,formalUpdated=False,scriptSha256=sha(Path(__file__).resolve()))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],sourceCalls=6,stageExits={k:v['actualExit'] for k,v in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
