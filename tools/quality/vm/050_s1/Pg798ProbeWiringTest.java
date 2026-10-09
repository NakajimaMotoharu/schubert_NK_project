import java.sql.SQLException;
import java.util.List;

/** Invokes the actual generated retain entry, no VM/business writes. */
public final class Pg798ProbeWiringTest{
  public static void main(String[]args)throws Exception{
    int vectors=0;
    for(boolean second:List.of(false,true))for(Throwable failure:List.of(new SQLException("PRIVATE"),new IllegalStateException("PRIVATE"),new AssertionError("PRIVATE"))){
      var a=new Pg797OwnedDatabaseTest.Fixture();var b=new Pg797OwnedDatabaseTest.Fixture();var al=a.lease();var bl=b.lease();
      Pg798DatabaseProbe.databaseScope=new Pg798DatabaseScope(al,bl);
      if(!Pg798DatabaseProbe.retainPulse())throw new AssertionError("initial heartbeat");
      var bad=second?b:a;bad.fault="statement.executeQuery";bad.failure=failure;
      try{(second?bl:al).verify();throw new AssertionError("body failure missing");}catch(SQLException|RuntimeException|Error actual){if(actual!=failure)throw new AssertionError("identity");}
      int aq=a.queries,bq=b.queries;
      for(int n=0;n<3;n++)if(Pg798DatabaseProbe.retainPulse()||a.queries!=aq||b.queries!=bq)throw new AssertionError("retain entry must stop both SQL");
      vectors++;
    }
    System.out.println("PG798_WIRING_ORACLE bodyLossRetainVectors="+vectors+" bothSQLStopped=true productionPT0=true");
  }
}
