package dev.codex.schubert.nk.web.form;
import static org.junit.jupiter.api.Assertions.*;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
/** QST/UI224236/SS313: QSFORM001..014; pure input contract, no controller/view fixture. */
public final class QuestionSearchInputContractTest {
  private static Map<String,List<String>> one(String k,String v){return Map.of(k,List.of(v));}
  private static QuestionSearchForm admin(Map<String,List<String>> p){return QuestionSearchForm.bind(p,UserRole.ADMIN);}
  private static void bad(String k,String v){
    var f=admin(one(k,v));assertFalse(f.isValid());assertTrue(f.getIssues().containsKey(k));
    assertEquals("invalid question search form",assertThrows(IllegalArgumentException.class,f::toRequest).getMessage());
  }
  @Test void qsform001EmptyInputsHaveClosedRoleSpecificDefaults(){
    for(UserRole role:List.of(UserRole.USER,UserRole.ADMIN)){
      var f=QuestionSearchForm.bind(Map.of(),role);assertTrue(f.isValid());assertEquals(role==UserRole.ADMIN,f.isAdmin());
      assertEquals(1,f.getPage());assertEquals(Map.of("keyword","","username","","state","","from","","to","","page",""),f.getValues());
      assertTrue(f.getIssues().isEmpty());var d=f.toRequest();assertEquals(Optional.empty(),d.keyword());
      assertEquals(Optional.empty(),d.username());assertEquals(Optional.empty(),d.answerState());
      assertEquals(Optional.empty(),d.submittedFrom());assertEquals(Optional.empty(),d.submittedTo());
      assertEquals(1,d.page());assertEquals(50,d.pageSize());
    }
  }
  @Test void qsform002UserCannotSupplyEvenEmptyUsernameButAdminCanFilter(){
    for(String value:List.of("","PUBLIC")){
      var user=QuestionSearchForm.bind(one("username",value),UserRole.USER);
      assertFalse(user.isValid());assertEquals("",user.getValues().get("username"));assertTrue(user.getIssues().containsKey("username"));
      assertThrows(IllegalArgumentException.class,user::toRequest);
      var a=admin(one("username",value));assertTrue(a.isValid());
      assertEquals(value.isEmpty()?Optional.empty():Optional.of("PUBLIC"),a.toRequest().username());
    }
  }
  @Test void qsform003NfcAndIndependentByteWidthsRespectBothLimits(){
    var n=admin(Map.of("keyword",List.of(" e\u0301 "),"username",List.of(" e\u0301 ")));
    assertTrue(n.isValid());assertEquals(Optional.of("é"),n.toRequest().keyword());assertEquals(Optional.of("é"),n.toRequest().username());
    for(String v:List.of("x".repeat(256),"é".repeat(128),"\uD800\uDC00".repeat(64)))
      assertTrue(admin(one("keyword",v)).isValid());
    for(String v:List.of("x".repeat(257),"é".repeat(129),"\uD800\uDC00".repeat(65)))bad("keyword",v);
    for(String v:List.of("x".repeat(64),"é".repeat(32),"\uD800\uDC00".repeat(16)))assertTrue(admin(one("username",v)).isValid());
    for(String v:List.of("x".repeat(65),"é".repeat(33),"\uD800\uDC00".repeat(17)))bad("username",v);
    assertTrue(admin(one("keyword","e\u0301".repeat(128))).isValid());
  }
  @Test void qsform004StatesMapOnlyTheThreeFixedEnums(){
    String[] text={"ANSWERED","UNANSWERED","ERROR"};AnswerState[] values={AnswerState.ANSWERED,AnswerState.UNANSWERED,AnswerState.ERROR};
    for(int i=0;i<text.length;i++){var f=admin(one("state",text[i]));assertTrue(f.isValid());assertEquals(Optional.of(values[i]),f.toRequest().answerState());}
    for(String v:List.of("answered","PUBLIC","ACTIVE"))bad("state",v);
  }
  @Test void qsform005ValidPageValuesHaveIndependentLiteralResults(){
    String[] in={"","0","-0","-1","-2147483648","1","2","999999","000002"};int[] out={1,1,1,1,1,1,2,999999,2};
    for(int i=0;i<in.length;i++){var f=admin(one("page",in[i]));assertTrue(f.isValid());assertEquals(out[i],f.getPage());assertEquals(out[i],f.toRequest().page());assertEquals(50,f.toRequest().pageSize());}
  }
  @Test void qsform006InvalidAndOverflowPagesCannotConvert(){
    for(String v:List.of("+1","1.0","PUBLIC","1000000","2147483647","2147483648","-2147483649")){
      var f=admin(one("page",v));assertFalse(f.isValid());assertEquals(1,f.getPage());assertTrue(f.getIssues().containsKey("page"));assertThrows(IllegalArgumentException.class,f::toRequest);
    }
  }
  @Test void qsform007JstDatesUseFixedUtcGoldensWithMissingSides(){
    var from=admin(one("from","2024-02-29"));assertTrue(from.isValid());
    assertEquals(Optional.of(Instant.parse("2024-02-28T15:00:00Z")),from.toRequest().submittedFrom());assertEquals(Optional.empty(),from.toRequest().submittedTo());
    var to=admin(one("to","2024-02-29"));assertTrue(to.isValid());
    assertEquals(Optional.empty(),to.toRequest().submittedFrom());assertEquals(Optional.of(Instant.parse("2024-02-29T14:59:59.999Z")),to.toRequest().submittedTo());
    var both=admin(Map.of("from",List.of("2024-02-29"),"to",List.of("2024-02-29")));assertTrue(both.isValid());
    assertEquals(Optional.of(Instant.parse("2024-02-28T15:00:00Z")),both.toRequest().submittedFrom());
    assertEquals(Optional.of(Instant.parse("2024-02-29T14:59:59.999Z")),both.toRequest().submittedTo());
  }
  @Test void qsform008InclusiveEndOfDayDefinesThe366DayAndReverseBounds(){
    var max=admin(Map.of("from",List.of("2024-01-01"),"to",List.of("2024-12-31")));assertTrue(max.isValid());
    assertEquals(Optional.of(Instant.parse("2023-12-31T15:00:00Z")),max.toRequest().submittedFrom());
    assertEquals(Optional.of(Instant.parse("2024-12-31T14:59:59.999Z")),max.toRequest().submittedTo());
    for(Map<String,List<String>> p:List.of(Map.of("from",List.of("2024-01-01"),"to",List.of("2025-01-01")),Map.of("from",List.of("2024-01-02"),"to",List.of("2024-01-01")))){
      var f=admin(p);assertFalse(f.isValid());assertEquals("受付日は366日以内で指定してください。",f.getIssues().get("to"));assertThrows(IllegalArgumentException.class,f::toRequest);
    }
  }
  @Test void qsform009StrictDatesRejectYearZeroFormatAndImpossibleDays(){
    for(String name:List.of("from","to"))for(String value:List.of("0000-01-01","2025-02-29","2024-13-01","2024-01-32","2024-2-29","2024-02-29T00:00"))bad(name,value);
    var space=admin(Map.of("from",List.of(" "),"to",List.of(" ")));assertTrue(space.isValid());assertEquals(Optional.empty(),space.toRequest().submittedFrom());assertEquals(Optional.empty(),space.toRequest().submittedTo());
  }
  @Test void qsform010UnknownAndNonSingleParametersKeepExplicitFailures(){
    var unknown=admin(one("owner","PUBLIC"));assertFalse(unknown.isValid());assertTrue(unknown.getIssues().containsKey("form"));
    for(String name:List.of("keyword","username","state","from","to","page"))for(List<String> values:List.of(List.<String>of(),List.of("PUBLIC","PUBLIC"))){
      var f=admin(Map.of(name,values));assertFalse(f.isValid());assertTrue(f.getIssues().containsKey(name));
    }
  }
  @Test void qsform011ControlAndSurrogateValidationIsBeforeNormalization(){
    for(String name:List.of("keyword","username","state","from","to","page"))for(String value:List.of("\u0000","\u007f","\u0085","\uD800","\uDC00"))bad(name,value);
    for(String value:List.of("é","\uE000","\uD800\uDC00")){var f=admin(one("keyword",value));assertTrue(f.isValid());assertEquals(Optional.of(value),f.toRequest().keyword());}
  }
  @Test void qsform012NullBoundariesDoNotCreatePartialForms(){
    assertThrows(NullPointerException.class,()->QuestionSearchForm.bind(null,UserRole.ADMIN));
    assertThrows(NullPointerException.class,()->QuestionSearchForm.bind(Map.of(),null));
    var key=new HashMap<String,List<String>>();key.put(null,List.of("PUBLIC"));assertThrows(NullPointerException.class,()->admin(key));
    var list=new HashMap<String,List<String>>();list.put("keyword",null);assertThrows(NullPointerException.class,()->admin(list));
    var elements=new ArrayList<String>();elements.add(null);assertThrows(NullPointerException.class,()->admin(Map.of("keyword",elements)));
  }
  @Test void qsform013CopiesAndRoleSnapshotsCannotBeMutatedByCallers(){
    var value=new ArrayList<>(List.of("PUBLIC"));var in=new HashMap<String,List<String>>();in.put("keyword",value);
    var f=admin(in);value.set(0,"CHANGED");in.clear();assertEquals("PUBLIC",f.getValues().get("keyword"));assertEquals(Optional.of("PUBLIC"),f.toRequest().keyword());
    assertThrows(UnsupportedOperationException.class,()->f.getValues().put("keyword","CHANGED"));assertThrows(UnsupportedOperationException.class,()->f.getIssues().put("form","PUBLIC"));
    assertTrue(f.isAdmin());assertFalse(QuestionSearchForm.bind(Map.of(),UserRole.USER).isAdmin());assertTrue(f.isValid());
  }
  @Test void qsform014InvalidConversionAndDiagnosticsDoNotRetainInput(){
    var f=admin(one("state","PUBLIC_UNRECOGNIZED"));assertEquals("QuestionSearchForm[REDACTED]",f.toString());
    var ex=assertThrows(IllegalArgumentException.class,f::toRequest);assertEquals("invalid question search form",ex.getMessage());assertNull(ex.getCause());assertEquals(0,ex.getSuppressed().length);
    assertEquals(Optional.of("OTHER"),admin(one("keyword","OTHER")).toRequest().keyword());assertFalse(f.isValid());
  }
}
