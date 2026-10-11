/** Independent fixed public CLI and actual DB Expected constructor vector; VM actions0. */
public final class Pg1372BootstrapRoleArgumentTest {
  static void check(boolean v){if(!v)throw new AssertionError("fixed role vector");}
  public static void main(String[] ignored){
    check(Pg1372BootstrapRolePreparation.arguments(new String[]{"prepare"}));
    for(String[] bad:new String[][]{null,{}, {""}, {"verify"}, {"execute"}, {"prepare","extra"}})check(!Pg1372BootstrapRolePreparation.arguments(bad));
    var expected=new Pg797OwnedDatabase.Expected(2,"schubert_batch","PG998-bootstrap-role","schubert_nk",true,true);
    check(expected.backend()==2&&expected.application().equals("PG998-bootstrap-role")&&expected.readOnly()&&expected.advisory());
    try{new Pg797OwnedDatabase.Expected(2,"schubert_batch","PG1372-bootstrap-role","schubert_nk",true,true);throw new AssertionError("fourdigit application accepted");}catch(IllegalArgumentException wanted){check(true);}
    System.out.println("PG1372_ROLE_ARGUMENT_VECTOR vectors=9");
  }
}
