import java.sql.*;
import java.util.Objects;

/** SSC238/DBLIVENESS797001..004: same server ownership, no data/timeout/connection mutation. */
public final class Pg797OwnedDatabase {
  public record Expected(int backend,String role,String application,String database,boolean readOnly,boolean advisory) {
    public Expected(int backend,String role,String application,String database){this(backend,role,application,database,true,true);}
    public Expected {
      Objects.requireNonNull(role);Objects.requireNonNull(application);Objects.requireNonNull(database);
      if(backend<2||!java.util.Set.of("schubert_batch","schubert_migration").contains(role)||!application.matches("PG[0-9]{3}-[a-z-]{1,32}")||!database.equals("schubert_nk")||role.equals("schubert_migration")&&(!readOnly||advisory)||role.equals("schubert_batch")&&!advisory)throw new IllegalArgumentException("fixed database expectation unavailable");
    }
    @Override public String toString(){return "OwnedDatabase.Expected[REDACTED]";}
  }
  private final Connection connection;
  private final Expected expected;
  private final long thread;
  private boolean lost;
  private boolean closed;
  public Pg797OwnedDatabase(Connection connection,Expected expected){this.connection=Objects.requireNonNull(connection);this.expected=Objects.requireNonNull(expected);thread=Thread.currentThread().threadId();}
  public boolean heartbeatAllowed(){return !lost&&!closed;}
  public void verify()throws SQLException {
    if(lost||closed)throw unavailable();
    try {
      require(thread==Thread.currentThread().threadId()&&!connection.isClosed()&&!connection.getAutoCommit()&&connection.isReadOnly()==expected.readOnly());
      try(var s=connection.createStatement();var r=s.executeQuery("select pg_backend_pid(),current_user,current_database(),current_setting('application_name'),current_setting('transaction_read_only'),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock' and granted)")){
        require(r.next());int backend=r.getInt(1);require(!r.wasNull()&&backend==expected.backend());
        require(expected.role().equals(r.getString(2))&&expected.database().equals(r.getString(3))&&expected.application().equals(r.getString(4))&&(expected.readOnly()?"on":"off").equals(r.getString(5)));
        boolean held=r.getBoolean(6);require(!r.wasNull()&&held==expected.advisory()&&!r.next());
      }
    }catch(SQLException|RuntimeException|Error failure){lost=true;throw failure;}
  }
  /** Only after actual caller rollback/close; cannot infer normal close from lost ownership. */
  public void confirmClosed()throws SQLException {
    if(lost||closed)throw unavailable();
    try{require(thread==Thread.currentThread().threadId()&&connection.isClosed());closed=true;}
    catch(SQLException|RuntimeException|Error failure){lost=true;throw failure;}
  }
  private static void require(boolean value)throws SQLException{if(!value)throw unavailable();}
  private static SQLException unavailable(){return new SQLException("owned database not confirmed");}
}
