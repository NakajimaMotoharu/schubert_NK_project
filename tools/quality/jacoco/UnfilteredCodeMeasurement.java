/*
 * Supplemental byte-only measurement using the locally pinned JaCoCo0.8.15/ASM9.10.1 APIs.
 * No target class is defined or initialized. No filter, instrumenter, Root report or JAR is changed.
 * Caller must bind exact permitted physical names and byte/exec hashes before invoking this tool.
 * Output is a separate measurement, never an authorization or a PG/PT acceptance decision.
 */
package org.jacoco.core.internal.analysis;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.DigestInputStream;
import java.security.DigestOutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.analysis.IMethodCoverage;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.ExecutionDataReader;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.data.ExecutionDataWriter;
import org.jacoco.core.data.SessionInfo;
import org.jacoco.core.internal.data.CRC64;
import org.jacoco.core.internal.flow.ClassProbesAdapter;
import org.jacoco.core.internal.flow.ClassProbesVisitor;
import org.jacoco.core.internal.flow.MethodProbesVisitor;
import org.jacoco.core.tools.ExecFileLoader;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.tree.MethodNode;

/**
 * F03/451; TOOL-CODEMEASURE001..012 / PT-OPS-EXEC-CRC-002, 005. Outputs original counters without
 * applying analysis filters.
 */
public final class UnfilteredCodeMeasurement {
  private UnfilteredCodeMeasurement() {}

  public static void main(String[] args) throws IOException {
    boolean originalExec = args.length > 0 && args[0].equals("--strict-original-exec");
    int optionCount = originalExec ? 1 : 0;
    boolean lineDeficits = args.length > optionCount && args[optionCount].equals("--line-deficits");
    int execIndex = optionCount + (lineDeficits ? 1 : 0);
    if (args.length < execIndex + 2)
      throw new IllegalArgumentException("exec and explicit class files required");
    ExecutionDataStore data = executionData(Path.of(args[execIndex]), originalExec);
    Set<String> measuredNames = new HashSet<>();
    for (int index = execIndex + 1; index < args.length; index++) {
      byte[] bytes = Files.readAllBytes(Path.of(args[index]));
      var reader = new ClassReader(bytes);
      String name = reader.getClassName();
      if (!measuredNames.add(name)) throw new IllegalArgumentException("duplicate class input");
      long id = CRC64.classId(bytes);
      ExecutionData observed = data.get(id);
      if (observed == null && data.contains(name))
        throw new IllegalStateException("execution/class CRC mismatch");
      if (observed != null && !observed.getName().equals(name))
        throw new IllegalStateException("execution/class name mismatch");
      var analysis = new Measurement(name, id, observed);
      reader.accept(new ClassProbesAdapter(analysis, false), 0);
      var coverage = analysis.coverage;
      System.out.println(
          "CLASS\t"
              + coverage.getName()
              + "\t"
              + String.format("%016x", id)
              + "\t"
              + (observed != null)
              + "\t"
              + analysis.totalProbes
              + "\t"
              + analysis.classAccess
              + counters(coverage));
      for (var method : coverage.getMethods()) {
        System.out.println(
            "METHOD\t"
                + coverage.getName()
                + "\t"
                + method.getName()
                + "\t"
                + method.getDesc()
                + "\t"
                + analysis.access.get(method.getName() + method.getDesc())
                + counters(method));
        if (lineDeficits) printLineDeficits(coverage.getName(), method);
      }
    }
  }

  private static ExecutionDataStore executionData(Path file, boolean original) throws IOException {
    if (!original) {
      var loader = new ExecFileLoader();
      loader.load(file.toFile());
      return loader.getExecutionDataStore();
    }
    var originalDigest = sha256();
    var canonicalDigest = sha256();
    try (var input =
            new DigestInputStream(
                new BufferedInputStream(Files.newInputStream(file)), originalDigest);
        var canonical = new DigestOutputStream(OutputStream.nullOutputStream(), canonicalDigest)) {
      var records = new OriginalExecutionReader(input, new ExecutionDataWriter(canonical)).load();
      // The pinned reader normalizes some encodings. The writer's encoding must match the original.
      if (!MessageDigest.isEqual(originalDigest.digest(), canonicalDigest.digest())) {
        throw new IOException("noncanonical original execution stream");
      }
      return records;
    }
  }

  private static MessageDigest sha256() {
    try {
      return MessageDigest.getInstance("SHA-256");
    } catch (NoSuchAlgorithmException exception) {
      throw new IllegalStateException("required SHA-256 digest unavailable", exception);
    }
  }

