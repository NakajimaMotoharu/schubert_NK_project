package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Map;
import java.util.TreeMap;

final class ArtifactSink {
  private static final ObjectMapper JSON =
      new ObjectMapper()
          .enable(SerializationFeature.INDENT_OUTPUT)
          .enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS);
  private final Path outputRoot;

  ArtifactSink(Path outputRoot) throws IOException {
    this.outputRoot = outputRoot.toAbsolutePath().normalize();
    Files.createDirectories(this.outputRoot.resolve("artifacts"));
    Files.createDirectories(this.outputRoot.resolve("screenshots"));
  }

  Path screenshot(String caseId, String name) {
    return outputRoot.resolve("screenshots").resolve(caseId + "-" + name + ".png");
  }

  void write(String caseId, Map<String, ?> evidence) throws IOException {
    Map<String, Object> record = new TreeMap<>();
    record.put("caseId", caseId);
    record.put("status", "PASS");
    record.putAll(evidence);
    writeJson(outputRoot.resolve("artifacts").resolve(caseId + ".json"), record);
  }

  void writeSupplemental(Map<String, ?> checks) throws IOException {
    writeJson(
        outputRoot.resolve("supplemental.json"),
        Map.of("schemaVersion", 1, "checks", checks));
  }

  void writeInventory(Map<String, ?> values) throws IOException {
    Map<String, Object> record = new TreeMap<>();
    record.put("status", "PASS");
    record.putAll(values);
    writeJson(outputRoot.resolve("inventory.json"), record);
  }

  private static void writeJson(Path target, Object value) throws IOException {
    Path temporary = target.resolveSibling(target.getFileName() + ".part");
    JSON.writeValue(temporary.toFile(), value);
    Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
  }

  static String sha256(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  static String compact(String value) {
    return value == null ? "" : value.replaceAll("\\s+", " ").strip();
  }
}
