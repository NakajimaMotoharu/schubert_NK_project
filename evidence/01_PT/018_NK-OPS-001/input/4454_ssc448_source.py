"""Extract same typed cleanup predicates into their repository; preserve the original behavior by inverse."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';design=json.loads((b/'evidence/PG36714-ssc448-design-main-v1/manifest.json').read_text());assert design['actualExit']==0 and not design['implementationIncluded'];name='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/RunReferenceRepository.java';p=r/name;old=p.read_text();assert old==subprocess.check_output(['git','show','e4794ddf45487268883334d0f8773d89bd47dcba:'+name],text=True)
row='''          if (row != null)
            try {
              row.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(rowFailure, secondary)) throw secondary;
            }'''
statement='''        if (statement != null)
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
          }'''
assert old.count(row)==old.count(statement)==1
helpers='''  // SSC448/BUG3126: one typed cleanup body, shared by normal and exceptional finally exits.
  private static void closeRow(@Nullable java.sql.ResultSet row, @Nullable Throwable primary)
      throws SQLException {
    if (row != null)
      try {
        row.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
      }
  }

  private static void closeStatement(
      @Nullable java.sql.PreparedStatement statement, @Nullable Throwable primary)
      throws SQLException {
    if (statement != null)
      try {
        statement.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
      }
  }

'''
new=old.replace(row,'          closeRow(row, rowFailure);').replace(statement,'        closeStatement(statement, statementFailure);').replace('  private static void require(boolean condition)',helpers+'  private static void require(boolean condition)',1)
inverse=new.replace(helpers,'',1).replace('          closeRow(row, rowFailure);',row,1).replace('        closeStatement(statement, statementFailure);',statement,1);assert inverse==old;p.write_text(new)
tp=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/RunReferenceRepositoryPureJdbcTest.java';before=tp.read_text();start=before.index('    for (int primaryKind =');end=before.index('    var both =',start);block=before[start:end];assert block.count('fixture.fail(ROW_CLOSE, 1, secondary);')==1
wrapped='    for (String closeScope : List.of(ROW_CLOSE, "statement.close")) {\n'+''.join('  '+line+'\n' for line in block.rstrip('\n').split('\n')).replace('fixture.fail(ROW_CLOSE, 1, secondary);','fixture.fail(closeScope, 1, secondary);')+'    }\n';after=before[:start]+wrapped+before[end:];assert after.count('@Test')==8;tp.write_text(after)
e=b/'evidence/PG36718-ssc448-exact-source-inverse-v1';e.mkdir();sha=lambda data:hashlib.sha256(data).hexdigest();(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,design=design,originalCore='e4794ddf45487268883334d0f8773d89bd47dcba',mainPath=name,sourceBeforeSha256=sha(old.encode()),sourceAfterBeforeFormatSha256=sha(new.encode()),exactUnformattedMainInverse=True,helperNames=['closeRow','closeStatement'],helpersArePrivateTypedAndInSameOwner=True,publicApiChanges=0,sqlBindAndOriginalBodyChanges=0,jdbcResourceFailuresChanged=False,original8DefinitionsRetained=True,fixtureChange='Extend existing full9 primary/secondary failure matrix from row-only to both row and statement scopes; expected identity/redaction/counters unchanged.',originalTestSha256=sha(before.encode()),testAfterBeforeFormatSha256=sha(after.encode()),realDbOrRootOrVmOrNativeOrHeld4Actions=0,formalAccepted=False),ensure_ascii=False,indent=2)+'\n');print('SSC448 exact typed extraction applied; inverse old Main exact; original8 definition count maintained')
