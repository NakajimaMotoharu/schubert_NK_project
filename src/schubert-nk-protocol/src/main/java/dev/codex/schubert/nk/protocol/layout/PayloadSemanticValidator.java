package dev.codex.schubert.nk.protocol.layout;

import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.HTTP_METHOD;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.LITERAL_COMPLETED;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.LITERAL_ERROR;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.LITERAL_FILE_BYTE;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.LITERAL_ID;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.PAGED_RESPONSES;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.PAGE_SIZES;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.RECEIPT_ID;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.RECORD_COUNT_LAYOUTS;
import static dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorRules.USERNAME;

import dev.codex.schubert.nk.protocol.time.JstWireTimestamp;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/**
 * Intrinsic layout and cross-field validation performed after named-type conversion. Trace:
 * NK-PRO-002, UI 234-236, SS 322 sections 5 and 9.
 */
public interface PayloadSemanticValidator {

  public static void validate(TypedPayloadValues values) {
    Objects.requireNonNull(values, "values");
    String layoutId = values.layoutId().value();
    FieldValueSet data = values.data().fields();
    List<FieldValueSet> records = values.records().stream().map(PayloadRecord::fields).toList();

    Integer pageSize = PAGE_SIZES.get(layoutId);
    if (pageSize != null) {
      requireEqual(numeric(data, "Page size"), pageSize, "page size is not the interface constant");
    }
    if (PAGED_RESPONSES.contains(layoutId)) {
      validatePaged(data, records.size());
    }
    if (RECORD_COUNT_LAYOUTS.contains(layoutId)) {
      requireEqual(
          numeric(data, "Total count"), records.size(), "total count differs from record count");
    }

    {
      final String dispatchValue0 = java.util.Objects.requireNonNull(layoutId);
      if (dispatchValue0.equals("LGNREQ01")) {
        validateLoginRequest(data);
      } else if (dispatchValue0.equals("LGNRSP01")) {
        validateLoginSuccess(data);
      } else if (dispatchValue0.equals("GAMRSP01")) {
        validateAscending(records, "Display order", false);
      } else if (dispatchValue0.equals("SPKRSP01")) {
        records.forEach(record -> requirePositive(record, "出現件数"));
      } else if ("SRCREQ01".equals(dispatchValue0) || "USRREQ01".equals(dispatchValue0)) {
        requirePositive(data, "Page");
      } else if (dispatchValue0.equals("SRCRSP01")) {
        validateScenarioSearchRecords(records);
      } else if (dispatchValue0.equals("RTERSP01")) {

        records.forEach(record -> requirePositive(record, "File件数"));
        validateAscending(records, "Prefix", true);

      } else if (dispatchValue0.equals("SCNRSP01")) {
        validateScenarioDetail(data, records);
      } else if ("AUDRSP01".equals(dispatchValue0)
          || "MEDRSP01".equals(dispatchValue0)
          || "VIDRSP01".equals(dispatchValue0)) {
        validateMediaDescriptor(data);
      } else if (dispatchValue0.equals("ANMRSP01")) {
        validateAnimationMenu(data);
      } else if (dispatchValue0.equals("ANLRSP01")) {
        validateAnimationRecords(records);
      } else if (dispatchValue0.equals("MTRRSP01")) {
        validateMusicRecords(records);
      } else if (dispatchValue0.equals("LGSREQ01")) {

        requirePositive(data, "Page");
        validateDateRange(data, "From日時", "To日時", 31);

      } else if (dispatchValue0.equals("UCRREQ01")) {
        validateUserCreation(data);
      } else if (dispatchValue0.equals("UDTRSP01")) {
        requireRange(
            numeric(data, "Active session数"), 0, 2, "active session count is outside 0..2");
      } else if (dispatchValue0.equals("UPWREQ01")) {
        validatePassword(text(data, "New Password"), Optional.empty());
      } else if ("NTSREQ01".equals(dispatchValue0) || "QSSREQ01".equals(dispatchValue0)) {

        requirePositive(data, "Page");
        validateDateRange(data, "受付日時From", "受付日時To", 366);

      } else if (dispatchValue0.equals("NTDRSP01")) {
        validateNotificationDetail(data);
      } else if (dispatchValue0.equals("NTCRSP01")) {
        validateCancellationSuccess(data);
      } else if (dispatchValue0.equals("QSSRSP01")) {
        records.forEach(PayloadSemanticValidator::validateQuestionSummary);
      } else if (dispatchValue0.equals("QSDRSP01")) {
        validateQuestionDetail(data);
      } else if (dispatchValue0.equals("QSBREQ01")) {
        validateQuestionSubmission(data);
      } else if ("QSBRSP01".equals(dispatchValue0) || "QWKREQ01".equals(dispatchValue0)) {
        validateReceipt(text(data, LITERAL_ID));
      } else if (dispatchValue0.equals("NTSRSP01")) {
        records.forEach(record -> validateReceipt(text(record, LITERAL_ID)));
      } else if (dispatchValue0.equals("WLGEVT01")) {
        validateWebLog(data);
      } else {

        // All remaining layouts have only invariants already established by their named types.

      }
    }
  }

