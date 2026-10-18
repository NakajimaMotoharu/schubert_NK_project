package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.classfile.ClassFile;
import java.lang.classfile.ClassTransform;
import java.lang.classfile.CodeTransform;
import java.lang.classfile.Opcode;
import java.lang.classfile.instruction.FieldInstruction;
import java.lang.classfile.instruction.InvokeInstruction;
import java.lang.classfile.instruction.NewPrimitiveArrayInstruction;
import java.lang.constant.ClassDesc;
import java.lang.constant.MethodTypeDesc;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Objects;
import java.util.Set;
import java.util.zip.Deflater;
import java.util.zip.Inflater;
import org.junit.jupiter.api.Test;

/** BUG1453/YKT1217, PT-IDEM-SCRATCH001..004: synthetic Error, never real heap exhaustion. */
public final class SnapshotScratchOwnershipTest {
  private static final ThreadLocal<Probe> ACTIVE = new ThreadLocal<>();
  private static final ClassDesc HOOK = ClassDesc.of(SnapshotScratchOwnershipTest.class.getName());
  private static final MethodTypeDesc OBJECT_HOOK =
      MethodTypeDesc.ofDescriptor("(Ljava/lang/Object;)V");
  private static final MethodTypeDesc NO_ARGUMENT = MethodTypeDesc.ofDescriptor("()V");

  @Test
  void scratch001CompressAllocationFailureCannotOwnNativeDeflater() throws Exception {
    fault(ResponseSnapshotCodec.class, "compress", 0);
  }

  @Test
  void scratch002DecompressAllocationFailureCannotOwnNativeInflater() throws Exception {
    fault(ResponseSnapshotCodec.class, "decompress", 0);
  }

  @Test
  void scratch003NegativeControlDetectsDeflaterBeforeUnprotectedArray() throws Exception {
    fault(LegacyScratchFixture.class, "compress", 1);
  }

  @Test
  void scratch004NegativeControlDetectsInflaterBeforeUnprotectedArray() throws Exception {
    fault(LegacyScratchFixture.class, "decompress", 1);
  }

  private static void fault(Class<?> original, String method, int expectedAcquired)
      throws Exception {
    // A distinct test-only name avoids mixing transformed class IDs into the
    // actual Main coverage/CRC inventory. No agent exclusion or Main seam is used.
    String copyName = original.getPackageName() + ".ScratchFaultCopy" + method;
    byte[] bytes = instrument(original, method, ClassDesc.of(copyName));
    Class<?> copy = new ProbeLoader().define(copyName, bytes);
    var target = copy.getDeclaredMethod(method, byte[].class);
    target.setAccessible(true);
    try (var probe = new Probe()) {
      ACTIVE.set(probe);
      try {
        InvocationTargetException thrown =
            assertThrows(
                InvocationTargetException.class,
                () -> target.invoke(null, (Object) new byte[] {0}));
        assertSame(probe.failure, thrown.getCause());
        assertEquals(
            expectedAcquired, probe.acquired.size(), "native acquisition before scratch failure");
        assertEquals(0, probe.ended.size());
      } finally {
        ACTIVE.remove();
      }
    }
  }

