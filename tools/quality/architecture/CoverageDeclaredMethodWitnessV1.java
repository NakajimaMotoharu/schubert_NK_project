import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.jacoco.core.instr.Instrumenter;
import org.jacoco.core.runtime.OfflineInstrumentationAccessGenerator;

/** Pure bytes: does not load, initialize or execute the target class. */
public final class CoverageDeclaredMethodWitnessV1 {
  private CoverageDeclaredMethodWitnessV1() {}
  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("two bounded public byte paths");
    byte[] original = Files.readAllBytes(Path.of(args[0]));
    byte[] instrumented = new Instrumenter(new OfflineInstrumentationAccessGenerator())
        .instrument(original, "public-composite-config");
    Files.write(Path.of(args[1]), instrumented, StandardOpenOption.CREATE_NEW);
    System.out.println("TARGET_CLASS_LOADED=false");
  }
}
