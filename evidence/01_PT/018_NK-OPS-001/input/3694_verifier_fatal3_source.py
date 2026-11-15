"""Add independent synthetic failure3 and restore original9 exactly through explicit constant/control inverse."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationVerifierJdbcPortTest.java';old=p.read_text();assert old.count('@Test')==9 and old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);s=old.replace('import static org.junit.jupiter.api.Assertions.assertEquals;','import static org.junit.jupiter.api.Assertions.assertArrayEquals;\nimport static org.junit.jupiter.api.Assertions.assertEquals;');names={'getAutoCommit':'JDBC_GET_AUTO_COMMIT','prepareStatement':'JDBC_PREPARE_STATEMENT','setString':'JDBC_SET_STRING','executeQuery':'JDBC_EXECUTE_QUERY','getObject':'JDBC_GET_OBJECT','getString':'JDBC_GET_STRING'}
for literal,name in names.items():s=s.replace('"'+literal+'"',name)
constants=''.join('  private static final String '+name+' = "'+literal+'";\n' for literal,name in names.items())+'  private static final String PUBLIC_SQL_STATE = "08006";\n  private static final String CLOSE_SUFFIX = ".close";\n';s=s.replace('final class AuthenticationVerifierJdbcPortTest {','final class AuthenticationVerifierJdbcPortTest {\n'+constants);hooks=[('    String failMethod = "";','    final Map<String, Throwable> injectedFailures = new HashMap<>();\n    String failMethod = "";'),('    void fault(String method) throws SQLException {','    void fault(String method) throws SQLException {\n      Throwable injected = injectedFailures.get(method);\n      if (injected instanceof SQLException sqlFailure) throw sqlFailure;\n      if (injected instanceof RuntimeException runtime) throw runtime;\n      if (injected instanceof Error fatal) throw fatal;'),('      closes.add(name);','      closes.add(name);\n      fault(name + CLOSE_SUFFIX);')]
for a,z in hooks:assert s.count(a)==1;s=s.replace(a,z)
new='''
  @Test
  void fatal001DirectBodyAndOwnedCloseErrorsKeepIdentityInBothVerificationModes() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      List<String> body = inspect
          ? List.of(JDBC_GET_AUTO_COMMIT, "isReadOnly", JDBC_PREPARE_STATEMENT, JDBC_SET_STRING, JDBC_EXECUTE_QUERY, "next", JDBC_GET_OBJECT, JDBC_GET_STRING)
          : List.of(JDBC_GET_AUTO_COMMIT, JDBC_PREPARE_STATEMENT, JDBC_SET_STRING, JDBC_EXECUTE_QUERY, "next", JDBC_GET_OBJECT, JDBC_GET_STRING, "setObject", "executeUpdate");
      List<String> closes = inspect ? List.of(SESSION_ROW, SESSION_STATEMENT) : List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT, TOUCH_STATEMENT);
      var positions = new ArrayList<>(body);
      for (String name : closes) positions.add(name + CLOSE_SUFFIX);
      for (String position : positions) {
        var f = new Fixture();
        f.readOnly = inspect;
        var fatal = new AssertionError("PUBLIC direct error");
        f.injectedFailures.put(position, fatal);
        assertSame(fatal, assertThrows(AssertionError.class, () -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); }));
        assertNull(fatal.getCause());
        assertEquals(0, fatal.getSuppressed().length);
        f.owned();
      }
    }
  }

  @Test
  void fatal002SqlAndDomainFailureSuppressedFatalUsesTheOriginalErrorInstance() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      var f = new Fixture();
      f.readOnly = inspect;
      var fatal = new AssertionError("PUBLIC wrapped error");
      var sql = new SQLException("PUBLIC wrapper", PUBLIC_SQL_STATE);
      sql.addSuppressed(fatal);
      f.injectedFailures.put(JDBC_GET_OBJECT, sql);
      assertSame(fatal, assertThrows(AssertionError.class, () -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); }));
      assertArrayEquals(new Throwable[] {fatal}, sql.getSuppressed());
      f.owned();
      var denied = new Fixture();
      denied.readOnly = inspect;
      denied.fields.put(COL_REVOKED, true);
      var cleanupError = new AssertionError("PUBLIC domain cleanup error");
      denied.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, cleanupError);
      assertSame(cleanupError, assertThrows(AssertionError.class, () -> { if (inspect) verifier.inspectReadOnly(denied.connection(), INPUT, NOW); else verifier.verify(denied.connection(), INPUT, NOW); }));
      assertFalse(denied.sql.contains(TOUCH));
      denied.owned();
    }
  }

  @Test
  void fatal003PrimarySecondaryAndSelfAliasPreserveOriginalFailureGraphInBothModes() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
        for (boolean fatalClose : List.of(false, true)) {
          var f = new Fixture();
          f.readOnly = inspect;
          Throwable primary = primaryKind == 0 ? new SQLException("PUBLIC body", PUBLIC_SQL_STATE) : primaryKind == 1 ? new IllegalStateException("PUBLIC body") : new AssertionError("PUBLIC body");
          Throwable secondary = fatalClose ? new AssertionError("PUBLIC close") : new SQLException("PUBLIC close", PUBLIC_SQL_STATE);
          f.injectedFailures.put(JDBC_GET_OBJECT, primary);
          f.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, secondary);
          if (primaryKind == 0 && !fatalClose) {
            fixedInfrastructure(() -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); });
          } else {
            Throwable expected = primaryKind == 0 ? secondary : primary;
            assertSame(expected, assertThrows(expected.getClass(), () -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); }));
          }
          assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
          f.owned();
        }
      }
      var alias = new Fixture();
      alias.readOnly = inspect;
      var same = new SQLException("PUBLIC same alias", PUBLIC_SQL_STATE);
      alias.injectedFailures.put(JDBC_GET_OBJECT, same);
      alias.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, same);
      var observed = assertThrows(IllegalArgumentException.class, () -> { if (inspect) verifier.inspectReadOnly(alias.connection(), INPUT, NOW); else verifier.verify(alias.connection(), INPUT, NOW); });
      assertSame(same, observed.getCause());
      assertEquals(0, same.getSuppressed().length);
      alias.owned();
    }
  }
''';s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p)],check=True,timeout=30);s=p.read_text();inv=s[:s.index('  @Test\n  void fatal001')].rstrip()+'\n}\n';inv=inv.replace('import static org.junit.jupiter.api.Assertions.assertArrayEquals;\n','');assert inv.count(constants)==1;inv=inv.replace(constants,'')
for a,z in reversed(hooks):assert inv.count(z)==1;inv=inv.replace(z,a)
for literal,name in names.items():inv=re.sub(r'\b'+name+r'\b','"'+literal+'"',inv)
v=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert v.returncode==0 and v.stdout==old.encode();m=ld(b/'evidence/PG34158-ssc427-verifier8-prepare-v2/manifest.json');assert all(sha(r/n)==h for n,h in m['inputHashes'].items() if '/src/test/java/' not in n);out=b/'evidence/PG34200-verifier-fatal3-source-binding-v1';out.mkdir();(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,productionCore='08eef7ec152adc5d886040bdef14188beaeea6ff',old9InverseFormattedExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newTestSha256=sha(p),fixedMethodNameConstants=names,fixedConstantsText=constants,defaultEmptyControls=hooks,allMainAndPomsUnchanged=True,expectedTests=12,newDefinitions=3,necessaryPriorDefinitions=9,originalStartSyntheticCases40Frozen=True,additionalDomainGeneratedCleanupCases=2,currentSyntheticCases=42,additionWithinSameExistingBudget=True,applicationTestsExecuted=0,formalUpdated=False),ensure_ascii=False,indent=2)+'\n');spec=b/'4313_VerifierJDK合成例外三・通常十二仕様.md';spec.write_text(spec.read_text()+'\n実装詳細補足: 元群開始の合成40条件は履歴保持。業務のrevoked判定からproduction自身が発行するAuthenticationContextExceptionへrow close Errorがsuppressedになる両mode2条件も同じFATAL002内へ追加し、現42条件（direct24/wrappedSQL2/domain-generated2/primary-alias14）。新Test定義3/全12・見積.15/.45/1.35 cap2は変更0、追加課金/別群/原9期待変更0。\n');print(json.dumps(dict(actualExit=0,old9InverseExact=True,whole=12,newDefinitions=3,originalPlannedFaultCases=40,currentFaultCases=42,MainChanged=False)))
