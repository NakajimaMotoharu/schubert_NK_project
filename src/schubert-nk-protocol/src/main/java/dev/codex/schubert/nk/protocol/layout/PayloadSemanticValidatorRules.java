package dev.codex.schubert.nk.protocol.layout;

import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/** Immutable non-public grammar cache. Trace: SSC451, SS322/323/333. */
interface PayloadSemanticValidatorRules {

  java.lang.String LITERAL_ID = "受付ID";

  java.lang.String LITERAL_FILE_BYTE = "File byte長";

  java.lang.String LITERAL_COMPLETED = "COMPLETED";

  java.lang.String LITERAL_ERROR = "ERROR";

  Pattern USERNAME = Pattern.compile("[A-Za-z0-9._-]+");
  Pattern RECEIPT_ID = Pattern.compile("[0-9A-HJKMNP-TV-Z]{26}");
  Pattern HTTP_METHOD = Pattern.compile("[A-Z]{3,8}");
  Set<String> RECORD_COUNT_LAYOUTS =
      Set.of(
          "GAMRSP01",
          "SPKRSP01",
          "RTERSP01",
          "SCFRSP01",
          "ANLRSP01",
          "MCTRSP01",
          "MCSRSP01",
          "MTRRSP01");
  Map<String, Integer> PAGE_SIZES =
      Map.ofEntries(
          Map.entry("SRCREQ01", 100),
          Map.entry("SRCRSP01", 100),
          Map.entry("LGSREQ01", 100),
          Map.entry("LGSRSP01", 100),
          Map.entry("USRREQ01", 50),
          Map.entry("USRRSP01", 50),
          Map.entry("NTSREQ01", 50),
          Map.entry("NTSRSP01", 50),
          Map.entry("QSSREQ01", 50),
          Map.entry("QSSRSP01", 50));
  Set<String> PAGED_RESPONSES = Set.of("SRCRSP01", "LGSRSP01", "USRRSP01", "NTSRSP01", "QSSRSP01");
}
