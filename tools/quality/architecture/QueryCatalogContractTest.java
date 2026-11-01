package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import org.junit.jupiter.api.Test;

/** SS332 fixed exception values only; no actual query, SQLstate mapping, DB or graph traversal. */
final class QueryCatalogContractTest {

  @Test
  void queryCatalog001LogCapacityUsesOnlyFixedCodesAndDiagnostic() {
    for (boolean capacity : new boolean[] {false, true}) {
      var value = new LogQueryException(capacity);
      catalog(value, value.resultCode(), capacity ? "9001" : "9000", "log query is unavailable");
    }
  }

  @Test
  void queryCatalog002MediaCapacityUsesOnlyFixedCodesAndDiagnostic() {
    for (boolean capacity : new boolean[] {false, true}) {
      var value = new MediaQueryException(capacity);
      catalog(value, value.resultCode(), capacity ? "9001" : "9000", "media query is unavailable");
    }
  }

  @Test
  void queryCatalog003ScenarioCapacityUsesOnlyFixedCodesAndDiagnostic() {
    for (boolean capacity : new boolean[] {false, true}) {
      var value = new ScenarioQueryException(capacity);
      catalog(value, value.resultCode(), capacity ? "9001" : "9000", "scenario query is unavailable");
    }
  }

  @Test
  void queryCatalog004UserCapacityUsesOnlyFixedCodesAndDiagnostic() {
    for (boolean capacity : new boolean[] {false, true}) {
      var value = new UserQueryException(capacity);
      catalog(value, value.resultCode(), capacity ? "9001" : "9000", "user query is unavailable");
    }
  }

  @Test
  void queryCatalog005QuestionRetainsItsRequiredCodeWithoutInventingClassification() {
    ResultCode[] codes = {ResultCode.TEMPORARY_FAILURE, ResultCode.RESOURCE_LIMIT};
    String[] wire = {"9000", "9001"};
    for (int index = 0; index < codes.length; index++) {
      var value = new QuestionQueryException(codes[index]);
      assertSame(codes[index], value.resultCode());
      catalog(value, value.resultCode(), wire[index], "question query is unavailable");
    }
    assertThrows(NullPointerException.class, () -> new QuestionQueryException(null));
  }

  private static void catalog(
      RuntimeException value, ResultCode actual, String expectedCode, String expectedMessage) {
    assertEquals(expectedCode, actual.wireValue());
    assertEquals(expectedMessage, value.getMessage());
    assertNull(value.getCause());
    assertEquals(0, value.getSuppressed().length);
  }
}
