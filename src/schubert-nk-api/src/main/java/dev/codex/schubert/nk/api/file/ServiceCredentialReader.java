package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Borrowed-root raw credential reader for one service. The caller owns the returned bytes and
 * clears them after strict password/key decoding; this does not create a DB/JMS client or process.
 * NK-OPS-001; SYS-002/004; UI243/253; SS343 §6; SSC-081; PG281/PT-OPS-CREDREAD-001..008.
 */
@NullMarked
public final class ServiceCredentialReader {
  private final ServiceConfigFiles.Service service;
  private final InspectorCredentialLoader reader;

  public ServiceCredentialReader(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      ServiceConfigFiles.Service service) {
    this.service = Objects.requireNonNull(service, "service");
    reader = new InspectorCredentialLoader(root, security);
  }

  ServiceCredentialReader(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      ServiceConfigFiles.Service service,
      InspectorCredentialLoader.Io io) {
    this.service = Objects.requireNonNull(service, "service");
    reader = new InspectorCredentialLoader(root, security, io);
  }

  /**
   * Mandatory fixed ID only; never returns partial bytes on missing, admission or close failure.
   */
  public byte[] read(ServiceCredentialId credential) throws ServiceCredentialException {
    Objects.requireNonNull(credential, "credential ID");
    if (credential.service() != service) throw new ServiceCredentialException();
    try {
      return reader.readService(credential);
    } catch (InspectorCredentialException failure) {
      throw new ServiceCredentialException();
    }
  }
}
