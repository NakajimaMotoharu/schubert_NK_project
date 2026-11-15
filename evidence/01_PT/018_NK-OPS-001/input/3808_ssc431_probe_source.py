"""One guard in Probe; original16 untouched, new graph1 and closed-failure1 independent fixtures."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pub=ld(b/'evidence/PG34522-ssc431-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC431';p=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginContextProbe.java';old=p.read_text();needle='        | DateTimeException failure) {\n      throw unavailable();';replacement='        | DateTimeException failure) {\n      JmsRequestReplyException.preserveFatal(failure);\n      throw unavailable();';assert old.count(needle)==1;p.write_text(old.replace(needle,replacement,1));test=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginContextProbeTest.java';prior=test.read_text();assert prior.count('@Test')==3
new='''
  @Test
  void probegraph001EveryCatalogFamilyPreservesFatalWipesAndReturnsTheOneSlot() throws Exception {
    for (int family = 0; family < 7; family++) {
      AssertionError fatal = new AssertionError(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
      Exception failure = probeGraphFailure(family, fatal);
      JmsRequestReplyClient oneSlot = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
      AtomicReference<byte[]> owned = new AtomicReference<>();
      var subject = new MqLoginContextProbe(oneSlot, (id, bytes) -> {
        owned.set(bytes);
        if (failure instanceof JMSException checked) throw checked;
        throw (RuntimeException) failure;
      }, CLOCK, () -> ID, WAIT);
      assertSame(fatal, assertThrows(AssertionError.class, () -> subject.isActive(CONTEXT)));
      assertArrayEquals(new byte[256], owned.get());
      assertEquals(0, oneSlot.pendingCount());
      UUID next = new UUID(0, 3);
      var recovered = new MqLoginContextProbe(oneSlot, (id, bytes) -> {
        owned.set(bytes);
        assertEquals(next, id);
        assertTrue(oneSlot.onReply(id, response(id, "a".repeat(64), FIXTURE_0000_876EEFE0, 0)));
      }, CLOCK, () -> next, WAIT);
      assertTrue(recovered.isActive(CONTEXT));
      assertArrayEquals(new byte[256], owned.get());
      assertEquals(0, oneSlot.pendingCount());
    }
  }

  private static Exception probeGraphFailure(int family, AssertionError fatal) throws Exception {
    return switch (family) {
      case 0 -> {
        var failure = new JMSException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
        failure.setLinkedException(new java.sql.SQLException(FIXTURE_SYNTHETIC_SECRET_BCCB0977, fatal));
        yield failure;
      }
      case 1 -> new JMSRuntimeException(FIXTURE_SYNTHETIC_SECRET_BCCB0977, null, fatal);
      case 2 -> new dev.codex.schubert.nk.protocol.codec.PermanentProtocolException(FIXTURE_SYNTHETIC_SECRET_BCCB0977, fatal);
      case 3 -> new IllegalArgumentException(FIXTURE_SYNTHETIC_SECRET_BCCB0977, fatal);
      case 4 -> {
        var failure = new IllegalStateException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
        failure.addSuppressed(fatal);
        yield failure;
      }
      case 5 -> new DateTimeException(FIXTURE_SYNTHETIC_SECRET_BCCB0977, fatal);
      case 6 -> {
        var full = new ReplyCorrelationRegistry(1);
        Instant at = Instant.parse("2026-09-08T00:00:00.123456Z");
        UUID occupying = new UUID(0, 99);
        full.register(occupying, at.plusSeconds(2), at).orElseThrow();
        var bounded = new JmsRequestReplyClient(full, CLOCK, 1);
        var failure = assertThrows(dev.codex.schubert.nk.web.messaging.JmsRequestReplyException.class,
            () -> bounded.exchange(ID, new byte[256], WAIT, (id, bytes) -> fail("full registry must not send")));
        failure.addSuppressed(fatal);
        assertTrue(full.cancel(occupying));
        yield failure;
      }
      default -> throw new AssertionError("unknown independent probe fixture family");
    };
  }
''';current=prior.rstrip()[:-1]+new+'}\n';current=current.replace('import static org.junit.jupiter.api.Assertions.assertNull;','import static org.junit.jupiter.api.Assertions.assertNull;\nimport static org.junit.jupiter.api.Assertions.assertSame;');test.write_text(current)
value=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginExchangeContractTest.java';value.open('x').write('''package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC431/YKT2556; PT-WEB-LOGINFAILVALUE001: closed failure cannot carry a hidden Error graph. */
final class MqLoginExchangeContractTest {
  @Test
  void loginfailvalue001ReasonAndFailureCannotRetainMutableDiagnostics() {
    assertEquals(List.of("INVALID_INPUT", "UNAVAILABLE"), Arrays.stream(MqLoginExchangeException.Reason.values()).map(Enum::name).toList());
    assertSame(MqLoginExchangeException.Reason.INVALID_INPUT, MqLoginExchangeException.Reason.valueOf("INVALID_INPUT"));
    assertSame(MqLoginExchangeException.Reason.UNAVAILABLE, MqLoginExchangeException.Reason.valueOf("UNAVAILABLE"));
    var reasons = MqLoginExchangeException.Reason.values();
    reasons[0] = MqLoginExchangeException.Reason.UNAVAILABLE;
    assertSame(MqLoginExchangeException.Reason.INVALID_INPUT, MqLoginExchangeException.Reason.values()[0]);
    for (var reason : MqLoginExchangeException.Reason.values()) {
      var failure = new MqLoginExchangeException(reason);
      assertSame(reason, failure.reason());
      assertEquals("login exchange rejected", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      var fatal = new AssertionError("public synthetic closed failure");
      failure.addSuppressed(fatal);
      assertEquals(0, failure.getSuppressed().length);
      assertThrows(IllegalStateException.class, () -> failure.initCause(fatal));
      assertNull(failure.getCause());
    }
    for (String invalid : List.of("", "UNKNOWN", "unavailable", " UNAVAILABLE "))
      assertThrows(IllegalArgumentException.class, () -> MqLoginExchangeException.Reason.valueOf(invalid));
    assertThrows(NullPointerException.class, () -> MqLoginExchangeException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new MqLoginExchangeException(null));
  }
}
''');formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p),str(test),str(value)],check=True,timeout=30);inverse=test.read_text();inverse=inverse[:inverse.index('  @Test\n  void probegraph001')].rstrip()+'\n}\n';inverse=inverse.replace('import static org.junit.jupiter.api.Assertions.assertSame;\n','',1);result=subprocess.run(formatter+['-'],input=inverse.encode(),capture_output=True,timeout=30);assert result.returncode==0 and result.stdout==prior.encode();assert p.read_text().replace(replacement,needle,1)==old
profilep=b/'evidence/PG26774-web-login-profile-v1/manifest.json';profile=ld(profilep);main=[path for path in profile['inputHashes'] if '/schubert-nk-web/src/main/' in path];assert len(main)==18;others=['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/'+n+'.java' for n in ['MqLoginClientTest','MqAuthenticationProviderTest']];assert [(r/x).read_text().count('@Test') for x in others]==[8,5] and all((r/x).read_bytes()==subprocess.check_output(['git','show','HEAD:'+x]) for x in others);tests=[dict(path=others[0],tests=8),dict(path=str(test.relative_to(r)),tests=4),dict(path=others[1],tests=5),dict(path=str(value.relative_to(r)),tests=1)];sdk=ld(b/'evidence/PG34484-ssc430-converter-source-inverse-v1/manifest.json')['sdkHashes'];extra={path:h for path,h in profile['dependencies'].items() if '/jakarta/jms/jakarta.jms-api/3.1.0/' in path};assert len(extra)==1;sdk.update(extra);assert all(sha(Path(path))==h for path,h in sdk.items());provider=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqAuthenticationProvider.java';failure=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginExchangeException.java';assert provider.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(provider.relative_to(r))]);assert 'public final class MqLoginExchangeException' in failure.read_text() and 'super("login exchange rejected", null, false, true);' in failure.read_text();out=b/'evidence/PG34524-ssc431-probe-source-inverse-v1';out.mkdir();v=dict(actualExit=0,designPublication=pub,mainSources=main,testSources=tests,inputHashes={path:sha(r/path) for path in main+[x['path'] for x in tests]},sdkHashes=sdk,oldProfileSourceReferenceOnly=ref(profilep),oldProbe3InverseFormattedExact=True,originalClient8Provider5ByteExact=True,onlyProbeGuardInverseExact=True,providerMainUnchanged=True,closedFailureFinalAndCannotRetainCauseSuppressed=True,newDefinitions=2,necessaryPriorDefinitions=16,expectedTests=18,newProbeFatalFamilies=7,eachHasOneSlotReentry=True,targets=['dev/codex/schubert/nk/web/security/'+n for n in ['MqLoginContextProbe','MqAuthenticationProvider','MqLoginExchangeException','MqLoginExchangeException$Reason']],noOldWholeJarPayloadAccess=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=18,tests=18,original16Preserved=True,sdk=len(sdk),providerChanged=False)))
