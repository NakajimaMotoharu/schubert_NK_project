"""Preserve original six oracles and use existing finite fatal graph before HTTP side effects."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pub=ld(b/'evidence/PG34602-ssc433-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC433'
mainp=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginFailureHandler.java';before=mainp.read_text();assert before.encode()==subprocess.check_output(['git','show','HEAD:'+str(mainp.relative_to(r))]);importBefore='import dev.codex.schubert.nk.web.logging.WebSecurityAudit;';importAfter='import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;\n'+importBefore;guardBefore='    var transport = WebRequestContext.require(request);';guardAfter=guardBefore+'\n    JmsRequestReplyException.preserveFatal(failure);';docBefore='Never reads\n * or stores exception diagnostics, form data or session.';docAfter='Transiently checks fatal exception graphs,\n * never logs or stores exception diagnostics and never reads form data or session.';s=before
for a,z in [(importBefore,importAfter),(guardBefore,guardAfter),(docBefore,docAfter)]:assert s.count(a)==1;s=s.replace(a,z,1)
mainp.write_text(s);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginFailurePortTest.java';old=p.read_text();assert old.count('@Test')==6;s=old;changes=[('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;'),('final class MqLoginFailurePortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class MqLoginFailurePortTest {'),('    try (var pool = Executors.newFixedThreadPool(2)) {','    var pool = Executors.newFixedThreadPool(2);\n    try {'),('      assertEquals(16, log.events.size());\n    }','      assertEquals(16, log.events.size());\n    } finally {\n      pool.shutdownNow();\n      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));\n    }')]
for a,z in changes:assert s.count(a)==1,a;s=s.replace(a,z,1)
new='''
  @Test
  void failurefatal007EveryHttpClassificationPreservesFatalIdentityBeforeResponseAndAudit() {
    for (int kind = 0; kind < 5; kind++) {
      for (int graph = 0; graph < 3; graph++) {
        AuthenticationException failure = classifiedFailure(kind);
        AssertionError fatal = new AssertionError(MARKER);
        if (graph == 0) {
          failure.initCause(fatal);
        } else if (graph == 1) {
          failure.addSuppressed(fatal);
        } else {
          var sql = new java.sql.SQLException(MARKER, fatal);
          var jms = new jakarta.jms.JMSException(MARKER);
          jms.setLinkedException(sql);
          failure.initCause(jms);
        }
        var f = new Fixture(1);
        var log = new MemoryLog();
        assertSame(fatal, assertThrows(AssertionError.class,
            () -> handler(log).onAuthenticationFailure(f.request(), f.response(), failure)));
        assertEquals(0, f.status);
        assertTrue(f.headers.isEmpty());
        assertTrue(log.events.isEmpty());
        assertEquals(List.of("request.getAttribute"), f.calls);
      }
    }
  }

  @Test
  void failurenonfatal008CyclesRemainFiniteAndKeepExplicitHttpAuditCatalog() throws Exception {
    List<Integer> status = List.of(302, 302, 400, 403, 503);
    List<Integer> events = List.of(1, 1, 0, 1, 0);
    for (int kind = 0; kind < 5; kind++) {
      AuthenticationException failure = classifiedFailure(kind);
      RuntimeException first = new RuntimeException(MARKER);
      RuntimeException second = new RuntimeException(MARKER);
      RuntimeException shared = new RuntimeException(MARKER);
      first.initCause(second);
      second.initCause(first);
      first.addSuppressed(shared);
      failure.initCause(first);
      failure.addSuppressed(shared);
      var f = new Fixture(1);
      var log = new MemoryLog();
      handler(log).onAuthenticationFailure(f.request(), f.response(), failure);
      assertEquals(status.get(kind), f.status);
      assertEquals(events.get(kind), log.events.size());
      Map<String, String> headers = switch (kind) {
        case 0 -> Map.of(RETRY, "7", LOCATION, LOCKED_URL);
        case 1 -> Map.of(LOCATION, ERROR_URL);
        default -> Map.of();
      };
      assertEquals(headers, f.headers);
      assertSame(second, first.getCause());
      assertSame(first, second.getCause());
    }
  }

  private static AuthenticationException classifiedFailure(int kind) {
    return switch (kind) {
      case 0 -> new MqLoginLockedException(7);
      case 1 -> new BadCredentialsException(MARKER);
      case 2 -> new LoginFormRejectedException();
      case 3 -> new CaddyRequestRejectedException();
      case 4 -> new AuthenticationServiceException(MARKER);
      default -> throw new AssertionError(MARKER);
    };
  }
'''
s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(mainp),str(p)],check=True,timeout=30)
inv=p.read_text();inv=inv[:inv.index('  @Test\n  void failurefatal007')].rstrip()+'\n}\n'
for a,z in reversed(changes):
 pattern=''.join(r'\s+' if part.isspace() else re.escape(part) for part in re.split(r'(\s+)',z.strip()));matches=list(re.finditer(pattern,inv));assert len(matches)==1,(a,z);m=matches[0];inv=inv[:m.start()]+a.strip()+inv[m.end():]
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==old.encode();inv=mainp.read_text().replace(importAfter,importBefore,1).replace(guardAfter,guardBefore,1);a=inv.index('/**');z=inv.index('public final class',a);original=before[before.index('/**'):before.index('public final class')];inv=inv[:a]+original+inv[z:];assert inv==before
main=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/'+n+'.java' for n in ['MqLoginFailureHandler','MqLoginLockedException','LoginFormRejectedException','CaddyRequestRejectedException','WebRequestContext','LoginClientAddress']]+['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/'+n+'.java' for n in ['SessionStoreException','InvalidSessionRowException','SessionPrincipal']]+['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebSecurityAudit.java','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/JmsRequestReplyException.java'];assert len(main)==11
sdk=ld(b/'evidence/PG34564-ssc432-provider-source-inverse-v1/manifest.json')['sdkHashes'];extra=ld(b/'evidence/PG34304-ssc429-source-oracle-inverse-v1/manifest.json')['sdkHashes']
for marker in ['/com/google/code/gson/gson/2.14.0/','/com/google/errorprone/error_prone_annotations/2.50.0/']:
 found={n:h for n,h in extra.items() if marker in n};assert len(found)==1;sdk.update(found)
assert len(sdk)==9 and all(n.startswith(str(r.parent/'toolchain/m2/repository')+'/') and sha(Path(n))==h for n,h in sdk.items());out=b/'evidence/PG34604-ssc433-failure-source-inverse-v1';out.mkdir();v=dict(actualExit=0,designPublication=pub,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=8)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r))]},sdkHashes=sdk,originalSixAssertionsInverseFormattedExact=True,onlyMainGuardImportAndDocInverseExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newDefinitions=2,necessaryPriorDefinitions=6,expectedTests=8,syntheticGraphCases=20,targets=['dev/codex/schubert/nk/web/security/MqLoginFailureHandler'],noWholeWebOrApiJarPayloadAccess=True,original2Workers16TasksGet10Preserved=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=11,tests=8,original6InverseExact=True,sdk=9,syntheticGraphCases=20)))
