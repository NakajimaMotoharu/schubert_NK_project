package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.file.WebNativeRuntimeCredentialFixture;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * NK-WEB-002/NK-OPS-001 / SS313314321342343352 / PT-OPS-NWEB-PART001..003. Independent
 * partial-owner oracle. Never claims native startup or provider failure coverage.
 */
final class WebNativeRuntimePartialTest {
  @TempDir Path temporary;

  private static DataSource unusedDatabase() {
    return (DataSource)
        Proxy.newProxyInstance(
            WebNativeRuntimePartialTest.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("partial owner must not borrow database");
            });
  }

  @Test
  void part001EmptyOwnerIsUnreadyAndClosesWithoutPromotingOrTouchingDependencies()
      throws Exception {
    var released = new AtomicInteger();
    var stopping = new AtomicBoolean();
    var admission =
        new ServiceStartupAdmission.Ready() {
          @Override
          public void release() {
            released.incrementAndGet();
          }

          @Override
          public Map<String, String> information() {
            return Map.of(
                "commit",
                "0000000000000000000000000000000000000001",
                "app",
                "0.1.0-SNAPSHOT",
                "config",
                "1",
                "schema",
                "027",
                "protocol",
                "0.1.0-SNAPSHOT");
          }
        };
    WebNativeRuntimeCredentialFixture.withKeys(
        temporary,
        keys -> {
          var runtime =
              new WebNativeRuntime(
                  unusedDatabase(),
                  keys,
                  WebNonSecretConfig.parse("", ""),
                  admission,
                  stopping::get);
          assertEquals("WebNativeRuntime[REDACTED]", runtime.toString());
          assertFalse(runtime.healthy());
          assertFalse(runtime.ready());
          stopping.set(true);
          assertFalse(runtime.healthy());
          stopping.set(false);
          runtime.close();
          assertFalse(runtime.healthy());
          assertFalse(runtime.ready());
          runtime.close();
          assertEquals(
              "Web startup unavailable",
              assertThrows(IOException.class, runtime::start).getMessage());
          assertEquals(0, released.get());
          assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
        });
  }

  @Test
  void part002AdmissionInfoFailureIsOriginalAndNeverPromotes() throws Exception {
    var primary = new IOException("literal admission unavailable");
    WebNativeRuntimeCredentialFixture.withKeys(
        temporary,
        keys -> {
          var admission =
              new ServiceStartupAdmission.Ready() {
                @Override
                public void release() {
                  fail("unavailable information must not promote");
                }

                @Override
                public Map<String, String> information() throws IOException {
                  throw primary;
                }
              };
          assertSame(
              primary,
              assertThrows(
                  IOException.class,
                  () ->
                      new WebNativeRuntime(
                          unusedDatabase(),
                          keys,
                          WebNonSecretConfig.parse("", ""),
                          admission,
                          () -> false)));
          assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
        });
  }

  @Test
  void part003AbsentInputsFailBeforeAnyAcquisition() throws Exception {
    WebNativeRuntimeCredentialFixture.withKeys(
        temporary,
        keys -> {
          var config = WebNonSecretConfig.parse("", "");
          var admission =
              new ServiceStartupAdmission.Ready() {
                @Override
                public void release() {
                  fail("invalid inputs must not promote");
                }

                @Override
                public Map<String, String> information() {
                  return Map.of();
                }
              };
          assertThrows(
              NullPointerException.class,
              () -> new WebNativeRuntime(null, keys, config, admission, () -> false));
          assertThrows(
              NullPointerException.class,
              () -> new WebNativeRuntime(unusedDatabase(), null, config, admission, () -> false));
          assertThrows(
              NullPointerException.class,
              () -> new WebNativeRuntime(unusedDatabase(), keys, null, admission, () -> false));
          assertThrows(
              NullPointerException.class,
              () -> new WebNativeRuntime(unusedDatabase(), keys, config, null, () -> false));
          assertThrows(
              NullPointerException.class,
              () -> new WebNativeRuntime(unusedDatabase(), keys, config, admission, null));
        });
  }
}
