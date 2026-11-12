"""BUG2750: replace only three incomplete-owner manual cleanup wrappers with SS333 handoff."""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess,sys,textwrap,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2071_p01706_handoff_source_pg_start.json').read_text());O=B/'evidence/PG28280-p01706-three-factory-handoff-source-static-v1';assert not O.exists();assert '## BUG-2750' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();helper=B/'input/1861_user_display_format_gate.py';nodes=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='tokens'];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
def span(s,start,end):
 assert s.count(start)==1;begin=s.index(start);finish=s.index(end,begin+len(start));return s[begin:finish]
def reindent(s,n):return textwrap.indent(textwrap.dedent(s),' '*n)
def replace_once(s,a,b):assert s.count(a)==1;return s.replace(a,b,1)
changes=[]
for path in c['implementationArtifactPaths']:
 p=R/path;old=subprocess.check_output(['git','show',c['source']+':'+path],text=True);assert old==p.read_text();new=old;changed=[];bodies=[];imp=''
 if p.stem=='BackupStartIntentFiles':
  begin='  public static BackupStartIntentFiles createService(';end='\n  BackupStartIntentFiles(\n';before=span(old,begin,end);marker='    var directory =\n';prefix=before[:before.index(marker)];body=before[before.index('    try {\n')+len('    try {\n'):before.index('    } catch (IOException | RuntimeException | Error failure) {')];assert body.count('return new BackupStartIntentFiles(')==1
  after=prefix+'''    return ResourceScope.<OwnedTransferDirectory, BackupStartIntentFiles, IOException>handoff(
        () ->
            OwnedTransferDirectory.open(
                LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup")),
        OwnedTransferDirectory::close,
        directory -> {
'''+reindent(body,10)+'''        });
  }
''';assert tokens(body)==tokens(reindent(body,10));new=replace_once(new,before,after);changed.append((begin,end,before,after));bodies.append(dict(factory='BackupStartIntentFiles.createService',normalBodySha256=hashlib.sha256(''.join(tokens(body)).encode()).hexdigest(),normalBodyTokensUnchanged=True,acquireBeforeAssembly=True,normalTransferDoesNotClose=True))
 else:
  imp='import dev.codex.schubert.nk.storage.ResourceScope;\n';anchor='import dev.codex.schubert.nk.batch.file.BackupStartIntentFiles;\n';assert imp not in new;new=replace_once(new,anchor,anchor+imp)
  begin='  private static MarkerLease beginNative(';end='\n  static BackupUnitStartClient create(\n';before=span(old,begin,end);prefix=before[:before.index('    var marker =')];body=before[before.index('    try {\n')+len('    try {\n'):before.index('    } catch (IOException | RuntimeException | Error failure) {')];assert body.count('var token = marker.begin();')==1 and body.count('marker.retire(token);')==1 and body.count('marker.close();')==1
  after=prefix+'''    return ResourceScope.<BackupStartIntentFiles, MarkerLease, IOException>handoff(
        () -> BackupStartIntentFiles.create(root, expected, target),
        BackupStartIntentFiles::close,
        marker -> {
'''+reindent(body,10)+'''        });
  }
''';new=replace_once(new,before,after);changed.append((begin,end,before,after));bodies.append(dict(factory='BackupUnitStartClient.beginNative',normalBodySha256=hashlib.sha256(''.join(tokens(body)).encode()).hexdigest(),normalBodyTokensUnchanged=True,retireThenCloseBodyUnchanged=True,normalTransferDoesNotClose=True))
  begin='  public static BackupUnitStartClient createService(';end='\n  /**\n   * Only the fixed Backup Unit';before=span(old,begin,end);opening='''        () -> {
          var marker = BackupStartIntentFiles.createService(root, morning, service, issued);
          try {
''';start=before.index(opening);normalStart=start+len(opening);normalEnd=before.index('          } catch (IOException | RuntimeException | Error failure) {',normalStart);body=before[normalStart:normalEnd];endLambda=before.index('        },\n',normalEnd)+len('        },\n');oldWrapper=before[start:endLambda];assert body.count('var token = marker.begin();')==1 and body.count('marker.close();')==2 and body.count('marker.requirePresent(token);')==1
  newWrapper='''        () ->
            ResourceScope.<BackupStartIntentFiles, MarkerLease, IOException>handoff(
                () -> BackupStartIntentFiles.createService(root, morning, service, issued),
                BackupStartIntentFiles::close,
                marker -> {
'''+reindent(body,18)+'''                }),
''';after=replace_once(before,oldWrapper,newWrapper);new=replace_once(new,before,after);changed.append((begin,end,before,after));bodies.append(dict(factory='BackupUnitStartClient.createService marker assembly',normalBodySha256=hashlib.sha256(''.join(tokens(body)).encode()).hexdigest(),normalBodyTokensUnchanged=True,allRetireObserveRetainedBodiesUnchanged=True,normalTransferDoesNotClose=True))
 reverse=new
 for begin,end,before,after in reversed(changed):reverse=replace_once(reverse,after,before)
 if imp:reverse=replace_once(reverse,imp,'')
 assert reverse==old;changes.append((p,old,new,changed,bodies,imp))
