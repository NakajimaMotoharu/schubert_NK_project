"""Fixed catalog guards only; no actual configuration, credential or service actions."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2208_settings_five_main_source_start.json').read_text());O=B/'evidence/PG28864-settings-five-main-source-static-v1';assert not O.exists();state=json.loads((R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json').read_text());assert state['ordinaryActiveGroup']==c['groupId'] and state['ordinaryGroupNotYetClosed'];assert '## BUG-2791' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();changes=[]
for name in c['implementationArtifactPaths']:
 p=R/name;old=subprocess.check_output(['git','show',c['source']+':'+name],text=True);assert p.read_text()==old;new=old;inverse=[]
 def rep(a,b,n=1):
  global new
  assert new.count(a)==n,(p.name,a,new.count(a));new=new.replace(a,b);inverse.append((b,a,n))
 imp='import dev.codex.schubert.nk.storage.StorageIoException;\n'
 if imp not in new:
  i=new.index('import java.');new=new[:i]+imp+new[i:];inverse.append((imp,'',1))
 if p.stem=='CaddyPublicConfiguration':
  a='    } catch (GeneralSecurityException failure) {\n';rep(a,a+'      StorageIoException.preserveFatal(failure);\n');calls=1
 elif p.stem=='ConfigurationGroupResolver':
  a='    } catch (InterruptedException failure) {\n      Thread.currentThread().interrupt();\n';rep(a,a+'      StorageIoException.preserveFatal(failure);\n')
  a='      if (cause instanceof RuntimeException)\n        throw new IllegalStateException("configuration group reader failed");';b='      if (cause instanceof RuntimeException) {\n        StorageIoException.preserveFatal(cause);\n        throw new IllegalStateException("configuration group reader failed");\n      }';rep(a,b);calls=2
 elif p.stem=='InspectorCredentialLoader':
  a='    } catch (IOException | IllegalArgumentException | UnsupportedOperationException failure) {\n';rep(a,a+'      if (!(failure instanceof IOException)) StorageIoException.preserveFatal(failure);\n',4)
  a='      if (failure.reason() == StorageIoException.Reason.MISSING && !entered.get() && optional)\n        return OptionalInt.empty();';b='      if (failure.reason() == StorageIoException.Reason.MISSING && !entered.get() && optional) {\n        StorageIoException.preserveFatal(failure);\n        return OptionalInt.empty();\n      }';rep(a,b);calls=5
 elif p.stem in ['ApiNonSecretConfig','WebNonSecretConfig']:
  a='    } catch (RuntimeException failure) {\n';rep(a,a+'      StorageIoException.preserveFatal(failure);\n',2);calls=2
 else:raise AssertionError(p.stem)
 reverse=new
 for a,b,n in reversed(inverse):assert reverse.count(a)==n;reverse=reverse.replace(a,b)
 assert reverse==old and new.count('StorageIoException.preserveFatal(')==calls;changes.append((p,old,new,inverse,calls))
assert sum(x[4] for x in changes)==12
O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,inverse,calls in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0;reverse=p.read_text()
 for a,b,n in reversed(inverse):assert reverse.count(a)==n,(p.name,a);reverse=reverse.replace(a,b)
 assert reverse==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalByteInverseExactAfterFormat=True,guardCalls=calls))
paths=c['implementationArtifactPaths'];listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);okay=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0 if okay else 1,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},proof=proof,stages=stages,originalSourceInverseExact=True,guardCalls=12,knownCatalogBoundaries=12,checkedIoPureCodecAndResourcePriorityUnchanged=True,irqRestoreBeforeGuard=True,rawOwnedWipeAndRootAuthorityUnchanged=True,bugs=['BUG2791'],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',actualCredentialKeyRootVmDbOrServiceActions=0,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert okay;print(json.dumps(dict(actualExit=0,changedSources=5,guardCalls=12,originalSourceInverseExact=True,productTestsExecuted=0)))
