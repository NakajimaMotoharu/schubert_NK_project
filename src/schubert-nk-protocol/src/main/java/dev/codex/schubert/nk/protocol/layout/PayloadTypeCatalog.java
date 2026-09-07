package dev.codex.schubert.nk.protocol.layout;

import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LoginRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LoginResponseData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutResponseData;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.log.WebLogEventData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MediaDescriptorData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.question.QuestionWorkData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;

/** Explicit SS 323 layout-to-named-type registry; runtime field-order reflection is forbidden. */
public final class PayloadTypeCatalog {
  private static final Map<String, Mapping> STANDARD =
      Map.ofEntries(
          Map.entry(
              "LGNREQ01", mapping("LGNREQ01", LoginRequestData.class, LoginRequestData::from)),
          Map.entry(
              "LGNRSP01", mapping("LGNRSP01", LoginResponseData.class, LoginResponseData::from)),
          Map.entry(
              "LOGREQ01", mapping("LOGREQ01", LogoutRequestData.class, LogoutRequestData::from)),
          Map.entry(
              "LOGRSP01", mapping("LOGRSP01", LogoutResponseData.class, LogoutResponseData::from)),
          Map.entry(
              "GAMREQ01",
              mapping("GAMREQ01", GameListRequestData.class, GameListRequestData::from)),
          Map.entry(
              "GAMRSP01",
              mapping(
                  "GAMRSP01",
                  GameListResponseData.class,
                  GameListResponseData::from,
                  GameRecord.class,
                  GameRecord::from)),
          Map.entry(
              "SPKREQ01",
              mapping("SPKREQ01", SpeakerListRequestData.class, SpeakerListRequestData::from)),
          Map.entry(
              "SPKRSP01",
              mapping(
                  "SPKRSP01",
                  SpeakerListResponseData.class,
                  SpeakerListResponseData::from,
                  SpeakerRecord.class,
                  SpeakerRecord::from)),
          Map.entry(
              "SRCREQ01",
              mapping(
                  "SRCREQ01", ScenarioSearchRequestData.class, ScenarioSearchRequestData::from)),
          Map.entry(
              "SRCRSP01",
              mapping(
                  "SRCRSP01",
                  PagedResponseData.class,
                  PagedResponseData::from,
                  ScenarioSearchRecord.class,
                  ScenarioSearchRecord::from)),
          Map.entry(
              "RTEREQ01",
              mapping("RTEREQ01", RouteListRequestData.class, RouteListRequestData::from)),
          Map.entry(
              "RTERSP01",
              mapping(
                  "RTERSP01",
                  RouteListResponseData.class,
                  RouteListResponseData::from,
                  RouteRecord.class,
                  RouteRecord::from)),
          Map.entry(
              "SCFREQ01",
              mapping(
                  "SCFREQ01",
                  ScenarioFileListRequestData.class,
                  ScenarioFileListRequestData::from)),
          Map.entry(
              "SCFRSP01",
              mapping(
                  "SCFRSP01",
                  ScenarioFileListResponseData.class,
                  ScenarioFileListResponseData::from,
                  ScenarioFileRecord.class,
                  ScenarioFileRecord::from)),
          Map.entry(
              "SCNREQ01",
              mapping(
                  "SCNREQ01", ScenarioDetailRequestData.class, ScenarioDetailRequestData::from)),
          Map.entry(
              "SCNRSP01",
              mapping(
                  "SCNRSP01",
                  ScenarioDetailResponseData.class,
                  ScenarioDetailResponseData::from,
                  ScenarioEntryRecord.class,
                  ScenarioEntryRecord::from)),
          Map.entry(
              "AUDREQ01",
              mapping(
                  "AUDREQ01", AudioDescriptorRequestData.class, AudioDescriptorRequestData::from)),
          Map.entry(
              "AUDRSP01",
              mapping("AUDRSP01", MediaDescriptorData.class, MediaDescriptorData::from)),
          Map.entry(
              "ANMREQ01",
              mapping("ANMREQ01", AnimationMenuRequestData.class, AnimationMenuRequestData::from)),
          Map.entry(
              "ANMRSP01",
              mapping(
                  "ANMRSP01", AnimationMenuResponseData.class, AnimationMenuResponseData::from)),
          Map.entry(
              "ANLREQ01",
              mapping("ANLREQ01", AnimationListRequestData.class, AnimationListRequestData::from)),
          Map.entry(
              "ANLRSP01",
              mapping(
                  "ANLRSP01",
                  AnimationListResponseData.class,
                  AnimationListResponseData::from,
                  AnimationRecord.class,
                  AnimationRecord::from)),
          Map.entry(
              "VIDREQ01",
              mapping(
                  "VIDREQ01", VideoDescriptorRequestData.class, VideoDescriptorRequestData::from)),
          Map.entry(
              "VIDRSP01",
              mapping(
                  "VIDRSP01",
                  VideoDescriptorResponseData.class,
                  VideoDescriptorResponseData::from)),
          Map.entry(
              "MCTREQ01",
              mapping("MCTREQ01", MusicCategoryRequestData.class, MusicCategoryRequestData::from)),
          Map.entry(
              "MCTRSP01",
              mapping(
                  "MCTRSP01",
                  MusicCategoryResponseData.class,
                  MusicCategoryResponseData::from,
                  MusicCategoryRecord.class,
                  MusicCategoryRecord::from)),
          Map.entry(
              "MCSREQ01",
              mapping("MCSREQ01", MusicSectionRequestData.class, MusicSectionRequestData::from)),
          Map.entry(
              "MCSRSP01",
              mapping(
                  "MCSRSP01",
                  MusicSectionResponseData.class,
                  MusicSectionResponseData::from,
                  MusicSectionRecord.class,
                  MusicSectionRecord::from)),
          Map.entry(
              "MTRREQ01",
              mapping("MTRREQ01", MusicTrackRequestData.class, MusicTrackRequestData::from)),
          Map.entry(
              "MTRRSP01",
              mapping(
                  "MTRRSP01",
                  MusicTrackResponseData.class,
                  MusicTrackResponseData::from,
                  MusicTrackRecord.class,
                  MusicTrackRecord::from)),
          Map.entry(
              "MEDREQ01",
              mapping(
                  "MEDREQ01", MusicDescriptorRequestData.class, MusicDescriptorRequestData::from)),
          Map.entry(
              "MEDRSP01",
              mapping("MEDRSP01", MediaDescriptorData.class, MediaDescriptorData::from)),
          Map.entry(
              "LGSREQ01",
              mapping("LGSREQ01", LogSearchRequestData.class, LogSearchRequestData::from)),
          Map.entry(
              "LGSRSP01",
              mapping(
                  "LGSRSP01",
                  PagedResponseData.class,
                  PagedResponseData::from,
                  LogRecord.class,
                  LogRecord::from)),
          Map.entry(
              "USRREQ01",
              mapping("USRREQ01", UserSearchRequestData.class, UserSearchRequestData::from)),
          Map.entry(
              "USRRSP01",
              mapping(
                  "USRRSP01",
                  PagedResponseData.class,
                  PagedResponseData::from,
                  UserRecord.class,
                  UserRecord::from)),
          Map.entry(
              "UCRREQ01",
              mapping("UCRREQ01", UserCreateRequestData.class, UserCreateRequestData::from)),
          Map.entry(
              "UCRRSP01",
              mapping("UCRRSP01", UserMutationResponseData.class, UserMutationResponseData::from)),
          Map.entry(
              "UDTREQ01",
              mapping("UDTREQ01", UserDetailRequestData.class, UserDetailRequestData::from)),
          Map.entry(
              "UDTRSP01",
              mapping("UDTRSP01", UserDetailResponseData.class, UserDetailResponseData::from)),
          Map.entry(
              "USTREQ01",
              mapping("USTREQ01", UserStatusRequestData.class, UserStatusRequestData::from)),
          Map.entry(
              "USTRSP01",
              mapping("USTRSP01", UserMutationResponseData.class, UserMutationResponseData::from)),
          Map.entry(
              "URLREQ01",
              mapping("URLREQ01", UserRoleRequestData.class, UserRoleRequestData::from)),
          Map.entry(
              "URLRSP01",
              mapping("URLRSP01", UserMutationResponseData.class, UserMutationResponseData::from)),
          Map.entry(
              "UPWREQ01",
              mapping("UPWREQ01", PasswordResetRequestData.class, PasswordResetRequestData::from)),
          Map.entry(
              "UPWRSP01",
              mapping("UPWRSP01", UserMutationResponseData.class, UserMutationResponseData::from)),
          Map.entry(
              "ULKREQ01",
              mapping("ULKREQ01", UserUnlockRequestData.class, UserUnlockRequestData::from)),
          Map.entry(
              "ULKRSP01",
              mapping("ULKRSP01", UserMutationResponseData.class, UserMutationResponseData::from)),
          Map.entry(
              "QSBREQ01",
              mapping(
                  "QSBREQ01", QuestionSubmitRequestData.class, QuestionSubmitRequestData::from)),
          Map.entry(
              "QSBRSP01",
              mapping(
                  "QSBRSP01", QuestionSubmitResponseData.class, QuestionSubmitResponseData::from)),
          Map.entry(
              "NTSREQ01",
              mapping(
                  "NTSREQ01",
                  NotificationSearchRequestData.class,
                  NotificationSearchRequestData::from)),
          Map.entry(
              "NTSRSP01",
              mapping(
                  "NTSRSP01",
                  PagedResponseData.class,
                  PagedResponseData::from,
                  NotificationRecord.class,
                  NotificationRecord::from)),
          Map.entry(
              "NTDREQ01",
              mapping(
                  "NTDREQ01",
                  NotificationDetailRequestData.class,
                  NotificationDetailRequestData::from)),
          Map.entry(
              "NTDRSP01",
              mapping(
                  "NTDRSP01",
                  NotificationDetailResponseData.class,
                  NotificationDetailResponseData::from)),
          Map.entry(
              "NTCREQ01",
              mapping(
                  "NTCREQ01",
                  NotificationCancelRequestData.class,
                  NotificationCancelRequestData::from)),
          Map.entry(
              "NTCRSP01",
              mapping(
                  "NTCRSP01",
                  NotificationCancelResponseData.class,
                  NotificationCancelResponseData::from)),
          Map.entry(
              "QSSREQ01",
              mapping(
                  "QSSREQ01", QuestionSearchRequestData.class, QuestionSearchRequestData::from)),
          Map.entry(
              "QSSRSP01",
              mapping(
                  "QSSRSP01",
                  PagedResponseData.class,
                  PagedResponseData::from,
                  QuestionSummaryRecord.class,
                  QuestionSummaryRecord::from)),
          Map.entry(
              "QSDREQ01",
              mapping(
                  "QSDREQ01", QuestionDetailRequestData.class, QuestionDetailRequestData::from)),
          Map.entry(
              "QSDRSP01",
              mapping(
                  "QSDRSP01", QuestionDetailResponseData.class, QuestionDetailResponseData::from)),
          Map.entry(
              "QDLREQ01",
              mapping(
                  "QDLREQ01", QuestionDeleteRequestData.class, QuestionDeleteRequestData::from)),
          Map.entry(
              "QDLRSP01",
              mapping(
                  "QDLRSP01", QuestionDeleteResponseData.class, QuestionDeleteResponseData::from)),
          Map.entry(
              "QWKREQ01", mapping("QWKREQ01", QuestionWorkData.class, QuestionWorkData::from)),
          Map.entry("WLGEVT01", mapping("WLGEVT01", WebLogEventData.class, WebLogEventData::from)));

