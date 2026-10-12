"""BUG1156 new-only ABI3/4 digits and actual constructor before ownership.

Failed111 files remain immutable. Same original baseline is reusable only
after the distinct1727 full recovery post qualifies every byte/resource.
"""
from pathlib import Path
import json
from pg1719_current_bootstrap_sources import files as old_files,SOURCE,W

TOOLS='pg1728-current-bootstrap-abi-tools-v1'

def bind(raw):
    return raw.replace('Pg1719','Pg1728').replace('PG1719','PG1728').replace('pg1719-current-bootstrap-tools-v1',TOOLS).replace('pg1719','pg1728')

def files(baseline_sha):
    post=json.loads((W/'pg1727-bootstrap-recovery-full-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['productionSource']!=SOURCE or post['guest']['beforeSha256']!=baseline_sha or post['guest']['ownedJavaDbAdvisoryMA0']is not True:
        raise ValueError('same unchanged full baseline after owned recovery required')
    result={bind(n):bind(raw)for n,raw in old_files(baseline_sha).items()}
    java=result['Pg1728BootstrapExisting.java'].replace('Pg797OwnedDatabase','Pg1728OwnedDatabase')
    java=java.replace('beforeOwnership(Pg1728BootstrapExisting::verifyInputClosure);','beforeOwnership(()->{verifyInputClosure();expectedBeforeOwnership(2,"schubert_batch","PG1728-bootstrap-guard","schubert_nk",true,true);});')
    marker='  public static void main(String[] args)throws Exception{'
    java=java.replace(marker,'  static Pg1728OwnedDatabase.Expected expectedBeforeOwnership(int backend,String role,String application,String database,boolean readOnly,boolean advisory){return new Pg1728OwnedDatabase.Expected(backend,role,application,database,readOnly,advisory);}\n'+marker)
    result['Pg1728BootstrapExisting.java']=java
    prior=(Path(__file__).parent/'vm/050_s1/Pg797OwnedDatabase.java').read_text()
    prior=prior.replace('Pg797OwnedDatabase','Pg1728OwnedDatabase').replace('PG[0-9]{3}-','PG[0-9]{3,4}-')
    prior=prior.replace('Objects.requireNonNull(role);Objects.requireNonNull(application);Objects.requireNonNull(database);','if(role==null||application==null||database==null)throw new IllegalArgumentException("fixed database expectation unavailable");')
    result['Pg1728OwnedDatabase.java']=prior
    result['Pg1728BootstrapExpectedTest.java']=EXPECTED_TEST
    # Retain all legacy liveness fault contracts with only renamed tool class.
    result['Pg1728OwnedDatabaseTest.java']=(Path(__file__).parent/'vm/050_s1/Pg797OwnedDatabaseTest.java').read_text().replace('Pg797OwnedDatabase','Pg1728OwnedDatabase')
    return result

EXPECTED_TEST=r'''
import java.util.Arrays;
import java.util.List;
public final class Pg1728BootstrapExpectedTest {
  private Pg1728BootstrapExpectedTest(){}
  static int checks;static int ownership;
  static void check(boolean value){checks++;if(!value)throw new AssertionError("ABI boundary "+checks);}
  static Pg1728OwnedDatabase.Expected expectation(int backend,String role,String label,String database,boolean readOnly,boolean advisory){return Pg1728BootstrapExisting.expectedBeforeOwnership(backend,role,label,database,readOnly,advisory);}
  static void refused(int backend,String role,String label,String database,boolean readOnly,boolean advisory)throws Exception{
    try{Pg1728BootstrapExisting.beforeOwnership(()->expectation(backend,role,label,database,readOnly,advisory));ownership++;throw new AssertionError("missing ABI rejection");}
    catch(IllegalArgumentException expected){check(ownership==0);check(expected.getMessage().equals("fixed database expectation unavailable"));}
  }
  public static void main(String[]args)throws Exception{
    for(String label:List.of("PG001-a","PG999-a","PG1000-a","PG9999-a","PG1728-bootstrap-guard","PG123-"+"a".repeat(32))){
      var e=expectation(2,"schubert_batch",label,"schubert_nk",true,true);
      check(e.backend()==2&&e.role().equals("schubert_batch")&&e.application().equals(label)&&e.database().equals("schubert_nk")&&e.readOnly()&&e.advisory());
    }
    var migration=expectation(Integer.MAX_VALUE,"schubert_migration","PG1000-a","schubert_nk",true,false);
    check(migration.effectiveRole().equals("nk_owner")&&migration.backend()==Integer.MAX_VALUE&&migration.readOnly()&&!migration.advisory());
    var batch=expectation(2,"schubert_batch","PG1000-a","schubert_nk",false,true);check(!batch.readOnly()&&batch.advisory());
    for(String label:Arrays.asList(null,"","PG12-a","PG12345-a","PG12x-a","PG１２３-a","PG123-","PG123-A","PG123-a/b","PG123-a\n","PG123-"+"a".repeat(33)))refused(2,"schubert_batch",label,"schubert_nk",true,true);
    for(int backend:List.of(Integer.MIN_VALUE,0,1))refused(backend,"schubert_batch","PG1728-bootstrap-guard","schubert_nk",true,true);
    for(String role:Arrays.asList(null,"","foreign"))refused(2,role,"PG1728-bootstrap-guard","schubert_nk",true,true);
    for(String database:Arrays.asList(null,"","foreign"))refused(2,"schubert_batch","PG1728-bootstrap-guard",database,true,true);
    for(boolean readOnly:List.of(false,true))refused(2,"schubert_batch","PG1728-bootstrap-guard","schubert_nk",readOnly,false);
    refused(2,"schubert_migration","PG1728-bootstrap-guard","schubert_nk",false,false);
    refused(2,"schubert_migration","PG1728-bootstrap-guard","schubert_nk",false,true);
    refused(2,"schubert_migration","PG1728-bootstrap-guard","schubert_nk",true,true);
    check(expectation(2,"schubert_batch","PG1728-bootstrap-guard","schubert_nk",true,true).toString().equals("OwnedDatabase.Expected[REDACTED]"));
    check(ownership==0);
    System.out.println("PG1728_EXPECTED_ABI independentChecks="+checks+" actualConstructor=true ownershipCallbacks0=true nullNpe0=true productionPT0=true");
  }
}
'''
