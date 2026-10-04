import java.util.*;
/** PT-OPS-ISO462001..003 independent fixed literals; no VM/process actions. */
public final class Pg462TimeoutIsolationTest {
  static int n;
  static void check(boolean v){n++;if(!v)throw new AssertionError("timeout isolation vector "+n);}
  public static void main(String[] args){
    var p=new HashMap<String,String>();for(String key:Pg410KnownAuthRecovery.FIELDS)p.put(key,"");
    p.putAll(Map.of("InvocationID","a93cd4cdb41a4709af0e976b37389598","Result","timeout","ExecMainCode","1","ExecMainStatus","143","ActiveState","failed","SubState","failed","MainPID","0","ControlPID","0","Job",""));
    check(Pg462TimeoutIsolation.parentValue(p));check(!Pg462TimeoutIsolation.parentValue(null));
    for(String key:List.of("InvocationID","Result","ExecMainCode","ExecMainStatus","ActiveState","SubState","MainPID","ControlPID","Job")){var v=new HashMap<>(p);v.put(key,"unexpected");check(!Pg462TimeoutIsolation.parentValue(v));v.put(key,null);check(!Pg462TimeoutIsolation.parentValue(v));v.remove(key);check(!Pg462TimeoutIsolation.parentValue(v));}
    var known30=new HashMap<>(p);known30.put("Result","exit-code");known30.put("ExecMainStatus","30");check(!Pg462TimeoutIsolation.parentValue(known30));
    var expected=new HashSet<>(Set.of("epoch.current","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.start.intent","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.start.intent"));
    for(String old:List.of("1eecb7b9-1e98-478f-9084-201422b31bff","d536cf5a-f5a8-4dd9-8679-3488fab17fdf","e8cce97a-163b-4814-b435-8fc26466e550","25020aa0-7b69-4554-be47-ea69588da569")){expected.add(old+".permit");expected.add(old+".owner");expected.add(old+".API.launch");expected.add(old+".WEB.launch");}
    check(expected.size()==23 && expected.equals(Pg462TimeoutIsolation.names()));check(!expected.contains("permit-start.intent"));
    var identity=new HashMap<String,String>();identity.putAll(Map.of("Uid","999 999 999 999","Gid","981 981 981 981","Groups","980 981 982 986","NoNewPrivs","1"));for(String k:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))identity.put(k,"0000000000000000");
    check(Pg462TimeoutIsolation.authority(identity,"999","981","980 981 982 986"));check(!Pg462TimeoutIsolation.authority(null,"999","981","980 981 982 986"));
    for(String key:identity.keySet()){var v=new HashMap<>(identity);v.put(key,"drift");check(!Pg462TimeoutIsolation.authority(v,"999","981","980 981 982 986"));v.put(key,null);check(!Pg462TimeoutIsolation.authority(v,"999","981","980 981 982 986"));}
    var live=Map.of("MainPID","771339","InvocationID","bbf96d392f424aa195e8cceb80d02115","ControlPID","0","Job","","ActiveState","active","SubState","running");
    check(Pg462TimeoutIsolation.liveValue(live,"771339","bbf96d392f424aa195e8cceb80d02115"));check(!Pg462TimeoutIsolation.liveValue(null,"771339","bbf96d392f424aa195e8cceb80d02115"));
    for(String key:live.keySet()){var v=new HashMap<>(live);v.put(key,"other");check(!Pg462TimeoutIsolation.liveValue(v,"771339","bbf96d392f424aa195e8cceb80d02115"));}
    System.out.println("PG462_ISOLATION_TEST assertions="+n+" independent=true vmMutation=false normalExitClaimed=false");
  }
}
