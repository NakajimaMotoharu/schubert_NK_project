import java.util.*;
public final class Pg468CompletedReadbackTest {
  static int checks;
  static void check(boolean ok){if(!ok)throw new AssertionError("literal snapshot oracle");checks++;}
  static void bad(String s){try{Pg468CompletedReadback.snapshot(s);throw new AssertionError("must reject");}catch(IllegalStateException expected){checks++;}}
  static void badBusiness(String s){try{Pg468CompletedReadback.businessBefore(s);throw new AssertionError("must reject");}catch(IllegalStateException expected){checks++;}}
  public static void main(String[] args) {
    check(Pg468CompletedReadback.snapshot("{}").isEmpty());
    check(Pg468CompletedReadback.snapshot("{={uid=0, gid=0}, x={size=5}/abc}").equals(Map.of("","{uid=0, gid=0}","x","{size=5}/abc")));
    check(Pg468CompletedReadback.snapshot("{x={size=5}/abc, ={uid=0, gid=0}}").equals(Map.of("","{uid=0, gid=0}","x","{size=5}/abc")));
    for(String s:new String[]{null,"","[]","{x}","{x=}","{x=a, x=b}","{x=a,y=b}","{x={a}","{x=a}}","{x={{{{{a}}}}}}"})bad(s);
    var allowed=Set.of(List.of(true,false,false,true),List.of(true,false,true,true),List.of(true,true,false,true),List.of(true,true,true,true));
    for(Boolean history:new Boolean[]{null,false,true})for(Boolean inbox:new Boolean[]{null,false,true})
      for(Boolean log:new Boolean[]{null,false,true})for(Boolean consistent:new Boolean[]{null,false,true})
        check(Pg468CompletedReadback.references(history,inbox,log,consistent)==allowed.contains(Arrays.asList(history,inbox,log,consistent)));
    var tables=List.of("schubert.app_users","schubert.auth_sessions","schubert.login_ip_attempts","schubert.script_files","schubert.speakers","schubert.script_entries","schubert.audio_files","schubert.entry_audio_links","schubert.media_assets","schubert.questions","schubert.answers","schubert.async_jobs","schubert.notifications","schubert.request_inbox","schubert.mq_outbox","schubert.app_logs","schubert_web_session.web_http_sessions","schubert_web_session.pending_context_revocations","schubert_web_session.web_log_outbox","schubert.games","schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress");
    String hash="0".repeat(64);
    String golden="{"+String.join(", ",tables.stream().map(t->t+"=Data[rows=0, digest="+hash+"]").toList())+"}";
    var parsed=Pg468CompletedReadback.businessBefore(golden);check(parsed.size()==23);
    for(String table:tables)check(parsed.get(table).equals(new Pg456SignedMigration.Data(0,hash)));
    badBusiness(null);badBusiness("{}");badBusiness(golden.replace("digest=","sha256="));
    badBusiness(golden.replace("schubert.games","schubert.unknown"));badBusiness("junk"+golden);
    badBusiness(golden.substring(0,golden.length()-1)+", schubert.games=Data[rows=0, digest="+hash+"]}");
    var tech=Set.of("schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress","schubert.app_logs","schubert.request_inbox","schubert.mq_outbox","schubert_web_session.web_log_outbox","schubert_web_session.web_http_sessions");
    check(Pg468CompletedReadback.allowedChanges(Set.of()));check(Pg468CompletedReadback.allowedChanges(tech));
    check(!Pg468CompletedReadback.allowedChanges(null));check(!Pg468CompletedReadback.allowedChanges(Set.of("schubert.unknown")));
    for(String table:tables)check(Pg468CompletedReadback.allowedChanges(Set.of(table))==tech.contains(table));
    var anonymous=Set.of(List.of(1L,0L,0L));
    for(Long users:new Long[]{null,0L,1L})for(Long contexts:new Long[]{null,0L,1L})for(Long invalid:new Long[]{null,0L,1L})
      check(Pg468CompletedReadback.anonymousFixture(users,contexts,invalid)==anonymous.contains(Arrays.asList(users,contexts,invalid)));
    var job=new com.google.gson.JsonObject();
    var literal=Map.of("_BOOT_ID","e07aa7061acd4e65b309d7f330f79d54","_PID","1","_UID","0","_COMM","systemd","MESSAGE_ID","39f53479d3a045ac8e11786248231fbf","UNIT","schubert-nk-morning-controller.service","INVOCATION_ID","c06707168be849ed85a5eb2a61dadfdf","JOB_ID","142470","JOB_TYPE","start","JOB_RESULT","done");
    literal.forEach(job::addProperty);job.addProperty("_SOURCE_REALTIME_TIMESTAMP","1791178838206452");check(Pg468CompletedReadback.jobDone(job));check(!Pg468CompletedReadback.jobDone(null));
    for(String key:literal.keySet()) {
      var missing=job.deepCopy();missing.remove(key);check(!Pg468CompletedReadback.jobDone(missing));
      var wrong=job.deepCopy();wrong.addProperty(key,"foreign");check(!Pg468CompletedReadback.jobDone(wrong));
      var nul=job.deepCopy();nul.add(key,com.google.gson.JsonNull.INSTANCE);check(!Pg468CompletedReadback.jobDone(nul));
      var num=job.deepCopy();num.addProperty(key,1);check(!Pg468CompletedReadback.jobDone(num));
    }
    for(String value:new String[]{"","null","1791178432999999","1791179472000001","-1","17911788382064520"}) {var bad=job.deepCopy();bad.addProperty("_SOURCE_REALTIME_TIMESTAMP",value);check(!Pg468CompletedReadback.jobDone(bad));}
    for(String value:new String[]{"1791178433000000","1791179472000000"}) {var edge=job.deepCopy();edge.addProperty("_SOURCE_REALTIME_TIMESTAMP",value);check(Pg468CompletedReadback.jobDone(edge));}
    var gc=new HashMap<String,String>();
    for(String key:List.of("Id","LoadState","ActiveState","SubState","Job","MainPID","ControlPID","InvocationID","Type","Restart","RemainAfterExit","Result","ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic","KillMode","SendSIGKILL"))gc.put(key,"");
    gc.putAll(Map.of("Id","schubert-nk-morning-controller.service","LoadState","loaded","ActiveState","inactive","SubState","dead","Type","oneshot","Restart","no","RemainAfterExit","no","Result","success","KillMode","control-group","SendSIGKILL","no"));
    for(String key:List.of("MainPID","ControlPID","ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic"))gc.put(key,"0");
    check(Pg468CompletedReadback.parentAfter(gc));check(!Pg468CompletedReadback.parentAfter(null));
    for(String key:gc.keySet()) {
      var missing=new HashMap<>(gc);missing.remove(key);check(!Pg468CompletedReadback.parentAfter(missing));
      var wrong=new HashMap<>(gc);wrong.put(key,"foreign");check(!Pg468CompletedReadback.parentAfter(wrong));
      var nul=new HashMap<>(gc);nul.put(key,null);check(!Pg468CompletedReadback.parentAfter(nul));
    }
    var retained=new HashMap<>(gc);retained.putAll(Map.of("InvocationID","c06707168be849ed85a5eb2a61dadfdf","ExecMainCode","1","ExecMainStartTimestampMonotonic","133322729500","ExecMainExitTimestampMonotonic","134500000000"));check(Pg468CompletedReadback.parentAfter(retained));
    for(String value:new String[]{"","0","133322729500","135122729501","-1","9999999999999999"}) {var bad=new HashMap<>(retained);bad.put("ExecMainExitTimestampMonotonic",value);check(!Pg468CompletedReadback.parentAfter(bad));}
    for(String value:new String[]{"133322729501","135122729500"}) {var edge=new HashMap<>(retained);edge.put("ExecMainExitTimestampMonotonic",value);check(Pg468CompletedReadback.parentAfter(edge));}
    System.out.println("PG468_COMPLETED_TEST independentAssertions="+checks+" mutation0=true");
  }
}
