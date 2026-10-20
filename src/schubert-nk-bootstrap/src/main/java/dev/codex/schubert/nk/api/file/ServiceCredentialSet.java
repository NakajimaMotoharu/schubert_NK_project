package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.api.maintenance.InspectorAesCredential;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Five fixed credentials for one Web/API process, loaded before external acceptance. The caller
 * closes the set; callers also erase any key/password copies. NK-OPS-001; SYS-002/004; UI243/253;
 * SS342/343 §6, SSC-081; PG284/BUG-258/259/YKT-194; PT-OPS-CREDSET-001..005.
 */
@NullMarked
public final class ServiceCredentialSet implements AutoCloseable {
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final ServiceConfigFiles.Service service;
  private final Map<ServiceCredentialId, InspectorDbCredential> passwords;
  private final Map<ServiceCredentialId, InspectorAesCredential> keys;
  private boolean closed;

  private ServiceCredentialSet(
      ServiceConfigFiles.Service service,
      Map<ServiceCredentialId, InspectorDbCredential> passwords,
      Map<ServiceCredentialId, InspectorAesCredential> keys) {
    this.service = service;
    this.passwords = passwords;
    this.keys = keys;
  }

  /** Partial material is erased before a failed load escapes. The reader owns no root lifetime. */
  public static ServiceCredentialSet load(
      ServiceCredentialReader reader, ServiceConfigFiles.Service service)
      throws ServiceCredentialException {
    Objects.requireNonNull(reader, "credential reader");
    Objects.requireNonNull(service, "service");
    var passwords =
        new EnumMap<ServiceCredentialId, InspectorDbCredential>(ServiceCredentialId.class);
    var keys = new EnumMap<ServiceCredentialId, InspectorAesCredential>(ServiceCredentialId.class);
    try {
      for (var id : ServiceCredentialId.forService(service)) {
        // The fixed catalog and its Kind enum contain exactly PASSWORD and KEY. This two-way
        // branch avoids a compiler-generated synthetic default that cannot occur or be tested.
        if (id.kind() == ServiceCredentialId.Kind.PASSWORD)
          passwords.put(id, reader.readPassword(id));
        else keys.put(id, reader.readKey(id));
      }
      return new ServiceCredentialSet(service, passwords, keys);
    } catch (ServiceCredentialException | RuntimeException | Error failure) {
      clear(passwords, keys);
      throw failure;
    }
  }

  /** Returned copy belongs to the caller and must be cleared after driver setup. */
  public char[] copyPassword(ServiceCredentialId id) {
    stateLock.lock();
    try {
      require(id, ServiceCredentialId.Kind.PASSWORD);
      return Objects.requireNonNull(passwords.get(id), "loaded password").copyPassword();
    } finally {
      stateLock.unlock();
    }
  }

  /** Returned copy belongs to the caller and must be cleared after codec setup. */
  public byte[] copyKey(ServiceCredentialId id) {
    stateLock.lock();
    try {
      require(id, ServiceCredentialId.Kind.KEY);
      return Objects.requireNonNull(keys.get(id), "loaded key").copyKey();
    } finally {
      stateLock.unlock();
    }
  }

  public String version(ServiceCredentialId id) {
    stateLock.lock();
    try {
      require(id, ServiceCredentialId.Kind.KEY);
      return Objects.requireNonNull(keys.get(id), "loaded key").version();
    } finally {
      stateLock.unlock();
    }
  }

  private void require(ServiceCredentialId id, ServiceCredentialId.Kind kind) {
    Objects.requireNonNull(id, "credential ID");
    if (closed) throw new IllegalStateException("service credentials are closed");
    if (id.service() != service || id.kind() != kind)
      throw new IllegalArgumentException("credential ID is not available for service");
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (!closed) {
        clear(passwords, keys);
        closed = true;
      }
    } finally {
      stateLock.unlock();
    }
  }

  private static void clear(
      Map<ServiceCredentialId, InspectorDbCredential> passwords,
      Map<ServiceCredentialId, InspectorAesCredential> keys) {
    passwords.values().forEach(InspectorDbCredential::close);
    keys.values().forEach(InspectorAesCredential::close);
  }

  @Override
  public String toString() {
    return "ServiceCredentialSet[REDACTED]";
  }
}
