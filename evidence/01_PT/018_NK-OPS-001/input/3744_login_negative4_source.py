"""Four independently specified Login repository/audit boundary definitions, original eighteen exact."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationServiceMemoryPortTest.java';old=p.read_text();assert old.count('@Test')==18;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());hooks=[('    boolean absent;','    boolean absent;\n    boolean autoCommit;\n    boolean ipAbsent;\n    boolean userWindowAbsent;\n    Optional<String> nullIpColumn = Optional.empty();\n    final Map<Stage, Integer> updateCounts = new HashMap<>();'),('case "getAutoCommit" -> false;','case "getAutoCommit" -> autoCommit;'),('                      yield 1;','                      yield updateCounts.getOrDefault(stage, 1);'),('          row.put("failure_window_started_at", userWindow.atOffset(ZoneOffset.UTC));','          row.put("failure_window_started_at", userWindowAbsent ? null : userWindow.atOffset(ZoneOffset.UTC));'),('        if (stage == Stage.IP) {','        if (stage == Stage.IP) {\n          if (ipAbsent) return List.of();'),('          row.put("window_started_at", ipWindow.atOffset(ZoneOffset.UTC));','          row.put("window_started_at", ipWindow.atOffset(ZoneOffset.UTC));\n          nullIpColumn.ifPresent(value -> row.put(value, null));')];s=old
for a,z in hooks:assert s.count(a)==1,a;s=s.replace(a,z)
new='''
  @Test
  void negative019DirectRequiredArgumentsKeyBytesAndTransactionBoundary() throws Exception {
    try (Fixture f = new Fixture()) {
      for (int missing = 0; missing < 4; missing++) {
        int slot = missing;
        assertThrows(NullPointerException.class, () -> f.attempts.lockForAttempt(
            slot == 0 ? null : f.connection, slot == 1 ? null : KEY,
            slot == 2 ? null : CLIENT, slot == 3 ? null : AT));
      }
      for (String invalid : List.of("", "x".repeat(97), "é".repeat(49)))
        assertThrows(IllegalArgumentException.class, () -> f.attempts.lockForAttempt(f.connection, invalid, CLIENT, AT));
      assertTrue(f.statements.isEmpty());
    }
    for (String boundary : List.of("a", "x".repeat(96), "é".repeat(48))) {
      try (Fixture f = new Fixture()) {
        f.expectedKey = boundary;
        var result = f.attempts.lockForAttempt(f.connection, boundary, CLIENT, AT);
        assertEquals(7, result.account().orElseThrow().identity().userId());
        assertEquals(List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages());
        for (var statement : f.statements) {
          assertEquals(1, statement.closed);
          for (var cursor : statement.cursors) assertEquals(1, cursor.closed);
        }
      }
    }
    try (Fixture f = new Fixture()) {
      f.autoCommit = true;
      expectStorageFailure(f::call);
      var locked = new LockedLoginAttempt(CLIENT.getHostAddress(), Optional.empty(),
          new LoginAttemptState(LoginAttemptKind.IP, 0, Optional.of(AT), Optional.empty()));
      expectStorageFailure(() -> f.attempts.recordSuccess(f.connection, locked, AT));
      expectStorageFailure(() -> f.attempts.recordFailure(f.connection, locked, AT));
      assertTrue(f.statements.isEmpty());
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void negative020PersistedRoleAndStatusHashCollisionsNeverAcquireAuthority() throws Exception {
    assertEquals(2614219, "USER".hashCode());
    assertEquals(2614219, "V4ER".hashCode());
    assertEquals(62130991, "ADMIN".hashCode());
    assertEquals(62130991, "B%MIN".hashCode());
    assertEquals("ACTIVE".hashCode(), "B$TIVE".hashCode());
    assertEquals("DISABLED".hashCode(), "E*SABLED".hashCode());
    for (String role : List.of("V4ER", "B%MIN", "", "user", " USER ")) {
      try (Fixture f = new Fixture()) {
        f.role = role;
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
    for (String status : List.of("B$TIVE", "E*SABLED", "", "active", " ACTIVE ")) {
      try (Fixture f = new Fixture()) {
        f.status = status;
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void negative021MissingIpRequiredColumnsAndOptionalUserWindow() throws Exception {
    for (String missing : List.of("ROW", "failed_count", "window_started_at")) {
      try (Fixture f = new Fixture()) {
        f.ipAbsent = missing.equals("ROW");
        if (!f.ipAbsent) f.nullIpColumn = Optional.of(missing);
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
    try (Fixture f = new Fixture()) {
      f.userWindowAbsent = true;
      f.matches = false;
      assertEquals(ResultCode.AUTHENTICATION_FAILED, f.call().resultCode());
      assertEquals(1, f.param(Stage.UPDATE_USER, 1));
      assertEquals(AT.atOffset(ZoneOffset.UTC), f.param(Stage.UPDATE_USER, 2));
      f.verifyAudit("0101", "PASSWORD_MISMATCH", "LOGIN_FAILED", DENIED, 0, false);
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void negative022EveryCriticalUpdateRequiresExactlyOneRowInEitherOutcome() throws Exception {
    for (Stage stage : List.of(Stage.UPDATE_USER, Stage.UPDATE_IP, Stage.LOGIN_AUDIT)) {
      for (int count : new int[] {0, 2}) {
        for (boolean matches : new boolean[] {false, true}) {
          try (Fixture f = new Fixture()) {
            f.matches = matches;
            f.updateCounts.put(stage, count);
            expectStorageFailure(f::call);
            assertEquals(stage, f.prepareAttempts.getLast());
            assertEquals(1, f.count(stage));
            f.verifyReleasedAndConsumed();
          }
        }
      }
    }
  }
''';s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p)],check=True,timeout=30);inv=p.read_text();inv=inv[:inv.index('  @Test\n  void negative019')].rstrip()+'\n}\n'
for before,after in reversed(hooks):
 if 'failure_window_started_at' in before:after='''          row.put(
              "failure_window_started_at",
              userWindowAbsent ? null : userWindow.atOffset(ZoneOffset.UTC));'''
 assert inv.count(after)==1,(before,after);inv=inv.replace(after,before)
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==old.encode();closure=ld(b/'evidence/PG34304-ssc429-source-oracle-inverse-v1/manifest.json');assert all(sha(r/x)==h for x,h in closure['inputHashes'].items() if '/src/main/' in x);out=b/'evidence/PG34330-login-negative4-source-inverse-v1';out.mkdir();v=dict(actualExit=0,original18InverseFormattedExact=True,originalTestSha256=hashlib.sha256(old.encode()).hexdigest(),mainSourcesUnchangedExact=True,baseClosure=closure,expectedTests=22,newDefinitions=4,necessaryPriorDefinitions=18,inputHashes={**{x:h for x,h in closure['inputHashes'].items() if '/src/main/' in x},str(p.relative_to(r)):sha(p)},testSource=str(p.relative_to(r)),testHooks=hooks,applicationTestsExecuted=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=22,original18InverseExact=True)))
