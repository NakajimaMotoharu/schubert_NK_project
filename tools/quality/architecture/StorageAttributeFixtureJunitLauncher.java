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
 * Frozen exact storage attribute fixture method catalog only; no package discovery or other tests.
 * No production server/DB/service startup; owned memory registries, supplied attribute maps and
 * own0700-scoped synthetic temporary files only.
 */
public final class StorageAttributeFixtureJunitLauncher {
  private static final int EXPECTED_TESTS = 7;
  private static final int EXPECTED_SUITES = 1;

  private StorageAttributeFixtureJunitLauncher() {}

  private record Result(String type, String method, String status, String failureType) {}

  private static java.util.Optional<Path> temporaryRoot = java.util.Optional.empty();
  private static final List<Path> createdTemporaryChildren = new ArrayList<>();
  private static java.util.Optional<java.nio.file.attribute.UserPrincipal> temporaryOwner =
      java.util.Optional.empty();

  private static void prepareOwnedTemp(Path parent, Path xml) throws Exception {
    parent = parent.toAbsolutePath().normalize();
    if (temporaryRoot.isPresent()
        || !parent.equals(xml.toAbsolutePath().normalize().getParent().resolve("owned-tmp"))
        || Files.isSymbolicLink(parent)
        || !Files.isDirectory(parent, java.nio.file.LinkOption.NOFOLLOW_LINKS)
        || !Files.getPosixFilePermissions(parent)
            .equals(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")))
      throw new IllegalStateException("new fixed private temporary parent required");
    try (var entries = Files.list(parent)) {
      if (entries.findAny().isPresent())
        throw new IllegalStateException("temporary parent must start empty");
    }
    temporaryOwner =
        java.util.Optional.of(Files.getOwner(parent, java.nio.file.LinkOption.NOFOLLOW_LINKS));
    temporaryRoot = java.util.Optional.of(parent);
  }

  public static final class OwnedTempDirs implements org.junit.jupiter.api.io.TempDirFactory {
    public OwnedTempDirs() {}

    @Override
    public Path createTempDirectory(
        org.junit.jupiter.api.extension.AnnotatedElementContext element,
        org.junit.jupiter.api.extension.ExtensionContext context)
        throws Exception {
      if (!(element.getAnnotatedElement() instanceof java.lang.reflect.Field field)
          || !field.getName().equals("root")
          || !field
              .getDeclaringClass()
              .getName()
              .equals("dev.codex.schubert.nk.storage.StorageAttributeGuardTest")
          || !context.getRequiredTestClass().getName().equals(field.getDeclaringClass().getName()))
        throw new IllegalStateException("only the fixed owned JUnit field is permitted");
      Path parent = temporaryRoot.orElseThrow();
      if (Files.isSymbolicLink(parent)
          || !Files.getOwner(parent, java.nio.file.LinkOption.NOFOLLOW_LINKS)
              .equals(temporaryOwner.orElseThrow())
          || !Files.getPosixFilePermissions(parent)
              .equals(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")))
        throw new IllegalStateException("private parent identity changed");
      Path child =
          Files.createTempDirectory(
              parent,
              "case-",
              java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
                  java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      if (!child.getParent().equals(parent)
          || Files.isSymbolicLink(child)
          || !Files.getOwner(child, java.nio.file.LinkOption.NOFOLLOW_LINKS)
              .equals(temporaryOwner.orElseThrow())
          || !Files.getPosixFilePermissions(child)
              .equals(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")))
        throw new IllegalStateException("temporary child outside private owner scope");
      createdTemporaryChildren.add(child);
      return child;
    }
  }

  private static void verifyOwnedTemp(Path output) throws Exception {
    Path parent = temporaryRoot.orElseThrow();
    if (createdTemporaryChildren.size() != EXPECTED_TESTS
        || new java.util.HashSet<>(createdTemporaryChildren).size() != EXPECTED_TESTS
        || !Files.getOwner(parent, java.nio.file.LinkOption.NOFOLLOW_LINKS)
            .equals(temporaryOwner.orElseThrow())
        || !Files.getPosixFilePermissions(parent)
            .equals(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")))
      throw new IllegalStateException("exact temporary lifecycle and private owner required");
    for (Path child : createdTemporaryChildren)
      if (Files.exists(child, java.nio.file.LinkOption.NOFOLLOW_LINKS))
        throw new IllegalStateException("JUnit temporary child remains");
    try (var entries = Files.list(parent)) {
      if (entries.findAny().isPresent())
        throw new IllegalStateException("temporary parent not empty after JUnit");
    }
    Files.writeString(
        output.resolve("temp-ownership.safe.tsv"),
        createdTemporaryChildren.stream()
            .map(p -> p.getFileName().toString() + "\tCREATED_AND_REMOVED\n")
            .collect(Collectors.joining()),
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 4)
      throw new IllegalArgumentException(
          "new XML directory, frozen catalog and fixed locale required");
    if (!Set.of("ja-JP", "tr-TR").contains(args[2])
        || !java.util.Locale.getDefault().toLanguageTag().equals(args[2]))
      throw new IllegalArgumentException("dedicated JVM locale does not match fixed case");
    prepareOwnedTemp(Path.of(args[3]), Path.of(args[0]));
    Set<String> allowed =
        Set.of(
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#med020LargeAssetSizesKeepTransferLimitAndUnixGuards",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#u01SizeAccountingIncludesEmptyPartialPartsButReadyRequiresWholeRecords",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#u02AccountingRejectsUnknownSizeBoundsAndInvalidOwnershipOrLinkAttributes",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#a01NullInvalidAndBoundaryOsIdentityNamesAreExplicit",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#a02FileRequiresOneLinkExactBytesAnd0640WithoutSpecialBits",
            "dev.codex.schubert.nk.storage.StorageAttributeGuardTest#a03ActualFileSymlinkHardLinkWrongPermissionAndOwnerRemainUntouched");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed storage attribute fixture class and zero-argument method" + " required");
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
      throw new IllegalStateException("exact storage attribute fixture inventory required");
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
            .configurationParameter(
                "junit.jupiter.tempdir.factory.default", OwnedTempDirs.class.getName())
            .configurationParameter("junit.jupiter.tempdir.cleanup.mode.default", "ALWAYS")
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
    verifyOwnedTemp(output);
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
    if (!passed)
      throw new IllegalStateException("exact storage attribute fixture run not successful");
  }
}
