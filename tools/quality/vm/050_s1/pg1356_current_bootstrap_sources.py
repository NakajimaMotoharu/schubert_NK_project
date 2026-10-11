"""Separate fresh filename generation from unchanged fixed DB authority/application."""
from pg1348_current_bootstrap_sources import files as previous, SOURCE, BEFORE, W

DATABASE_VECTOR = '''
public final class Pg1356BootstrapDatabaseApplicationTest {
  static void require(boolean value){if(!value)throw new AssertionError("DB application vector");}
  public static void main(String[] args){
    require(args.length==0);
    var valid=new Pg797OwnedDatabase.Expected(2,"schubert_batch","PG998-bootstrap-guard","schubert_nk",true,true);
    require(valid.backend()==2&&valid.role().equals("schubert_batch")&&valid.application().equals("PG998-bootstrap-guard")&&valid.database().equals("schubert_nk")&&valid.readOnly()&&valid.advisory());
    for(var bad:new String[]{"PG1356-bootstrap-guard","PG99-bootstrap-guard","","PG998-bootstrap1"}){
      boolean refused=false;try{new Pg797OwnedDatabase.Expected(2,"schubert_batch",bad,"schubert_nk",true,true);}catch(IllegalArgumentException expected){refused=true;}
      require(refused);
    }
    System.out.println("PG1356_DB_APPLICATION_VECTOR vectors=5");
  }
}
'''

def files(baseline_sha):
    values = {}
    for name, raw in previous(baseline_sha).items():
        name = name.replace('1348', '1356')
        raw = raw.replace('Pg1348', 'Pg1356').replace('pg1348', 'pg1356').replace('PG1348', 'PG1356')
        raw = raw.replace('PG1356-bootstrap-guard', 'PG998-bootstrap-guard')
        values[name] = raw
    values['Pg1356BootstrapDatabaseApplicationTest.java'] = DATABASE_VECTOR
    return values
