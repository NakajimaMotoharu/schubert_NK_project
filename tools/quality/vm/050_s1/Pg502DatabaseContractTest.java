import dev.codex.schubert.nk.batch.repository.*;
import java.lang.reflect.Proxy;
import java.sql.*;
import java.time.Instant;
import java.util.UUID;

/** BUG810/YKT579 / SS331332 / independent literal JDBC contract, no DB connection. */
public final class Pg502DatabaseContractTest {
  static int prepared,rowClosed,statementClosed,position,checks;
  static final BatchRun RUN=new BatchRun(UUID.fromString("11111111-2222-4333-8444-555555555555"),
      Instant.parse("2026-10-06T15:00:00.000000Z"));
  static void require(boolean value){if(!value)throw new AssertionError("independent JDBC oracle");checks++;}
  static ResultSet row(){return (ResultSet)Proxy.newProxyInstance(Pg502DatabaseContractTest.class.getClassLoader(),new Class<?>[]{ResultSet.class},
      (proxy,method,args)->switch(method.getName()){
        case "next" -> ++position==1;
        case "getObject" -> switch((String)args[0]){
          case "has_batch_history","has_inbox_progress","identity_consistent" -> Boolean.TRUE;
          case "has_log_progress" -> Boolean.FALSE;
          default -> throw new AssertionError("unknown projection");};
        case "close" -> {rowClosed++;yield null;}
        default -> throw new AssertionError("unknown row call");});}
  static PreparedStatement statement(){return (PreparedStatement)Proxy.newProxyInstance(Pg502DatabaseContractTest.class.getClassLoader(),new Class<?>[]{PreparedStatement.class},
      (proxy,method,args)->switch(method.getName()){
        case "setQueryTimeout" -> {require((Integer)args[0]==5);yield null;}
        case "setObject" -> {
          require((Integer)args[0]==1 ? RUN.id().equals(args[1]) : RUN.cutoff().atOffset(java.time.ZoneOffset.UTC).equals(args[1]));yield null;}
        case "executeQuery" -> row();
        case "close" -> {statementClosed++;yield null;}
        default -> throw new AssertionError("unknown statement call");});}
  static Connection connection(boolean readOnly,boolean autoCommit,int isolation){
    return (Connection)Proxy.newProxyInstance(Pg502DatabaseContractTest.class.getClassLoader(),new Class<?>[]{Connection.class},
      (proxy,method,args)->switch(method.getName()){
        case "getAutoCommit" -> autoCommit;
        case "isReadOnly" -> readOnly;
        case "getTransactionIsolation" -> isolation;
        case "prepareStatement" -> {
          prepared++;require(args[0].equals("select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent from schubert.maintenance_read_run_references(?,?)"));yield statement();}
        default -> throw new AssertionError("parent lifecycle/config changed");});
  }
  public static void main(String[] args){
    for(int mode=0;mode<5;mode++){
      prepared=0;
      var db=connection(mode==0,mode==1,switch(mode){case 2->Connection.TRANSACTION_SERIALIZABLE;case 3->Connection.TRANSACTION_REPEATABLE_READ;case 4->Connection.TRANSACTION_READ_UNCOMMITTED;default->Connection.TRANSACTION_READ_COMMITTED;});
      try{new RunReferenceRepository(db).read(RUN);throw new AssertionError("invalid parent accepted");}
      catch(BatchRepositoryException expected){require(prepared==0);require(expected.getCause()==null);}
    }
    require(new RunReferenceRepository(connection(false,false,Connection.TRANSACTION_READ_COMMITTED)).read(RUN)
        .equals(new RunReferences(true,true,false,true)));
    require(prepared==1 && rowClosed==1 && statementClosed==1 && position==2);
    System.out.println("PG502_DB_ORACLE independentAssertions="+checks+" rejectedModes=5 readonlyStatement0=true parentLifecycleCalls0=true actualDB0=true");
  }
}
