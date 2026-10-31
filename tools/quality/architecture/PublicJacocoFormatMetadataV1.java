import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import org.jacoco.core.data.ExecutionDataReader;

/** WBS-G07/3021: public exec format metadata only; never load target classes or print values. */
public final class PublicJacocoFormatMetadataV1 {
  private PublicJacocoFormatMetadataV1() {}

  private static boolean printable(String value) {
    return value.chars().allMatch(c -> c >= 32 && c <= 126);
  }

  private static final class Counts extends ExecutionDataReader {
    long headers;
    long sessions;
    long classes;
    long probes;
    long hits;
    long sessionUnits;
    long classUnits;
    long asciiSessions;
    long asciiClasses;
    long orderedSessions;

    Counts(ByteArrayInputStream input) {
      super(input);
      setSessionInfoVisitor(
          info -> {
            sessions++;
            sessionUnits += info.getId().length();
            if (printable(info.getId())) asciiSessions++;
            if (info.getStartTimeStamp() >= 0
                && info.getDumpTimeStamp() >= info.getStartTimeStamp()) orderedSessions++;
          });
      setExecutionDataVisitor(
          data -> {
            classes++;
            classUnits += data.getName().length();
            if (printable(data.getName())) asciiClasses++;
            probes += data.getProbes().length;
            for (boolean hit : data.getProbes()) if (hit) hits++;
          });
    }

    @Override
    protected boolean readBlock(byte type) throws java.io.IOException {
      boolean result = super.readBlock(type);
      if (type == 1) headers++;
      return result;
    }
  }

  public static void main(String[] args) {
    try {
      if (args.length != 1) throw new IllegalArgumentException();
      Path path = Path.of(args[0]);
      long size = Files.size(path);
      if (size < 5 || size > 1_048_576) throw new IllegalArgumentException();
      byte[] bytes = Files.readAllBytes(path);
      var input = new ByteArrayInputStream(bytes);
      var reader = new Counts(input);
      if (reader.read() || input.available() != 0 || reader.headers < 1)
        throw new IllegalArgumentException();
      System.out.printf(
          Locale.ROOT,
          "{\"bytes\":%d,\"headers\":%d,\"sessions\":%d,\"classes\":%d,"
              + "\"probes\":%d,\"hits\":%d,\"sessionUnits\":%d,\"classUnits\":%d,"
              + "\"asciiSessions\":%d,\"asciiClasses\":%d,\"orderedSessions\":%d}%n",
          bytes.length, reader.headers, reader.sessions, reader.classes, reader.probes, reader.hits,
          reader.sessionUnits, reader.classUnits, reader.asciiSessions, reader.asciiClasses,
          reader.orderedSessions);
    } catch (Exception failure) {
      // A rejected metadata input is not a successful product test. Never echo input or message.
      System.err.println("METADATA_INPUT_REJECTED:" + failure.getClass().getSimpleName());
      System.exit(2);
    }
  }
}
