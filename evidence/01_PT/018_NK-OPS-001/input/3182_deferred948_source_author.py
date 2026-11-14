"""Owned finalization order, explicit memory fixture phases; no database or transaction execution."""
from pathlib import Path
import re,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'src/schubert-nk-bootstrap/src';m=d/'main/java/dev/codex/schubert/nk/migration/MigrationMasterFinalizer.java';p=m.with_name('MigrationMasterTargetPublisher.java');ft=d/'test/java/dev/codex/schubert/nk/migration/MigrationMasterFinalizerTest.java';tt=ft.with_name('MigrationMasterTargetPublisherTest.java');old={x:x.read_text() for x in [m,p,ft,tt]};out={};SQL='SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE'
def once(s,a,z):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,z)
s=old[m].replace('SSC371;','SSC371/406;').replace('PT-MIG-FINAL001..028','PT-MIG-FINAL001..030')
anchor='      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);\n      // All five checks'
s=once(s,anchor,'      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);\n      if (statement.executeUpdate("'+SQL+'") != 0\n          || statement.getWarnings() != null) throw invalid();\n      // All five checks');out[m]=s
out[p]=old[p].replace('SSC373/379/381/382/403; PT-MIG-TARGET001..034','SSC373/379/381/382/403/404/405/406; PT-MIG-TARGET001..038');assert out[p]!=old[p]
s=old[ft].replace('PT-MIG-FINAL001..028','PT-MIG-FINAL001..030');s=once(s,'  private static final String CALL_AUTO =','  private static final String FLUSH_SQL = "'+SQL+'";\n  private static final String CALL_CONSTRAINT = "constraint";\n  private static final String CALL_CONSTRAINT_WARNINGS = "constraintWarnings";\n  private static final String CALL_AUTO =');s=once(s,'    expected.addAll(MAX_SQL);','    expected.add(FLUSH_SQL);\n    expected.addAll(MAX_SQL);').replace('assertEquals(6, f.warningReads);','assertEquals(7, f.warningReads);').replace('assertEquals(16, f.sql.size());','assertEquals(17, f.sql.size());').replace('final012LastMaxMismatchCannotIssueAnyMutation','final012LastMaxMismatchCannotIssueSequenceOrAnalyze').replace('assertEquals(MAX_SQL, f.sql);','assertEquals(FLUSH_SQL, f.sql.get(0));\n    assertEquals(MAX_SQL, f.sql.subList(1, f.sql.size()));')
s=once(s,'              case CALL_OUTER_TIMEOUT -> List.of(0, 0, 1);','              case CALL_OUTER_TIMEOUT, CALL_CONSTRAINT, CALL_CONSTRAINT_WARNINGS -> List.of(0, 0, 1);')
s=once(s,'    private int badAnalyze = -1;','    private boolean badConstraintUpdate;\n    private boolean badConstraintWarning;\n    private boolean constraintWarningPending;\n    private int badAnalyze = -1;')
s=once(s,'                  case "executeUpdate":\n                    int position = analyzes;','                  case "executeUpdate":\n                    if (FLUSH_SQL.equals(args[0])) {\n                      sql.add(FLUSH_SQL);\n                      constraintWarningPending = true;\n                      hit(CALL_CONSTRAINT, 0);\n                      return badConstraintUpdate ? 1 : 0;\n                    }\n                    int position = analyzes;')
s=once(s,'                    warningReads++;\n                    int warning = analyzes - 1;','                    warningReads++;\n                    if (constraintWarningPending) {\n                      constraintWarningPending = false;\n                      hit(CALL_CONSTRAINT_WARNINGS, 0);\n                      return badConstraintWarning ? new SQLWarning("synthetic deferred constraint") : null;\n                    }\n                    int warning = analyzes - 1;')
anchor='  private static void finish(Fixture f, MigrationMasterCopyDataset declared) throws SQLException {'
new='''  @Test
  void final029DeferredConstraintMustSucceedBeforeAnyMaxOrSequence() throws Exception {
    for (boolean warning : List.of(false, true)) {
      var f = new Fixture();
      f.badConstraintUpdate = !warning;
      f.badConstraintWarning = warning;
      assertEquals(DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
      assertEquals(List.of(FLUSH_SQL), f.sql);
      assertEquals(0, f.reads);
      assertEquals(0, f.prepares);
      assertEquals(0, f.analyzes);
      assertEquals(0, f.resultCloses);
      assertEquals(0, f.preparedCloses);
      assertEquals(1, f.outerCloses);
      assertEquals(warning ? 1 : 0, f.warningReads);
    }
  }

  @Test
  void final030BothDeferredPhasesPreservePrimaryAndOuterCleanupIdentity() throws Exception {
    failuresAt(CALL_CONSTRAINT, 0, 1);
    failuresAt(CALL_CONSTRAINT_WARNINGS, 0, 1);
    var declared = normal();
    for (String phase : List.of(CALL_CONSTRAINT, CALL_CONSTRAINT_WARNINGS)) {
      for (int kind = 0; kind < failures().size(); kind++) {
        for (int cleanup = 0; cleanup <= failures().size(); cleanup++) {
          Throwable primary = failures().get(kind);
          Throwable secondary = cleanup == failures().size() ? primary : failures().get(cleanup);
          var f = new Fixture();
          f.failCall = phase;
          f.failSlot = 0;
          f.failure = primary;
          f.extraOuter = secondary;
          assertSame(primary, assertThrows(primary.getClass(), () -> finish(f, declared)));
          assertEquals(secondary == primary ? 0 : 1, primary.getSuppressed().length);
          if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);
          assertEquals(List.of(FLUSH_SQL), f.sql);
          assertEquals(0, f.reads);
          assertEquals(0, f.prepares);
          assertEquals(0, f.analyzes);
          assertEquals(1, f.outerCloses);
          assertEquals(0, f.resultCloses);
          assertEquals(0, f.preparedCloses);
        }
      }
    }
  }

''';s=once(s,anchor,new+anchor);out[ft]=s
s=old[tt].replace('PT-MIG-TARGET001..036; independent94 SQL','PT-MIG-TARGET001..038; independent95 SQL');s=once(s,'  private static final int PREPARE_END =','  private static final String FLUSH_SQL = "'+SQL+'";\n  private static final int PREPARE_END =');s=s.replace('SETVAL_FIRST = 83;','SETVAL_FIRST = 84;').replace('ANALYZE_FIRST = 88;','ANALYZE_FIRST = 89;').replace('SQL_COUNT = 94;','SQL_COUNT = 95;')
a=s.index('  private static final List<String> SQL =');z=s.index(';',a);block=s[a:z];first='          "SELECT COALESCE(MAX(id),0) FROM schubert.speakers",';assert block.count(first)==1;block=block.replace(first,'          FLUSH_SQL,\n'+first);s=s[:a]+block+s[z:]
a=s.index('  private static final List<Integer> CLOSE_SQL_PREFIX =');z=s.index(';',a);block=s[a:z];vals=[int(x) for x in re.findall(r'\d+',block)];assert vals==[6,12,13,14,16,19,23,31,43,71,78,84,85,86,87,88,94];newvals=[x if x<=78 else x+1 for x in vals];s=s[:a]+'  private static final List<Integer> CLOSE_SQL_PREFIX =\n      List.of('+', '.join(map(str,newvals))+')'+s[z:]
s=once(s,'    private int analyzes;','    private boolean badConstraintUpdate;\n    private boolean badConstraintWarning;\n    private boolean failConstraintWarning;\n    private boolean constraintWarningPending;\n    private int analyzes;')
s=once(s,'operation < PREPARE_END\n                            || List.of(27, 28).contains(operation)','operation < PREPARE_END\n                            || operation == CONTENT_END\n                            || List.of(27, 28).contains(operation)')
s=once(s,'                    recordSql(update);\n                    if (update.startsWith("ANALYZE ")) analyzes++;','                    recordSql(update);\n                    if (FLUSH_SQL.equals(update)) {\n                      constraintWarningPending = true;\n                      return badConstraintUpdate ? 1 : 0;\n                    }\n                    if (update.startsWith("ANALYZE ")) analyzes++;')
s=once(s,'                  case "getWarnings":\n                    return badWarning == analyzes - 1','                  case "getWarnings":\n                    if (constraintWarningPending) {\n                      constraintWarningPending = false;\n                      if (failConstraintWarning) throw failure;\n                      return badConstraintWarning ? new SQLWarning("synthetic deferred constraint") : null;\n                    }\n                    return badWarning == analyzes - 1')
anchor='  private static int catalogFieldCount(int table) {'
new='''  @Test
  void target037DeferredConstraintRejectionStopsBeforeSequence() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (boolean warning : List.of(false, true)) {
      var f = new Fixture();
      f.badConstraintUpdate = !warning;
      f.badConstraintWarning = warning;
      assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
      assertEquals(SQL.subList(0, CONTENT_END + 1), f.sql);
      assertEquals(REFERENCE_SCALARS_END, f.scalarReads);
      assertEquals(0, f.preparedCreates);
      assertEquals(0, f.preparedExecutions);
      assertEquals(0, f.analyzes);
      assertEquals(CLOSE_RESULTS.get(CONTENT_CLOSE), f.resultCloses);
      assertEquals(PREPARED_FIRST_CLOSE + 1, f.closeAttempts);
    }
  }

  @Test
  void target038DeferredPhaseFailureKeepsPrimaryAndCleanupIdentity() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (boolean warningPhase : List.of(false, true)) {
      for (int kind = 0; kind < failures().size(); kind++) {
        for (int cleanup = 0; cleanup <= failures().size(); cleanup++) {
          Throwable primary = failures().get(kind);
          Throwable secondary = cleanup == failures().size() ? primary : failures().get(cleanup);
          var f = new Fixture();
          f.badSql = warningPhase ? -1 : CONTENT_END;
          f.failConstraintWarning = warningPhase;
          f.failure = primary;
          f.badClose = PREPARED_FIRST_CLOSE;
          f.closeFailure = secondary;
          assertSame(primary, assertThrows(primary.getClass(), () -> workflow(publisher, f, declared)));
          assertEquals(secondary == primary ? 0 : 1, primary.getSuppressed().length);
          if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);
          assertEquals(SQL.subList(0, CONTENT_END + 1), f.sql);
          assertEquals(0, f.preparedCreates);
          assertEquals(0, f.preparedExecutions);
          assertEquals(0, f.analyzes);
          assertEquals(CLOSE_RESULTS.get(CONTENT_CLOSE), f.resultCloses);
          assertEquals(PREPARED_FIRST_CLOSE + 1, f.closeAttempts);
        }
      }
    }
  }

''';s=once(s,anchor,new+anchor);out[tt]=s
assert len(re.findall(r'@Test\b',out[ft]))==30 and len(re.findall(r'@Test\b',out[tt]))==38
# All source/slot guards complete before the first write.
e=b/'evidence/PG33086-deferred948-source-v1';assert not e.exists();e.mkdir()
for x in old:(e/('original-'+x.name+'.txt')).open('x').write(old[x]);x.write_text(out[x])
(e/'author-receipt.json').open('x').write(json.dumps(dict(actualExit=0,sourceOnly=True,newDefinitions=4,wholeExpected=948,fixedCommand=SQL,oldQueryCount=94,newQueryCount=95,sqlActuallyExecuted=False),indent=2)+'\n');print(dict(actualExit=0,changedMain=2,newDefinitions=4,whole=948))
