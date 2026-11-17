package dev.codex.schubert.nk.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.FieldCodec;
import dev.codex.schubert.nk.protocol.file.LargeResultRecordCodec;
import dev.codex.schubert.nk.protocol.file.MediaDescriptorValidator;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** Public namespace contract, SSC451/SS322/323/333. No member access override or instances. */
class ProtocolNamespaceContractTest {
  @Test
  void fieldCodecHasOnlyTheEightDesignedStaticOperations() {
    assertNamespace(
        FieldCodec.class,
        Set.of(
            "encodeText",
            "decodeText",
            "encodeNumeric",
            "decodeNumeric",
            "decodeNumericOrErrorFiller",
            "encodeBoolean",
            "decodeBoolean",
            "requireSpaces"));
  }

  @Test
  void largeResultCodecHasOnlyWriteAndDecodeOperations() {
    assertNamespace(LargeResultRecordCodec.class, Set.of("write", "decode"));
  }

  @Test
  void mediaValidatorExposesNoGrammarCacheOrInstanceOperation() {
    assertNamespace(MediaDescriptorValidator.class, Set.of("validate"));
  }

  @Test
  void semanticValidatorRetainsBothDesignedEntryPointsOnly() {
    assertNamespace(PayloadSemanticValidator.class, Set.of("validate", "validateScenarioSequence"));
  }

  private static void assertNamespace(Class<?> type, Set<String> expectedOperations) {
    assertTrue(type.isInterface(), "SSC451 non-instance namespace");
    assertEquals(0, type.getConstructors().length, "no public construction");
    assertEquals(0, type.getFields().length, "immutable grammar is not a public field");
    assertEquals(
        expectedOperations,
        Arrays.stream(type.getMethods())
            .map(java.lang.reflect.Method::getName)
            .collect(Collectors.toSet()));
    assertTrue(
        Arrays.stream(type.getMethods()).allMatch(m -> Modifier.isStatic(m.getModifiers())),
        "all public operations retain static invocation");
  }
}
