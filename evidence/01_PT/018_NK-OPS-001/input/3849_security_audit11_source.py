"""Preserve original ten audit oracles and add public closed-enum contract; no Main change."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebSecurityAuditPortTest.java';old=p.read_text();assert old.count('@Test')==10 and old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);s=old;changes=[('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;'),('final class WebSecurityAuditPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class WebSecurityAuditPortTest {'),('    try (var workers = Executors.newFixedThreadPool(2)) {','    var workers = Executors.newFixedThreadPool(2);\n    try {'),('      for (var future : pending) assertTrue(future.get(10, TimeUnit.SECONDS));\n    }','      for (var future : pending) assertTrue(future.get(10, TimeUnit.SECONDS));\n    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n    }')]
for a,z in changes:assert s.count(a)==1,a;s=s.replace(a,z,1)
new='''
  @Test
  void secaud011ClosedEnumsHaveExactNamesLookupAndDefensiveArrays() {
    List<String> eventNames = List.of("LOGIN_SUCCEEDED", "LOGIN_FAILED", "LOGIN_LOCKED",
        "CSRF_DENIED", "ROLE_DENIED", "PROXY_DENIED", "AUTHENTICATION_REQUIRED",
        "API_SESSION_INVALID", "LOGOUT_SUCCEEDED", "LOGOUT_REVOCATION_QUEUED");
    List<Event> events = List.of(Event.LOGIN_SUCCEEDED, Event.LOGIN_FAILED, Event.LOGIN_LOCKED,
        Event.CSRF_DENIED, Event.ROLE_DENIED, Event.PROXY_DENIED, Event.AUTHENTICATION_REQUIRED,
        Event.API_SESSION_INVALID, Event.LOGOUT_SUCCEEDED, Event.LOGOUT_REVOCATION_QUEUED);
    assertEquals(events, List.of(Event.values()));
    for (int index = 0; index < eventNames.size(); index++) {
      assertEquals(eventNames.get(index), events.get(index).name());
      assertSame(events.get(index), Event.valueOf(eventNames.get(index)));
    }
    List<String> routeNames = List.of("LOGIN", "LOGOUT", "ALL_WEB", "ADMIN_USERS", "LOGS");
    List<Route> routes = List.of(Route.LOGIN, Route.LOGOUT, Route.ALL_WEB, Route.ADMIN_USERS, Route.LOGS);
    assertEquals(routes, List.of(Route.values()));
    for (int index = 0; index < routeNames.size(); index++) {
      assertEquals(routeNames.get(index), routes.get(index).name());
      assertSame(routes.get(index), Route.valueOf(routeNames.get(index)));
    }
    Event[] eventCopy = Event.values();
    eventCopy[0] = Event.LOGIN_FAILED;
    assertSame(Event.LOGIN_SUCCEEDED, Event.values()[0]);
    Route[] routeCopy = Route.values();
    routeCopy[0] = Route.LOGS;
    assertSame(Route.LOGIN, Route.values()[0]);
    for (String unknown : List.of("UNKNOWN", "", "login", "LOGIN ")) {
      assertThrows(IllegalArgumentException.class, () -> Event.valueOf(unknown));
      assertThrows(IllegalArgumentException.class, () -> Route.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> Event.valueOf(null));
    assertThrows(NullPointerException.class, () -> Route.valueOf(null));
  }
'''
s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p)],check=True,timeout=30);inv=p.read_text();inv=inv[:inv.index('  @Test\n  void secaud011')].rstrip()+'\n}\n'
for a,z in reversed(changes):
 pattern=''.join(r'\s+' if part.isspace() else re.escape(part) for part in re.split(r'(\s+)',z.strip()));matches=list(re.finditer(pattern,inv));assert len(matches)==1;m=matches[0];inv=inv[:m.start()]+a.strip()+inv[m.end():]
value=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert value.returncode==0 and value.stdout==old.encode();main=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'+n+'.java' for n in ['logging/WebSecurityAudit','session/SessionPrincipal']];assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main);prior=ld(b/'evidence/PG34604-ssc433-failure-source-inverse-v2/manifest.json');sdk={n:h for n,h in prior['sdkHashes'].items() if '/com/google/code/gson/gson/2.14.0/' in n or '/com/google/errorprone/error_prone_annotations/2.50.0/' in n};assert len(sdk)==2 and all(sha(Path(n))==h for n,h in sdk.items());out=b/'evidence/PG34640-security-audit11-source-inverse-v1';out.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=11)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r))]},sdkHashes=sdk,originalTenAssertionsInverseFormattedExact=True,mainSourcesUnchanged=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newDefinitions=1,necessaryPriorDefinitions=10,expectedTests=11,targets=['dev/codex/schubert/nk/web/logging/WebSecurityAudit'+x for x in ['', '$Event','$Route']],noWholeWebOrApiJarPayloadAccess=True,original2Workers8TasksGet10Preserved=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=2,tests=11,original10InverseExact=True,sdk=2)))
