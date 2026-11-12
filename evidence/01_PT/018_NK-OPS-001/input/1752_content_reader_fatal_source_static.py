"""Four existing fatal classifier calls only; exact source inverse, no Main compile/runtime."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27670-content-reader-fatal4-source-static-v1';source='43d4489fda4018505827c8f125f93ef501c92e14';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists();before=json.loads((B/'evidence/PG27666-scenario-detail-nine-contract-v1/before.json').read_text());plans=[]
for row in before['targets']:
 p=R/row['path'];old=subprocess.check_output(['git','show',source+':'+row['path']],text=True);assert p.read_text()==old and sha(p)==row['sha256'];new=old;changes=[]
 for pattern in row['catchPatterns']:
  lines=new.splitlines(keepends=True);found=[(i,x) for i,x in enumerate(lines) if pattern in x];assert len(found)==1;i,line=found[0];indent=line[:len(line)-len(line.lstrip())];addition=indent+'  SessionStoreException.preserveFatal(failure);\n';assert addition not in new;lines.insert(i+1,addition);new=''.join(lines);changes.append(dict(before=line,after=line+addition))
 im='import dev.codex.schubert.nk.web.session.SessionStoreException;\n'
 if im not in old:
  anchor='import java.nio.channels.FileChannel;\n';assert new.count(anchor)==1;new=new.replace(anchor,im+anchor);changes.append(dict(before=anchor,after=im+anchor))
 inverse=new
 for x in reversed(changes):assert inverse.count(x['after'])==1;inverse=inverse.replace(x['after'],x['before'])
 assert inverse==old and new.count('SessionStoreException.preserveFatal(failure);')==row['callsNeeded'];plans.append(dict(path=p,old=old,new=new,changes=changes,bug=row['bug']))
assert len(plans)==2
for row in plans:row['path'].write_text(row['new'])
O.mkdir();c.SLOT=O;paths=[str(x['path']) for x in plans];jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*paths],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*paths],R));passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');v=dict(actualExit=0 if passed else 1,sourceBefore=source,inputHashes={str(x['path'].relative_to(R)):sha(x['path']) for x in plans},stages=stages,originalSourceInverseExact=True,fourExistingModuleLocalFatalCallsAndOneImportOnly=True,normalHttpFileReasonWireBorrowedOwnershipAndCleanupUnchanged=True,sourceChangeDetails=[dict(path=str(x['path'].relative_to(R)),oldSha256=hashlib.sha256(x['old'].encode()).hexdigest(),newSha256=sha(x['path']),changes=x['changes'],bug=x['bug']) for x in plans],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2715/BUG-2716',horizontal='YKT-2359_63_LIMITED_SITES_RUNTIME_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert passed;print(json.dumps(dict(actualExit=0,changedSources=2,calls=4,stageExits={k:x['actualExit'] for k,x in stages.items()},manifestSha256=sha(O/'manifest.json'))))