  private PayloadTypeCatalog() {}

  public static TypedPayloadValues decode(PayloadValues values) {
    Objects.requireNonNull(values, "values");
    Mapping mapping = require(values.layoutId());
    PayloadData data = mapping.dataDecoder().apply(values.data());
    List<PayloadRecord> records = decodeRecords(values, mapping.recordMapping());
    TypedPayloadValues typed = new TypedPayloadValues(values.layoutId(), data, records);
    PayloadSemanticValidator.validate(typed);
    return typed;
  }

  public static PayloadValues encode(TypedPayloadValues values) {
    Objects.requireNonNull(values, "values");
    Mapping mapping = require(values.layoutId());
    if (!mapping.dataType().isInstance(values.data())) {
      throw new LayoutValidationException("named data type does not match layout");
    }
    validateRecordTypes(values.records(), mapping.recordMapping());
    PayloadSemanticValidator.validate(values);
    List<FieldValueSet> records = values.records().stream().map(PayloadRecord::fields).toList();
    return new PayloadValues(values.layoutId(), values.data().fields(), records);
  }

  public static Class<? extends PayloadData> dataType(LayoutId layoutId) {
    return require(layoutId).dataType();
  }

  public static Optional<Class<? extends PayloadRecord>> recordType(LayoutId layoutId) {
    return require(layoutId).recordMapping().map(RecordMapping::recordType);
  }