O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,changed,bodies,imp in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0 and tokens(new)==tokens(p.read_text());reverse=p.read_text()
 for begin,end,before,after in reversed(changed):
  actual=span(reverse,begin,end);assert tokens(actual)==tokens(after);reverse=replace_once(reverse,actual,before)
 if imp:reverse=replace_once(reverse,imp,'')
 assert reverse==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),explicitWrapperInverseOriginalByteExactAfterFormat=True,normalAssemblyBodyProof=bodies,wholeRemainderByteUnchanged=True,changedFactories=len(changed)))
listing=O/'sources.txt';paths=c['implementationArtifactPaths'];listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);okay=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0 if okay else 1,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},proof=proof,stages=stages,originalSourceInverseExact=True,inverseMeaning='RestoreOnlyThreeExplicitWrappersAfterAllNormalBodyTokenEqualityAndWholeRemainderByteEquality',changedFactories=3,normalAssemblyAndCompletedOwnerBodiesUnchanged=True,completeOwnerTransferredOnce=True,incompleteOwnerReleasedOnceByExistingResourceScope=True,resourceScopeImplementationUnchanged=True,resourceScopeSha256=sha(R/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'),compoundPriority='ExistingSS333IOExceptionVsUnknownPrimaryAndSecondaryNoBlanketFatalGuard',actualAuthorityRulesChanged=False,bug='BUG2750',horizontal='YKT2395_OPEN',productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',runtimeStatus='HOLD_ROOT_NATIVE_INTENT_WHOLE_TESTS_NO_EXTRACTION_OR_NEW_FIXTURE',actualBackendOrBackupOrRootOperations=0,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert okay
spec=R/'evidence/01_PT/017_NK-BAT-001/4200_P01706未完owner三factory製造・未実施PT仕様.md';assert not spec.exists();spec.write_text('# P01706未完owner三factory製造・未実施PT\n\nBUG2750/YKT2395、BFENCE/BSTART/IOFACT、SS333/343/SSC308。二Main三factoryの未完owner組立だけ既存ResourceScope.handoffへ接続し、元のcontext/epoch/marker/正常組立/返却ownerのretire-close/観測保持bodyを全token同一に保つ。完成ownerはtransferしcloseしない、組立失敗/nullだけ一回close・SS333 IOException/unknown複合型優先/固定secondaryへ従う。既完owner退役中不明で自動close/unlinkしない。\n\nPG28280は三wrapper逆変換で元sourcebyte完全一致・全normalbody token同一・他全領域byte不変/GJF-CSのsourcePGのみ。Maincompile/NullAway/PMD/SB/元Root-native-intent実経路wholePT/coverageはHOLD未実施、BUG2750/YKT2395 OPEN。追加必要PTはacquire前callback検査、各組立点IO/runtime/NPE/Error/null、全primary-secondary型matrix、正常transferclose0・未完close1・既ownerretire未知保持を独立oracleで元wholeTestへ対応し、旧ResourceScope単体成功をcallerへ転用しない。実factory/intent/permit/Unit/cohortの試し操作0、部分抽出/新fixture0。\n')
p=R/'documents/400_PGPT/440_判断/441_実装判断記録.md';s=p.read_text();assert max(map(int,re.findall(r'PG-D-(\d+)',s)))==356;p.write_text(s+'\n\n## PG-D-357：P01706未完owner三factoryのSS333 handoff接続（2026-11-13）\n\nBUG2750/YKT2395、SS333/343/SSC308。BackupStartIntentFiles.createService/BackupUnitStartClient.beginNative及びcreateService marker組立の三手動catch-closeを既存ResourceScope.handoffへ接続する。全正常assembly/完成ownerのretire-close/観測保持bodyを全token同一、全context/epoch/target/authority検査不変更、未完だけ一回closeと既存複合型優先を適用する。ResourceScope本体を変更せず、通常retire不明時の資源保全・UNKNOWN隔離を一般finallyへ変えない。内部資源契約具体化で新QA/SSC不要。sourcePGの逆変換/GJF-CSのみ、Maincompile/PT/coverageと実Root-native-intent経路HOLD未受入・BUG OPEN。\n');print(json.dumps(dict(actualExit=0,changedSources=2,factorySites=3,normalAssemblyBodiesUnchanged=True,originalSourceInverseExact=True,productTestsExecuted=0)))
