"""Add independent Admin fatal60 vectors with default-empty controls; preserve original11 inverse exactly."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AdminPreludeJdbcPortTest.java';old=p.read_text();assert old.count('@Test')==11 and old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);s=old.replace('import static org.junit.jupiter.api.Assertions.assertEquals;','import static org.junit.jupiter.api.Assertions.assertArrayEquals;\nimport static org.junit.jupiter.api.Assertions.assertEquals;');constants='''  private static final String PUBLIC_SQL_STATE = "08006";
  private static final String PUBLIC_PRIMARY = "PUBLIC synthetic primary";
  private static final String PUBLIC_CLOSE = "PUBLIC synthetic close";
  private static final String QUERY_SUFFIX = ".executeQuery";
  private static final String CLOSE_SUFFIX = ".close";
  private static final String ROW_SUFFIX = ".row";
  private static final String STATEMENT_SUFFIX = ".statement";
  private static final String METHOD_NEXT = "next";
  private static final String METHOD_GET_LONG = "getLong";
  private static final String METHOD_WAS_NULL = "wasNull";
  private static final String METHOD_GET_OBJECT = "getObject";
  private static final String METHOD_GET_STRING = "getString";
''';marker='final class AdminPreludeJdbcPortTest {\n';assert s.count(marker)==1;s=s.replace(marker,marker+constants);hooks=[('    String faultAt = "";','    final Map<String, Throwable> injectedFailures = new HashMap<>();\n    String faultAt = "";'),('    void fault(String at) throws SQLException {','    void fault(String at) throws SQLException {\n      Throwable injected = injectedFailures.get(at);\n      if (injected instanceof SQLException sqlFailure) throw sqlFailure;\n      if (injected instanceof RuntimeException runtime) throw runtime;\n      if (injected instanceof Error fatal) throw fatal;'),('      closed.add(at);','      closed.add(at);\n      fault(at + CLOSE_SUFFIX);')]
for a,z in hooks:assert s.count(a)==1;s=s.replace(a,z)
new='''
  @Test
  void fatal001AllPreludeBodyAndOwnedCloseErrorsKeepOriginalIdentityAndOwnership() {
    var positions = new ArrayList<>(List.of("getAutoCommit", "isReadOnly"));
    List<String> labels = List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION, TOUCH);
    for (String label : labels) {
      positions.add(label + ".prepare");
      positions.add(label + (label.equals(TOUCH) ? ".executeUpdate" : QUERY_SUFFIX));
    }
    var getters = Map.of(
        CANDIDATE, List.of(METHOD_NEXT, METHOD_GET_LONG, METHOD_WAS_NULL),
        ADVISORY, List.of(METHOD_NEXT),
        USERS, List.of(METHOD_NEXT, METHOD_GET_LONG, METHOD_WAS_NULL),
        LOCKED, List.of(METHOD_NEXT, METHOD_GET_LONG, METHOD_WAS_NULL),
        AUTH_USER, List.of(METHOD_NEXT),
        AUTH_SESSION, List.of(METHOD_NEXT, METHOD_GET_OBJECT, METHOD_GET_STRING));
    for (var row : getters.entrySet()) for (String method : row.getValue()) positions.add(row.getKey() + "." + method);
    for (String label : labels) {
      positions.add(label + STATEMENT_SUFFIX + CLOSE_SUFFIX);
      if (!label.equals(TOUCH)) positions.add(label + ROW_SUFFIX + CLOSE_SUFFIX);
    }
    assertEquals(43, positions.size());
    for (String position : positions) {
      Fixture f = new Fixture();
      var fatal = new AssertionError("PUBLIC direct prelude error");
      f.injectedFailures.put(position, fatal);
      assertSame(fatal, assertThrows(AssertionError.class, () -> identity(f, Mutation.DISABLE, OptionalLong.of(20))));
      assertNull(fatal.getCause());
      assertEquals(0, fatal.getSuppressed().length);
      f.ownerUnchanged();
    }
  }

  @Test
  void fatal002WrappedSqlAndProductionDomainCleanupErrorUseOriginalFatalIdentity() {
    Fixture f = new Fixture();
    var fatal = new AssertionError("PUBLIC wrapped prelude error");
    var sql = new SQLException("PUBLIC wrapper", PUBLIC_SQL_STATE);
    sql.addSuppressed(fatal);
    f.injectedFailures.put(USERS + QUERY_SUFFIX, sql);
    assertSame(fatal, assertThrows(AssertionError.class, () -> identity(f, Mutation.DISABLE, OptionalLong.of(20))));
    assertArrayEquals(new Throwable[] {fatal}, sql.getSuppressed());
    f.ownerUnchanged();
    Fixture missing = new Fixture();
    missing.candidateRows = List.of();
    var cleanup = new AssertionError("PUBLIC missing candidate cleanup");
    missing.injectedFailures.put(CANDIDATE + ROW_SUFFIX + CLOSE_SUFFIX, cleanup);
    assertSame(cleanup, assertThrows(AssertionError.class, () -> identity(missing, Mutation.DISABLE, OptionalLong.of(20))));
    assertEquals(List.of(CANDIDATE), missing.order);
    missing.ownerUnchanged();
  }

  @Test
  void fatal003ClassifiedAndOrdinaryPrimarySecondarySelfAliasKeepTheirExactContract() {
    for (int kind = 0; kind < 5; kind++) {
      for (boolean fatalClose : List.of(false, true)) {
        Fixture f = new Fixture();
        Throwable primary = primary(kind);
        Throwable secondary = fatalClose ? new AssertionError(PUBLIC_CLOSE) : new SQLException(PUBLIC_CLOSE, PUBLIC_SQL_STATE);
        f.injectedFailures.put(USERS + QUERY_SUFFIX, primary);
        f.injectedFailures.put(USERS + STATEMENT_SUFFIX + CLOSE_SUFFIX, secondary);
        if (kind < 3 && !fatalClose) {
          infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
        } else {
          Throwable expected = kind < 3 ? secondary : primary;
          assertSame(expected, assertThrows(expected.getClass(), () -> identity(f, Mutation.DISABLE, OptionalLong.of(20))));
        }
        assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
        f.ownerUnchanged();
      }
      Fixture alias = new Fixture();
      Throwable same = primary(kind);
      alias.injectedFailures.put(USERS + QUERY_SUFFIX, same);
      alias.injectedFailures.put(USERS + STATEMENT_SUFFIX + CLOSE_SUFFIX, same);
      if (kind == 4) {
        assertSame(same, assertThrows(AssertionError.class, () -> identity(alias, Mutation.DISABLE, OptionalLong.of(20))));
      } else {
        infrastructure(alias, Mutation.DISABLE, OptionalLong.of(20));
      }
      assertEquals(0, same.getSuppressed().length);
      alias.ownerUnchanged();
    }
  }

  private static Throwable primary(int kind) {
    return switch (kind) {
      case 0 -> new SQLException(PUBLIC_PRIMARY, PUBLIC_SQL_STATE);
      case 1 -> new IllegalArgumentException(PUBLIC_PRIMARY);
      case 2 -> new java.time.DateTimeException(PUBLIC_PRIMARY);
      case 3 -> new IllegalStateException(PUBLIC_PRIMARY);
      case 4 -> new AssertionError(PUBLIC_PRIMARY);
      default -> throw new IllegalArgumentException("unsupported synthetic failure kind");
    };
  }
''';s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p)],check=True,timeout=30);s=p.read_text();inv=s[:s.index('  @Test\n  void fatal001')].rstrip()+'\n}\n';inv=inv.replace('import static org.junit.jupiter.api.Assertions.assertArrayEquals;\n','');assert inv.count(constants)==1;inv=inv.replace(constants,'')
for a,z in reversed(hooks):assert inv.count(z)==1;inv=inv.replace(z,a)
v=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert v.returncode==0 and v.stdout==old.encode();m=ld(b/'evidence/PG34246-ssc428-admin11-prepare-v1/manifest.json');assert all(sha(r/n)==h for n,h in m['inputHashes'].items() if '/src/test/java/' not in n);out=b/'evidence/PG34270-admin-fatal3-source-binding-v1';out.mkdir();(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,productionCore='fdcf397bd80a0a8d2131b465897bc29722ec3900',old11InverseFormattedExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newTestSha256=sha(p),fixedConstantsText=constants,defaultEmptyControls=hooks,allMainAndPomsUnchanged=True,expectedTests=14,newDefinitions=3,necessaryPriorDefinitions=11,currentSyntheticCases=60,syntheticDirect43=True,wrappedSqlDomain2=True,classifiedOrdinaryPrimaryAlias15=True,applicationTestsExecuted=0,formalUpdated=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,old11InverseExact=True,whole=14,newDefinitions=3,syntheticCases=60,MainChanged=False)))