  private static List<PayloadRecord> decodeRecords(
      PayloadValues values, Optional<RecordMapping> optionalMapping) {
    if (optionalMapping.isEmpty()) {
      if (!values.records().isEmpty()) {
        throw new LayoutValidationException("layout does not define repeating records");
      }
      return List.of();
    }
    RecordMapping mapping = optionalMapping.orElseThrow();
    List<PayloadRecord> records = new ArrayList<>(values.records().size());
    for (FieldValueSet fields : values.records()) {
      records.add(mapping.recordDecoder().apply(fields));
    }
    return List.copyOf(records);
  }

  private static void validateRecordTypes(
      List<PayloadRecord> records, Optional<RecordMapping> optionalMapping) {
    if (optionalMapping.isEmpty()) {
      if (!records.isEmpty()) {
        throw new LayoutValidationException("layout does not define repeating records");
      }
      return;
    }
    Class<? extends PayloadRecord> expected = optionalMapping.orElseThrow().recordType();
    for (PayloadRecord record : records) {
      if (!expected.isInstance(record)) {
        throw new LayoutValidationException("named record type does not match layout");
      }
    }
  }

  private static Mapping require(LayoutId layoutId) {
    Objects.requireNonNull(layoutId, "layoutId");
    Mapping mapping = STANDARD.get(layoutId.value());
    if (mapping == null) {
      throw new UnsupportedLayoutException("unsupported named payload layout");
    }
    return mapping;
  }

  private static Mapping mapping(
      String layoutId,
      Class<? extends PayloadData> dataType,
      Function<FieldValueSet, ? extends PayloadData> dataDecoder) {
    return new Mapping(layoutId, dataType, dataDecoder, Optional.empty());
  }

  private static Mapping mapping(
      String layoutId,
      Class<? extends PayloadData> dataType,
      Function<FieldValueSet, ? extends PayloadData> dataDecoder,
      Class<? extends PayloadRecord> recordType,
      Function<FieldValueSet, ? extends PayloadRecord> recordDecoder) {
    return new Mapping(
        layoutId, dataType, dataDecoder, Optional.of(new RecordMapping(recordType, recordDecoder)));
  }

  private record Mapping(
      String layoutId,
      Class<? extends PayloadData> dataType,
      Function<FieldValueSet, ? extends PayloadData> dataDecoder,
      Optional<RecordMapping> recordMapping) {}

  private record RecordMapping(
      Class<? extends PayloadRecord> recordType,
      Function<FieldValueSet, ? extends PayloadRecord> recordDecoder) {}
}
