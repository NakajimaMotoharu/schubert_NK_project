package dev.codex.schubert.nk.web.form;
import static org.junit.jupiter.api.Assertions.*;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
/** NTF/UI224236/SS313: NTFORM001..012; pure input contract, no view/controller fixture. */
public final class NotificationSearchInputContractTest {
  private static Map<String,List<String>> one(String k,String v){return Map.of(k,List.of(v));}
  private static void bad(String k,String v){
    var f=NotificationSearchForm.bind(one(k,v));assertFalse(f.isValid());assertTrue(f.getIssues().containsKey(k));
    assertEquals("invalid notification search form",assertThrows(IllegalArgumentException.class,f::toRequest).getMessage());
  }
  @Test void ntform001DefaultsHaveNoOwnerOrDates(){
    var f=NotificationSearchForm.bind(Map.of());assertTrue(f.isValid());assertTrue(f.getIssues().isEmpty());assertEquals(1,f.getPage());
    assertEquals(Map.of("type","","from","","to","","page",""),f.getValues());var d=f.toRequest();
    assertEquals(Optional.empty(),d.notificationType());assertEquals(Optional.empty(),d.submittedFrom());assertEquals(Optional.empty(),d.submittedTo());assertEquals(1,d.page());assertEquals(50,d.pageSize());
  }
  @Test void ntform002OnlyThreeNotificationTypesBecomeEnums(){
    String[] in={"ACCEPTED","COMPLETED","ERROR"};NotificationType[] out={NotificationType.ACCEPTED,NotificationType.COMPLETED,NotificationType.ERROR};
    for(int i=0;i<in.length;i++){var f=NotificationSearchForm.bind(one("type",in[i]));assertTrue(f.isValid());assertEquals(Optional.of(out[i]),f.toRequest().notificationType());}
    for(String v:List.of("accepted","PUBLIC","ANSWERED"))bad("type",v);
  }
  @Test void ntform003PageClampAndUpperBoundaryHaveLiteralResults(){
    String[] in={"","0","-0","-1","-2147483648","1","2","999999","000002"};int[] out={1,1,1,1,1,1,2,999999,2};
    for(int i=0;i<in.length;i++){var f=NotificationSearchForm.bind(one("page",in[i]));assertTrue(f.isValid());assertEquals(out[i],f.getPage());assertEquals(out[i],f.toRequest().page());assertEquals(50,f.toRequest().pageSize());}
  }
  @Test void ntform004InvalidAndOverflowPagesRemainFailures(){
    for(String value:List.of("+1","1.0","PUBLIC","1000000","2147483647","2147483648","-2147483649")){
      var f=NotificationSearchForm.bind(one("page",value));assertFalse(f.isValid());assertEquals(1,f.getPage());assertTrue(f.getIssues().containsKey("page"));assertThrows(IllegalArgumentException.class,f::toRequest);
    }
  }
  @Test void ntform005IndependentJstUtcPairsAndMissingSides(){
    var from=NotificationSearchForm.bind(one("from","2024-02-29"));assertTrue(from.isValid());assertEquals(Optional.of(Instant.parse("2024-02-28T15:00:00Z")),from.toRequest().submittedFrom());assertEquals(Optional.empty(),from.toRequest().submittedTo());
    var to=NotificationSearchForm.bind(one("to","2024-02-29"));assertTrue(to.isValid());assertEquals(Optional.empty(),to.toRequest().submittedFrom());assertEquals(Optional.of(Instant.parse("2024-02-29T14:59:59.999Z")),to.toRequest().submittedTo());
  }
  @Test void ntform006SameDayAnd366DayMinusMillisecondAreAllowedNotTheNextDay(){
    var same=NotificationSearchForm.bind(Map.of("from",List.of("2024-02-29"),"to",List.of("2024-02-29")));assertTrue(same.isValid());
    var max=NotificationSearchForm.bind(Map.of("from",List.of("2024-01-01"),"to",List.of("2024-12-31")));assertTrue(max.isValid());
    assertEquals(Optional.of(Instant.parse("2023-12-31T15:00:00Z")),max.toRequest().submittedFrom());assertEquals(Optional.of(Instant.parse("2024-12-31T14:59:59.999Z")),max.toRequest().submittedTo());
    for(Map<String,List<String>> p:List.of(Map.of("from",List.of("2024-01-01"),"to",List.of("2025-01-01")),Map.of("from",List.of("2024-01-02"),"to",List.of("2024-01-01")))){
      var f=NotificationSearchForm.bind(p);assertFalse(f.isValid());assertEquals("受付日は366日以内で指定してください。",f.getIssues().get("to"));assertThrows(IllegalArgumentException.class,f::toRequest);
    }
  }
  @Test void ntform007StrictDatesRejectInvalidYearFormatAndCalendar(){
    for(String name:List.of("from","to"))for(String value:List.of("0000-01-01","2025-02-29","2024-13-01","2024-01-32","2024-2-29","2024-02-29T00:00"))bad(name,value);
  }
  @Test void ntform008UnknownOwnerAndNonSingleParametersAreNeverIgnored(){
    var unknown=NotificationSearchForm.bind(one("owner","PUBLIC"));assertFalse(unknown.isValid());assertTrue(unknown.getIssues().containsKey("form"));
    for(String name:List.of("type","from","to","page"))for(List<String> values:List.of(List.<String>of(),List.of("PUBLIC","PUBLIC"))){
      var f=NotificationSearchForm.bind(Map.of(name,values));assertFalse(f.isValid());assertTrue(f.getIssues().containsKey(name));
    }
  }
  @Test void ntform009ControlAndSurrogateChecksPrecedeTrimWhileSpacesRemainOptional(){
    for(String name:List.of("type","from","to","page"))for(String value:List.of("\u0000","\u007f","\u0085","\uD800","\uDC00","é","\uE000","\uD800\uDC00"))bad(name,value);
    var f=NotificationSearchForm.bind(Map.of("type",List.of(" ACCEPTED "),"from",List.of(" "),"to",List.of(" "),"page",List.of(" 2 ")));assertTrue(f.isValid());
    assertEquals(Optional.of(NotificationType.ACCEPTED),f.toRequest().notificationType());assertEquals(Optional.empty(),f.toRequest().submittedFrom());assertEquals(Optional.empty(),f.toRequest().submittedTo());assertEquals(2,f.getPage());
  }
  @Test void ntform010NullMapKeyListAndElementNeverCreateAForm(){
    assertThrows(NullPointerException.class,()->NotificationSearchForm.bind(null));
    var key=new HashMap<String,List<String>>();key.put(null,List.of("PUBLIC"));assertThrows(NullPointerException.class,()->NotificationSearchForm.bind(key));
    var list=new HashMap<String,List<String>>();list.put("type",null);assertThrows(NullPointerException.class,()->NotificationSearchForm.bind(list));
    var values=new ArrayList<String>();values.add(null);assertThrows(NullPointerException.class,()->NotificationSearchForm.bind(Map.of("type",values)));
  }
  @Test void ntform011SnapshotsAndIssueMapsAreImmutableCopies(){
    var values=new ArrayList<>(List.of("ERROR"));var in=new HashMap<String,List<String>>();in.put("type",values);
    var f=NotificationSearchForm.bind(in);values.set(0,"CHANGED");in.clear();assertEquals("ERROR",f.getValues().get("type"));assertEquals(Optional.of(NotificationType.ERROR),f.toRequest().notificationType());
    assertThrows(UnsupportedOperationException.class,()->f.getValues().put("type","CHANGED"));assertThrows(UnsupportedOperationException.class,()->f.getIssues().put("form","PUBLIC"));
    assertTrue(f.isValid());assertTrue(NotificationSearchForm.bind(Map.of()).isValid());
  }
  @Test void ntform012ConversionFailureAndDiagnosticRemainValueFree(){
    var f=NotificationSearchForm.bind(one("type","PUBLIC_UNRECOGNIZED"));assertEquals("NotificationSearchForm[REDACTED]",f.toString());
    var ex=assertThrows(IllegalArgumentException.class,f::toRequest);assertEquals("invalid notification search form",ex.getMessage());assertNull(ex.getCause());assertEquals(0,ex.getSuppressed().length);
    assertFalse(f.isValid());assertEquals(Optional.of(NotificationType.ERROR),NotificationSearchForm.bind(one("type","ERROR")).toRequest().notificationType());
  }
}
