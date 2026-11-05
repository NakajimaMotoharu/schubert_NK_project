package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Public SHA256 vectors only; no capture/preflight/promote/secret scan or original files. */
final class CharacterizationHashTest {
  @TempDir Path temporary;

  @Test
  void bothReadersMatchPublicVectorsAndTheIndependentOverBufferVector() throws Exception {
    String[][] vectors = {
      {"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
      {"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
      {"a".repeat(1_048_577), "4a3f0c0c213adea174f9a3d4c13177315b588bdb2e9c1012d3d0bf0453ca0f6a"}
    };
    Path file = temporary.resolve("public-vector.txt");
    for (String[] vector : vectors) {
      Files.writeString(file, vector[0], StandardCharsets.UTF_8);
      for (HashReader reader : readers()) assertEquals(vector[1], reader.read(file));
    }
  }

  @Test
  void nullAndUnavailableInputsNeverBecomeAnEmptyOrSuccessfulDigest() {
    for (HashReader reader : readers()) {
      assertThrows(IllegalArgumentException.class, () -> reader.read(null));
      assertThrows(IOException.class, () -> reader.read(temporary.resolve("missing")));
      assertThrows(IOException.class, () -> reader.read(temporary));
    }
  }

  private static List<HashReader> readers() {
    return List.of(GateCli::sha256, GateContractValidator::sha256);
  }

  @FunctionalInterface
  private interface HashReader {
    String read(Path file) throws IOException, NoSuchAlgorithmException;
  }
}
