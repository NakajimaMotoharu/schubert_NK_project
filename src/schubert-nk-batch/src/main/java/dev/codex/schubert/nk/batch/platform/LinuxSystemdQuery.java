package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC239 fresh fixed system-manager read, never a service action or cached authorization.
 * NK-OPS-001/OPS009/SYS002/UI251/SS343354; PT-OPS-MANAGER817001..006. One owned connection per
 * read; uncertain close retains the capability and refuses a next read.
 */
@NullMarked
final class LinuxSystemdQuery {
  enum Property {
    ID("Id", "Unit", 's'),
    LOAD("LoadState", "Unit", 's'),
    ACTIVE("ActiveState", "Unit", 's'),
    SUB("SubState", "Unit", 's'),
    PID("MainPID", "Service", 'u'),
    INVOCATION("InvocationID", "Unit", 'a'),
    GROUP("ControlGroup", "Unit", 's'),
    START("ExecMainStartTimestampMonotonic", "Service", 't');

    final String member;
    final String kind;
    final char type;

    Property(String member, String kind, char type) {
      this.member = member;
      this.kind = kind;
      this.type = type;
    }
  }

  record Owner(int pid, int uid, String unique) {
    Owner {
      Objects.requireNonNull(unique);
    }

    @Override
    public String toString() {
      return "SystemManagerOwner[REDACTED]";
    }
  }

  interface Session {
    void start(long remainingMicros) throws IOException;

    Owner owner(long remainingMicros) throws IOException;

    String read(RootStartupContext.Service service, Property property, long remainingMicros)
        throws IOException;

    void close() throws IOException;

    boolean closed();
  }

  @FunctionalInterface
  interface Factory {
    Session create() throws IOException;
  }

  private final Factory factory;
  private final LongSupplier clock;
  private final long ownerThread;
  private @Nullable Session pending;

  LinuxSystemdQuery(Factory factory, LongSupplier clock) {
    this.factory = Objects.requireNonNull(factory);
    this.clock = Objects.requireNonNull(clock);
    ownerThread = Thread.currentThread().threadId();
  }

  static LinuxSystemdQuery create() {
    return new LinuxSystemdQuery(new LinuxSystemdSession.Factory()::create, System::nanoTime);
  }

  byte[] read(RootStartupContext.Service service, String fields) throws IOException {
    Objects.requireNonNull(service);
    Objects.requireNonNull(fields);
    if (ownerThread != Thread.currentThread().threadId()
        || pending != null
        || Thread.currentThread().isInterrupted()) throw unavailable();
    Property[] properties;
    if (fields.equals("Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup"))
      properties =
          new Property[] {
            Property.ID,
            Property.LOAD,
            Property.ACTIVE,
            Property.SUB,
            Property.PID,
            Property.INVOCATION,
            Property.GROUP
          };
    else if (fields.equals("Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic"))
      properties = new Property[] {Property.ID, Property.INVOCATION, Property.PID, Property.START};
    else throw unavailable();
    long began = clock.getAsLong();
    Session session = Objects.requireNonNull(factory.create(), "fresh system manager session");
    pending = session;
    try {
      return ResourceScope.use(
          session::close,
          () -> {
            session.start(remaining(began));
            Owner first = session.owner(remaining(began));
            if (first.pid() != 1
                || first.uid() != 0
                || first.unique().length() > 64
                || !first.unique().matches(":[0-9]+\\.[0-9]+")) throw unavailable();
            var result = new StringBuilder();
            for (Property property : properties) {
              String value =
                  Objects.requireNonNull(
                      session.read(service, property, remaining(began)), "system manager property");
              if (value.length() > 4096 || !value.chars().allMatch(c -> c >= 32 && c <= 126))
                throw unavailable();
              result.append(property.member).append('=').append(value).append('\n');
              if (result.length() > 4096) throw unavailable();
            }
            if (!first.equals(session.owner(remaining(began)))) throw unavailable();
            remaining(began);
            return result.toString().getBytes(StandardCharsets.US_ASCII);
          });
    } finally {
      if (session.closed()) pending = null;
    }
  }

  private long remaining(long began) throws IOException {
    long elapsed = clock.getAsLong() - began;
    long remaining = 5_000_000_000L - elapsed;
    if (elapsed < 0 || remaining < 1000 || Thread.currentThread().isInterrupted())
      throw unavailable();
    return remaining / 1000;
  }

  static IOException unavailable() {
    return new IOException("system manager read unavailable");
  }
}
