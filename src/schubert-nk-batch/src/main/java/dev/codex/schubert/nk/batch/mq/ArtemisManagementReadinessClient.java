package dev.codex.schubert.nk.batch.mq;

import java.util.Objects;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientRequestor;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.api.core.management.ManagementHelper;
import org.apache.activemq.artemis.api.core.management.ResourceNames;

/**
 * Reads actual broker values using a caller-owned, ops-authenticated Core session. Management
 * request/reply creates and deletes an ephemeral Address/Queue only inside the Ops namespace; it
 * does not mutate business resources. This is not the complete SS321 §13 gate: journal recovery
 * errors, acceptor, ACL, address settings and per-Queue limits still require independent proof
 * before API startup. Never use an application-role session or log the provider response.
 * NK-OPS-001; MQ-001/002/009/010,SYS-004; UI231/251; SS321/342; PG235/PT-OPS-MQ-005..007.
 */
public final class ArtemisManagementReadinessClient {
  @FunctionalInterface
  interface Reader {
    Object read(ClientSession session, String attribute);
  }

  @FunctionalInterface
  interface Exchange {
    Object query(ClientSession session, String attribute) throws InterruptedException;
  }

  @FunctionalInterface
  private interface MessageWriter {
    void write(ClientMessage message);
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
    return read(session, attribute, ArtemisManagementReadinessClient::query);
  }

  static Object addressSettings(ClientSession session, String address) {
    return read(
        session,
        address,
        (borrowed, name) -> query(borrowed, message -> putAddressSettingsOperation(message, name)));
  }

  static Object acceptors(ClientSession session) {
    return read(
        session,
        "acceptors",
        (borrowed, ignored) ->
            query(borrowed, ArtemisManagementReadinessClient::putAcceptorsOperation));
  }

  static void putAcceptorsOperation(ClientMessage message) {
    try {
      ManagementHelper.putOperationInvocation(message, ResourceNames.BROKER, "getAcceptorsAsJSON");
    } catch (Exception failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  static Object acceptorStarted(ClientSession session) {
    return read(
        session,
        "started",
        (borrowed, ignored) ->
            query(
                borrowed,
                message ->
                    ManagementHelper.putAttribute(
                        message, ResourceNames.ACCEPTOR + "core", "started")));
  }

  static Object roles(ClientSession session, String addressMatch) {
    return read(
        session,
        addressMatch,
        (borrowed, match) -> query(borrowed, message -> putRolesOperation(message, match)));
  }

  static void putRolesOperation(ClientMessage message, String addressMatch) {
    try {
      ManagementHelper.putOperationInvocation(
          message, ResourceNames.BROKER, "getRolesAsJSON", addressMatch);
    } catch (Exception failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  static void putAddressSettingsOperation(ClientMessage message, String address) {
    try {
      ManagementHelper.putOperationInvocation(
          message, ResourceNames.BROKER, "getAddressSettingsAsJSON", address);
    } catch (Exception failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  static Object read(ClientSession session, String attribute, Exchange exchange) {
    try {
      return exchange.query(session, attribute);
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new ArtemisManagementReadinessException();
    } catch (RuntimeException failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  // ClientRequestor.close declares Exception although its 2.56.0 constituent Core close methods
  // declare ActiveMQException. TWR preserves the primary error and closes the ephemeral reply
  // Address/Queue. The outer read boundary also restores interrupt from an Exchange port.
  @SuppressWarnings("try")
  private static Object query(ClientSession session, String attribute) {
    return query(
        session,
        message -> ManagementHelper.putAttribute(message, ResourceNames.BROKER, attribute));
  }

  @SuppressWarnings("try")
  private static Object query(ClientSession session, MessageWriter writer) {
    try {
      session.start();
      try (var requestor = new ClientRequestor(session, "activemq.management")) {
        var request = session.createMessage(false);
        writer.write(request);
        var reply = requestor.request(request, 2_000L);
        if (reply == null || !ManagementHelper.hasOperationSucceeded(reply))
          throw new ArtemisManagementReadinessException();
        return ManagementHelper.getResult(reply);
      }
    } catch (Exception failure) {
      throw new ArtemisManagementReadinessException();
    }
  }
}
