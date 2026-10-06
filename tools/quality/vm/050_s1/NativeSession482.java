import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** BOOT482005: independent exact ordinary Bootstrap session and actual wrapper bounds. */
public final class NativeSession482 {
  public static void main(String[] args)throws Exception{
    if(args.length!=1)throw new IllegalArgumentException("one fixed fresh bootstrap stream required");
    var loader=new ExecFileLoader();loader.load(new File(args[0]));var all=loader.getSessionInfoStore().getInfos();
    if(all.size()!=1)throw new IllegalStateException("single fresh bootstrap session required");
    var session=all.getFirst();
    if(!session.getId().equals("BOOTSTRAP-9af0cd0f91984eac95995c0cdf265c88-ordinary") || session.getStartTimeStamp()<1791279715000L || session.getStartTimeStamp()>1791279730000L || session.getDumpTimeStamp()<session.getStartTimeStamp() || session.getDumpTimeStamp()>1791279730000L)throw new IllegalStateException("fixed bootstrap session rejected");
    System.out.println("PG482_NATIVE_SESSION single=true roleIdMatched=true start="+session.getStartTimeStamp()+" dump="+session.getDumpTimeStamp());
  }
}
