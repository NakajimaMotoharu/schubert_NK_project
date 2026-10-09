import java.sql.SQLException;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

/** Independent whole-wiring vectors, not Production PT. */
public final class Pg798DatabaseScopeTest{
  static int assertions;
  static void check(boolean v){assertions++;if(!v)throw new AssertionError("scope vector "+assertions);}
  public static void main(String[]args)throws Exception{
    for(boolean second:List.of(false,true))for(Throwable failure:List.of(new SQLException("PRIVATE"),new IllegalStateException("PRIVATE"),new AssertionError("PRIVATE"))){
      var a=new Pg797OwnedDatabaseTest.Fixture();var b=new Pg797OwnedDatabaseTest.Fixture();var scope=new Pg798DatabaseScope(a.lease(),b.lease());scope.verify();check(scope.confirmed()&&scope.observations()==1&&a.queries==1&&b.queries==1);
      var bad=second?b:a;bad.fault="statement.executeQuery";bad.failure=failure;
      try{scope.verify();throw new AssertionError("missing refusal");}catch(SQLException|RuntimeException|Error actual){check(actual==failure);}
      check(!scope.confirmed());int aq=a.queries,bq=b.queries;
      for(int n=0;n<3;n++){try{scope.verify();throw new AssertionError("missing latch");}catch(SQLException actual){check(a.queries==aq&&b.queries==bq);}}
    }
    for(boolean second:List.of(false,true)){
      var a=new Pg797OwnedDatabaseTest.Fixture();var b=new Pg797OwnedDatabaseTest.Fixture();var al=a.lease();var bl=b.lease();var scope=new Pg798DatabaseScope(al,bl);var bad=second?b:a;bad.closed=true;
      try{(second?bl:al).verify();throw new AssertionError();}catch(SQLException expected){check(!scope.confirmed());}
      try{scope.verify();throw new AssertionError();}catch(SQLException expected){check(a.queries==0&&b.queries==0);}
    }
    var a=new Pg797OwnedDatabaseTest.Fixture();var b=new Pg797OwnedDatabaseTest.Fixture();var scope=new Pg798DatabaseScope(a.lease(),b.lease());scope.verify();scope.verify();check(scope.observations()==2&&scope.maxGapNanos()>=0);
    var failure=new AtomicReference<Throwable>();var thread=new Thread(()->{try{scope.verify();}catch(Throwable actual){failure.set(actual);}});thread.start();thread.join();check(failure.get()instanceof SQLException&&!scope.confirmed()&&a.queries==2&&b.queries==2);
    for(boolean first:List.of(false,true))try{new Pg798DatabaseScope(first?null:a.lease(),first?b.lease():null);throw new AssertionError();}catch(NullPointerException expected){check(true);}
    System.out.println("PG798_SCOPE_ORACLE assertions="+assertions+" pairLostNoSQL=true productionPT0=true");
  }
}
