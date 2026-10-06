import java.util.*;
/** PT-OPS-REC204001..004: independent literals; no filesystem/process/database actions. */
public final class Pg497CanonicalInvalidationTest {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("recovery vector "+count);}
  static java.sql.Connection connection(String role,List<String> events,int fault){
    boolean[] state={true,true};
    return (java.sql.Connection)java.lang.reflect.Proxy.newProxyInstance(Pg497CanonicalInvalidationTest.class.getClassLoader(),new Class<?>[]{java.sql.Connection.class},(proxy,method,values)->{
      String name=method.getName();events.add(role+":"+name+(name.equals("setReadOnly")?":"+values[0]:""));
      if(events.size()==fault)throw new java.sql.SQLException("literal fault");
      switch(name){
        case "setReadOnly":state[0]=(Boolean)values[0];return null;
        case "setAutoCommit":state[1]=(Boolean)values[0];return null;
        case "setClientInfo":return null;
        case "getTransactionIsolation":return java.sql.Connection.TRANSACTION_READ_COMMITTED;
        case "isReadOnly":return state[0];
        case "getAutoCommit":return state[1];
        default:throw new AssertionError("unexpected connection operation "+name);
      }
    });
  }
  public static void main(String[] args)throws Exception{
    check(Pg497CanonicalInvalidation.businessTableNames().equals(Set.of("schubert.app_users","schubert.auth_sessions","schubert.login_ip_attempts","schubert.script_files","schubert.speakers","schubert.script_entries","schubert.audio_files","schubert.entry_audio_links","schubert.media_assets","schubert.questions","schubert.answers","schubert.async_jobs","schubert.notifications","schubert.request_inbox","schubert.mq_outbox","schubert.app_logs","schubert.games","schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress","schubert_web_session.web_http_sessions","schubert_web_session.pending_context_revocations","schubert_web_session.web_log_outbox","schubert_web_session.web_receipt_references")));
    var events=new ArrayList<String>();Pg497CanonicalInvalidation.prepareDatabases(connection("batch",events,-1),connection("snapshot",events,-1));
    check(events.equals(List.of("batch:setClientInfo","snapshot:setClientInfo","batch:setReadOnly:false","batch:setAutoCommit","snapshot:setReadOnly:true","snapshot:setAutoCommit","batch:getTransactionIsolation","batch:isReadOnly","batch:getAutoCommit","snapshot:isReadOnly","snapshot:getAutoCommit")));
    int normalCount=events.size();
    for(int at=1;at<=normalCount;at++){
      events=new ArrayList<>();
      try{Pg497CanonicalInvalidation.prepareDatabases(connection("batch",events,at),connection("snapshot",events,at));throw new AssertionError("fault not reached");}
      catch(java.sql.SQLException|java.lang.reflect.UndeclaredThrowableException expected){check(events.size()==at);}
    }
    Pg497CanonicalInvalidation.configureSigned();
    check(Pg387TrustedDeployment.expectedSqlCount==28 && Pg387TrustedDeployment.expectedHistoryCount()==29);
    check(Pg387TrustedDeployment.LABEL.equals("PG489") && Pg387TrustedDeployment.STEM.equals("pg489"));
    check(Pg387TrustedDeployment.SOURCE.equals("38899a05b5c2daeecfc5af8ea5ae748e29954c60"));
    check(Pg387TrustedDeployment.RELEASE.equals(java.nio.file.Path.of("/opt/schubert-nk/releases/0.1.0-PG489")));
    check(dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot.Target.MORNING.unit().equals("schubert-nk-morning-controller.service"));
    var parent=new HashMap<String,String>();
    for(String key:List.of("Id","LoadState","ActiveState","SubState","MainPID","ControlPID","Job","InvocationID","ExecMainCode","ExecMainStatus","Result","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic","KillMode","SendSIGKILL","Restart","Type","RemainAfterExit"))parent.put(key,"");
    parent.putAll(Map.of("InvocationID","52accf6d68f44487b6e0b3635c20396f","Result","timeout","ExecMainCode","1","ExecMainStatus","143","ActiveState","failed","SubState","failed","MainPID","0","ControlPID","0","Job",""));
    check(Pg497CanonicalInvalidation.parentValue(parent));check(!Pg497CanonicalInvalidation.parentValue(null));
    for(String key:parent.keySet()){
      var v=new HashMap<>(parent);v.remove(key);check(!Pg497CanonicalInvalidation.parentValue(v));
      v=new HashMap<>(parent);v.put(key,null);check(!Pg497CanonicalInvalidation.parentValue(v));
    }
    for(String key:List.of("InvocationID","Result","ExecMainCode","ExecMainStatus","ActiveState","SubState","MainPID","ControlPID","Job")){
      var v=new HashMap<>(parent);v.put(key,"changed");check(!Pg497CanonicalInvalidation.parentValue(v));
    }
    var extra=new HashMap<>(parent);extra.put("unknown","");check(!Pg497CanonicalInvalidation.parentValue(extra));
    var normal=new HashMap<>(parent);normal.put("Result","success");normal.put("ExecMainStatus","0");check(!Pg497CanonicalInvalidation.parentValue(normal));
    var expected=new HashSet<String>();
    expected.add("epoch.current");
    // Independent golden namespace, not obtained by invoking the operator under test.
    for(String epoch:List.of("4d35762d-54b4-4187-ab03-cc9b7e9e3baf","15e4559b-13ab-46d7-a7a8-c15f1de4a245","1ba8ece5-5297-47c3-9933-95b2330beeb0","1eecb7b9-1e98-478f-9084-201422b31bff","25020aa0-7b69-4554-be47-ea69588da569","29563d77-6e4d-40b2-8845-b1496e460fad","37599b0d-d64a-41e9-92b5-bfeec4e5e6b6","3ee3d362-630f-49e6-80a6-1b3e9177817b","42efb43b-658e-4771-8ad4-b01d658a677b","44f16eb0-565f-41d0-9105-aa95b3a658c7","452f7343-5257-4d82-9d5d-b633e4b0af6f","630a67d3-6df6-4088-abbb-cce84aca5898","6f95548f-43a6-456f-80df-a3f564477b5c","931b4954-8962-41a7-a656-4cacee6a43bc","bcd85e18-8926-4a3c-9e9c-78da9dba2670","d536cf5a-f5a8-4dd9-8679-3488fab17fdf","df0ac0a4-e348-4130-b6a3-eb0552816f81","e8cce97a-163b-4814-b435-8fc26466e550")){
      expected.add(epoch+".permit");expected.add(epoch+".owner");expected.add(epoch+".API.launch");expected.add(epoch+".WEB.launch");
    }
    check(expected.size()==73);check(expected.equals(Pg497CanonicalInvalidation.names()));
    check(expected.stream().noneMatch(name->name.contains("intent")));
    for(String phase:List.of("DATABASE_BODY","DATABASE_SCOPE_CLOSE","A_SCOPE_CLOSE","M_SCOPE_CLOSE")){
      for(boolean mutated:List.of(false,true))for(boolean suppressed:List.of(false,true)){
        var failure=new Exception("independent");if(suppressed)failure.addSuppressed(new Exception("close"));
        boolean expectedRetain=mutated || suppressed || !phase.equals("DATABASE_BODY");
        check(Pg497CanonicalInvalidation.retainRequired(phase,mutated,failure)==expectedRetain);
      }
    }
    try{Pg497CanonicalInvalidation.retainRequired(null,false,new Exception());throw new AssertionError();}catch(NullPointerException expectedNull){count++;}
    try{Pg497CanonicalInvalidation.retainRequired("DATABASE_BODY",false,null);throw new AssertionError();}catch(NullPointerException expectedNull){count++;}
    System.out.println("PG497_RECOVERY_TEST assertions="+count+" independent=true vmMutation=false formalAccepted=false");
  }
}
