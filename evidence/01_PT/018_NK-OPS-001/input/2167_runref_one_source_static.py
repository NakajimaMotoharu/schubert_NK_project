"""Selected SQL graph guards with actual Error primary tracked before finally. No backend actions."""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2166_runref_one_source_start.json').read_text());O=B/'evidence/PG28636-runref-one-source-static-v1';assert not O.exists();ledger=(R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();assert '## BUG-2775' in ledger;changes=[]
for name in c['implementationArtifactPaths']:
 p=R/name;old=subprocess.check_output(['git','show',c['source']+':'+name],text=True);assert p.read_text()==old;new=old;inverse=[]
 def rep(a,b,n=1):
  global new
  assert new.count(a)==n,(p.name,a,new.count(a));new=new.replace(a,b);inverse.append((b,a,n))
 imp='import dev.codex.schubert.nk.storage.StorageIoException;\n';assert imp not in new;i=new.index('import java.');new=new[:i]+imp+new[i:];inverse.append((imp,'',1))
 rep('    } catch (SQLException failure) {\n','    } catch (SQLException failure) {\n      StorageIoException.preserveFatal(failure);\n');calls=1
 reverse=new
 for add,remove,n in reversed(inverse):assert reverse.count(add)==n;reverse=reverse.replace(add,remove)
 assert reverse==old and new.count('StorageIoException.preserveFatal(')==calls;changes.append((p,old,new,inverse,calls))
O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,inverse,calls in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0;reverse=p.read_text()
 for add,remove,n in reversed(inverse):assert reverse.count(add)==n;reverse=reverse.replace(add,remove)
 assert reverse==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalByteInverseExactAfterFormat=True,guardCalls=calls))
paths=c['implementationArtifactPaths'];listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);okay=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0 if okay else 1,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},proof=proof,stages=stages,originalSourceInverseExact=True,guardCalls=1,knownCatalogBoundaries=1,originalUnknownPrimaryCleanupSelectionAndCheckedIoUnchanged=True,normalSqlCredentialAndBorrowedResourceOrderUnchanged=True,bugs=['BUG2775'],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',actualDbRootCredentialOperations=0,normalPt='NOT_RUN_REQUIRES_ELIGIBLE_WHOLE_FIXTURE',wholeCleanupDbRootTest='HOLD_NO_EXTRACTION_OR_REPLACEMENT',verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert okay
print(json.dumps(dict(actualExit=0,changedSources=1,guardCalls=1,originalSourceInverseExact=True,productTestsExecuted=0)))