  private static void validateLoginRequest(FieldValueSet data) {
    String username = text(data, "Username");
    require(
        !username.isBlank() && username.equals(username.trim()), "login username is not trimmed");
    String password = text(data, "Password");
    require(!password.isEmpty(), "login password is empty");
    require(!password.endsWith(" "), "login password has a trailing ASCII space");
  }

  private static void validateLoginSuccess(FieldValueSet data) {
    requirePresent(data, "Username");
    requirePresent(data, "Role");
    requirePresent(data, "認証context ID");
    requirePresent(data, "発行日時");
    requirePresent(data, "期限日時");
    requireEqual(numeric(data, "Retry after秒"), 0, "successful login has retry delay");
    requireEqual(numeric(data, "残り試行回数"), 0, "successful login exposes remaining attempts");
    require(!present(data, "利用者message"), "successful login contains an error message");
    require(
        JstWireTimestamp.parse(text(data, "発行日時"))
            .isBefore(JstWireTimestamp.parse(text(data, "期限日時"))),
        "login expiry is not after issue time");
  }

  private static void validatePaged(FieldValueSet data, int recordCount) {
    long effectivePage = numeric(data, "Effective page");
    long pageSize = numeric(data, "Page size");
    long totalCount = numeric(data, "Total count");
    long totalPages = numeric(data, "Total pages");
    long firstResult = numeric(data, "First result");
    long lastResult = numeric(data, "Last result");
    requireRange(effectivePage, 1, 999_999, "effective page is outside 1..999999");
    long expectedPages = Math.max(1, Math.floorDiv(totalCount + pageSize - 1, pageSize));
    requireEqual(totalPages, expectedPages, "total pages is arithmetically inconsistent");
    require(effectivePage <= totalPages, "effective page exceeds total pages");
    if (totalCount == 0) {
      requireEqual(firstResult, 0, "empty page has a first result");
      requireEqual(lastResult, 0, "empty page has a last result");
      requireEqual(recordCount, 0, "empty page contains records");
      return;
    }
    long expectedFirst = (effectivePage - 1) * pageSize + 1;
    long expectedLast = Math.min(effectivePage * pageSize, totalCount);
    requireEqual(firstResult, expectedFirst, "first result is arithmetically inconsistent");
    requireEqual(lastResult, expectedLast, "last result is arithmetically inconsistent");
    requireEqual(
        recordCount, expectedLast - expectedFirst + 1, "page record count is inconsistent");
  }

  private static void validateScenarioSearchRecords(List<FieldValueSet> records) {
    for (FieldValueSet record : records) {
      requirePositive(record, "Line番号");
      boolean audio = flag(record, "Audio有無");
      require(
          present(record, "Audio ID") == audio && present(record, "Audio display path") == audio,
          "scenario search audio fields disagree with its flag");
    }
  }

