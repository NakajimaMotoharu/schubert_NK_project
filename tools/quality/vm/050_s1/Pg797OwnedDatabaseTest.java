import java.lang.reflect.Proxy;
import java.sql.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

/** Literal query contract/fault/lost-state vectors. No VM, no real connection or Production PT. */
public final class Pg797OwnedDatabaseTest {
  static int assertions;
  static void check(boolean v){assertions++;if(!v)throw new AssertionError("database liveness vector "+assertions);}
  interface Op{void run()throws Exception;}
  static void refused(Class<? extends Throwable>type,Op op)throws Exception{
    try{op.run();throw new AssertionError("missing refusal");}catch(Throwable t){check(type.isInstance(t));}
  }
  static final class Fixture{
    boolean closed,auto,readOnly=true,locked=true,nullNumber,first=true,second;
    int backend=17,queries,cursor;String role="schubert_batch",database="schubert_nk",application="PG798-fixed-pending",transaction="on",fault="";Throwable failure=new SQLException("PRIVATE");
    void at(String method)throws Throwable{if(fault.equals(method))throw failure;}
    ResultSet rows(){cursor=0;return(ResultSet)Proxy.newProxyInstance(getClass().getClassLoader(),new Class<?>[]{ResultSet.class},(p,m,a)->{
      at("result."+m.getName());return switch(m.getName()){
        case"next"->++cursor==1?first:second;case"getInt"->backend;case"wasNull"->nullNumber;case"getBoolean"->locked;
        case"getString"->switch((int)a[0]){case 2->role;case 3->database;case 4->application;case 5->transaction;default->throw new AssertionError("foreign field");};case"close"->null;default->throw new AssertionError("unexpected result call");};});}
    Statement statement(){return(Statement)Proxy.newProxyInstance(getClass().getClassLoader(),new Class<?>[]{Statement.class},(p,m,a)->{
      at("statement."+m.getName());if(m.getName().equals("close"))return null;
      check(m.getName().equals("executeQuery"));String q=(String)a[0];check(q.startsWith("select pg_backend_pid(),current_user,current_database(),current_setting('application_name')")&&q.contains("71419602")&&q.contains("mode='ExclusiveLock'")&&!q.contains("set_config"));queries++;return rows();});}
    Connection connection(){return(Connection)Proxy.newProxyInstance(getClass().getClassLoader(),new Class<?>[]{Connection.class},(p,m,a)->{
      at("connection."+m.getName());return switch(m.getName()){case"isClosed"->closed;case"getAutoCommit"->auto;case"isReadOnly"->readOnly;case"createStatement"->statement();default->throw new AssertionError("mutation/reopen not allowed");};});}
    Pg797OwnedDatabase lease(){return new Pg797OwnedDatabase(connection(),new Pg797OwnedDatabase.Expected(17,"schubert_batch","PG798-fixed-pending","schubert_nk"));}
  }
  public static void main(String[]args)throws Exception{
    var f=new Fixture();var lease=f.lease();lease.verify();lease.verify();check(f.queries==2&&lease.heartbeatAllowed());f.closed=true;lease.confirmClosed();check(!lease.heartbeatAllowed());refused(SQLException.class,lease::verify);refused(SQLException.class,lease::confirmClosed);check(f.queries==2);
    for(String bad:List.of("closed","auto","readOnly","backend","role","database","application","transaction","locked","nullNumber","first","second","nullRole")){
      var v=new Fixture();switch(bad){case"closed"->v.closed=true;case"auto"->v.auto=true;case"readOnly"->v.readOnly=false;case"backend"->v.backend=18;case"role"->v.role="foreign";case"database"->v.database="foreign";case"application"->v.application="foreign";case"transaction"->v.transaction="off";case"locked"->v.locked=false;case"nullNumber"->v.nullNumber=true;case"first"->v.first=false;case"second"->v.second=true;case"nullRole"->v.role=null;default->throw new AssertionError();}
      var l=v.lease();refused(SQLException.class,l::verify);check(!l.heartbeatAllowed());int count=v.queries;refused(SQLException.class,l::verify);refused(SQLException.class,l::confirmClosed);check(v.queries==count);
    }
    for(String point:List.of("connection.isClosed","connection.getAutoCommit","connection.isReadOnly","connection.createStatement","statement.executeQuery","result.next","result.getInt","result.wasNull","result.getString","result.getBoolean","result.close","statement.close"))for(Throwable failure:List.of(new SQLException("PRIVATE"),new IllegalStateException("PRIVATE"),new AssertionError("PRIVATE"))){
      var v=new Fixture();v.fault=point;v.failure=failure;var l=v.lease();try{l.verify();throw new AssertionError("missing failure");}catch(SQLException|RuntimeException|Error actual){check(actual==failure);}
      check(!l.heartbeatAllowed());int count=v.queries;refused(SQLException.class,l::verify);check(v.queries==count);
    }
    var open=new Fixture();var l=open.lease();refused(SQLException.class,l::confirmClosed);check(!l.heartbeatAllowed());
    var other=new Fixture();var owned=other.lease();var error=new AtomicReference<Throwable>();var t=new Thread(()->{try{owned.verify();}catch(Throwable failure){error.set(failure);}});t.start();t.join();check(error.get()instanceof SQLException&&!owned.heartbeatAllowed()&&other.queries==0);
    refused(NullPointerException.class,()->new Pg797OwnedDatabase(null,new Pg797OwnedDatabase.Expected(17,"schubert_batch","PG798-fixed-pending","schubert_nk")));
    refused(NullPointerException.class,()->new Pg797OwnedDatabase(new Fixture().connection(),null));
    for(Object[]v:List.of(new Object[]{0,"schubert_batch","PG798-fixed-pending","schubert_nk"},new Object[]{17,"foreign","PG798-fixed-pending","schubert_nk"},new Object[]{17,"schubert_batch","PRIVATE","schubert_nk"},new Object[]{17,"schubert_batch","PG798-fixed-pending","foreign"}))refused(IllegalArgumentException.class,()->new Pg797OwnedDatabase.Expected((int)v[0],(String)v[1],(String)v[2],(String)v[3]));
    check(new Pg797OwnedDatabase.Expected(17,"schubert_batch","PG798-fixed-pending","schubert_nk").toString().equals("OwnedDatabase.Expected[REDACTED]"));
    System.out.println("PG797_DATABASE_ORACLE assertions="+assertions+" mutations0=true actualSessionNotInferred=true productionPT0=true");
  }
}
