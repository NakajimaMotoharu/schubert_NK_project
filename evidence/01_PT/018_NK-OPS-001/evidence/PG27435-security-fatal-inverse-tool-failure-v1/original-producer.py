"""Twelve module-local calls and needed imports, exact seven-source inverse; no Main execution."""
from pathlib import Path
import hashlib,json,re,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27436-web-security-fatal12-source-static-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=ld(B/'evidence/PG27432-web-security-contract-v1/before.json');assert not O.exists();paths=[];inverse={};imports=0
for row in before['sites']:
 p=R/row['path'];old=subprocess.check_output(['git','show','fa9b9fa81706b0e62a34c3bd374a3971c2495499:'+row['path']],text=True);assert p.read_text()==old and sha(p)==row['sha256'];lines=old.splitlines(keepends=True);out=[];changed=[]
 for i,line in enumerate(lines):
  out.append(line)
  if i+1 in {v['line'] for v in row['missingFatalCatchSites']}:
   m=re.search(r'(\w+)\) \{\s*$',line);assert m;statement=' '* (len(line)-len(line.lstrip())+2)+'SessionStoreException.preserveFatal('+m.group(1)+');\n';out.append(statement);changed.append(statement)
 s=''.join(out);newimport='import dev.codex.schubert.nk.web.session.SessionStoreException;\n';added=newimport not in old
 if added:
  anchor='import jakarta.' if '\nimport jakarta.' in s else 'import java.';assert anchor in s;s=s.replace(anchor,newimport+'\n'+anchor,1);imports+=1
 inv=s
 for call in changed:assert inv.count(call)==1;inv=inv.replace(call,'',1)
 if added:inv=inv.replace(newimport+'\n','',1)
 assert inv==old;p.write_text(s);paths.append(p);inverse[row['path']]=dict(beforeSha256=row['sha256'],afterSha256=sha(p),calls=len(changed),newImport=added,exactInverse=True)
assert len(paths)==7 and sum(x['calls'] for x in inverse.values())==12 and imports==5
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*map(str,paths)],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*map(str,paths)],R));passed=all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');v=dict(actualExit=0 if passed else 1,sourceBefore='fa9b9fa81706b0e62a34c3bd374a3971c2495499',inputHashes={str(p.relative_to(R)):sha(p) for p in paths},stages=stages,originalSourceInverseExact=True,twelveExistingModuleLocalFatalCallsOnly=True,neededImports=5,inverse=inverse,httpAuthorizationCsrfCookiePersistenceNullAndDiagnosticsUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2707',horizontal='YKT-2359_53_LIMITED_SITES_RUNTIME_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],stageExits={k:x['actualExit'] for k,x in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