  private static void validateScenarioDetail(FieldValueSet data, List<FieldValueSet> records) {
    requirePaired(data, "Previous file ID", "Previous title");
    requirePaired(data, "Next file ID", "Next title");
    String mode = text(data, "Delivery mode");
    if (mode.equals("I")) {
      require(records.size() <= 200, "inline scenario contains more than 200 records");
      requireAbsent(data, "File ID");
      requireAbsent(data, "File relative path");
      requireAbsent(data, "File SHA-256");
      requireEqual(numeric(data, LITERAL_FILE_BYTE), 0, "inline scenario has a file byte length");
      requireEqual(numeric(data, "File record長"), 0, "inline scenario has a file record length");
      requireEqual(numeric(data, "File record件数"), 0, "inline scenario has a file record count");
      validateScenarioSequence(records);
      return;
    }
    require(mode.equals("F"), "scenario delivery mode is unknown");
    require(records.isEmpty(), "file-mode scenario contains inline records");
    requirePresent(data, "File ID");
    requirePresent(data, "File relative path");
    requirePresent(data, "File SHA-256");
    requirePositive(data, LITERAL_FILE_BYTE);
    requireEqual(numeric(data, "File record長"), 4_800, "large-result record length is not 4800");
    long count = numeric(data, "File record件数");
    requireRange(count, 1, 10_000, "large-result record count is outside 1..10000");
    requireEqual(
        numeric(data, LITERAL_FILE_BYTE),
        Math.multiplyExact(4_800, count),
        "large-result byte length differs from record length times count");
  }

  /**
   * Shared inline/file sequence contract; field bytes are checked separately by PayloadCodec.
   * Trace: NK-PRO-002/NK-SCN-001; UI234 §10, SS333; PG-D-054; PT-SCN-008-D02/004.
   */
  public static void validateScenarioSequence(List<FieldValueSet> records) {
    records = List.copyOf(records);
    Set<Long> seenEntryIds = new HashSet<>();
    long previousEntryId = -1;
    long previousEntrySequence = 0;
    long previousAudioSequence = -1;
    String previousText = "";
    for (FieldValueSet record : records) {
      requirePositive(record, "Entry sequence");
      requirePositive(record, "Line番号");
      long entryId = numeric(record, "Entry ID");
      long entrySequence = numeric(record, "Entry sequence");
      long audioSequence = numeric(record, "Audio sequence");
      boolean hasAudio = present(record, "Audio ID") || present(record, "Audio display path");
      require(
          present(record, "Audio ID") == present(record, "Audio display path"),
          "scenario audio ID and path presence differ");
      require(
          hasAudio ? audioSequence >= 1 : audioSequence == 0,
          "scenario audio sequence disagrees with audio presence");
      if (entryId == previousEntryId) {
        requireEqual(entrySequence, previousEntrySequence, "same entry has a different sequence");
        require(previousAudioSequence >= 1, "entry without audio has more than one record");
        requireEqual(audioSequence, previousAudioSequence + 1, "audio sequence is not consecutive");
        require(text(record, "本文").equals(previousText), "same entry has different body text");
      } else {
        require(seenEntryIds.add(entryId), "entry ID reappears after another entry");
        requireEqual(entrySequence, previousEntrySequence + 1, "entry sequence is not consecutive");
        require(
            audioSequence == 0 || audioSequence == 1, "new entry audio sequence must be 0 or 1");
      }
      previousEntryId = entryId;
      previousEntrySequence = entrySequence;
      previousAudioSequence = audioSequence;
      previousText = text(record, "本文");
    }
  }

  private static void validateMediaDescriptor(FieldValueSet data) {
    requirePositive(data, LITERAL_FILE_BYTE);
  }

  private static void validateAnimationMenu(FieldValueSet data) {
    long expected =
        numeric(data, "Main/SUBTRACK件数")
            + numeric(data, "OVA件数")
            + (flag(data, "Opening有無") ? 1 : 0);
    requireEqual(numeric(data, "総file件数"), expected, "animation menu counts are inconsistent");
  }

  private static void validateAnimationRecords(List<FieldValueSet> records) {
    for (FieldValueSet record : records) {
      requirePositive(record, LITERAL_FILE_BYTE);
      boolean subtrack = text(record, "Category").equals("SUBTRACK");
      require(
          present(record, "Parent main ID") == subtrack,
          "animation parent ID disagrees with category");
    }
    validateAscending(records, "Display order", false);
  }

  private static void validateMusicRecords(List<FieldValueSet> records) {
    for (FieldValueSet record : records) {
      requirePositive(record, LITERAL_FILE_BYTE);
      boolean paired = !text(record, "Pair role").equals("N");
      require(present(record, "Pair key") == paired, "music pair key disagrees with pair role");
    }
    validateAscending(records, "Display order", false);
  }

