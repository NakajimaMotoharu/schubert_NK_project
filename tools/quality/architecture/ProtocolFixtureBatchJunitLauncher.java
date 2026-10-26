import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import javax.xml.stream.XMLOutputFactory;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.engine.support.descriptor.MethodSource;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/**
 * Frozen exact pure Protocol semantic method catalog only; no package discovery or other tests. No
 * Spring/DB/service startup.
 */
public final class ProtocolFixtureBatchJunitLauncher {
  private static final int EXPECTED_TESTS = 102;
  private static final int EXPECTED_SUITES = 22;

  private ProtocolFixtureBatchJunitLauncher() {}

  private record Result(String type, String method, String status, String failureType) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException(
          "new XML directory, frozen catalog and fixed locale required");
    if (!Set.of("ja-JP", "tr-TR").contains(args[2])
        || !java.util.Locale.getDefault().toLanguageTag().equals(args[2]))
      throw new IllegalArgumentException("dedicated JVM locale does not match fixed case");
    Set<String> allowed =
        Set.of(
            "dev.codex.schubert.nk.protocol.codec.AuthenticationErrorProfileTest#loginLockAndFailurePreserveOnlyApprovedErrorFields",
            "dev.codex.schubert.nk.protocol.codec.AuthenticationErrorProfileTest#malformedLoginErrorBoundariesAndTypesAreRejected",
            "dev.codex.schubert.nk.protocol.codec.AuthenticationErrorProfileTest#allOtherResponseErrorProfilesRetainTheirIndividualContracts",
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest#textEncodeNormalizesUtf8AndPadsWithAsciiSpace",
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest#textDecodeIsStrictCanonicalAndOptionalAware",
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest#numericCodecChecksDigitsRangeAndOverflow",
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest#numericErrorFillerDoesNotBecomeBusinessZero",
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest#booleanAndReservedFieldsRejectUnknownBytes",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#headerEncodingMatchesIndependentUi232GoldenVector",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#responseAndEventHeadersRoundTripWithoutLeakingContext",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#headerDecoderRejectsEveryFixedFieldAndProfileCorruption",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#fixedPayloadIsDefensiveAndWireMessageChecksLengths",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#transportAndRouteContractsRejectEveryMismatch",
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest#metadataAndExpectedRouteEstablishNullAndRangeContracts",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#allSixtyFourLayoutsRoundTripMinimumSuccessValues",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#everyResponseLayoutUsesExactErrorFillersAndNoRecords",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#fixedAndIndependentGoldenFieldsEncodeAtExactOffsets",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#encodeRejectsUnknownMissingWrongTypeAndRecordViolations",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#valuesAreImmutableNullSafeAndRedacted",
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#numericDigitLimitIsCheckedWithoutOverflow",
            "dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest#allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes",
            "dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest#everyRepeatingLayoutAcceptsItsMaximumRecordBoundary",
            "dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest#sharedCodecProducesIdenticalBytesUnderConcurrentUse",
            "dev.codex.schubert.nk.protocol.codec.ScenarioRecordEncodingTest#w03SingleRecordGoldenHasNoInventedDataAndRejectsNullUnknownAndNonRecordLayouts",
            "dev.codex.schubert.nk.protocol.codec.ScenarioRecordEncodingTest#rd02SingleRecordDecodeUsesLiteralGoldenAndOwnsItsValues",
            "dev.codex.schubert.nk.protocol.codec.ScenarioRecordEncodingTest#rd02RejectsNullUnknownNonRecordLengthAndMalformedFieldBytes",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#verificationRejectsAllThirtyTwoDigestBytePositions",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#descriptorAcceptsOnlyCanonicalPathHashAndLengthEquation",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#writesAndReadsHeaderlessExactRecordsWithIndependentHash",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#acceptsTheDocumentedTenThousandRecordFortyEightMillionByteMaximum",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#writeRejectsNullCountLengthAndIoFailure",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#decodeRejectsTruncationExtraHashAndIoFailure",
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest#contentMetadataRejectsInvalidValues",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#acceptsExactlySevenSsc004ExtensionMimePairs",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#dispositionMapsOnlyIAndA",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#utf8MaximumFieldsAndN12UseIndependentCanonicalBoundaries",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#bug040StorageExtensionCannotBeHiddenByDisplayMetadata",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#rejectsNonCanonicalTextPathsNamesSizesAndHashes",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#rejectsEveryMimeCrossProductAndVideoAttachment",
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest#constructorRejectsNullComponents",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#enumsMapOnlyApprovedWireValues",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#authenticationContextValidatesAndRedacts",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#validHeadersCoverRequestResponseErrorAndEventProfiles",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerConstructorRejectsEveryStructuralViolation",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerValidateAgainstRejectsEachMetadataMismatch",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerReferencesRejectNullAtTheNamedInvariantBoundary",
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow",
            "dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#catalogMatchesIndependentUi234To236Fixture",
            "dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#parserRejectsMalformedUnknownAndDuplicateRows",
            "dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#layoutFieldsRejectWrongAreaGapLengthAndNull",
            "dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#registryMatchesIndependentUi233Catalog",
            "dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#registryRejectsEmptyNullDuplicateAndKindMismatches",
            "dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#layoutDefinitionChecksEveryLengthAndKindInvariant",
            "dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#layoutIdAndFieldDefinitionAreStrictAndOneBased",
            "dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest#page001SecondPageHasIndependentExpectedBounds",
            "dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest#page002MaximumEffectivePageKeepsExactNineDigitArithmetic",
            "dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest#page003RejectsIndependentRangeAndOneFieldArithmeticChanges",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#pageConstantsCountsAndArithmeticAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#listRecordConditionsAndOrderingAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#scenarioInlineAndLargeFileConditionsAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#mediaAnimationAndMusicConditionsAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#loginUserPasswordDateAndSessionRulesAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#notificationCancellationAndQuestionStateConditionsAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#receiptWebAndDefensiveContractsAreEnforced",
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest#deletedNotificationNeverContainsAnswer",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allNamedTypesHaveIndependentDirectionalFieldMeaning",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#explicitCatalogMatchesIndependentSs323NamedTypeFixture",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes",
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#typedModelsAndHelpersRejectNullMissingAndWrongKinds",
            "dev.codex.schubert.nk.protocol.layout.SemanticDirectBoundaryTest#sem001PasswordCharacterByteAndUsernameLimits",
            "dev.codex.schubert.nk.protocol.layout.SemanticDirectBoundaryTest#sem002InclusiveDateLimitsAndOneSidedFilters",
            "dev.codex.schubert.nk.protocol.layout.SemanticDirectBoundaryTest#sem003QuestionAndWebLogTextContracts",
            "dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticHelpersDecodeAndEncodeEverySupportedShape",
            "dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects",
            "dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticValueObjectsNormalizeValidateCompareAndRedact",
            "dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticEncodingHelpersRejectNullReferences",
            "dev.codex.schubert.nk.protocol.layout.semantic.EnumWireCompatibilityTest#enum001SerializedAnswerStateMatchesIndependentProtocolVector",
            "dev.codex.schubert.nk.protocol.layout.semantic.EnumWireCompatibilityTest#enum002EverySemanticEnumRetainsItsFieldIndependentSerialDescriptor",
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables",
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#allN12IdentifierTypesEnforceTheSharedPositiveRange",
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#typedHelpersConvertIntAndIdentifiersWithoutLosingWireKinds",
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#allAllowlistedEnumsExposeExplicitWireValuesAndGenericConversion",
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues",
            "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest#bug037ExpandedYearsAndUnrepresentableInstantsAreRejected",
            "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest#bug037HeaderSenderRejectsBadTimeAndPreservesAdjacentContext",
            "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest#bug037RequiredAndOptionalDataSendersRejectBadTime",
            "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest#formatsAndParsesStrictJstMilliseconds",
            "dev.codex.schubert.nk.protocol.transport.BrokerTopologyTest#sixDestinationsMatchTheIndependentPhysicalAndLimitOracle",
            "dev.codex.schubert.nk.protocol.transport.BrokerTopologyTest#nullUnknownAndNearMatchAddressesAreDenied",
            "dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest#iso009PrimaryAndProtocolAreRequired",
            "dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest#iso010SameNodeIsRetainedWithoutSelfSuppression",
            "dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest#iso011EqualsTrueDoesNotHideDistinctProtocolIdentity",
            "dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest#iso012DisabledPrimarySuppressionCannotHideProtocol",
            "dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackExceptionTest#primaryAndRollbackMustBothBePresent",
            "dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackExceptionTest#sameNodeIsRetainedOnceWithoutSelfSuppression",
            "dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackExceptionTest#distinctEqualValuedNodesAreBothRetained",
            "dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackExceptionTest#disabledPrimarySuppressionDoesNotHideRollbackFailure");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed pure Protocol semantic class and zero-argument method" + " required");
      }
      var names = methods.computeIfAbsent(row[0], ignored -> new ArrayList<>());
      if (names.contains(row[1])) throw new IllegalStateException("duplicate method");
      names.add(row[1]);
    }
    var expected =
        methods.entrySet().stream()
            .flatMap(entry -> entry.getValue().stream().map(name -> entry.getKey() + "#" + name))
            .collect(Collectors.toSet());
    if (!expected.equals(allowed)
        || expected.size() != EXPECTED_TESTS
        || methods.size() != EXPECTED_SUITES)
      throw new IllegalStateException("exact pure Protocol semantic inventory required");
    Path output = Path.of(args[0]);
    Files.createDirectory(output);
    List<Result> results = new ArrayList<>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier id, TestExecutionResult outcome) {
            if (!id.isTest()) return;
            var source = (MethodSource) id.getSource().orElseThrow();
            results.add(
                new Result(
                    source.getClassName(),
                    source.getMethodName(),
                    outcome.getStatus().name(),
                    outcome.getThrowable().map(t -> t.getClass().getName()).orElse("")));
          }

          @Override
          public void executionSkipped(TestIdentifier id, String reason) {
            if (!id.isTest()) return;
            var source = (MethodSource) id.getSource().orElseThrow();
            results.add(new Result(source.getClassName(), source.getMethodName(), "SKIPPED", ""));
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                methods.entrySet().stream()
                    .flatMap(
                        entry ->
                            entry.getValue().stream()
                                .map(name -> DiscoverySelectors.selectMethod(entry.getKey(), name)))
                    .toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .configurationParameter("junit.jupiter.extensions.autodetection.enabled", "false")
            .build());
    var value = summary.getSummary();
    boolean passed =
        results.size() == EXPECTED_TESTS
            && expected.equals(
                results.stream().map(r -> r.type() + "#" + r.method()).collect(Collectors.toSet()))
            && results.stream().allMatch(r -> r.status().equals("SUCCESSFUL"))
            && value.getTestsFoundCount() == EXPECTED_TESTS
            && value.getTestsStartedCount() == EXPECTED_TESTS
            && value.getTestsSucceededCount() == EXPECTED_TESTS
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0;
    for (String type : methods.keySet()) {
      var rows = results.stream().filter(r -> r.type().equals(type)).toList();
      try (var stream =
          Files.newBufferedWriter(
              output.resolve("TEST-" + type + ".xml"),
              StandardCharsets.UTF_8,
              StandardOpenOption.CREATE_NEW)) {
        var xml = XMLOutputFactory.newFactory().createXMLStreamWriter(stream);
        xml.writeStartDocument("UTF-8", "1.0");
        xml.writeStartElement("testsuite");
        xml.writeAttribute("name", type);
        xml.writeAttribute("tests", Integer.toString(rows.size()));
        xml.writeAttribute(
            "failures",
            Long.toString(rows.stream().filter(r -> r.status().equals("FAILED")).count()));
        xml.writeAttribute("errors", "0");
        xml.writeAttribute(
            "skipped",
            Long.toString(
                rows.stream()
                    .filter(r -> !List.of("SUCCESSFUL", "FAILED").contains(r.status()))
                    .count()));
        for (var row : rows) {
          xml.writeStartElement("testcase");
          xml.writeAttribute("classname", row.type());
          xml.writeAttribute("name", row.method());
          if (!row.status().equals("SUCCESSFUL")) {
            xml.writeEmptyElement(row.status().equals("FAILED") ? "failure" : "skipped");
            xml.writeAttribute("type", row.failureType());
          }
          xml.writeEndElement();
        }
        xml.writeEndElement();
        xml.writeEndDocument();
        xml.close();
      }
    }
    String counts =
        "found="
            + value.getTestsFoundCount()
            + ";started="
            + value.getTestsStartedCount()
            + ";succeeded="
            + value.getTestsSucceededCount()
            + ";failed="
            + value.getTestsFailedCount()
            + ";skipped="
            + value.getTestsSkippedCount()
            + ";aborted="
            + value.getTestsAbortedCount()
            + ";containerFailed="
            + value.getContainersFailedCount()
            + ";containerAborted="
            + value.getContainersAbortedCount()
            + ";passed="
            + passed;
    Files.writeString(
        output.resolve("summary.safe.txt"),
        counts,
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW);
    System.out.println("locale=" + java.util.Locale.getDefault().toLanguageTag());
    System.out.println("runtime.version=" + Runtime.version());
    System.out.println("os.name=" + System.getProperty("os.name"));
    System.out.println("os.arch=" + System.getProperty("os.arch"));
    System.out.println("os.version=" + System.getProperty("os.version"));
    System.out.println(counts);
    if (!passed) throw new IllegalStateException("exact pure Protocol semantic run not successful");
  }
}
