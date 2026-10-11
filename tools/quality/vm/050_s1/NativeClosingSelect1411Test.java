import java.util.*;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.SessionInfo;

/** Independent handwritten sessions/probes; no Production expected calculation. */
public final class NativeClosingSelect1411Test {
  static int assertions;
  static void check(boolean v){assertions++;if(!v)throw new AssertionError("closing vector");}
  static void refuse(Runnable operation){boolean refused=false;try{operation.run();}catch(IllegalArgumentException expected){refused=true;}check(refused);}
  public static void main(String[] ignored) {
    var first=new SessionInfo("public-golden",100,110);var last=new SessionInfo("public-golden",100,120);
    var before=List.of(new ExecutionData(7,"Golden",new boolean[]{true,false}));
    var after=List.of(new ExecutionData(7,"Golden",new boolean[]{true,true}),new ExecutionData(8,"New",new boolean[]{true}));
    NativeClosingSelect1411.verify(first,last,before,after,100,120);check(true);
    NativeClosingSelect1411.verify(first,new SessionInfo("public-golden",100,110),before,before,100,120);check(true);
    for(var bad:List.of(new SessionInfo("foreign",100,120),new SessionInfo("public-golden",101,120),new SessionInfo("public-golden",100,109),new SessionInfo("public-golden",100,121)))
      refuse(()->NativeClosingSelect1411.verify(first,bad,before,after,100,120));
    for(var bad:List.of(List.of(new ExecutionData(7,"Golden",new boolean[]{false,true})),List.of(new ExecutionData(7,"Foreign",new boolean[]{true,true})),List.of(new ExecutionData(7,"Golden",new boolean[]{true})),List.of(new ExecutionData(8,"New",new boolean[]{true})),List.of(new ExecutionData(7,"Golden",new boolean[]{true,true}),new ExecutionData(7,"Golden",new boolean[]{true,true}))))
      refuse(()->NativeClosingSelect1411.verify(first,last,before,bad,100,120));
    refuse(()->NativeClosingSelect1411.verify(null,last,before,after,100,120));
    refuse(()->NativeClosingSelect1411.verify(first,null,before,after,100,120));
    refuse(()->NativeClosingSelect1411.verify(first,last,null,after,100,120));
    refuse(()->NativeClosingSelect1411.verify(first,last,before,null,100,120));
    refuse(()->NativeClosingSelect1411.verify(first,last,before,List.of(),100,120));
    refuse(()->NativeClosingSelect1411.verify(first,last,before,after,0,120));
    refuse(()->NativeClosingSelect1411.verify(first,last,before,after,121,120));
    refuse(()->NativeClosingSelect1411.verify(new SessionInfo("public-golden",100,99),last,before,after,100,120));
    var nullEntry=new ArrayList<ExecutionData>();nullEntry.add(null);
    refuse(()->NativeClosingSelect1411.verify(first,last,before,nullEntry,100,120));
    System.out.println("CLOSING1411_ORACLE assertions="+assertions);
  }
}