  private static void validateDateRange(
      FieldValueSet data, String fromName, String toName, long maximumDays) {
    Optional<Instant> from = optionalInstant(data, fromName);
    Optional<Instant> to = optionalInstant(data, toName);
    if (from.isPresent() && to.isPresent()) {
      Duration duration = Duration.between(from.orElseThrow(), to.orElseThrow());
      require(!duration.isNegative(), "date range is reversed");
      require(duration.compareTo(Duration.ofDays(maximumDays)) <= 0, "date range is too long");
    }
  }

  private static void validateUserCreation(FieldValueSet data) {
    String username = text(data, "Username");
    require(USERNAME.matcher(username).matches(), "username contains a disallowed character");
    validatePassword(text(data, "Initial Password"), Optional.of(username));
  }

  private static void validatePassword(String password, Optional<String> username) {
    int characters = password.codePointCount(0, password.length());
    int bytes = password.getBytes(StandardCharsets.UTF_8).length;
    require(characters >= 12 && characters <= 128, "password character length is outside 12..128");
    require(bytes <= 256, "password byte length exceeds 256");
    require(!password.endsWith(" "), "password has a trailing ASCII space");
    require(
        username.isEmpty() || !password.equalsIgnoreCase(username.orElseThrow()),
        "password equals username");
  }

  private static void validateNotificationDetail(FieldValueSet data) {
    String state = text(data, "内部状態");
    String expectedType;
    {
      final String dispatchValue1 = java.util.Objects.requireNonNull(state);
      if (LITERAL_COMPLETED.equals(dispatchValue1)) {
        expectedType = LITERAL_COMPLETED;
      } else if (LITERAL_ERROR.equals(dispatchValue1)) {
        expectedType = LITERAL_ERROR;
      } else {
        expectedType = "ACCEPTED";
      }
    }
    require(
        text(data, "通知区分").equals(expectedType),
        "notification type disagrees with its internal state");
    validateReceipt(text(data, LITERAL_ID));
    boolean started = present(data, "処理開始日時");
    boolean completed = present(data, "処理完了日時");
    boolean failed = present(data, "Error日時");
    boolean cancelled = present(data, "取消日時");
    boolean errorFields = present(data, "Error code") && present(data, "利用者向けerror");
    int timestampMask =
        (started ? 8 : 0) | (completed ? 4 : 0) | (failed ? 2 : 0) | (cancelled ? 1 : 0);
    int expectedTimestampMask;
    {
      final String dispatchValue2 = java.util.Objects.requireNonNull(state);
      if (dispatchValue2.equals("RECEIVED")) {
        expectedTimestampMask = 0;
      } else if (dispatchValue2.equals("PROCESSING")) {
        expectedTimestampMask = 8;
      } else if (LITERAL_COMPLETED.equals(dispatchValue2)) {
        expectedTimestampMask = 12;
      } else if (LITERAL_ERROR.equals(dispatchValue2)) {
        expectedTimestampMask = 10;
      } else if (dispatchValue2.equals("CANCELLED")) {
        expectedTimestampMask = 1;
      } else {
        throw new LayoutValidationException(
            "layout semantic violation: unknown notification state");
      }
    }
    require(timestampMask == expectedTimestampMask, state + " timestamps are inconsistent");
    if (state.equals(LITERAL_ERROR)) {
      require(errorFields, "ERROR notification does not contain both error fields");
    }
    if (!state.equals(LITERAL_ERROR)) {
      require(
          !present(data, "Error code") && !present(data, "利用者向けerror"),
          "non-error notification contains error fields");
    }
    boolean deleted = flag(data, "質問削除済み");
    require(
        present(data, "質問本文") != deleted && present(data, "Question ID") != deleted,
        "question deletion flag disagrees with question fields");
    // BUG562/UI224/SS323: a deleted question also retires its answer, even when completed.
    if (deleted || !state.equals(LITERAL_COMPLETED)) {
      requireAbsent(data, "回答本文");
    }
  }

  private static void validateCancellationSuccess(FieldValueSet data) {
    require(
        text(data, "更新後状態").equals("CANCELLED"), "successful cancellation state is not CANCELLED");
    requirePresent(data, "取消日時");
  }

  private static void validateQuestionSummary(FieldValueSet record) {
    String state = text(record, "回答状態");
    require(
        present(record, "回答日時") == state.equals("ANSWERED"),
        "question summary answer timestamp disagrees with state");
    validateReceipt(text(record, LITERAL_ID));
  }