  /** Validate an original stream before emitting any coverage rows. */
  private static final class OriginalExecutionReader extends ExecutionDataReader {
    private static final String REQUIRED_SESSION = "single ordered execution session required";

    private final ExecutionDataStore records = new ExecutionDataStore();
    private final ExecutionDataWriter canonical;
    private boolean headerSeen;
    private boolean sessionSeen;

    private OriginalExecutionReader(InputStream input, ExecutionDataWriter canonical) {
      super(input);
      this.canonical = canonical;
      setSessionInfoVisitor(this::visitSession);
      setExecutionDataVisitor(this::visitExecution);
    }

    private ExecutionDataStore load() throws IOException {
      read(); // The JaCoCo file reader consumes all ordinary blocks up to EOF.
      if (!sessionSeen) throw new IOException(REQUIRED_SESSION);
      return records;
    }

    @Override
    protected boolean readBlock(byte kind) throws IOException {
      if (kind == ExecutionDataWriter.BLOCK_HEADER) {
        if (headerSeen) throw new IOException("duplicate execution header");
        headerSeen = true;
      }
      return super.readBlock(kind);
    }

    private void visitSession(SessionInfo session) {
      if (sessionSeen
          || session.getStartTimeStamp() < 0
          || session.getDumpTimeStamp() < session.getStartTimeStamp()) {
        throw new IllegalArgumentException(REQUIRED_SESSION);
      }
      sessionSeen = true;
      canonical.visitSessionInfo(session);
    }

    private void visitExecution(ExecutionData record) {
      if (records.get(record.getId()) != null) {
        throw new IllegalArgumentException("duplicate execution class ID");
      }
      if (records.contains(record.getName())) {
        throw new IllegalArgumentException("duplicate execution class name");
      }
      records.put(record);
      canonical.visitClassExecution(record);
    }
  }

  private static void printLineDeficits(String owner, IMethodCoverage method) {
    if (method.getFirstLine() < 0) return;
    for (int number = method.getFirstLine(); number <= method.getLastLine(); number++) {
      var line = method.getLine(number);
      var instructions = line.getInstructionCounter();
      var branches = line.getBranchCounter();
      if (instructions.getMissedCount() == 0 && branches.getMissedCount() == 0) continue;
      System.out.printf(
          "DEFICIT\t%s\t%s\t%s\t%d\tINSTRUCTION:%d:%d\tBRANCH:%d:%d%n",
          owner,
          method.getName(),
          method.getDesc(),
          number,
          instructions.getMissedCount(),
          instructions.getCoveredCount(),
          branches.getMissedCount(),
          branches.getCoveredCount());
    }
  }

  private static String counters(ICoverageNode node) {
    var out = new StringBuilder();
    for (var entity : ICoverageNode.CounterEntity.values()) {
      ICounter count = node.getCounter(entity);
      out.append('\t')
          .append(entity.name())
          .append(':')
          .append(count.getMissedCount())
          .append(':')
          .append(count.getCoveredCount());
    }
    return out.toString();
  }

  private static final class Measurement extends ClassProbesVisitor {
    private final ClassCoverageImpl coverage;
    private final ExecutionData data;
    private final boolean[] probes;
    private final Map<String, Integer> access = new HashMap<>();
    private int classAccess;
    private int totalProbes;

    private Measurement(String name, long id, ExecutionData data) {
      coverage = new ClassCoverageImpl(name, id, false);
      this.data = data;
      probes = data == null ? null : data.getProbes();
    }

    @Override
    public void visit(
        int version,
        int flags,
        String name,
        String signature,
        String superName,
        String[] interfaces) {
      classAccess = flags;
      coverage.setSignature(signature);
      coverage.setSuperName(superName);
      coverage.setInterfaces(interfaces);
    }

    @Override
    public void visitSource(String source, String debug) {
      coverage.setSourceFileName(source);
    }

    @Override
    public MethodProbesVisitor visitMethod(
        int flags, String name, String descriptor, String signature, String[] exceptions) {
      access.put(name + descriptor, flags);
      var instructions = new InstructionsBuilder(probes);
      return new MethodAnalyzer(instructions) {
        @Override
        public void accept(MethodNode node, MethodVisitor visitor) {
          super.accept(node, visitor);
          var method = new MethodCoverageImpl(name, descriptor, signature);
          // Deliberately do not call any IFilter or mutate the default JaCoCo analysis path.
          new MethodCoverageCalculator(instructions.getInstructions()).calculate(method);
          if (method.containsCode()) coverage.addMethod(method);
        }
      };
    }

    @Override
    public void visitTotalProbeCount(int count) {
      totalProbes = count;
      if (data != null) data.assertCompatibility(coverage.getId(), coverage.getName(), count);
    }
  }
}
