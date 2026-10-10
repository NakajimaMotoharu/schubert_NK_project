"""New-only same completed D5 stop with fixed three-digit DB application."""
import ast
import pg1198_current_stop_binding as old

SOURCE=old.SOURCE
BEFORE=old.BEFORE
OWNED=old.OWNED
RECOVERY='d85fbf1524fc1edae344b349f7828fac6fd8ff6b763fe635dc1c3b30de4c1247'


def bindings(proof):
    if type(proof)is not dict or proof.get('normalMetadataRecoveryAfterSha256')!=RECOVERY or proof.get('recoveryActualExit')!=0:
        raise ValueError('fresh fixed owner recovery actual post required')
    return old.bindings(proof)


def generate(proof):
    bindings(proof)
    values={name.replace('1198','1208'):raw.replace('Pg1198','Pg1208').replace('pg1198','pg1208').replace('PG1198','PG1208')for name,raw in old.generate(proof).items()}
    for name in list(values):values[name]=values[name].replace('PG1208-native-stop','PG998-native-stop')
    java=values['Pg1208NativeStop.java']
    ctor='new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG998-native-stop","schubert_nk",true,true)'
    java=old.replace_once(java,ctor,'expected(pid)')
    sql='select pg_backend_pid(),set_config(\'application_name\',\'PG998-native-stop\',false),pg_try_advisory_lock(71419602)'
    java=old.replace_once(java,'s.executeQuery("'+sql+'")','s.executeQuery(ownershipSql())')
    java=old.replace_once(java,'  static String phase="PREFLIGHT";',
        '  static String phase="PREFLIGHT";\n  static Pg797OwnedDatabase.Expected expected(int pid){return '+ctor+';}\n  static String ownershipSql(){return "'+sql+'";}')
    values['Pg1208NativeStop.java']=java
    values['Pg1208StopLabelTest.java']=LABEL_TEST
    for name,raw in values.items():
        if name.endswith('.py'):ast.parse(raw)
    return values


LABEL_TEST=r'''
public final class Pg1208StopLabelTest {
  private Pg1208StopLabelTest(){}
  static void check(boolean value){if(!value)throw new AssertionError("fixed management label oracle");}
  public static void main(String[] ignored){
    int checks=0;
    var expected=Pg1208NativeStop.expected(12345);
    check(expected.backend()==12345 && expected.role().equals("schubert_batch") && expected.application().equals("PG998-native-stop") && expected.database().equals("schubert_nk") && expected.readOnly() && expected.advisory());checks++;
    check(Pg1208NativeStop.ownershipSql().equals("select pg_backend_pid(),set_config('application_name','PG998-native-stop',false),pg_try_advisory_lock(71419602)"));checks++;
    for(int backend:new int[]{Integer.MIN_VALUE,-1,0,1}){
      try{Pg1208NativeStop.expected(backend);throw new AssertionError("bad backend accepted");}catch(IllegalArgumentException wanted){checks++;}
    }
    for(String bad:new String[]{"PG1208-native-stop","PG99-native-stop","PG998-","foreign","PG998-native-stop\n"}){
      try{new Pg797OwnedDatabase.Expected(12345,"schubert_batch",bad,"schubert_nk",true,true);throw new AssertionError("bad label accepted");}catch(IllegalArgumentException wanted){checks++;}
    }
    for(String bad:new String[]{"foreign","schubert_backup",""}){
      try{new Pg797OwnedDatabase.Expected(12345,bad,"PG998-native-stop","schubert_nk",true,true);throw new AssertionError("bad role accepted");}catch(IllegalArgumentException wanted){checks++;}
    }
    try{new Pg797OwnedDatabase.Expected(12345,"schubert_batch","PG998-native-stop","foreign",true,true);throw new AssertionError("bad DB accepted");}catch(IllegalArgumentException wanted){checks++;}
    try{new Pg797OwnedDatabase.Expected(12345,"schubert_batch","PG998-native-stop","schubert_nk",true,false);throw new AssertionError("missing advisory accepted");}catch(IllegalArgumentException wanted){checks++;}
    System.out.println("PG1208_FIXED_LABEL_ORACLE independentAssertions="+checks+" actualConstructor=true DB0=true");
  }
}
'''