  private static void validateQuestionDetail(FieldValueSet data) {
    String state = text(data, "回答状態");
    boolean answered = state.equals("ANSWERED");
    require(present(data, "回答日時") == answered, "question answer timestamp disagrees with state");
    if (!answered) {
      requireAbsent(data, "回答本文");
    }
    validateReceipt(text(data, LITERAL_ID));
  }

  private static void validateQuestionSubmission(FieldValueSet data) {
    String question = text(data, "質問本文");
    require(!question.isEmpty(), "question text is empty");
    require(!question.endsWith(" "), "question text has a trailing ASCII space");
  }

  private static void validateReceipt(String receiptId) {
    require(RECEIPT_ID.matcher(receiptId).matches(), "receipt ID format is invalid");
  }

  private static void validateWebLog(FieldValueSet data) {
    // QA054/SSC336: only the two approved pairs; no Web-issued API audit action.
    String category = text(data, "Log type");
    String action = present(data, "Action") ? text(data, "Action") : "HTTP_REQUEST_COMPLETED";
    require(
        (category.equals("REQUEST") && action.equals("HTTP_REQUEST_COMPLETED"))
            || (category.equals("ACTION") && action.equals("MENU_VIEWED")),
        "web log category/action pair is not approved");
    require(
        HTTP_METHOD.matcher(text(data, "HTTP method")).matches(), "HTTP method format is invalid");
    String path = text(data, "Path");
    require(
        path.startsWith("/") && path.indexOf('?') < 0, "web log path is not a query-free URI path");
  }

  private static void validateAscending(
      List<FieldValueSet> records, String fieldName, boolean strictlyIncreasing) {
    long previous = -1;
    for (FieldValueSet record : records) {
      long current = numeric(record, fieldName);
      require(
          strictlyIncreasing ? current > previous : current >= previous,
          "record order is not ascending: " + fieldName);
      previous = current;
    }
  }

  private static void requirePositive(FieldValueSet fields, String name) {
    require(numeric(fields, name) >= 1, name + " must be positive");
  }

  private static void requirePaired(FieldValueSet fields, String first, String second) {
    require(
        present(fields, first) == present(fields, second),
        first + " and " + second + " must be paired");
  }

  private static void requirePresent(FieldValueSet fields, String name) {
    require(present(fields, name), name + " is required by its condition");
  }

  private static void requireAbsent(FieldValueSet fields, String name) {
    require(!present(fields, name), name + " must be unset by its condition");
  }

  private static boolean present(FieldValueSet fields, String name) {
    return fields.getOrUnset(name) != FieldValue.Unset.INSTANCE;
  }

  private static long numeric(FieldValueSet fields, String name) {
    FieldValue value = fields.getOrUnset(name);
    if (value instanceof FieldValue.Numeric numeric) {
      return numeric.value();
    }
    throw new LayoutValidationException(
        "layout semantic violation: numeric field is unavailable: " + name);
  }

  private static String text(FieldValueSet fields, String name) {
    FieldValue value = fields.getOrUnset(name);
    if (value instanceof FieldValue.Text text) {
      return text.value();
    }
    throw new LayoutValidationException(
        "layout semantic violation: text field is unavailable: " + name);
  }

  private static boolean flag(FieldValueSet fields, String name) {
    FieldValue value = fields.getOrUnset(name);
    if (value instanceof FieldValue.Flag flag) {
      return flag.value();
    }
    throw new LayoutValidationException(
        "layout semantic violation: boolean field is unavailable: " + name);
  }

  private static Optional<Instant> optionalInstant(FieldValueSet fields, String name) {
    FieldValue value = fields.getOrUnset(name);
    if (value == FieldValue.Unset.INSTANCE) {
      return Optional.empty();
    }
    if (value instanceof FieldValue.Text text) {
      return Optional.of(JstWireTimestamp.parse(text.value()));
    }
    throw new LayoutValidationException(
        "layout semantic violation: timestamp field has the wrong type: " + name);
  }

  private static void requireEqual(long actual, long expected, String message) {
    require(actual == expected, message);
  }

  private static void requireRange(long value, long minimum, long maximum, String message) {
    require(value >= minimum && value <= maximum, message);
  }

  private static void require(boolean condition, String message) {
    if (!condition) {
      throw new LayoutValidationException("layout semantic violation: " + message);
    }
  }
}
