"""One meaningful SQL-fatal regression; preserves all nine existing whole test methods."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102';TC=R.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');start=ld(B/'input/2169_runref10_normal_start.json');ck=ld(S/'checkpoint.json');assert ck['ordinaryActiveGroup']==start['groupId'] and ck['ordinaryGroupNotYetClosed'];p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/RunReferencePortTest.java';old=p.read_text();assert old==subprocess.check_output(['git','show',start['source']+':'+str(p.relative_to(R))],text=True);assert len(re.findall(r'@Test\b',old))==9
addition='''  /** RUNPORT010/BUG2775: fixed provider-point table and independent fatal graph identities. */
  @Test
  void knownSqlFatalGraphsNeverBecomeFixedRepositoryFailures() {
    var points =
        new ArrayList<>(
            List.of(
                AUTO,
                READONLY,
                ISOLATION,
                PREPARE,
                TIMEOUT,
                BIND_ONE,
                BIND_TWO,
                QUERY,
                FIRST_NEXT,
                SECOND_NEXT,
                ROW_CLOSE,
                STATEMENT_CLOSE));
    points.addAll(COLUMNS);
    assertEquals(16, points.size());
    for (String point : points) {
      for (int graph = 0; graph < 3; graph++) {
        Fixture fixture = new Fixture();
        var marker = new AssertionError("own fatal provider marker");
        var provider = new SQLException("own declared provider fault");
        switch (graph) {
          case 0 -> provider.initCause(marker);
          case 1 -> provider.addSuppressed(marker);
          default -> {
            var cycle = new IllegalStateException("own cyclic provider graph");
            provider.initCause(cycle);
            cycle.initCause(provider);
            cycle.addSuppressed(marker);
          }
        }
        fixture.faults = Map.of(point, provider);
        assertSame(
            marker,
            assertThrows(
                AssertionError.class,
                () -> new RunReferenceRepository(fixture.connection()).read(RUN)),
            point);
        assertEquals(0, marker.getSuppressed().length);
        boolean statement = !List.of(AUTO, READONLY, ISOLATION, PREPARE).contains(point);
        boolean row = statement && !List.of(TIMEOUT, BIND_ONE, BIND_TWO, QUERY).contains(point);
        fixture.assertClosed(statement ? 1 : 0, row ? 1 : 0);
      }
    }
  }

''';anchor='  private static List<Throwable> providerFailures() {';assert old.count(anchor)==1;new=old.replace(anchor,addition+anchor);p.write_text(new);q=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],capture_output=True,text=True);assert q.returncode==0;assert p.read_text().replace(addition,'')==old;assert len(re.findall(r'@Test\b',p.read_text()))==10
main=[f'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/{n}.java' for n in ['RunReferenceRepository','RunReferences','BatchRun','JdbcResourceFailures','BatchRepositoryException']]+['src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java'];inventory={x['path']:x['owner'] for x in ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts']};closure=B/'evidence/PG28650-runref10-current-source-oracle-closure-v1';assert not closure.exists();closure.mkdir();wr(closure/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=start['source'],mainInputHashes={n:sha(R/n) for n in main},wholeMainReviewed=6,mainSourceOwners={n:inventory[n] for n in main},existingWholeTestOriginalSha256=hashlib.sha256(old.encode()).hexdigest(),testPath=str(p.relative_to(R)),testSha256=sha(p),existing9AllBytesInverseExactAfterGjf=True,newDefinitions=1,wholeTests=10,independentNewVectors='All16literalproviderpointtable x cause/suppressed/cycle3: originalError identity, zero suppressed when otherclose succeeds, exactresourcepost andforbidden borrowedconnectionmethods. No Productionmethod computesexpected.',existingIndependentOracles='LiteralSQL/query5/UTCbinds/16Booleanprojectiontuples/nonnull/RC-readwrite-activeTX/rowcardinality/typedcompoundfailure/selfsupp/IRQ/independentparents. Bothworkerpools Future5-finallyshutdownNow-await5 unchanged.',noGuardSdkRootOrBackendDependency=True,productTestsExecuted=0,newAcceptance=0))
spec=R/'evidence/01_PT/004_NK-DAT-001/4226_RunReference原九新一通常単体仕様.md';assert not spec.exists();spec.write_text('# RunReference原九新一の通常単体仕様\n\nNK-DAT-001/WBS-P004-03、Batch共通。DAT009/OPS009/UI251/SS3313.12・332063199・352/451。BUG2775/YKT2359。全Main6/全physical7、既RunReferencePort9の448行全body/helper/期待値を追加逆変換で保存、newRUNPORT010一つを加えwhole10だけ実行する。Root型/Guard/SDK/実DB/実Lock/FS/VM依存なし。\n\n原RUNPORT001..009：固定SQL・query5・UUIDとUTC日時二bind・16Boolean tupleの独立bit表/null/重複row/RC-active-write条件/typedSQL-unknown/selfsame/suppdisabled/借用connection操作0/IRQflag保持と二独立parent。worker二口は元通りFuture5→finallyshutdownNow-await5で後条件を確認する。新RUNPORT010：独立固定16provider点×三graph（cause/suppressed/cycle）で元Error同一性、他close正常時supp0・取得済みStatement/rowだけ一回close、Connectionの未許可操作はProxyが即失敗。期待値はproduction呼出で作らず元SS列/順序/独立点tableと固定identityによる。\n\nRootJava25/NullAway、PMD-CS-SB-GJF、source固定後whole10一回・全FESabort0・独立postによる全7class/CRC/init/全counter検査。RunReferenceRepositoryとRunReferences全二source四counter100を確認しStorage/他helperのmissは残す。旧exec合算・generated除外・coverage用無意味呼出0。全P00403他owner/実DB/原本/退役/Root/全451/正式1964-53/190受入は別、工数null。各canonicalID/Fixture/hashはPG28650。実行commandはpgpt_closed_host_profile.py prestyle/prepare/static/preflight/run <fixedsource>と独立pgpt_closed_host_post.py <sameprofile> <samefixedsource>、結果書に実OS/JDK/commit/code/XML/hashを記録する。\n')
c=ld(B/'input/2103_jdbc_known_pair8_profile.json');c.update(id='PG28662-RUNREF-ORIGINAL9-NEW1-NORMAL',productionCoreMain=start['source'],mainSources=main,testSources=[dict(path=str(p.relative_to(R)),tests=10)],expectedTests=10,newTestDefinitions=1,productOwnerByMainPath={n:inventory[n] for n in main},oracleSpecs=[ref(spec)],closureProofs=[ref(closure/'manifest.json')],sdkJars=[],physicalClasses=sorted([n.split('/src/main/java/')[1][:-5]+'.class' for n in main]+['dev/codex/schubert/nk/storage/StorageIoException$Reason.class']),targetClasses=['dev/codex/schubert/nk/batch/repository/RunReferenceRepository','dev/codex/schubert/nk/batch/repository/RunReferences'],standardCompilerSwitchMaps=[]);assert len(c['physicalClasses'])==7;c['slots']={k:'evidence/01_PT/018_NK-OPS-001/evidence/'+v for k,v in dict(prestyle='PG28652-runref10-prestyle-v1',prepare='PG28654-runref10-prepare-v1',static='PG28656-runref10-static-v1',preflight='PG28658-runref10-preflight-v1',unit='PG28662-runref10-unit-v1',post='PG28664-runref10-post-v1').items()};c['privateDirs']=dict(prepare='pg28654-runref10-prepare-v1',unit='pg28662-runref10-unit-v1');out=B/'input/2170_runref10_closed_profile.json';assert not out.exists();wr(out,c);print(json.dumps(dict(actualExit=0,original9InverseExact=True,newDefinitions=1,Main6=True,physical7=True,noGuardOrSDK=True,ProductPT=0)))
