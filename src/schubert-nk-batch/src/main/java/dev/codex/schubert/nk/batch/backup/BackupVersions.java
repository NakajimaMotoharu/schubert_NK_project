package dev.codex.schubert.nk.batch.backup;

import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Nonsecret release tokens, not command output. BAK/BKO/UI251/SS341 6.4; PG165/BAT178..185. */
@NullMarked
public record BackupVersions(
    String host,
    String app,
    String schema,
    String os,
    String jdk,
    String postgresql,
    String artemis,
    String age) {
  public BackupVersions {
    Objects.requireNonNull(schema, "schema");
    for (String value : List.of(host, app, os, jdk, postgresql, artemis, age)) {
      if (!value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,127}"))
        throw new IllegalArgumentException("invalid backup release token");
    }
    if (!schema.matches("[0-9]{3}") || schema.equals("000"))
      throw new IllegalArgumentException("invalid backup schema");
  }

  @Override
  public String toString() {
    return "BackupVersions[release=<redacted>]";
  }
}
