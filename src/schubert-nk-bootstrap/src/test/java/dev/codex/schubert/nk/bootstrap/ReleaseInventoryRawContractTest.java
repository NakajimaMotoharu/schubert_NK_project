package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-BOM-RAW001..002 / SS343 11.1 / PG-D1174. Public claims only, no authority or file IO. */
class ReleaseInventoryRawContractTest {
  private static final String DIGEST = "a".repeat(64);
  private static final String ARTIFACT_PATH = "api/VERSION";
  private static final String COORDINATE = "org.example:demo:1.0";
  private static final String API_LIBRARY = "api/lib/demo-1.0.jar";
  private static final String WEB_LIBRARY = "web/lib/demo-1.0.jar";

  @Test
  void raw001ArtifactIdentityIncludesAllThreePublicClaims() {
    var value = new ReleaseInventory.Artifact(ARTIFACT_PATH, 3, DIGEST);
    var sameValue = new ReleaseInventory.Artifact(ARTIFACT_PATH, 3, "a".repeat(64));
    assertEquals(value, value);
    assertEquals(value, sameValue);
    assertEquals(sameValue, value);
    assertEquals(1840924000, value.hashCode());
    assertEquals(1840924000, sameValue.hashCode());
    assertEquals("Artifact[path=api/VERSION, size=3, sha256=" + DIGEST + "]", value.toString());
    assertEquals(ARTIFACT_PATH, value.path());
    assertEquals(3, value.size());
    assertEquals(DIGEST, value.sha256());
    assertFalse(value.equals(null));
    assertFalse(value.equals("other-type"));
    assertNotEquals(value, new ReleaseInventory.Artifact("web/VERSION", 3, DIGEST));
    assertNotEquals(value, new ReleaseInventory.Artifact(ARTIFACT_PATH, 4, DIGEST));
    assertNotEquals(value, new ReleaseInventory.Artifact(ARTIFACT_PATH, 3, "b".repeat(64)));
  }

  @Test
  void raw002DependencyValueOwnsOrderedPathsAndRetainsNoCallerMutation() {
    List<String> expected = List.of(API_LIBRARY, WEB_LIBRARY);
    List<String> caller = new ArrayList<>(expected);
    var value = new ReleaseInventory.Dependency(COORDINATE, caller);
    caller.clear();
    assertEquals(expected, value.paths());
    assertThrows(
        UnsupportedOperationException.class,
        () -> value.paths().add("operations/lib/demo-1.0.jar"));
    var sameValue = new ReleaseInventory.Dependency(COORDINATE, List.of(API_LIBRARY, WEB_LIBRARY));
    assertEquals(value, value);
    assertEquals(value, sameValue);
    assertEquals(sameValue, value);
    assertEquals(2100783537, value.hashCode());
    assertEquals(2100783537, sameValue.hashCode());
    assertEquals(COORDINATE, value.coordinate());
    assertEquals(
        "Dependency[coordinate=org.example:demo:1.0, paths=[api/lib/demo-1.0.jar, web/lib/demo-1.0.jar]]",
        value.toString());
    assertFalse(value.equals(null));
    assertFalse(value.equals("other-type"));
    assertNotEquals(value, new ReleaseInventory.Dependency("org.example:demo:1.1", expected));
    assertNotEquals(value, new ReleaseInventory.Dependency(COORDINATE, List.of(API_LIBRARY)));
  }
}
