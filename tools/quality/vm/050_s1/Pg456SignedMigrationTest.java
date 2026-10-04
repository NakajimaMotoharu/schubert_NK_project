import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.zip.CRC32;

/** Independent literal schema/profile/renderer vectors, tool-only, not native authority/PT credit. */
public final class Pg456SignedMigrationTest {
  static void require(boolean value) {if(!value)throw new AssertionError("independent vector differs");}
  static byte[] bytes(String value) {return value.getBytes(StandardCharsets.US_ASCII);}
  static String profile(String schema) {
    return "{\"profile\":\"NKBACKUPPROFILE1\",\"host\":\"pgpt-host\",\"app\":\"0.1.0-PG381\",\"schema\":\""+schema
        +"\",\"os\":\"ubuntu-26.04\",\"jdk\":\"25.0.4+6\",\"postgresql\":\"18.6\",\"artemis\":\"2.56.0\",\"age\":\"1.2.1\","
        + String.join(",",List.of("pgDumpWrapperSha256","pgRestoreWrapperSha256","pgDumpSha256","pgRestoreSha256","tarSha256","ageSha256","artemisArtifactSha256")
            .stream().map(k->"\""+k+"\":\""+"1".repeat(64)+"\"").toList())+"}\n";
  }
  public static void main(String[] args) throws Exception {
    if(args.length!=0)throw new IllegalArgumentException("fixed vectors only");int count=0;
    byte[] before=bytes(profile("025")),next=bytes(profile("027"));
    require(Pg456SignedMigration.schemaOnly(before,next));count++;
    require(!Pg456SignedMigration.schemaOnly(before,before));count++;
    require(!Pg456SignedMigration.schemaOnly(next,before));count++;
    require(!Pg456SignedMigration.schemaOnly(bytes(profile("023")),next));count++;
    require(!Pg456SignedMigration.schemaOnly(before,bytes(profile("027").replace("pgpt-host","different-host"))));count++;
    require(!Pg456SignedMigration.schemaOnly(null,next));count++;
    String template="https://<GLOBAL_IP>:55160 {\n    bind <GLOBAL_IP>\n}\n";
    require(Arrays.equals(bytes("https://10.0.2.15:55160 {\n    bind 10.0.2.15\n}\n"),Pg456SignedMigration.render(bytes(template))));count++;
    for(byte[] bad:new byte[][]{null,new byte[0],bytes(template.replace("bind <GLOBAL_IP>","bind 0.0.0.0")),bytes(template+"<GLOBAL_IP>")}) {
      try {Pg456SignedMigration.render(bad);throw new AssertionError("unapproved placeholder accepted");}
      catch(IllegalArgumentException expected) {count++;}
    }
    Path root=Files.createTempDirectory("pg456-tool-vectors-");
    Files.setPosixFilePermissions(root,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    Path candidate=Files.createDirectories(root.resolve("candidate/db/migration")),old=Files.createDirectories(root.resolve("old/db/migration"));
    for(int i=1;i<=27;i++) {
      String file=String.format(Locale.ROOT,"V%03d__literal.sql",i),sql="select "+i+";\n";
      Files.writeString(candidate.resolve(file),sql,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
      if(i<=25)Files.writeString(old.resolve(file),sql,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    }
    for(int size:new int[]{25,27}) {
      var rows=Pg456SignedMigration.expected(root.resolve("candidate"),root.resolve("old"),size);
      require(rows.size()==size+1 && rows.get(0).equals(Arrays.asList(0,null,"SCHEMA","\"schubert_meta\"",null,true)));count++;
      for(int i=1;i<=size;i++) {
        var crc=new CRC32();crc.update(bytes("select "+i+";"));
        require(rows.get(i).equals(Arrays.asList(i,String.format(Locale.ROOT,"%03d",i),"SQL",String.format(Locale.ROOT,"V%03d__literal.sql",i),(int)crc.getValue(),true)));count++;
      }
    }
    try {Pg456SignedMigration.expected(root.resolve("candidate"),root.resolve("old"),26);throw new AssertionError("observed intermediate inventory accepted");}
    catch(IllegalArgumentException expected) {count++;}
    Files.writeString(old.resolve("V025__literal.sql"),"select 999;\n",StandardCharsets.UTF_8);
    try {Pg456SignedMigration.expected(root.resolve("candidate"),root.resolve("old"),27);throw new AssertionError("old SQL drift accepted");}
    catch(IllegalStateException expected) {count++;}
    require(Arrays.equals(before,bytes(profile("025"))) && Arrays.equals(next,bytes(profile("027"))));count++;
    System.out.println("PG456_MIGRATION_TOOL_PASS independentAssertions="+count+" productionPtCount=0 nativeExecuted=false");
  }
}
