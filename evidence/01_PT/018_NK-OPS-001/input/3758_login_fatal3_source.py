"""Independent finite synthetic JDBC failure semantics for original Login22; no backend operation."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationServiceMemoryPortTest.java';old=p.read_text();assert old.count('@Test')==22;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());s=old
hooks=[('    CLOSE_STATEMENT\n','    CLOSE_STATEMENT,\n    READ,\n    TRANSACTION\n'),('    Optional<Fault> fault = Optional.empty();','    Optional<Fault> fault = Optional.empty();\n    final Map<Stage, Map<Site, Throwable>> additionalFailures = new java.util.EnumMap<>(Stage.class);'),('case "getAutoCommit" -> autoCommit;','case "getAutoCommit" -> {\n                    inject(Stage.USER, Site.TRANSACTION);\n                    yield autoCommit;\n                  }'),('                      case "getString", "getObject" -> {','                      case "getString", "getObject" -> {\n                        inject(stage, Site.READ);')]
for before,after in hooks:assert s.count(before)==1,before;s=s.replace(before,after)
start=s.index('    void inject(Stage stage, Site site) throws SQLException {');end=s.index('\n    void useSecondActor()',start);originalInject=s[start:end];extra='''      var extra = Optional.ofNullable(additionalFailures.get(stage)).map(values -> values.get(site));
      if (extra.isPresent()) {
        Throwable failure = extra.orElseThrow();
        if (failure instanceof SQLException sql) throw sql;
        if (failure instanceof RuntimeException runtime) throw runtime;
        if (failure instanceof Error error) throw error;
        throw new AssertionError("unsupported additional JDBC fixture failure type");
      }
''';assert originalInject.endswith('    }\n');changedInject=originalInject[:-6]+extra+'    }\n\n    void addFault(Stage stage, Site site, Throwable failure) {\n      additionalFailures.computeIfAbsent(stage, ignored -> new java.util.EnumMap<>(Site.class)).put(site, failure);\n    }\n';s=s[:start]+changedInject+s[end:]
new='''
  @Test
  void fatal023DirectErrorIdentityAcrossEveryLoginOwnedResourceBoundary() throws Exception {
    for (Stage stage : List.of(Stage.USER, Stage.CREATE_IP, Stage.IP, Stage.UPDATE_USER, Stage.UPDATE_IP, Stage.LOGIN_AUDIT)) {
      for (Site site : List.of(Site.PREPARE, Site.EXECUTE, Site.CLOSE_STATEMENT)) {
        try (Fixture f = new Fixture()) {
          AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
          f.fault = Optional.of(new Fault(stage, site, fatal));
          assertSame(fatal, assertThrows(AssertionError.class, f::call));
          assertEquals(0, fatal.getSuppressed().length);
          f.verifyReleasedAndConsumed();
        }
      }
    }
    for (Stage stage : List.of(Stage.USER, Stage.IP)) {
      for (Site site : List.of(Site.NEXT, Site.READ, Site.CLOSE_RESULT)) {
        try (Fixture f = new Fixture()) {
          AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
          f.fault = Optional.of(new Fault(stage, site, fatal));
          assertSame(fatal, assertThrows(AssertionError.class, f::call));
          assertEquals(0, fatal.getSuppressed().length);
          f.verifyReleasedAndConsumed();
        }
      }
    }
    try (Fixture f = new Fixture()) {
      AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
      f.fault = Optional.of(new Fault(Stage.USER, Site.TRANSACTION, fatal));
      assertSame(fatal, assertThrows(AssertionError.class, f::call));
      assertTrue(f.statements.isEmpty());
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void fatal024WrappedSqlAndProductionRowcountFailurePreserveCleanupFatal() throws Exception {
    for (Stage stage : List.of(Stage.USER, Stage.IP, Stage.LOGIN_AUDIT)) {
      try (Fixture f = new Fixture()) {
        AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
        SQLException sql = new SQLException(SYNTHETIC_FAULT);
        sql.addSuppressed(fatal);
        f.fault = Optional.of(new Fault(stage, Site.EXECUTE, sql));
        assertSame(fatal, assertThrows(AssertionError.class, f::call));
        assertArrayEquals(new Throwable[] {fatal}, sql.getSuppressed());
        f.verifyReleasedAndConsumed();
      }
    }
    for (Stage stage : List.of(Stage.UPDATE_USER, Stage.UPDATE_IP, Stage.LOGIN_AUDIT)) {
      try (Fixture f = new Fixture()) {
        AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
        f.updateCounts.put(stage, 0);
        f.addFault(stage, Site.CLOSE_STATEMENT, fatal);
        assertSame(fatal, assertThrows(AssertionError.class, f::call));
        assertEquals(stage, f.prepareAttempts.getLast());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void fatal025PrimarySecondaryAndSelfaliasMatchIndependentJdkContract() throws Exception {
    for (Stage stage : List.of(Stage.UPDATE_USER, Stage.LOGIN_AUDIT)) {
      for (int kind = 0; kind < 6; kind++) {
        for (boolean fatalClose : new boolean[] {false, true}) {
          try (Fixture f = new Fixture()) {
            Throwable primary = syntheticPrimary(kind);
            Throwable secondary = fatalClose ? new AssertionError(SYNTHETIC_FAULT) : new SQLException(SYNTHETIC_FAULT);
            f.addFault(stage, Site.EXECUTE, primary);
            f.addFault(stage, Site.CLOSE_STATEMENT, secondary);
            if (kind < 4) {
              if (fatalClose) assertSame(secondary, assertThrows(AssertionError.class, f::call));
              else expectStorageFailure(f::call);
            } else assertSame(primary, assertThrows(primary.getClass(), f::call));
            assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
            assertEquals(stage, f.prepareAttempts.getLast());
            f.verifyReleasedAndConsumed();
          }
        }
        try (Fixture f = new Fixture()) {
          Throwable primary = syntheticPrimary(kind);
          f.addFault(stage, Site.EXECUTE, primary);
          f.addFault(stage, Site.CLOSE_STATEMENT, primary);
          if (primary instanceof Error) assertSame(primary, assertThrows(AssertionError.class, f::call));
          else expectStorageFailure(f::call);
          assertEquals(0, primary.getSuppressed().length);
          assertEquals(stage, f.prepareAttempts.getLast());
          f.verifyReleasedAndConsumed();
        }
      }
    }
  }

  private static Throwable syntheticPrimary(int kind) {
    return switch (kind) {
      case 0 -> new SQLException(SYNTHETIC_FAULT);
      case 1 -> new IllegalArgumentException(SYNTHETIC_FAULT);
      case 2 -> new IllegalStateException(SYNTHETIC_FAULT);
      case 3 -> new java.time.DateTimeException(SYNTHETIC_FAULT);
      case 4 -> new UnsupportedOperationException(SYNTHETIC_FAULT);
      case 5 -> new AssertionError(SYNTHETIC_FAULT);
      default -> throw new AssertionError("unknown independent fixture primary");
    };
  }
''';s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p)],check=True,timeout=30);inv=p.read_text();inv=inv[:inv.index('  @Test\n  void fatal023')].rstrip()+'\n}\n';start=inv.index('    void inject(Stage stage, Site site) throws SQLException {');end=inv.index('\n    void useSecondActor()',start);inv=inv[:start]+originalInject+inv[end:]
for before,after in reversed(hooks):
 if after.startswith('    Optional<Fault>'):after=after.replace('    final Map<Stage, Map<Site, Throwable>> additionalFailures = new java.util.EnumMap<>(Stage.class);','    final Map<Stage, Map<Site, Throwable>> additionalFailures =\n        new java.util.EnumMap<>(Stage.class);')
 assert inv.count(after)==1,(before,after);inv=inv.replace(after,before)
result=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert result.returncode==0 and result.stdout==old.encode();closure=ld(b/'evidence/PG34336-login-negative4-prepare-v2/manifest.json');assert all(sha(r/x)==h for x,h in closure['inputHashes'].items() if '/src/test/' not in x);out=b/'evidence/PG34360-login-fatal3-source-inverse-v1';out.mkdir();(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,original22InverseFormattedExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newTestSha256=sha(p),allMainAndPomsUnchanged=True,syntheticCases=67,expectedTests=25,newDefinitions=3,necessaryPriorDefinitions=22,testSource=str(p.relative_to(r)),testHooks=hooks,applicationTestsExecuted=0),indent=2)+'\n');print(json.dumps(dict(actualExit=0,original22InverseExact=True,whole=25,syntheticCases=67)))
