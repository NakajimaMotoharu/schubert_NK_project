"""Two Main/six connections source-only independent inverse and configured style, not PT PASS."""
from pathlib import Path
import hashlib,json,re,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27084-user-mutation-fatal6-static-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists()
base='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/';paths=[base+'UserCommandService.java',base+'UserMutationReplayService.java'];checks=[]
for path,count in zip(paths,[2,4]):
 p=R/path;s=p.read_text();old=subprocess.check_output(['git','show','aa869405cde9eeda70058c951e1b675f5509f572:'+path],text=True)
 if count==2:
  pat=r'(catch \(IllegalArgumentException invalid\) \{\n)(\s*)TemporaryInfrastructureException.preserveFatal\(invalid\);\n\2(return rejected\(ResultCode.VALIDATION_ERROR,)'
  inverse,n=re.subn(pat,lambda m:m[1]+m[2]+m[3],s);assert n==2
 else:
  added='      TemporaryInfrastructureException.preserveFatal(failure);\n';assert s.count(added)==4;inverse=s.replace(added,'')
 assert inverse==old
 checks.append(dict(path=path,sha256=sha(p),addedCalls=count,originalRecoveredExactly=True,oldExceptionTypesCatalogAuthorizationSqlWireAndWipeUnchanged=True))
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths))
stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R))
passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
v=dict(actualExit=0 if passed else 1,sourceBefore='aa869405cde9eeda70058c951e1b675f5509f572',checks=checks,inputHashes={p:sha(R/p) for p in paths},stages=stages,productTestsExecuted=0,MainCompiled=False,actualHeldClassBinaryReadHashParseInit=False,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_HOLD_NOT_PASS',bugs=['BUG-2692','BUG-2693'],horizontal='YKT-2359_ALL23_RUNTIME_PENDING_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],sourceCalls=6,stageExits={k:x['actualExit'] for k,x in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
