/** Independent numeric µs→ms window oracle, no actual native invocation or raw session output. */
public final class NativeStreamInspect538Test {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("native window vector "+count);}
  public static void main(String[] args){
    long start=1791416025194L,end=1791416026860L;
    String id="BOOTSTRAP-"+"08face250787426aab68796452a0289f"+"-ordinary";
    check(NativeStreamInspect538.current("ordinary-bootstrap196",id,start,start));
    check(NativeStreamInspect538.current("ordinary-bootstrap196",id,end,end));
    check(NativeStreamInspect538.current("ordinary-bootstrap196",id,start,end));
    for(long[] bad:new long[][]{{start-1,start},{end+1,end+1},{start,start-1},{start,end+1},{0,0},{Long.MIN_VALUE,Long.MAX_VALUE}})
      check(!NativeStreamInspect538.current("ordinary-bootstrap196",id,bad[0],bad[1]));
    for(String bad:new String[]{null,"","foreign",id.replace("ordinary","root"),id+"extra"})
      check(!NativeStreamInspect538.current("ordinary-bootstrap196",bad,start,end));
    for(String bad:new String[]{null,"foreign","root-bootstrap196","ordinary-bootstrapadmin196"})
      check(!NativeStreamInspect538.current(bad,id,start,end));
    // Prior positive8 retain their original windows, not the Bootstrap window.
    check(NativeStreamInspect538.current("parent","literal",1791402389837L,1791403731344L));
    check(!NativeStreamInspect538.current("parent","literal",start,end));
    System.out.println("PG538_SESSION_WINDOW_ORACLE independentAssertions="+count+" nullNegative=true rawSessionOutput0=true vmActions0=true productionPT0=true");
  }
}
