"""BUG1146 new-only four-identity guarded candidate placement source."""
import pg1645_completed_candidate_compile_v2 as previous

TOOLS = 'pg1659-completed-unused-tools-v3'

IDENTITY = r'''
  static void verifyCurrentIdentity(){
    require("PG1544".equals(Pg387TrustedDeployment.LABEL)
      &&"pg1544".equals(Pg387TrustedDeployment.STEM)
      &&"4d6bcbddb417b76d27e52d5d9640752c300edccf".equals(Pg387TrustedDeployment.SOURCE)
      &&Path.of("/opt/schubert-nk/releases/0.1.0-PG1544").equals(Pg387TrustedDeployment.RELEASE));
  }
'''

TEST = r'''
import java.nio.file.Path;
public final class Pg1660CurrentIdentityTest {
 private Pg1660CurrentIdentityTest(){}
 static int checks;
 static void reset(){Pg387TrustedDeployment.LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544";Pg387TrustedDeployment.SOURCE="4d6bcbddb417b76d27e52d5d9640752c300edccf";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1544");}
 static void refused(){try{Pg1640UnusedStage.verifyCurrentIdentity();throw new AssertionError("foreign identity accepted");}catch(IllegalStateException expected){checks++;}}
 public static void main(String[] args){
  reset();Pg1640UnusedStage.verifyCurrentIdentity();checks++;
  for(String value:new String[]{"PG1292","PG1638",null}){reset();Pg387TrustedDeployment.LABEL=value;refused();}
  for(String value:new String[]{"pg1292","pg1638",null}){reset();Pg387TrustedDeployment.STEM=value;refused();}
  for(String value:new String[]{"769ddb15cd735c25fef581b5f9850ef9d0053c0f","2741c4546afad6c1e8b6efbd53dfb58144edf7bb",null}){reset();Pg387TrustedDeployment.SOURCE=value;refused();}
  for(Path value:new Path[]{Path.of("/opt/schubert-nk/releases/0.1.0-PG1292"),Path.of("/opt/schubert-nk/releases/0.1.0-PG1638"),null}){reset();Pg387TrustedDeployment.RELEASE=value;refused();}
  reset();if(checks!=13)throw new AssertionError("independent identity case count");
  System.out.println("PG1660_CURRENT_IDENTITY independentChecks=13 actualMethod=true IO0=true nullNpe0=true");
 }
}
'''


def sources(bom):
    result = {}
    for name, raw in previous.sources(bom).items():
        raw = raw.replace('pg1645-completed-unused-tools-v2', TOOLS).replace('pg1646', 'pg1661').replace('pg1647-completed-unused-placement-v2', 'pg1662-completed-unused-placement-v3')
        raw = raw.replace('PG1292', 'PG1544')
        if name == 'Pg1640UnusedStage.java':
            marker = 'var approval=Pg387TrustedDeployment.verify();'
            if raw.count(marker) != 1 or raw.count('  public static void main') != 1:
                raise ValueError('one current signed verifier identity boundary required')
            raw = raw.replace(marker, 'verifyCurrentIdentity();' + marker).replace('  public static void main', IDENTITY + '\n  public static void main')
        result[name] = raw
    result['Pg1660CurrentIdentityTest.java'] = TEST
    return result
