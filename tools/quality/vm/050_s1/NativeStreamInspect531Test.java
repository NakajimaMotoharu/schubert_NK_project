/** Literal fixed bounds, role, null and boundary oracle. No stream, VM or production invocation. */
public final class NativeStreamInspect531Test {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("native window vector "+count);}
  public static void main(String[] args){
    long start=java.time.Instant.parse("2026-10-07T19:46:29.837227Z").toEpochMilli();
    long end=java.time.Instant.parse("2026-10-07T20:08:51.344734Z").toEpochMilli();
    for(String role:new String[]{"parent","backup","cleanup","expiry"}){
      check(NativeStreamInspect531.current(role,"literal",start,start));check(NativeStreamInspect531.current(role,"literal",end,end));
      check(!NativeStreamInspect531.current(role,"literal",start-1,start));check(!NativeStreamInspect531.current(role,"literal",end+1,end+1));
      check(!NativeStreamInspect531.current(role,"literal",start,start-1));check(!NativeStreamInspect531.current(role,"literal",start,end+1));
      check(!NativeStreamInspect531.current(role,null,start,end));check(!NativeStreamInspect531.current(role,"",start,end));
    }
    String[] roles={"root-api193","root-web193","ordinary-api193","ordinary-web193"};
    String[] ids={"API-844d2217a6494e4f9f852fc4f488a0fa-root","WEB-7127bb06489a4218acd2b72570ce1ec5-root","API-844d2217a6494e4f9f852fc4f488a0fa-ordinary","WEB-7127bb06489a4218acd2b72570ce1ec5-ordinary"};
    long[] ends={end,end,1791407716520L,1791407714709L};
    for(int i=0;i<roles.length;i++){
      check(NativeStreamInspect531.current(roles[i],ids[i],start,ends[i]));check(!NativeStreamInspect531.current(roles[i],ids[i],start,ends[i]+1));
      check(!NativeStreamInspect531.current(roles[i],"foreign",start,end));check(!NativeStreamInspect531.current(roles[i],ids[i],end+1,end+1));
      check(!NativeStreamInspect531.current(roles[i],ids[i],start-1,start));check(!NativeStreamInspect531.current(roles[i],ids[i],start,start-1));
    }
    check(!NativeStreamInspect531.current(null,"literal",start,end));check(!NativeStreamInspect531.current("foreign","literal",start,end));
    System.out.println("PG531_SESSION_WINDOW_ORACLE independentAssertions="+count+" nullNegative=true rawSessionOutput0=true vmActions0=true productionPT0=true");
  }
}
