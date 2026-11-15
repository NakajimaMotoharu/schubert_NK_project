"""Two public value/display contracts with original closed projection four unchanged."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/';main=[base+n+'.java' for n in ['session/SessionPrincipal','view/TopBarViewModel','security/ClosedWebAuthentication','session/SessionStoreException','session/InvalidSessionRowException']];oldtest='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/ClosedAuthenticationValueTest.java';h=sha(r/oldtest);assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[oldtest]);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/PrincipalTopBarValueTest.java';assert not p.exists();p.write_text('''package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-WEB-PRINCIPALVALUE001002; UI222226/SS313314: public unissued synthetic values only. */
final class PrincipalTopBarValueTest {
  private static final String USERNAME = "é";
  private static final String OTHER = "other";
  private static final AuthenticationContext PUBLIC_CONTEXT = AuthenticationContext.of("a".repeat(64));
  private static final Instant AT = Instant.parse("2026-01-02T03:04:05.123Z");

  @Test
  void principalvalue001AllFourComponentsAndNfcDefineEqualityHashAndMapIdentity() {
    var value = new SessionPrincipal("e\\u0301", UserRole.USER, PUBLIC_CONTEXT, AT);
    var equal = new SessionPrincipal(USERNAME, UserRole.USER, PUBLIC_CONTEXT, AT);
    assertEquals(USERNAME, value.username());
    assertEquals(USERNAME, value.getName());
    assertEquals(UserRole.USER, value.role());
    assertEquals(PUBLIC_CONTEXT, value.authenticationContext());
    assertEquals(AT, value.loginAt());
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals(OTHER, Map.of(value, OTHER).get(equal));
    for (var changed : List.of(
        new SessionPrincipal(OTHER, UserRole.USER, PUBLIC_CONTEXT, AT),
        new SessionPrincipal(USERNAME, UserRole.ADMIN, PUBLIC_CONTEXT, AT),
        new SessionPrincipal(USERNAME, UserRole.USER, AuthenticationContext.of("b".repeat(64)), AT),
        new SessionPrincipal(USERNAME, UserRole.USER, PUBLIC_CONTEXT, AT.plusSeconds(1)))) assertNotEquals(value, changed);
    assertNotEquals(value, null);
    assertNotEquals(value, OTHER);
    assertEquals("SessionPrincipal[REDACTED]", value.toString());
  }

  @Test
  void principalvalue002TopBarHasLiteralBrandRoleAndNormalizedUsernameOnly() {
    for (var entry : Map.of(UserRole.USER, "USER", UserRole.ADMIN, "ADMIN").entrySet()) {
      var value = new SessionPrincipal("e\\u0301", entry.getKey(), PUBLIC_CONTEXT, AT);
      var display = TopBarViewModel.from(value);
      assertEquals("schubert NK", display.getBrand());
      assertEquals(USERNAME, display.getUsername());
      assertEquals(entry.getValue(), display.getRole());
      assertEquals("TopBarViewModel[REDACTED]", display.toString());
    }
    assertThrows(NullPointerException.class, () -> TopBarViewModel.from(null));
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert sha(r/oldtest)==h;prior=ld(b/'evidence/PG34564-ssc432-provider-source-inverse-v1/manifest.json');markers=['/org/springframework/spring-core/7.0.9/','/org/springframework/security/spring-security-core/7.1.1/','/commons-logging/commons-logging/1.4.0/'];sdk={n:v for n,v in prior['sdkHashes'].items() if any(m in n for m in markers)};assert len(sdk)==3 and all(sha(Path(n))==v for n,v in sdk.items());out=b/'evidence/PG34800-principal-topbar6-source-v1';out.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=2),dict(path=oldtest,tests=4)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r)),oldtest]},sdkHashes=sdk,mainSourcesUnchanged=True,oldClosedFourByteExact=True,oldTestSha256=h,newDefinitions=2,necessaryPriorDefinitions=4,expectedTests=6,targets=['dev/codex/schubert/nk/web/'+n for n in ['session/SessionPrincipal','view/TopBarViewModel']],noWholeWebOrApiJarPayloadAccess=True,applicationTestsExecuted=0,newAcceptance=0,realAuthenticationOrSessionStoreActions=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=len(main),tests=v['expectedTests'],newDefinitions=v['newDefinitions'],originalClosed4Unchanged=True,sdk=len(sdk))))
