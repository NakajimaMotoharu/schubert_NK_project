/** Independent literals for lossless old private Map snapshots. Tool-only, Production PT zero. */
public final class Pg456AppliedCompletionTest {
  public static void main(String[] args) {
    if(args.length!=0)throw new IllegalArgumentException("literal vectors only");int count=0;
    String hash="1".repeat(64);
    String input="{/a={uid=0, ino=44, ctime=2026-10-04T00:00:00Z}/"+hash+", /b={gid=986, mode=33184}}";
    String expected="{/a={ctime=2026-10-04T00:00:00Z, ino=44, uid=0}/"+hash+", /b={gid=986, mode=33184}}";
    if(!expected.equals(Pg456AppliedCompletion.canonical(input)))throw new AssertionError("literal canonical value");count++;
    if(!expected.equals(Pg456AppliedCompletion.canonical("{/b={mode=33184, gid=986}, /a={ino=44, ctime=2026-10-04T00:00:00Z, uid=0}/"+hash+"}")))throw new AssertionError("JVM order changes");count++;
    if(expected.equals(Pg456AppliedCompletion.canonical(input.replace("ino=44","ino=45"))))throw new AssertionError("inode loss");count++;
    if(expected.equals(Pg456AppliedCompletion.canonical(input.replace(hash,"2".repeat(64)))))throw new AssertionError("byte hash loss");count++;
    if(!"{}".equals(Pg456AppliedCompletion.canonical("{}")))throw new AssertionError("empty literal");count++;
    if(!"{={ino=44, uid=0}, file={ino=45}}".equals(Pg456AppliedCompletion.canonical("{file={ino=45}, ={uid=0, ino=44}}")))throw new AssertionError("empty relative root path");count++;
    if("{={ino=44}}".equals(Pg456AppliedCompletion.canonical("{={ino=45}}")))throw new AssertionError("root inode omitted");count++;
    for(String bad:new String[]{null,"","{a=1, a=2}","{=1, =2}","{a=}","{a}","{a=1","{a=1}/bad","{a={b=1}"}) {
      try {Pg456AppliedCompletion.canonical(bad);throw new AssertionError("malformed snapshot accepted");}
      catch(IllegalArgumentException expectedFailure) {count++;}
    }
    for(int mode:new int[]{0100400,0100600}) {
      var good=java.util.Map.<String,Object>of("uid",0,"gid",0,"mode",mode,"nlink",1);
      if(!Pg456AppliedCompletion.privateMetadata(good,mode))throw new AssertionError("fixed private mode");count++;
      for(String key:new String[]{"uid","gid","mode","nlink"}) {
        var bad=new java.util.HashMap<>(good);bad.put(key,key.equals("mode")?(mode==0100400?0100600:0100400):2);
        if(Pg456AppliedCompletion.privateMetadata(bad,mode))throw new AssertionError("wrong private metadata");count++;
      }
    }
    if(Pg456AppliedCompletion.privateMetadata(null,0100400) || Pg456AppliedCompletion.privateMetadata(java.util.Map.of(),0100400)
        || Pg456AppliedCompletion.privateMetadata(java.util.Map.of("uid",0,"gid",0,"mode",0100640,"nlink",1),0100640))throw new AssertionError("unsupported private metadata");count++;
    System.out.println("PG456_APPLIED_TOOL_PASS independentAssertions="+count+" productionPtCount=0 nativeExecuted=false");
  }
}
