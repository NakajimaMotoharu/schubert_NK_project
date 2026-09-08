package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import java.io.IOException;

/** DB-free manifest/physical inspection port; NK-MED-001, SS312/333, PT-MED-047..049. */
@FunctionalInterface
public interface MediaFileInspector {
  void verify(MediaDescriptor descriptor) throws IOException;
}
