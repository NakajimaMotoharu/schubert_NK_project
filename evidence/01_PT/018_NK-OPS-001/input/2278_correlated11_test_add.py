"""Add two literal ordinary tool oracles to unchanged whole9; no Main/capture/backend actions."""
from pathlib import Path
import hashlib,json
R=Path.cwd();p=R/'program/characterization/tests/java/dev/codex/schubert/characterization/CorrelatedLogEvidenceValidatorTest.java';old=p.read_text();assert old.count('@Test')==9
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG29276-correlated11-source-oracles-v1';assert not out.exists();out.mkdir();(out/'original-whole9.java.txt').write_text(old)
addition='''  /** PT-CHR-LOG-COR-010: approved literal pairs, one initial event per operation. */
  @Test
  void qa054ActionPairsAreOncePerOperationAndMenuRequiresExactHttpAndWitnesses() {
    ObjectNode healthy = actionFixture();
    assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(healthy));
    assertEquals("MENU_VIEWED", healthy.at("/expected/nk/2/action").asText());
    assertEquals("LOG_SEARCHED", healthy.at("/expected/nk/3/action").asText());
    assertEquals(6, healthy.at("/expected/nk").size());
    assertEquals(6, healthy.at("/observed/nk/witnesses").size());

    ObjectNode missing = actionFixture();
    array(missing, "/expected/nk").remove(2);
    assertTrue(CorrelatedLogEvidenceValidator.validate(missing)
        .contains("LOG_PROJECTION_APPROVED_ACTION_PAIR"));
    ObjectNode duplicate = actionFixture();
    for (String side : List.of(FIXTURE_CURRENT, "nk")) {
      ObjectNode extra = object(duplicate, FIXTURE_EXPECTED_2C89F398 + side + "/2").deepCopy();
      extra.put(FIXTURE_EVENT, "EV_DUPLICATE_INITIAL");
      array(duplicate, FIXTURE_EXPECTED_2C89F398 + side).add(extra);
    }
    assertTrue(CorrelatedLogEvidenceValidator.validate(duplicate)
        .contains("LOG_PROJECTION_APPROVED_ACTION_PAIR"));
    for (String variant : List.of("method", FIXTURE_PATH, FIXTURE_STATUS)) {
      ObjectNode invalid = actionFixture();
      ObjectNode http = object(invalid, "/expected/nk/2/http");
      switch (variant) {
        case "method" -> http.put("method", "POST");
        case "path" -> http.put(FIXTURE_PATH, "/different");
        case "status" -> http.put(FIXTURE_STATUS, 201);
        default -> throw new AssertionError("closed independent case list");
      }
      assertTrue(CorrelatedLogEvidenceValidator.validate(invalid)
          .contains("LOG_PROJECTION_EXPECTED_PAYLOAD"), variant);
    }
  }

  /** PT-CHR-LOG-COR-011: optional N12 and equal-size field-set negatives. */
  @Test
  void optionalResponseBytesAndSameSizeFieldReplacementStayStrict() {
    for (JsonNode value : List.of(JSON.getNodeFactory().textNode("1"),
        JSON.getNodeFactory().numberNode(-1),
        JSON.getNodeFactory().numberNode(1_000_000_000_000L),
        JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")))) {
      ObjectNode invalid = fixture();
      object(invalid, "/expected/nk/0/http").set("responseBytes", value);
      assertTrue(CorrelatedLogEvidenceValidator.validate(invalid)
          .contains("LOG_PROJECTION_EXPECTED_PAYLOAD"));
    }
    ObjectNode swapped = fixture();
    ObjectNode expected = object(swapped, "/expected/nk/0");
    JsonNode event = expected.remove(FIXTURE_EVENT);
    expected.set("unexpectedEventField", event);
    assertEquals(7, expected.size());
    assertTrue(CorrelatedLogEvidenceValidator.validate(swapped)
        .contains("LOG_PROJECTION_EXPECTED_PAYLOAD"));
  }

  private static ObjectNode actionFixture() {
    ObjectNode input = fixture();
    for (String side : List.of(FIXTURE_CURRENT, "nk")) {
      boolean nk = "nk".equals(side);
      for (String operation : List.of("OP_LOGIN", "OP_SECOND")) {
        for (boolean menu : List.of(true, false)) {
          String action = menu ? (nk ? "MENU_VIEWED" : "menu")
              : (nk ? "LOG_SEARCHED" : "log_search");
          String event = (menu ? "EV_MENU_" : "EV_SEARCH_") + operation;
          ObjectNode http = JSON.createObjectNode();
          if (nk && menu) {
            http.put("method", "GET").put(FIXTURE_PATH, "/").put(FIXTURE_STATUS, 200)
                .put(FIXTURE_ELAPSEDMS, 0).put("responseBytes", 0);
          }
          ObjectNode value = payload("ACTION", action, event, http);
          value.put(FIXTURE_OPERATION, operation).put(FIXTURE_REQUEST, "REQ_" + operation);
          array(input, FIXTURE_EXPECTED_2C89F398 + side).add(value.deepCopy());
          array(input, "/observed/" + side + "/after")
              .add(row(side + "_" + event, value.deepCopy()));
          if (nk && menu) {
            for (String stage : List.of("LOCAL", "OUTBOX")) {
              array(input, "/observed/nk/witnesses")
                  .add(JSON.createObjectNode().put("stage", stage)
                      .set(FIXTURE_PAYLOAD, value.deepCopy()));
            }
          }
        }
      }
    }
    return input;
  }

'''
idx=old.index('  static ObjectNode fixture() {');new=old[:idx]+addition+old[idx:];assert new.count('@Test')==11;p.write_text(new)
m=dict(actualExit=0,oldWhole9Sha256=hashlib.sha256(old.encode()).hexdigest(),newTests=2,oldTestBodiesByteUnchangedByBlockRemoval=True,newWholeTests=11,MainChanged=False,productionCoreMain='eeba9dd506a3d221e447b3031fa4497e21f948c4',productTestsExecuted=0,normalRun='NOT_RUN',oracle='Independent literal QA054 current menu/log_search and NK MENU_VIEWED/LOG_SEARCHED; per-operation exact count/witness/HTTP/N12/shape; no validator-generated expected.',actualBackendVmNativeCaptureActions=0)
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('whole9 preserved; independent new2 written, not executed')
