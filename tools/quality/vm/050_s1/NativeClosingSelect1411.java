import java.io.File;
import java.util.*;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.SessionInfo;
import org.jacoco.core.tools.ExecFileLoader;

/** PT-OPS-CLOSING1411001/SS342343354/451: monotonic independent oracle, select no union. */
public final class NativeClosingSelect1411 {
  private NativeClosingSelect1411() {}
  static void require(boolean value) {
    if (!value) throw new IllegalArgumentException("fixed closing pair refused");
  }
  static Map<Long,ExecutionData> index(Collection<ExecutionData> values) {
    require(values!=null&&!values.isEmpty());
    var result=new HashMap<Long,ExecutionData>();
    for(var v:values) {
      require(v!=null&&v.getName()!=null&&!v.getName().isEmpty()&&v.getProbes()!=null&&v.getProbes().length>0);
      require(result.putIfAbsent(v.getId(),v)==null);
    }
    return result;
  }
  static void verify(SessionInfo terminal,SessionInfo closing,Collection<ExecutionData> before,
                     Collection<ExecutionData> after,long lower,long upper) {
    require(terminal!=null&&closing!=null&&lower>0&&upper>=lower);
    require(terminal.getId()!=null&&terminal.getId().equals(closing.getId())
        &&terminal.getStartTimeStamp()==closing.getStartTimeStamp()
        &&terminal.getStartTimeStamp()>=lower
        &&terminal.getDumpTimeStamp()>=terminal.getStartTimeStamp()
        &&closing.getDumpTimeStamp()>=terminal.getDumpTimeStamp()
        &&closing.getDumpTimeStamp()<=upper);
    var first=index(before);var last=index(after);
    for(var entry:first.entrySet()) {
      var v=entry.getValue();var w=last.get(entry.getKey());
      require(w!=null&&v.getName().equals(w.getName())&&v.getProbes().length==w.getProbes().length);
      var a=v.getProbes();var b=w.getProbes();
      for(int i=0;i<a.length;i++)require(!a[i]||b[i]);
    }
  }
  public static void main(String[] args)throws Exception {
    require(args!=null&&args.length==4&&Arrays.stream(args).allMatch(Objects::nonNull));
    var first=new ExecFileLoader();first.load(new File(args[0]));
    var last=new ExecFileLoader();last.load(new File(args[1]));
    var a=first.getSessionInfoStore().getInfos();var b=last.getSessionInfoStore().getInfos();
    require(a.size()==1&&b.size()==1);
    verify(a.getFirst(),b.getFirst(),first.getExecutionDataStore().getContents(),last.getExecutionDataStore().getContents(),Long.parseLong(args[2]),Long.parseLong(args[3]));
    System.out.println("{\"sameSession\":true,\"probeMonotonic\":true,\"latestClosingOnly\":true,\"terminalClasses\":"+first.getExecutionDataStore().getContents().size()+",\"closingClasses\":"+last.getExecutionDataStore().getContents().size()+"}");
  }
}
