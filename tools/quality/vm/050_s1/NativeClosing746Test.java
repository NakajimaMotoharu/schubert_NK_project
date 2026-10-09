import java.util.*;
import org.jacoco.core.data.*;

/** Independent literal sessions/probes, not Production-generated expected/native authority. */
public final class NativeClosing746Test {
  static final String ID = "BOOTSTRAP-1234567890abcdef1234567890abcdef-ordinary";
  static final List<SessionInfo> FIRST = List.of(new SessionInfo(ID, 1000, 1100));
  static final List<SessionInfo> LAST = List.of(new SessionInfo(ID, 1000, 1200));
  static List<ExecutionData> data(long id, String name, boolean... probes) {
    return List.of(new ExecutionData(id, name, probes));
  }
  static void denied(Runnable operation) {
    try { operation.run(); } catch (IllegalStateException expected) { return; }
    throw new AssertionError("negative vector accepted");
  }
  public static void main(String[] args) {
    var first = data(123, "literal/F", true, false, false);
    var last = data(123, "literal/F", true, true, false);
    if (NativeClosing746.validate(FIRST,LAST,first,last,ID,900,1300) != 1) throw new AssertionError("one independently added probe");
    if (NativeClosing746.validate(FIRST,FIRST,first,first,ID,900,1300) != 0) throw new AssertionError("same-millisecond valid zero gain");
    denied(() -> NativeClosing746.validate(List.of(),LAST,first,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,List.of(),first,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,List.of(LAST.getFirst(),LAST.getFirst()),first,last,ID,900,1300));
    for (SessionInfo s : List.of(new SessionInfo("foreign",1000,1200), new SessionInfo(ID,1001,1200),
        new SessionInfo(ID,1000,1099),new SessionInfo(ID,1000,1301)))
      denied(() -> NativeClosing746.validate(FIRST,List.of(s),first,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,last,ID,1001,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,last,ID,900,1199));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,data(123,"literal/F",false,true,false),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,data(124,"literal/F",true,true,false),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,data(123,"foreign",true,true,false),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,data(123,"literal/F",true,true),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,List.of(),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,List.of(),last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,List.of(last.getFirst(),last.getFirst()),ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,List.of(first.getFirst(),first.getFirst()),last,ID,900,1300));
    denied(() -> NativeClosing746.validate(null,LAST,first,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,null,first,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,null,last,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,null,ID,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,last,null,900,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,last,ID,0,1300));
    denied(() -> NativeClosing746.validate(FIRST,LAST,first,last,ID,1301,1300));
    System.out.println("CLOSING746 literalPositive=2 negative=24 noFallback=true noNativeAuthority=true");
  }
}