  private static byte[] instrument(Class<?> original, String method, ClassDesc copy)
      throws IOException {
    byte[] bytes;
    String oldName = original.getName().replace('.', '/');
    try (var input =
        Objects.requireNonNull(original.getResourceAsStream('/' + oldName + ".class"))) {
      bytes = input.readAllBytes();
    }
    ClassFile files = ClassFile.of();
    var model = files.parse(bytes);
    int[] sites = new int[3];
    CodeTransform selfReferences =
        (builder, element) -> {
          if (element instanceof FieldInstruction field
              && field.owner().asInternalName().equals(oldName)) {
            builder.fieldAccess(
                field.opcode(), copy, field.name().stringValue(), field.typeSymbol());
          } else if (element instanceof InvokeInstruction invoke
              && invoke.owner().asInternalName().equals(oldName)) {
            builder.invoke(
                invoke.opcode(),
                copy,
                invoke.name().stringValue(),
                invoke.typeSymbol(),
                invoke.isInterface());
          } else {
            builder.with(element);
          }
        };
    CodeTransform allocationFault =
        (builder, element) -> {
          if (element instanceof NewPrimitiveArrayInstruction) {
            sites[0]++;
            builder.invokestatic(HOOK, "failScratch", NO_ARGUMENT);
          }
          if (element instanceof InvokeInstruction invoke && zip(invoke)) {
            if (invoke.opcode() == Opcode.INVOKESPECIAL && invoke.name().equalsString("<init>")) {
              sites[1]++;
              builder.with(element).dup().invokestatic(HOOK, "acquired", OBJECT_HOOK);
            } else if (invoke.name().equalsString("end")) {
              sites[2]++;
              builder.dup().with(element).invokestatic(HOOK, "ended", OBJECT_HOOK);
            } else {
              builder.with(element);
            }
          } else {
            builder.with(element);
          }
        };
    byte[] transformed =
        files.transformClass(
            model,
            copy,
            ClassTransform.transformingMethodBodies(selfReferences)
                .andThen(
                    ClassTransform.transformingMethodBodies(
                        m -> m.methodName().equalsString(method), allocationFault)));
    assertEquals(1, sites[0], "one actual primitive scratch allocation");
    assertEquals(1, sites[1], "one actual native constructor");
    assertEquals(2, sites[2], "normal and exceptional native cleanup sites");
    assertEquals(Collections.emptyList(), files.verify(transformed));
    return transformed;
  }

  private static boolean zip(InvokeInstruction invoke) {
    String owner = invoke.owner().asInternalName();
    return owner.equals("java/util/zip/Deflater") || owner.equals("java/util/zip/Inflater");
  }

  public static void failScratch() {
    throw Objects.requireNonNull(ACTIVE.get()).failure;
  }

  public static void acquired(Object value) {
    Objects.requireNonNull(ACTIVE.get()).acquired.add(value);
  }

  public static void ended(Object value) {
    Objects.requireNonNull(ACTIVE.get()).ended.add(value);
  }

  private static final class ProbeLoader extends ClassLoader {
    ProbeLoader() {
      super(SnapshotScratchOwnershipTest.class.getClassLoader());
    }

    Class<?> define(String name, byte[] bytes) {
      return defineClass(name, bytes, 0, bytes.length);
    }
  }

  private static final class Probe implements AutoCloseable {
    final OutOfMemoryError failure = new OutOfMemoryError("synthetic scratch allocation fixture");
    final ArrayList<Object> acquired = new ArrayList<>();
    final Set<Object> ended = Collections.newSetFromMap(new IdentityHashMap<>());

    @Override
    public void close() {
      // Even the deliberately leaking negative controls release their real
      // native allocations here. These are not production cleanup credits.
      for (Object value : acquired) {
        if (!ended.contains(value)) {
          if (value instanceof Deflater deflater) {
            deflater.end();
          } else if (value instanceof Inflater inflater) {
            inflater.end();
          } else {
            throw new AssertionError("unexpected native fixture type");
          }
        }
      }
    }
  }

  /** Deliberately unsafe shape for negative-control validation, never production. */
  public static final class LegacyScratchFixture {
    private LegacyScratchFixture() {}

    private static byte[] compress(byte[] ignored) {
      Deflater nativeOwner = new Deflater(3);
      byte[] scratch = new byte[8192];
      try {
        return scratch;
      } finally {
        nativeOwner.end();
      }
    }

    private static byte[] decompress(byte[] ignored) {
      Inflater nativeOwner = new Inflater();
      byte[] scratch = new byte[8192];
      try {
        return scratch;
      } finally {
        nativeOwner.end();
      }
    }
  }
}
