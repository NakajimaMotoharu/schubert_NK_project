import java.util.*;

/** MIG202008 independent argument boundary; not permission, guest mutation or PT credit. */
public final class Pg503ResumePreparationTest {
  public static void main(String[] ignored){
    String s="a".repeat(40),d="b".repeat(64);
    String[][] refused={null,new String[0],new String[]{s},new String[]{null,d},new String[]{s,null},new String[]{s,d,"extra"},new String[]{"x".repeat(40),d},new String[]{s,"X".repeat(64)}};
    for(var value:refused)if(Pg503ResumePreparation.arguments(value))throw new AssertionError("foreign arguments accepted");
    if(!Pg503ResumePreparation.arguments(new String[]{s,d}))throw new AssertionError("fixed demand refused");
    if(!Pg503ResumePreparation.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg503-resume-preparation-v1"))throw new AssertionError("foreign target");
    System.out.println("PG503_RESUME_CALLER_ORACLE independentAssertions=10 actual0=true vmAuthority0=true");
  }
}
