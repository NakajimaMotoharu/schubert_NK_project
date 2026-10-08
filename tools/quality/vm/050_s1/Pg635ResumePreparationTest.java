/** Independent CLI literals; no Root/DB/Unit operations. */
public final class Pg635ResumePreparationTest {
  public static void main(String[] args) {
    if(!Pg635ResumePreparation.arguments(new String[]{"prepare"}))throw new AssertionError();
    String[][] invalid={null,new String[0],new String[]{null},new String[]{"start"},new String[]{"prepare","foreign"},new String[]{""}};
    for(var value:invalid)if(Pg635ResumePreparation.arguments(value))throw new AssertionError();
    if(!Pg635ResumePreparation.SOURCE.equals("36fe7a0b938489d61d17d49c1c30a6fbbef699d5") || !Pg635ResumePreparation.DIGEST.equals("57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe"))throw new AssertionError();
    if(!Pg635ResumePreparation.TOOLS.toString().equals("/var/lib/pgpt-s1-preservation/pg635-resume-tools-v1") || !Pg635ResumePreparation.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg635-resume-preparation-v1"))throw new AssertionError();
    System.out.println("PG635_INDEPENDENT_CLI actual0=true authority0=true");
  }
}
