package dev.codex.schubert.nk.storage;

import org.jspecify.annotations.NullMarked;

/** Fixed non-secret YAML source contract; NK-OPS-001, SS343 §4, PG276. */
@NullMarked
public interface NonSecretConfigSource {
  ServiceConfigFiles.Contents read(ServiceConfigFiles.Service service) throws StorageIoException;
}
