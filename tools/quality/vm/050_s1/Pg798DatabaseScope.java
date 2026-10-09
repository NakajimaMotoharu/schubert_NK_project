import java.sql.SQLException;
import java.util.Objects;

/** BUG945/YKT714: one owner, both leases, sticky whole-scope loss; no new Connection. */
public final class Pg798DatabaseScope {
  private final Pg797OwnedDatabase first,second;
  private final long owner=Thread.currentThread().threadId();
  private boolean lost;
  private long last,maxGap,observations;
  public Pg798DatabaseScope(Pg797OwnedDatabase first,Pg797OwnedDatabase second){this.first=Objects.requireNonNull(first);this.second=Objects.requireNonNull(second);}
  public boolean confirmed(){return !lost&&first.heartbeatAllowed()&&second.heartbeatAllowed();}
  public void verify()throws SQLException{
    if(lost)throw new SQLException("owned database scope not confirmed");
    try{
      if(Thread.currentThread().threadId()!=owner||!confirmed())throw new SQLException("owned database scope not confirmed");
      long now=System.nanoTime();if(last!=0)maxGap=Math.max(maxGap,now-last);
      if(last!=0&&now-last>=java.util.concurrent.TimeUnit.SECONDS.toNanos(30))throw new SQLException("owned database observation interval exceeded");
      first.verify();second.verify();last=now;observations++;
    }catch(SQLException|RuntimeException|Error failure){lost=true;throw failure;}
  }
  public long maxGapNanos(){return maxGap;}
  public long observations(){return observations;}
}
