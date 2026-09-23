package dev.codex.schubert.nk.batch.mq;

import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.api.core.management.ManagementHelper;
import org.apache.activemq.artemis.api.core.management.ResourceNames;

/**
 * Reads actual broker values using a caller-owned, ops-authenticated Core session. This is not the
 * complete SS321 §13 gate: journal recovery errors, acceptor, ACL, address settings and per-Queue
 * limits still require independent proof before API startup. Never use an application-role session
 * or log the provider response. NK-OPS-001; MQ-001/002/009/010,SYS-004; UI231/251; SS321/342;
 * PG235/PT-OPS-MQ-005..007.
 */
public final class ArtemisManagementReadinessClient {
  @FunctionalInterface
  interface Reader {
    Object read(ClientSession session, String attribute);
  }

  private final Reader reader;

  public ArtemisManagementReadinessClient() {
    this(ArtemisManagementReadinessClient::read);
  }

  ArtemisManagementReadinessClient(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "management reader");
  }

  /** Fail closed on missing, malformed or inconsistent effective values; borrow, never close. */
  public void verifyBroker(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    try {
      require("schubert-nk-broker".equals(reader.read(session, "name")));
      require(Boolean.TRUE.equals(reader.read(session, "persistenceEnabled")));
      require("NIO".equals(reader.read(session, "journalType")));
      require(integer(reader.read(session, "journalFileSize")) == 10 * 1024 * 1024);
      require(integer(reader.read(session, "journalMinFiles")) == 4);
      require(integer(reader.read(session, "journalPoolFiles")) == 20);
      require(integer(reader.read(session, "globalMaxSize")) == 512L * 1024 * 1024);
      require(integer(reader.read(session, "IDCacheSize")) == 20_000);
      require(Boolean.TRUE.equals(reader.read(session, "persistIDCache")));
      require(integer(reader.read(session, "maxDiskUsage")) == 90);
      Object usage = reader.read(session, "diskStoreUsage");
      require(usage instanceof Number);
      double fraction = ((Number) usage).doubleValue();
      require(fraction >= 0.0 && fraction < 0.9);
    } catch (RuntimeException failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  private static long integer(Object value) {
    if (value instanceof Integer number) return number.longValue();
    if (value instanceof Long number) return number;
    throw new ArtemisManagementReadinessException();
  }

  private static void require(boolean condition) {
    if (!condition) throw new ArtemisManagementReadinessException();
  }

  static Object read(ClientSession session, String attribute) {
    var result = new AtomicReference<>();
    try {
      ManagementHelper.doManagement(
          session,
          request -> ManagementHelper.putAttribute(request, ResourceNames.BROKER, attribute),
          reply -> result.set(ManagementHelper.getResult(reply)),
          ignored -> {
            throw new ArtemisManagementReadinessException();
          });
    } catch (Exception failure) {
      throw new ArtemisManagementReadinessException();
    }
    return result.get();
  }
}
