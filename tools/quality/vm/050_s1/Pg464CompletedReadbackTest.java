import java.util.*;
public final class Pg464CompletedReadbackTest {
  static int checks;
  static void check(boolean ok){if(!ok)throw new AssertionError("literal snapshot oracle");checks++;}
  static void bad(String s){try{Pg464CompletedReadback.snapshot(s);throw new AssertionError("must reject");}catch(IllegalStateException expected){checks++;}}
  static void badBusiness(String s){try{Pg464CompletedReadback.businessBefore(s);throw new AssertionError("must reject");}catch(IllegalStateException expected){checks++;}}
  public static void main(String[] args) {
    check(Pg464CompletedReadback.snapshot("{}").isEmpty());
    check(Pg464CompletedReadback.snapshot("{={uid=0, gid=0}, x={size=5}/abc}").equals(Map.of("","{uid=0, gid=0}","x","{size=5}/abc")));
    check(Pg464CompletedReadback.snapshot("{x={size=5}/abc, ={uid=0, gid=0}}").equals(Map.of("","{uid=0, gid=0}","x","{size=5}/abc")));
    for(String s:new String[]{null,"","[]","{x}","{x=}","{x=a, x=b}","{x=a,y=b}","{x={a}","{x=a}}","{x={{{{{a}}}}}}"})bad(s);
    var allowed=Set.of(List.of(true,false,false,true),List.of(true,false,true,true),List.of(true,true,false,true),List.of(true,true,true,true));
    for(Boolean history:new Boolean[]{null,false,true})for(Boolean inbox:new Boolean[]{null,false,true})
      for(Boolean log:new Boolean[]{null,false,true})for(Boolean consistent:new Boolean[]{null,false,true})
        check(Pg464CompletedReadback.references(history,inbox,log,consistent)==allowed.contains(Arrays.asList(history,inbox,log,consistent)));
    var tables=List.of("schubert.app_users","schubert.auth_sessions","schubert.login_ip_attempts","schubert.script_files","schubert.speakers","schubert.script_entries","schubert.audio_files","schubert.entry_audio_links","schubert.media_assets","schubert.questions","schubert.answers","schubert.async_jobs","schubert.notifications","schubert.request_inbox","schubert.mq_outbox","schubert.app_logs","schubert_web_session.web_http_sessions","schubert_web_session.pending_context_revocations","schubert_web_session.web_log_outbox","schubert.games","schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress");
    String hash="0".repeat(64);
    String golden="{"+String.join(", ",tables.stream().map(t->t+"=Data[rows=0, digest="+hash+"]").toList())+"}";
    var parsed=Pg464CompletedReadback.businessBefore(golden);check(parsed.size()==23);
    for(String table:tables)check(parsed.get(table).equals(new Pg456SignedMigration.Data(0,hash)));
    badBusiness(null);badBusiness("{}");badBusiness(golden.replace("digest=","sha256="));
    badBusiness(golden.replace("schubert.games","schubert.unknown"));badBusiness("junk"+golden);
    badBusiness(golden.substring(0,golden.length()-1)+", schubert.games=Data[rows=0, digest="+hash+"]}");
    var tech=Set.of("schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress","schubert.app_logs","schubert.request_inbox","schubert.mq_outbox","schubert_web_session.web_log_outbox","schubert_web_session.web_http_sessions");
    check(Pg464CompletedReadback.allowedChanges(Set.of()));check(Pg464CompletedReadback.allowedChanges(tech));
    check(!Pg464CompletedReadback.allowedChanges(null));check(!Pg464CompletedReadback.allowedChanges(Set.of("schubert.unknown")));
    for(String table:tables)check(Pg464CompletedReadback.allowedChanges(Set.of(table))==tech.contains(table));
    var anonymous=Set.of(List.of(0L,0L,0L));
    for(Long users:new Long[]{null,0L,1L})for(Long contexts:new Long[]{null,0L,1L})for(Long invalid:new Long[]{null,0L,1L})
      check(Pg464CompletedReadback.anonymousFixture(users,contexts,invalid)==anonymous.contains(Arrays.asList(users,contexts,invalid)));
    System.out.println("PG464_COMPLETED_TEST independentAssertions="+checks+" mutation0=true");
  }
}
