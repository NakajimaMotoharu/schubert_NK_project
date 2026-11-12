"""Selected SQL graph guards with actual Error primary tracked before finally. No backend actions."""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2097_db_session_jdbc_two_main_pg_start.json').read_text());O=B/'evidence/PG28362-db-session-jdbc-source-static-v1';assert not O.exists();ledger=(R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();assert '## BUG-2752' in ledger and '## BUG-2757' in ledger;changes=[]
for name in c['implementationArtifactPaths']:
 p=R/name;old=subprocess.check_output(['git','show',c['source']+':'+name],text=True);assert p.read_text()==old;new=old;inverse=[]
 def rep(a,b,n=1):
  global new
  assert new.count(a)==n,(p.name,a,new.count(a));new=new.replace(a,b);inverse.append((b,a,n))
 anchor='import java.';i=new.index(anchor);imp='import dev.codex.schubert.nk.storage.StorageIoException;\n';assert imp not in new;new=new[:i]+imp+new[i:];inverse.append((imp,'',1))
 if p.stem=='CleanupDatabaseSession':
  a='''    } catch (SQLException | IOException | BatchRepositoryException failure) {
      primary = failure;
      throw unavailable();''';b='''    } catch (SQLException | IOException | BatchRepositoryException failure) {
      primary = failure;
      if (failure instanceof SQLException || failure instanceof BatchRepositoryException) {
        try {
          StorageIoException.preserveFatal(failure);
        } catch (Error fatal) {
          primary = fatal;
          throw fatal;
        }
      }
      throw unavailable();''';rep(a,b)
  a='''    if (!known) primary.addSuppressed(new BatchRepositoryException());
    return false;''';b='''    if (!known) primary.addSuppressed(new BatchRepositoryException());
    else {
      if (primary instanceof SQLException || primary instanceof BatchRepositoryException)
        StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(secondary);
    }
    return false;''';rep(a,b);calls=3
 else:
  a='''    if (!(primary instanceof SQLException)) primary.addSuppressed(new BatchRepositoryException());
    return false;''';b='''    if (!(primary instanceof SQLException)) primary.addSuppressed(new BatchRepositoryException());
    else {
      StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(secondary);
    }
    return false;''';rep(a,b);calls=2
 reverse=new
 for add,remove,n in reversed(inverse):assert reverse.count(add)==n;reverse=reverse.replace(add,remove)
 assert reverse==old and new.count('StorageIoException.preserveFatal(')==calls;changes.append((p,old,new,inverse,calls))
O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,inverse,calls in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0;reverse=p.read_text()
 for add,remove,n in reversed(inverse):assert reverse.count(add)==n;reverse=reverse.replace(add,remove)
 assert reverse==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalByteInverseExactAfterFormat=True,guardCalls=calls))
paths=c['implementationArtifactPaths'];listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);okay=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0 if okay else 1,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},proof=proof,stages=stages,originalSourceInverseExact=True,guardCalls=5,actualFatalPrimaryRecordedBeforeFinally=True,originalUnknownPrimaryCleanupSelectionAndCheckedIoUnchanged=True,normalSqlCredentialAndBorrowedResourceOrderUnchanged=True,bugs=['BUG2752','BUG2757'],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',actualDbRootCredentialOperations=0,ordinaryHelper8Qualification='PRICED_NEXT_NOT_YET_RUN',wholeCleanupSessionDbTest='HOLD_NO_EXTRACTION_OR_REPLACEMENT',verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert okay
p=R/'evidence/01_PT/017_NK-BAT-001/4207_DBSession実primary・JDBC既知pair製造仕様.md';assert not p.exists();p.write_text('# DBSession実primary・JDBC既知pair製造仕様\n\nBUG2752/2757、YKT2359、SS312/332SSC063199310/333/341/352、UI251、CDB001..009/BAT087/121。Session executeのSQL/BatchRepoだけfatal分類、選択したErrorをactualprimaryへ記録してからfinally一回closeへ渡す。IOException自体の従来固定化/unknown型優先不変更。Session closeReplaceとJdbcResourceFailures knownSQLpairは元null/unknown選択後だけprimary→secondary graph分類。全元bodyは追加逆変換でbyte一致、SQL/借用owner/権限/credential消去不変更。\n\nPG28362はsourcePG/GJF-CSだけ、Session fullDBRoot TestはHOLD・部分抽出なし、Maincompile/fullstatic/PT/coverageは未受入。次の純JdbcResourceFailures新whole8はJDKThrowableだけで独立literal・identity/fresh固定secondary/cause-suppressed-next-cycleを直接検証する別scopeで、Session/全RepositoryのDB後条件や親ownerを認定しない。新定義数と実行件数を区別し元1964-53/190/工数nullを維持する。\n');p=R/'documents/400_PGPT/440_判断/441_実装判断記録.md';s=p.read_text();assert max(map(int,re.findall(r'PG-D-(\d+)',s)))==358;p.write_text(s+'\n\n## PG-D-359：既知SQL graphから選択した実primaryのfinally保持（2026-11-13）\n\nBUG2752/2757/YKT2359。SQL/BatchRepoのみのfatal分類で選ばれたErrorをcatch内でprimaryへ記録し、finallyが古いknownSQLを参照しない。checkedIOException自体の既定は変更せず、knownSQLpairの破棄直前だけ分類。SS332/333 unknown型の優先選択を先に維持する。元権限/SQL/credential/借用資源順序不変更、上位変更不要。二Main sourcePG/GJF-CSと原body逆変換だけ、独立新helper8は別scopeで必要資格、全DBRoot callerPT/coverageはHOLD未受入。\n');print(json.dumps(dict(actualExit=0,changedSources=2,guardCalls=5,originalSourceInverseExact=True,productTestsExecuted=0)))
