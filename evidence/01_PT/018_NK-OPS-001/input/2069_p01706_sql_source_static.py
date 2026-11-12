"""BUG2749: conversion-only SQL graph guards, retain all primary/cleanup selection first."""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2068_p01706_sql_source_pg_start.json').read_text());O=B/'evidence/PG28270-p01706-sql-five-source-static-v1';assert not O.exists();assert '## BUG-2749' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();helper=B/'input/1861_user_display_format_gate.py';nodes=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='tokens'];assert len(nodes)==1;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals());changes=[]
for path in c['implementationArtifactPaths']:
 p=R/path;old=subprocess.check_output(['git','show',c['source']+':'+path],text=True);assert p.read_text()==old;new=old;inverse=[]
 if p.stem=='CleanupBackupAdmission':
  a='    } catch (SQLException | BatchRepositoryException failure) {\n';b=a+'      StorageIoException.preserveFatal(failure);\n';assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a))
  a='''        return;
      }
      throw unavailable();
    } catch (RuntimeException | Error cleanup) {''';b='''        return;
      }
      StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(cleanup);
      throw unavailable();
    } catch (RuntimeException | Error cleanup) {''';assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a))
  a='      if (cleanup instanceof BatchRepositoryException) throw unavailable();\n';b='''      if (cleanup instanceof BatchRepositoryException) {
        StorageIoException.preserveFatal(primary);
        StorageIoException.preserveFatal(cleanup);
        throw unavailable();
      }
''';assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a));expectedCalls=5
 else:
  imp='import dev.codex.schubert.nk.storage.StorageIoException;\n';anchor='import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;\n' if p.stem=='BackupFailureSnapshot' else 'import dev.codex.schubert.nk.batch.backup.BackupManifest;\n';assert new.count(anchor)==1 and imp not in new;new=new.replace(anchor,anchor+imp);inverse.append((imp,''));a='    } catch (SQLException failure) {\n';b=a+'      StorageIoException.preserveFatal(failure);\n';assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a));expectedCalls=1
 reverse=new
 for added,removed in reversed(inverse):assert reverse.count(added)==1;reverse=reverse.replace(added,removed,1)
 assert reverse==old;assert new.count('StorageIoException.preserveFatal(')-old.count('StorageIoException.preserveFatal(')==expectedCalls;changes.append((p,old,new,inverse,expectedCalls))
O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,inverse,count in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0 and tokens(new)==tokens(p.read_text());reverse=p.read_text()
 for added,removed in reversed(inverse):assert reverse.count(added)==1;reverse=reverse.replace(added,removed,1)
 assert reverse==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalByteInverseExactAfterFormat=True,guardCalls=count,unknownPrimaryAndCleanupSelectionUnchanged=True))
paths=c['implementationArtifactPaths'];listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);okay=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0 if okay else 1,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},proof=proof,stages=stages,originalSourceInverseExact=True,normalizationBoundaries=5,guardCalls=7,unknownPrimaryTypePriorityUnchanged=True,checkedIoAndResourceScopeUnchanged=True,sqlTransactionResourceOrderAndLiteralsUnchanged=True,sourceHelper='StorageIoException.preserveFatal',sourceHelperSha256=sha(R/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java'),bug='BUG2749',horizontal='YKT2359_OPEN',productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',runtimeStatus='HOLD_REAL_DB_WHOLE_TESTS_NO_EXTRACTION_OR_NEW_FIXTURE',actualBackendOrBackupOrRootOperations=0,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert okay;spec=R/'evidence/01_PT/017_NK-BAT-001/4199_P01706既知SQL五境界製造・未実施PT仕様.md';assert not spec.exists();spec.write_text('# P01706既知SQL五境界の製造・未実施PT\n\nBUG2749/YKT2359、CBA001..005/CFDB001..004/BAT210..217、SS312/332/341/343/352/UI251。三Main五catalog境界/七helpercallのみ。unknown primaryが先の既存type優先を保ち、選択済みknown fallback直前だけ原因/suppressed fatalgraphを分類。三Mainの全旧bodyは追加部分の逆変換でbyte完全一致、SQL/transaction/borrowedclose/既literal/SS333のcheckedIO priority不変更。既存三Testは@BeforeAll実DB全HOLD、部分抽出/新代替fixture0。\n\nPG28270は元source/変更hash/command/exit/GJF/CS/元body逆変換のsourcePGだけ。Main compile/NullAway/PMD/SpotBugs/製品PT/coverageは未実施・未受入。必要な独立PTはfatal cause/suppressed/循環の固定vector・unknown primary/cleanup優先・rollback失敗時復元0/全column SQL後条件/borrowed資源を含む元wholeTestで実施し、旧helper純4の成功をcallerへ転用しない。BUG2749はOPENのまま、実DB/Root等HOLDを解除しない。\n');decision=R/'documents/400_PGPT/440_判断/441_実装判断記録.md';s=decision.read_text();assert max(map(int,re.findall(r'PG-D-(\d+)',s)))==355;decision.write_text(s+'\n\n## PG-D-356：P01706既知SQL診断変換前の五graph境界（2026-11-13）\n\nBUG2749/YKT2359、SS312/332/341/343/352。CleanupBackupAdmission.verify/recoverのunknown-primary既定優先を先に維持し、known fallbackだけprimary→cleanupを分類。BackupFailureSnapshot.verifyRow/BackupStepRepository.inspectは既知SQL固定化前だけ分類する。例外型優先/SQL/transaction/borrowed資源/SS333 checkedIO規則/外部仕様は変更せず新QA/SSC不要。三Main五境界七callのbyte逆変換/GJF-CS sourcePGだけ、元wholeDB TestのPT/coverageはHOLD未実施、BUGはOPEN。\n');print(json.dumps(dict(actualExit=0,changedSources=3,normalizationBoundaries=5,guardCalls=7,originalSourceInverseExact=True,productTestsExecuted=0)))
