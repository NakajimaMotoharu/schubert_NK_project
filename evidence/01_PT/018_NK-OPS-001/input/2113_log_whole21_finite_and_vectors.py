from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/LogCleanupTransactionPortTest.java';old=p.read_text();assert len(old.splitlines())==684 and old.count('@Test')==19;assert '## BUG-2755' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();begin=old.index('  @Test\n  void independentConnectionsInParallel');end=old.index('  @Test\n  void suppressionDisabledPrimary',begin);worker=old[begin:end];a='    try (var workers = Executors.newFixedThreadPool(2)) {\n';b='    var workers = Executors.newFixedThreadPool(2);\n    try {\n';assert worker.count(a)==1;newworker=worker.replace(a,b);closing='    }\n  }\n\n';assert newworker.endswith(closing);replacement='''    } finally {
      workers.shutdownNow();
      if (!workers.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("owned log transaction workers did not terminate");
    }
  }

''';newworker=newworker[:-len(closing)]+replacement;assert newworker.replace(b,a).replace(replacement,closing)==worker;addition='''  /** LOGTX2751001: literal fatal identity and SS341 clean-recovery resource postconditions. */
  @Test
  void fatalKnownBodyGraphPreservedAfterSuccessfulRecovery() {
    for (int edge = 0; edge < 3; edge++) {
      var f = new Fixture();
      var fatal = new AssertionError("SYNTHETIC_FATAL_BODY");
      f.failures.put(POINT_BODY, fatalSqlGraph(edge, fatal));
      assertSame(fatal, assertThrows(Error.class, () -> service().execute(f.connection, RUN)));
      assertEquals(0, fatal.getSuppressed().length);
      assertEquals(1, f.rollbacks);
      assertEquals(1, f.restores);
      assertEquals(0, f.commits);
      assertTrue(f.autoCommit);
      assertEquals("LOCK,BEGIN,BODY,ROLLBACK,RESTORE,UNLOCK", String.join(",", f.events));
      f.assertBorrowed();
    }
  }

  /** LOGTX2751002: retain fatal rollback identity while a retained lease fails disposal. */
  @Test
  void fatalKnownRollbackGraphPreservedThroughLeaseFailure() {
    for (int edge = 0; edge < 3; edge++) {
      var f = new Fixture();
      var fatal = new AssertionError("SYNTHETIC_FATAL_ROLLBACK");
      f.failures.put(POINT_BODY, new SQLException("SYNTHETIC_NORMAL_SQL_BODY"));
      f.failures.put(RECOVER_ROLLBACK, fatalSqlGraph(edge, fatal));
      assertSame(fatal, assertThrows(Error.class, () -> service().execute(f.connection, RUN)));
      fixedSecondaries(fatal, 1);
      assertEquals(1, f.rollbacks);
      assertEquals(0, f.restores);
      assertEquals(0, f.commits);
      assertFalse(f.autoCommit);
      assertEquals("LOCK,BEGIN,BODY,ROLLBACK", String.join(",", f.events));
      f.assertBorrowed();
    }
  }

  private static SQLException fatalSqlGraph(int edge, Error fatal) {
    var sql = new SQLException("SYNTHETIC_SQL_GRAPH");
    switch (edge) {
      case 0 -> sql.initCause(fatal);
      case 1 -> sql.addSuppressed(fatal);
      case 2 -> sql.setNextException(new SQLException("SYNTHETIC_SQL_LINK", fatal));
      default -> throw new IllegalArgumentException("unknown fixture graph edge");
    }
    return sql;
  }

''';anchor='  private static LogCleanupService service() {\n';assert old.count(anchor)==1;new=old[:begin]+newworker+old[end:];new=new.replace(anchor,addition+anchor);assert new.replace(addition,'').replace(newworker,worker)==old;O=B/'evidence/PG28402-log-original19-new2-finite-transform-v1';assert not O.exists();O.mkdir();(O/'test-before.txt').write_text(old);p.write_text(new);command=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)];result=subprocess.run(command,capture_output=True,text=True);assert result.returncode==0;after=p.read_text();assert after.replace(addition,'').replace(newworker,worker)==old;originalMethods=re.findall(r'@Test\s*void (\w+)\s*\(',old);afterMethods=re.findall(r'@Test\s*void (\w+)\s*\(',after);assert len(originalMethods)==19 and len(afterMethods)==21 and set(originalMethods)<set(afterMethods);assert newworker.count('future.get(3, TimeUnit.SECONDS)')==worker.count('future.get(3, TimeUnit.SECONDS)')==1;m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),test=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),wholeOriginal19InverseByteExactAfterFormat=True,originalMethods=originalMethods,newMethodIds={'LOGTX2751001':'fatalKnownBodyGraphPreservedAfterSuccessfulRecovery','LOGTX2751002':'fatalKnownRollbackGraphPreservedThroughLeaseFailure'},newProductTestDefinitions=2,expectedWholeTests=21,finiteWorker=dict(originalFutureSeconds=3,originalTasks=20,finallyShutdownNow=True,awaitSeconds=10,onceOnlyPoolClose=True),format=dict(command=command,actualExit=0,stdout=result.stdout,stderr=result.stderr),MainChanged=False,productTestsExecuted=0,bug='BUG2755',horizontal='YKT2387_OPEN',actualDbRootNativeOrHeldOperations=0,verifierSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,original19InverseExact=True,newDefinitions=2,wholeTests=21)))
