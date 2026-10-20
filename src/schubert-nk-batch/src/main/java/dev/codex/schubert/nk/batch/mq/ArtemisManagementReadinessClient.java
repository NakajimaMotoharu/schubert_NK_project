package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
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
  private static final long MINIMUM_REQUEST_TIMEOUT_NANOS = 1_000_000L;

  // SSC125: a synchronous borrowed timeout, never a role/credential/parent capability.
  // All existing fixed Ops/Expiry management exchanges pass through query below.
  private static final ThreadLocal<Optional<MaintenanceOwnerFrame.Guard>> PARENT_DEADLINE =
      ThreadLocal.withInitial(Optional::empty);

  @FunctionalInterface
  public interface OwnedOperation<T> {
    T execute() throws IOException;
  }

  public static <T> T withParentDeadline(
      MaintenanceOwnerFrame.Guard owner, OwnedOperation<T> operation) throws IOException {
    Objects.requireNonNull(owner, "actual same-parent deadline");
    Objects.requireNonNull(operation, "synchronous management operation");
    if (PARENT_DEADLINE.get().isPresent()) throw new IOException("management owner unavailable");
    owner.check();
    PARENT_DEADLINE.set(Optional.of(owner));
    try {
      T result = Objects.requireNonNull(operation.execute(), "owned management result");
      owner.check();
      return result;
    } finally {
      PARENT_DEADLINE.remove();
    }
  }

  static long requestTimeoutMillis() throws IOException {
    var owner = PARENT_DEADLINE.get();
    if (owner.isEmpty()) return 2000L; // Existing standalone read-only/PT contract.
    long remaining = owner.orElseThrow().remainingNanos();
    if (remaining < MINIMUM_REQUEST_TIMEOUT_NANOS)
      throw new IOException("management deadline unavailable");
    return Math.min(2000L, remaining / 1_000_000L);
  }

  private static void checkParentDeadline() throws IOException {
    var owner = PARENT_DEADLINE.get();
    if (owner.isPresent()) owner.orElseThrow().check();
  }

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

  @FunctionalInterface
  interface OperationEncoder<E extends Exception> {
    void encode(ClientMessage message, String resource, String operation, Object... arguments)
        throws E;
  }

  // PG-D453/PT-OPS-ENC001..003: the provider declares checked failures at this boundary.
  // PG-D454: preserve the unchecked category together; normalize only checked failures.
  // Error would also escape without this clause: Exception does not catch Error.
  static <E extends Exception> void encodeOperation(
      ClientMessage message,
      String resource,
      String operation,
      OperationEncoder<E> encoder,
      Object... arguments) {
    Objects.requireNonNull(encoder, "management operation encoder");
    try {
      encoder.encode(message, resource, operation, arguments);
    } catch (RuntimeException | Error unknown) {
      throw unknown;
    } catch (Exception failure) {
      throw managementFailure(failure);
    }
  }

  private static ArtemisManagementReadinessException managementFailure(Exception failure) {
    if (failure instanceof InterruptedException) Thread.currentThread().interrupt();
    return new ArtemisManagementReadinessException();
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
    inspectBroker(session);
  }

  /** SSC130: same-query verified values, immutable data only, no readiness capability. */
  public Map<String, String> inspectBroker(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    var canonical = new LinkedHashMap<String, String>();
    new ArtemisManagementReadinessClient(
            (borrowed, attribute) -> {
              Object value = reader.read(borrowed, attribute);
              // Capture a disk Number once before policy; don't retain a possibly mutable Number.
              if (attribute.equals("diskStoreUsage") && value instanceof Number number) {
                double fraction = number.doubleValue();
                value = fraction;
                canonical.put(
                    attribute, HexFormat.of().toHexDigits(Double.doubleToRawLongBits(fraction)));
              } else if (value instanceof String string) {
                canonical.put(attribute, string);
              } else if (value instanceof Boolean bit) {
                canonical.put(attribute, bit ? "1" : "0");
              } else if (value instanceof Integer || value instanceof Long) {
                canonical.put(attribute, Long.toString(((Number) value).longValue()));
              }
              return value;
            })
        .verifyValues(session);
    return Map.copyOf(canonical);
  }

  private void verifyValues(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    {
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
    encodeOperation(
        message,
        ResourceNames.BROKER,
        "getAcceptorsAsJSON",
        ManagementHelper::putOperationInvocation);
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
    encodeOperation(
        message,
        ResourceNames.BROKER,
        "getRolesAsJSON",
        ManagementHelper::putOperationInvocation,
        addressMatch);
  }

  static Object queueMetric(ClientSession session, String queue, String attribute) {
    return read(
        session,
        attribute,
        (borrowed, ignored) ->
            query(
                borrowed,
                message ->
                    ManagementHelper.putAttribute(
                        message, ResourceNames.QUEUE + queue, attribute)));
  }

  /** SSC-076: only the fixed Expiry Queue and a nonempty numeric-cutoff selector are mutable. */
  static Object expiryOperation(ClientSession session, String operation, String selector) {
    if (!("countMessages".equals(operation) || "removeMessages".equals(operation))
        || selector == null
        || !selector.matches("_AMQ_ACTUAL_EXPIRY < -?[0-9]+")) {
      throw new ArtemisManagementReadinessException();
    }
    return read(
        session,
        operation,
        (borrowed, ignored) ->
            query(borrowed, message -> putExpiryOperation(message, operation, selector)));
  }

  static void putExpiryOperation(ClientMessage message, String operation, String selector) {
    encodeOperation(
        message,
        ResourceNames.QUEUE + "nk.expiry.q",
        operation,
        ManagementHelper::putOperationInvocation,
        selector);
  }

  static void putAddressSettingsOperation(ClientMessage message, String address) {
    encodeOperation(
        message,
        ResourceNames.BROKER,
        "getAddressSettingsAsJSON",
        ManagementHelper::putOperationInvocation,
        address);
  }

  static Object read(ClientSession session, String attribute, Exchange exchange) {
    try {
      return exchange.query(session, attribute);
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
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
      checkParentDeadline();
      session.start();
      Object result;
      try (var requestor = new ClientRequestor(session, "activemq.management")) {
        var request = session.createMessage(false);
        writer.write(request);
        var reply = requestor.request(request, requestTimeoutMillis());
        checkParentDeadline();
        if (reply == null || !ManagementHelper.hasOperationSucceeded(reply))
          throw new ArtemisManagementReadinessException();
        result = ManagementHelper.getResult(reply);
      }
      checkParentDeadline();
      return result;
    } catch (RuntimeException | Error unknown) {
      throw unknown;
    } catch (Exception failure) {
      throw managementFailure(failure);
    }
  }
}
