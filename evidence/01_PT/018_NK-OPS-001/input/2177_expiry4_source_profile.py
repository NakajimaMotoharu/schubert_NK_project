"""Keep original three complete methods/helpers; add an independent fatal SQL graph regression."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';TC=R.parent/'toolchain';S=R.parent/'PMO/pgpt-completion-stage-20261102';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');start=ld(I/'2176_expiry4_normal_start.json');state=ld(S/'checkpoint.json');assert state['ordinaryActiveGroup']==start['groupId'] and state['ordinaryGroupNotYetClosed'];p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditResourceFailureTest.java';old=p.read_text();original=ld(B/'evidence/PG28630-expiry-resource-whole-transitive-closure-v1/manifest.json');assert sha(p)==original['wholeTestsAndHelper'][0]['sha256'];assert len(re.findall(r'@Test\b',old))==3
addition='''  /** EXP310004/BUG2774: independently fixed provider points and fatal graph identity. */
  @Test
  void knownSqlFatalGraphsKeepOriginalErrorAndCloseEveryAcquiredResource() {
    for (String point :
        new String[] {
          "audit.prepare",
          "statement.setQueryTimeout",
          "statement.setLong",
          "statement.setObject",
          "statement.setInt",
          "statement.executeQuery",
          "row.next",
          "row.getString",
          "row.getObject",
          "row.close",
          "statement.close"
        }) {
      for (int graph = 0; graph < 3; graph++) {
        var probe = new Probe();
        probe.auditPresent = true;
        var marker = new AssertionError("public fatal graph marker");
        var failure = new SQLException("public declared provider fixture");
        switch (graph) {
          case 0 -> failure.initCause(marker);
          case 1 -> failure.addSuppressed(marker);
          default -> {
            var cycle = new IllegalArgumentException("public cyclic provider fixture");
            failure.initCause(cycle);
            cycle.initCause(failure);
            cycle.addSuppressed(marker);
          }
        }
        probe.faults.put(point, failure);
        assertSame(
            marker,
            assertThrows(
                AssertionError.class,
                () -> new ExpiryAuditRepository(probe.connection()).read(HANDLE)),
            point);
        assertEquals(0, marker.getSuppressed().length);
        probe.assertAuditClosed();
      }
    }
  }

''';anchor='  static final class Probe {';assert old.count(anchor)==1;p.write_text(old.replace(anchor,addition+anchor));q=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],capture_output=True,text=True);assert q.returncode==0;assert p.read_text().replace(addition,'')==old;assert len(re.findall(r'@Test\b',p.read_text()))==4
oldproof=ld(B/'evidence/PG28676-guard-type-only-current-source-contract-v1/manifest.json');proof=oldproof.copy();proof.update(atJST=datetime.datetime.now().astimezone().isoformat(),source=start['source'],priorThreeWholeSourceProof=ref(B/'evidence/PG28676-guard-type-only-current-source-contract-v1/manifest.json'),existing3InverseExactAfterGjf=True,newDefinitions=1,wholeTests=4,independentNewVectors='literal11providerpoints x cause/suppressed/cycle3; originalError identity, zero suppressed when other close succeeds, all acquired owned resources exactly once, borrowedConnection forbiddenmethods throw in unchanged handler',wholeTestHashes={**oldproof['wholeTestHashes'],str(p.relative_to(R)):sha(p)});O=B/'evidence/PG28686-expiry4-current-source-oracle-closure-v1';assert not O.exists();O.mkdir();wr(O/'manifest.json',proof)
spec=R/'evidence/01_PT/017_NK-BAT-001/4229_Expiry原三新一通常単体仕様.md';assert not spec.exists();spec.write_text('# Expiry原三新一通常単体仕様\n\nNK-BAT-001/WBS-P017-11、DAT009/OPS009/UI251/SS331200・332063199・352/451、BUG2774/YKT2359。全Main11（Guard実型一つ・全miss）/全physical22、既ExpiryAuditResourceFailureTest全3/helper68の全body・入力・独立期待値を保持。新EXP310004一つは固定11provider点×cause/suppressed/cycleの元Error同一性、他close正常時supp0、全取得済みrow/statementのclose回数と借用Connection未許可操作0を独立fixtureで確認。Production呼出でexpectedを生成しない。元empty/snapshot/null全必須列/11未知provider/68typedcompoundclose/5秒/固定projectionの期待も変更0。\n\n実DB/Driver/Lock/FS/Root/Guard defaultcodeを呼ばない。Guardはsuccessfulの型でreadでは未実行、明示type-only sourceproofの全hash/全Testpath/3→4追加逆変換を固定し、Guard実probe0・全counter covered0・全missesを残す。Outerと解析専用六型はcompiler/analyzer専用、実runtime禁止。SS332SSC310§9のsuccessful二scopeは既Java25TWR/selfsupp、stage-finishの既tierは全保持。\n\nprestyle→RootJava25NullAway全Main/Testcompile→PMD/CS/SB/GJF全分類→Gitfixedwhole4一回→独立post。同source/全XML/終了0/FESabort0/全physicalCRC/classinit/coverage生counter/hashを保存。Expiry readの部分的証拠で全repository四100/全451/原190受入を宣言せず未網羅を保持する。manifest各stageにOS/JDK/tool/command/終了code/input/source/branch/hash。旧exec/別sourceの合算なし。\n')
c=ld(I/'2170_runref10_closed_profile.json');main=list(oldproof['mainInputHashes']);inventory={x['path']:x['owner'] for x in ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts']};g=ld(I/'2126_log_whole21_qualified_profile.json');physical=[n.split('/src/main/java/')[1][:-5]+'.class' for n in main];base='dev/codex/schubert/nk/batch/repository/';physical += [base+'ExpiryAuditRepository$'+n+'.class' for n in ['Stage','Snapshot','Prior','JdbcAcquire','JdbcRelease','JdbcRead']]+[base+'BatchStepResult$'+n+'.class' for n in ['Status','Reason','1']]+['dev/codex/schubert/nk/storage/StorageIoException$Reason.class','dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard.class'];assert len(physical)==22
c.update(id='PG28694-EXPIRY-ORIGINAL3-NEW1-NORMAL',mainSources=main,testSources=[dict(path=n,tests=4 if n==str(p.relative_to(R)) else 0) for n in proof['wholeTestHashes']],expectedTests=4,newTestDefinitions=1,productionCoreMain=start['source'],productOwnerByMainPath={n:inventory[n] for n in main},oracleSpecs=[ref(spec)],closureProofs=[ref(O/'manifest.json'),g['reviewedGuardSignature']['witness'],g['reviewedAnalysisOnlyContext']['witness']],physicalClasses=sorted(physical),targetClasses=[base+'ExpiryAuditRepository',base+'ExpiryAuditRepository$Snapshot'],guardTypeOnly=dict(sourceClosure=ref(O/'manifest.json')),reviewedGuardSignature=g['reviewedGuardSignature'],reviewedAnalysisOnlyContext=g['reviewedAnalysisOnlyContext'],forbiddenInitializedClasses=g['forbiddenInitializedClasses'],standardCompilerSwitchMaps=ld(I/'2055_batch_step8_profile.json')['standardCompilerSwitchMaps']);c['slots']={k:'evidence/01_PT/018_NK-OPS-001/evidence/'+v for k,v in dict(prestyle='PG28688-expiry4-prestyle-v1',prepare='PG28690-expiry4-prepare-v1',static='PG28692-expiry4-static-v1',preflight='PG28693-expiry4-preflight-v1',unit='PG28694-expiry4-unit-v1',post='PG28696-expiry4-post-v1').items()};c['privateDirs']=dict(prepare='pg28690-expiry4-prepare-v1',unit='pg28694-expiry4-unit-v1');out=I/'2177_expiry4_closed_profile.json';assert not out.exists();wr(out,c);print(json.dumps(dict(actualExit=0,original3InverseExact=True,newDefinitions=1,whole4=True,Main11=True,physical22=True,guardCodeExecutionPermitted=False,ProductPT=0)))
