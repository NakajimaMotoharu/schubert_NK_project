import java.nio.file.Files;
/** BUG722 read-only field-name diagnostics: never prints values or replaces saved originals. */
public final class Pg466ReadbackDiagnostic {
  public static void main(String[] args)throws Exception{
    if(args.length!=0)throw new IllegalArgumentException("no arguments");
    var actual=Pg466HandoffReadback.values();int differences=0;
    for(var e:actual.entrySet())if(!e.getValue().equals(Files.readString(Pg466HandoffReadback.SAVE.resolve(e.getKey()+".private")))){
      if(!java.util.Set.of("business","backup","original","history","fixture","rows").contains(e.getKey()))throw new IllegalStateException("startup metadata differs");
      System.out.println("PG466_READBACK_DIFFERENT field="+e.getKey());differences++;
    }
    System.out.println("PG466_READBACK_DIAGNOSTIC differences="+differences+" mutation0=true");
  }
}
