package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PayloadSemanticValidatorTest {
  private static final String TIME = "20260902123456789";
  private static final String LATER = "20260902133456789";

  @Test
  void pageConstantsCountsAndArithmeticAreEnforced() {
    assertInvalid(withData(valid("SRCREQ01", 0), "Page size", n(50)));
    assertInvalid(withData(valid("USRREQ01", 0), "Page", n(0)));
    assertInvalid(withData(valid("GAMRSP01", 1), "Total count", n(0)));

    assertValid(valid("SRCRSP01", 0));
    assertValid(valid("SRCRSP01", 1));
    assertInvalid(withData(valid("SRCRSP01", 1), "Effective page", n(0)));
    assertInvalid(withData(valid("SRCRSP01", 1), "Total pages", n(2)));
    assertInvalid(
        withData(
            valid("SRCRSP01", 1),
            "Effective page", n(2),
            "Total pages", n(1)));
    assertInvalid(withData(valid("SRCRSP01", 0), "First result", n(1)));
    assertInvalid(withData(valid("SRCRSP01", 0), "Last result", n(1)));
    assertInvalid(withRecords(valid("SRCRSP01", 0), valid("SRCRSP01", 1).records()));
    assertInvalid(withData(valid("SRCRSP01", 1), "First result", n(2)));
    assertInvalid(withData(valid("SRCRSP01", 1), "Last result", n(0)));
    assertInvalid(withData(valid("SRCRSP01", 1), "Total count", n(2), "Last result", n(2)));
  }

  @Test
  void listRecordConditionsAndOrderingAreEnforced() {
    assertInvalid(withRecord(valid("SPKRSP01", 1), 0, "出現件数", n(0)));
    PayloadValues games = valid("GAMRSP01", 2);
    games = withRecord(games, 0, "Display order", n(2));
    games = withRecord(games, 1, "Display order", n(1));
    assertInvalid(games);

    assertInvalid(withRecord(valid("SRCRSP01", 1), 0, "Line番号", n(0)));
    assertInvalid(withRecord(valid("SRCRSP01", 1), 0, "Audio ID", t("1")));
    assertInvalid(
        withRecord(
            valid("SRCRSP01", 1),
            0,
            "Audio有無", b(true),
            "Audio ID", t("1")));
    PayloadValues audioSearch =
        withRecord(
            valid("SRCRSP01", 1),
            0,
            "Audio有無", b(true),
            "Audio ID", t("1"),
            "Audio display path", t("audio/file.ogg"));
    assertValid(audioSearch);

    assertInvalid(withRecord(valid("RTERSP01", 1), 0, "File件数", n(0)));
    PayloadValues routes = valid("RTERSP01", 2);
    routes = withRecord(routes, 0, "Prefix", n(1));
    routes = withRecord(routes, 1, "Prefix", n(2));
    assertValid(routes);
    assertInvalid(withRecord(routes, 1, "Prefix", n(1)));

    PayloadValues files = valid("SCFRSP01", 2);
    files = withRecord(files, 0, "Script file ID", n(2));
    files = withRecord(files, 1, "Script file ID", n(1));
    assertValid(files);
  }

  @Test
  void scenarioInlineAndLargeFileConditionsAreEnforced() {
    PayloadValues inline = valid("SCNRSP01", 1);
    assertValid(inline);
    assertInvalid(withData(inline, "Previous file ID", t("1")));
    assertInvalid(withData(inline, "Next title", t("next")));
    assertInvalid(withData(inline, "File ID", t("123e4567-e89b-12d3-a456-426614174000")));
    assertInvalid(withData(inline, "File relative path", t("transfer/result.bin")));
    assertInvalid(withData(inline, "File SHA-256", t("a".repeat(64))));
    assertInvalid(withData(inline, "File byte長", n(1)));
    assertInvalid(withData(inline, "File record長", n(4_800)));
    assertInvalid(withData(inline, "File record件数", n(1)));
    assertInvalid(withRecords(inline, java.util.Collections.nCopies(201, inline.records().getFirst())));

    PayloadValues secondEntry = withRecords(inline, List.of(inline.records().getFirst(), inline.records().getFirst()));
    secondEntry = withRecord(secondEntry, 1, "Entry ID", n(2), "Entry sequence", n(2));
    assertValid(secondEntry);
    assertInvalid(withRecord(secondEntry, 1, "Entry sequence", n(1)));
    assertInvalid(withRecord(secondEntry, 1, "Line番号", n(0)));
    assertInvalid(withRecord(inline, 0, "Audio sequence", n(1)));
    assertInvalid(withRecord(inline, 0, "Audio ID", t("1"), "Audio sequence", n(1)));
    assertInvalid(withRecord(inline, 0, "Audio display path", t("audio/one.ogg")));
    assertInvalid(
        withRecord(
            inline,
            0,
            "Audio sequence", n(0),
            "Audio ID", t("1"),
            "Audio display path", t("audio/one.ogg")));

    PayloadValues noAudioRepeated =
        withRecords(inline, List.of(inline.records().getFirst(), inline.records().getFirst()));
    assertInvalid(noAudioRepeated);

    PayloadValues firstAudio =
        withRecord(
            inline,
            0,
            "Audio sequence", n(1),
            "Audio ID", t("1"),
            "Audio display path", t("audio/one.ogg"));
    PayloadValues sameEntry =
        withRecords(firstAudio, List.of(firstAudio.records().getFirst(), firstAudio.records().getFirst()));
    sameEntry =
        withRecord(
            sameEntry,
            1,
            "Audio sequence", n(2),
            "Audio ID", t("2"),
            "Audio display path", t("audio/two.ogg"));
    assertValid(sameEntry);
    assertInvalid(withRecord(sameEntry, 1, "Entry sequence", n(2)));
    assertInvalid(withRecord(sameEntry, 1, "Audio sequence", n(3)));
    assertInvalid(withRecord(sameEntry, 1, "本文", t("different")));
    assertInvalid(withRecord(secondEntry, 1, "Audio sequence", n(2), "Audio ID", t("2"), "Audio display path", t("audio/two.ogg")));

    PayloadValues repeatedEntry =
        withRecords(
            firstAudio,
            List.of(
                firstAudio.records().getFirst(),
                withRecord(secondEntry, 1, "Entry ID", n(2)).records().get(1),
                firstAudio.records().getFirst()));
    repeatedEntry = withRecord(repeatedEntry, 2, "Entry sequence", n(3));
    assertInvalid(repeatedEntry);

    PayloadValues file =
        withData(
            valid("SCNRSP01", 0),
            "Delivery mode", t("F"),
            "File ID", t("123e4567-e89b-12d3-a456-426614174000"),
            "File relative path", t("transfer/result.bin"),
            "File byte長", n(4_800),
            "File SHA-256", t("a".repeat(64)),
            "File record長", n(4_800),
            "File record件数", n(1));
    assertValid(file);
    assertInvalid(withRecords(file, inline.records()));
    assertInvalid(withData(file, "File ID", u()));
    assertInvalid(withData(file, "File relative path", u()));
    assertInvalid(withData(file, "File SHA-256", u()));
    assertInvalid(withData(file, "File byte長", n(0)));
    assertInvalid(withData(file, "File record長", n(4_799)));
    assertInvalid(withData(file, "File record件数", n(0)));
    assertInvalid(withData(file, "File record件数", n(10_001), "File byte長", n(48_004_800)));
    assertInvalid(withData(file, "File byte長", n(4_801)));
  }

  @Test
  void mediaAnimationAndMusicConditionsAreEnforced() {
    assertInvalid(withData(valid("AUDRSP01", 0), "File byte長", n(0)));
    assertInvalid(withData(valid("ANMRSP01", 0), "総file件数", n(1)));
    assertValid(
        withData(
            valid("ANMRSP01", 0),
            "Main/SUBTRACK件数", n(1),
            "OVA件数", n(2),
            "Opening有無", b(true),
            "総file件数", n(4)));

    assertInvalid(withRecord(valid("ANLRSP01", 1), 0, "File byte長", n(0)));
    assertInvalid(withRecord(valid("ANLRSP01", 1), 0, "Parent main ID", t("main")));
    assertValid(
        withRecord(
            valid("ANLRSP01", 1),
            0,
            "Category", t("SUBTRACK"),
            "Parent main ID", t("main")));

    assertInvalid(withRecord(valid("MTRRSP01", 1), 0, "File byte長", n(0)));
    assertInvalid(withRecord(valid("MTRRSP01", 1), 0, "Pair key", t("pair")));
    assertValid(
        withRecord(
            valid("MTRRSP01", 1),
            0,
            "Pair role", t("M"),
            "Pair key", t("pair")));
  }

  @Test
  void loginUserPasswordDateAndSessionRulesAreEnforced() {
    assertInvalid(withData(valid("LGNREQ01", 0), "Username", t(" user")));
    assertInvalid(withData(valid("LGNREQ01", 0), "Username", t(" ")));
    assertInvalid(withData(valid("LGNREQ01", 0), "Password", t("")));
    assertInvalid(withData(valid("LGNREQ01", 0), "Password", t("PublicTestPassword ")));
    assertInvalid(withData(valid("LGNRSP01", 0), "Username", u()));
    assertInvalid(withData(valid("LGNRSP01", 0), "Role", u()));
    assertInvalid(withData(valid("LGNRSP01", 0), "認証context ID", u()));
    assertInvalid(withData(valid("LGNRSP01", 0), "発行日時", u()));
    assertInvalid(withData(valid("LGNRSP01", 0), "期限日時", u()));
    assertInvalid(withData(valid("LGNRSP01", 0), "Retry after秒", n(1)));
    assertInvalid(withData(valid("LGNRSP01", 0), "残り試行回数", n(1)));
    assertInvalid(withData(valid("LGNRSP01", 0), "利用者message", t("error")));
    assertInvalid(withData(valid("LGNRSP01", 0), "期限日時", t(TIME)));

    assertInvalid(withData(valid("UCRREQ01", 0), "Username", t("bad!")));
    assertInvalid(withData(valid("UCRREQ01", 0), "Initial Password", t("short")));
    assertInvalid(withData(valid("UCRREQ01", 0), "Initial Password", t("a".repeat(129))));
    assertInvalid(withData(valid("UCRREQ01", 0), "Initial Password", t("PublicTest12 ")));
    assertInvalid(withData(valid("UCRREQ01", 0), "Initial Password", t("😀".repeat(65))));
    assertInvalid(
        withData(
            valid("UCRREQ01", 0),
            "Username", t("sameusername"),
            "Initial Password", t("SAMEUSERNAME")));
    assertInvalid(withData(valid("UPWREQ01", 0), "New Password", t("short")));
    assertInvalid(withData(valid("UPWREQ01", 0), "New Password", t("PublicTest12 ")));
    assertInvalid(withData(valid("UDTRSP01", 0), "Active session数", n(3)));

    assertValid(withData(valid("LGSREQ01", 0), "From日時", t(TIME), "To日時", t(LATER)));
    assertInvalid(withData(valid("LGSREQ01", 0), "From日時", t(LATER), "To日時", t(TIME)));
    assertInvalid(
        withData(
            valid("LGSREQ01", 0),
            "From日時", t("20260101000000000"),
            "To日時", t("20260202000000000")));
    assertValid(withData(valid("NTSREQ01", 0), "受付日時From", t(TIME)));
  }

  @Test
  void notificationCancellationAndQuestionStateConditionsAreEnforced() {
    PayloadValues received = valid("NTDRSP01", 0);
    assertValid(received);
    assertInvalid(withData(received, "処理開始日時", t(TIME)));

    PayloadValues processing =
        withData(received, "内部状態", t("PROCESSING"), "処理開始日時", t(TIME));
    assertValid(processing);
    assertInvalid(withData(processing, "処理完了日時", t(LATER)));

    PayloadValues completed =
        withData(
            received,
            "内部状態", t("COMPLETED"),
            "通知区分", t("COMPLETED"),
            "処理開始日時", t(TIME),
            "処理完了日時", t(LATER));
    assertValid(completed);
    assertInvalid(withData(completed, "Error日時", t(LATER)));

    PayloadValues failed =
        withData(
            received,
            "内部状態", t("ERROR"),
            "通知区分", t("ERROR"),
            "処理開始日時", t(TIME),
            "Error日時", t(LATER),
            "Error code", t("PROCESS_FAILED"),
            "利用者向けerror", t("safe error"));
    assertValid(failed);
    assertInvalid(withData(failed, "Error code", u()));
    assertInvalid(withData(failed, "通知区分", t("ACCEPTED")));

    PayloadValues cancelled =
        withData(received, "内部状態", t("CANCELLED"), "取消日時", t(TIME));
    assertValid(cancelled);
    assertInvalid(withData(cancelled, "処理開始日時", t(TIME)));
    assertInvalid(withData(received, "Error code", t("PROCESS_FAILED")));
    assertInvalid(withData(received, "利用者向けerror", t("safe error")));
    assertInvalid(withData(received, "質問削除済み", b(true)));
    assertInvalid(
        withData(
            received,
            "質問削除済み", b(true),
            "質問本文", u()));
    assertValid(
        withData(
            received,
            "質問削除済み", b(true),
            "質問本文", u(),
            "Question ID", u()));
    assertInvalid(withData(received, "回答本文", t("answer")));

    assertInvalid(withData(valid("NTCRSP01", 0), "更新後状態", t("PROCESSING")));
    assertInvalid(withData(valid("NTCRSP01", 0), "取消日時", u()));

    assertInvalid(withRecord(valid("QSSRSP01", 1), 0, "回答日時", t(TIME)));
    assertValid(
        withRecord(
            valid("QSSRSP01", 1),
            0,
            "回答状態", t("ANSWERED"),
            "回答日時", t(TIME)));
    assertInvalid(withData(valid("QSDRSP01", 0), "回答日時", t(TIME)));
    assertValid(
        withData(
            valid("QSDRSP01", 0),
            "回答状態", t("ANSWERED"),
            "回答本文", t("answer"),
            "回答日時", t(TIME)));
    assertInvalid(withData(valid("QSDRSP01", 0), "回答本文", t("answer")));
    assertInvalid(withData(received, "受付ID", t("INVALID")));
  }

  @Test
  void receiptWebAndDefensiveContractsAreEnforced() {
    assertInvalid(withData(valid("QSBREQ01", 0), "質問本文", t("")));
    assertInvalid(withData(valid("QSBREQ01", 0), "質問本文", t("question ")));
    assertInvalid(withData(valid("QSBRSP01", 0), "受付ID", t("INVALID")));
    assertInvalid(withRecord(valid("NTSRSP01", 1), 0, "受付ID", t("INVALID")));
    assertInvalid(withData(valid("QWKREQ01", 0), "受付ID", t("INVALID")));
    assertInvalid(withData(valid("WLGEVT01", 0), "HTTP method", t("get")));
    assertInvalid(withData(valid("WLGEVT01", 0), "Path", t("safe")));
    assertInvalid(withData(valid("WLGEVT01", 0), "Path", t("/safe?q=secret")));
    assertThrows(NullPointerException.class, () -> PayloadSemanticValidator.validate(null));

    PayloadData wrongNumeric =
        () -> new FieldValueSet(Map.of("Page size", t("50")));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(new LayoutId("USRREQ01"), wrongNumeric, List.of())));
    PayloadData wrongText =
        () ->
            new FieldValueSet(
                Map.of(
                    "Username", n(1),
                    "Password", t("PublicTestPassword"),
                    "Client address", t("127.0.0.1")));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(new LayoutId("LGNREQ01"), wrongText, List.of())));
    PayloadData wrongFlag =
        () ->
            new FieldValueSet(
                Map.of(
                    "Main/SUBTRACK件数", n(0),
                    "OVA件数", n(0),
                    "Opening有無", t("0"),
                    "総file件数", n(0)));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(new LayoutId("ANMRSP01"), wrongFlag, List.of())));
    PayloadData wrongTimestamp =
        () ->
            new FieldValueSet(
                Map.of(
                    "Page", n(1),
                    "Page size", n(100),
                    "From日時", b(false),
                    "To日時", u()));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(new LayoutId("LGSREQ01"), wrongTimestamp, List.of())));
    PayloadData unknownNotificationState =
        () -> replace(valid("NTDRSP01", 0).data(), "内部状態", t("UNKNOWN"));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(
                    new LayoutId("NTDRSP01"), unknownNotificationState, List.of())));
  }

  private static PayloadValues valid(String layoutId, int recordCount) {
    return PayloadTypeCatalogTest.validPayload(layoutId, recordCount);
  }

  private static PayloadValues withData(PayloadValues source, Object... replacements) {
    return new PayloadValues(
        source.layoutId(), replace(source.data(), replacements), source.records());
  }

  private static PayloadValues withRecord(
      PayloadValues source, int index, Object... replacements) {
    ArrayList<FieldValueSet> records = new ArrayList<>(source.records());
    records.set(index, replace(records.get(index), replacements));
    return new PayloadValues(source.layoutId(), source.data(), records);
  }

  private static PayloadValues withRecords(
      PayloadValues source, List<FieldValueSet> records) {
    return new PayloadValues(source.layoutId(), source.data(), records);
  }

  private static FieldValueSet replace(FieldValueSet source, Object... replacements) {
    if (replacements.length % 2 != 0) {
      throw new IllegalArgumentException("fixture replacements must be name/value pairs");
    }
    LinkedHashMap<String, FieldValue> values = new LinkedHashMap<>();
    for (String name : source.names()) {
      values.put(name, source.getOrUnset(name));
    }
    for (int index = 0; index < replacements.length; index += 2) {
      values.put((String) replacements[index], (FieldValue) replacements[index + 1]);
    }
    return new FieldValueSet(values);
  }

  private static FieldValue t(String value) {
    return new FieldValue.Text(value);
  }

  private static FieldValue n(long value) {
    return new FieldValue.Numeric(value);
  }

  private static FieldValue b(boolean value) {
    return new FieldValue.Flag(value);
  }

  private static FieldValue u() {
    return FieldValue.Unset.INSTANCE;
  }

  private static void assertValid(PayloadValues values) {
    assertDoesNotThrow(() -> PayloadTypeCatalog.decode(values));
  }

  private static void assertInvalid(PayloadValues values) {
    assertThrows(LayoutValidationException.class, () -> PayloadTypeCatalog.decode(values));
  }
}
