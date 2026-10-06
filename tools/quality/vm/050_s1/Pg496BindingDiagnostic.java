import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
/** BUG802/YKT571: readonly binding/parse diagnostic, no recovery or private payload output. */
public final class Pg496BindingDiagnostic {
  public static void main(String[] args)throws Exception{
    System.out.println("PG496_BINDING morning="+InspectorUnitSnapshot.Target.MORNING.unit());
    for(Class<?> type:new Class<?>[]{InspectorUnitSnapshot.class,InspectorUnitSnapshot.Target.class,Pg410KnownAuthRecovery.class}){
      System.out.println("PG496_BINDING type="+type.getName()+" source="+type.getProtectionDomain().getCodeSource().getLocation());
    }
    try{Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING);System.out.println("PG496_PARSE actual0=true");}
    catch(Exception failure){
      System.out.println("PG496_PARSE actualFailure="+failure.getClass().getName());
      for(var frame:failure.getStackTrace())System.out.println("PG496_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
      throw new IllegalStateException("readonly binding rejected");
    }
  }
}
