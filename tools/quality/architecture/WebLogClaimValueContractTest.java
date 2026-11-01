package dev.codex.schubert.nk.web.logging;
import static org.junit.jupiter.api.Assertions.*;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
/** MON003/MQ008/UI242/SS324331352; WLGCLAIM001..006; public immutable value, no outbox execution. */
public final class WebLogClaimValueContractTest {
  private static final Instant CREATED=Instant.parse("2026-01-01T00:00:00Z");
  private static final Instant NEXT=Instant.parse("2026-01-01T00:15:00Z");
  private static final Instant UNTIL=Instant.parse("2026-01-01T00:16:00Z");
  private static WebLogPayloadIdentity identity(){return new WebLogPayloadIdentity(new UUID(0,91),new UUID(0,92));}
  private static EncryptedWebLogPayload payload(){return new EncryptedWebLogPayload("PUBLIC",new byte[29]);}
  private static ClaimedWebLog row(long id,int attempt,String worker){
    return new ClaimedWebLog(id,identity(),payload(),attempt,NEXT,CREATED,worker,UNTIL);
  }
  @Test void wlgclaim001AllClosedValuesAndBothNumericBoundsAreRetained(){
    var identity=identity();var payload=payload();
    for(long id:new long[]{1,999_999_999_999L})for(int attempt:new int[]{0,100}){
      var r=new ClaimedWebLog(id,identity,payload,attempt,NEXT,CREATED,"PUBLIC",UNTIL);
      assertEquals(id,r.id());assertSame(identity,r.identity());assertSame(payload,r.payload());assertEquals(attempt,r.attemptCount());
      assertEquals(Instant.parse("2026-01-01T00:15:00Z"),r.nextAttemptAt());assertEquals(Instant.parse("2026-01-01T00:00:00Z"),r.createdAt());
      assertEquals("PUBLIC",r.leaseOwner());assertEquals(Instant.parse("2026-01-01T00:16:00Z"),r.leaseUntil());
    }
  }
  @Test void wlgclaim002N12BoundsDoNotWrapOrClamp(){
    for(long id:new long[]{-1,0,1_000_000_000_000L}){
      var ex=assertThrows(IllegalArgumentException.class,()->row(id,0,"PUBLIC"));
      assertEquals("web log row ID is outside N12",ex.getMessage());assertNull(ex.getCause());
    }
  }
  @Test void wlgclaim003AttemptBoundsDoNotBecomeRetryPolicy(){
    for(int attempt:new int[]{-1,101}){
      var ex=assertThrows(IllegalArgumentException.class,()->row(1,attempt,"PUBLIC"));
      assertEquals("web log attempt count is outside 0..100",ex.getMessage());assertNull(ex.getCause());
    }
  }
  @Test void wlgclaim004WorkerIsOnlyABoundedAsciiValueNotAnOwnerProof(){
    for(String worker:List.of("A","A".repeat(64),"PUBLIC._-09")){
      assertSame(worker,ClaimedWebLog.requireWorker(worker));assertEquals(worker,row(1,0,worker).leaseOwner());
    }
    for(String worker:List.of("","A".repeat(65)," ","PUBLIC/OTHER","é","PUBLIC\n")){
      assertEquals("web log lease owner is invalid",assertThrows(IllegalArgumentException.class,()->row(1,0,worker)).getMessage());
    }
  }
  @Test void wlgclaim005EachRequiredBoundaryRejectsNull(){
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,null,payload(),0,NEXT,CREATED,"PUBLIC",UNTIL));
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,identity(),null,0,NEXT,CREATED,"PUBLIC",UNTIL));
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,identity(),payload(),0,null,CREATED,"PUBLIC",UNTIL));
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,identity(),payload(),0,NEXT,null,"PUBLIC",UNTIL));
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,identity(),payload(),0,NEXT,CREATED,null,UNTIL));
    assertThrows(NullPointerException.class,()->new ClaimedWebLog(1,identity(),payload(),0,NEXT,CREATED,"PUBLIC",null));
  }
  @Test void wlgclaim006DiagnosticAndPayloadCopiesExposeNoLeaseOrMutableBuffer(){
    byte[] input=new byte[29];input[7]=3;var p=new EncryptedWebLogPayload("PUBLIC",input);
    var r=new ClaimedWebLog(1,identity(),p,0,NEXT,CREATED,"PUBLIC_WORKER",UNTIL);
    input[7]=9;byte[] expected=new byte[29];expected[7]=3;assertArrayEquals(expected,r.payload().ciphertext());
    byte[] returned=r.payload().ciphertext();returned[7]=8;assertArrayEquals(expected,r.payload().ciphertext());
    assertEquals("ClaimedWebLog[identity/payload/lease=<redacted>]",r.toString());assertEquals("PUBLIC_WORKER",r.leaseOwner());
  }
}
