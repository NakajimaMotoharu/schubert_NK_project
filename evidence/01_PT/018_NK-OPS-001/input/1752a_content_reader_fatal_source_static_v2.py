"""Four existing fatal classifier calls only; exact source inverse, no Main compile/runtime."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27670-content-reader-fatal4-source-static-v1';source='43d4489fda4018505827c8f125f93ef501c92e14';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists();before=json.loads((B/'evidence/PG27666-scenario-detail-nine-contract-v1/before.json').read_text());plans=[]
import ast
helper=B/'input/1634_web_security_fatal_source_static.py';tree=ast.parse(helper.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['revert_calls','require_owned']];assert len(nodes)==2;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
def plan_calls(old, patterns, add_import):
 call_body='SessionStoreException.preserveFatal(failure);'
 assert not any(line.strip()==call_body for line in old.splitlines()), 'OLD_ALREADY_CONTAINS_CALL'
 new=old;calls=[]
 for pattern in patterns:
  lines=new.splitlines(keepends=True);found=[(i,x) for i,x in enumerate(lines) if pattern in x]
  assert len(found)==1, 'CATCH_NOT_UNIQUE'
  i,line=found[0];indent=line[:len(line)-len(line.lstrip())];addition=indent+'  '+call_body+'\n';lines.insert(i+1,addition);new=''.join(lines);calls.append(addition)
 im='import dev.codex.schubert.nk.web.session.SessionStoreException;\n';anchor='import java.nio.channels.FileChannel;\n'
 if add_import:
  assert im not in old and new.count(anchor)==1;new=new.replace(anchor,im+anchor)
 inverse=revert_calls(new,calls)
 if add_import:inverse=inverse.replace(im,'')
 assert inverse==old, 'ORIGINAL_INVERSE_MISMATCH'
 return new,calls

for row in before['targets']:
 p=R/row['path'];old=subprocess.check_output(['git','show',source+':'+row['path']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];new,calls=plan_calls(old,row['catchPatterns'],'import dev.codex.schubert.nk.web.session.SessionStoreException;\n' not in old);already=require_owned(p.read_text(),old,new);assert len(calls)==row['callsNeeded'];plans.append(dict(path=p,old=old,new=new,changes=[dict(addedCallLine=x) for x in calls],bug=row['bug'],alreadyPlanned=already))
assert len(plans)==2
for row in plans:
 if not row['alreadyPlanned']:row['path'].write_text(row['new'])
O.mkdir();c.SLOT=O;paths=[str(x['path']) for x in plans];jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*paths],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*paths],R));passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');v=dict(actualExit=0 if passed else 1,sourceBefore=source,inputHashes={str(x['path'].relative_to(R)):sha(x['path']) for x in plans},stages=stages,originalSourceInverseExact=True,fourExistingModuleLocalFatalCallsAndOneImportOnly=True,normalHttpFileReasonWireBorrowedOwnershipAndCleanupUnchanged=True,sourceChangeDetails=[dict(path=str(x['path'].relative_to(R)),oldSha256=hashlib.sha256(x['old'].encode()).hexdigest(),newSha256=sha(x['path']),changes=x['changes'],bug=x['bug']) for x in plans],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2715/BUG-2716',horizontal='YKT-2359_63_LIMITED_SITES_RUNTIME_OPEN',formalUpdated=False,verifiedReusableInverseHelper=dict(path=str(helper.relative_to(R)),sha256=sha(helper)),toolDefect='BUG-2717',verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert passed;print(json.dumps(dict(actualExit=0,changedSources=2,calls=4,stageExits={k:x['actualExit'] for k,x in stages.items()},manifestSha256=sha(O/'manifest.json'))))
