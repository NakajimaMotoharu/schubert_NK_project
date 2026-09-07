package dev.codex.schubert.nk.storage;

import java.util.Objects;

/** Configured OS identities, never an application user. SS333 §2/343 §2; PT-SCN-008-A01. */
public record StorageIdentity(String owner, String group) {
  public StorageIdentity {
    validate(owner);
    validate(group);
  }

  private static void validate(String name) {
    Objects.requireNonNull(name, "OS identity");
    if (!name.matches("[a-z_][a-z0-9_-]{0,31}")) {
      throw new IllegalArgumentException("invalid storage OS identity");
    }
  }

  @Override
  public String toString() {
    return "StorageIdentity[REDACTED]";
  }
}
