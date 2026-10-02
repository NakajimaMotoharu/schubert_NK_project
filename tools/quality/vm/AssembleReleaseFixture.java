import com.google.gson.GsonBuilder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import org.flywaydb.core.internal.resolver.ChecksumCalculator;
import org.flywaydb.core.internal.resource.StringResource;

/**
 * PG315 / SSC097 / PT-OPS-NATIVE-028 fixture builder, NOT a deployment authority.
 * Generates actual thin-JAR candidate artifacts using Maven's resolved GAV/classifier inventory.
 * SQL expectations use pinned Flyway13.4 primary implementation, never DB or Production verifier.
 * No credential/signature/approval/permit/current mutation; output must be a new private directory.
 */
public final class AssembleReleaseFixture {
  private static final String APP = "0.1.0-SNAPSHOT";
  public static void main(String[] args) throws Exception {
    if ((args.length != 4 && args.length != 6) || !args[2].matches("[0-9a-f]{40}")
        || !args[3].matches("[A-Za-z0-9][A-Za-z0-9._-]{0,63}"))
      throw new IllegalArgumentException("fixture arguments");
    Path repo=Path.of(args[0]).toAbsolutePath().normalize();
    Path output=Path.of(args[1]).toAbsolutePath().normalize();
    if(Files.exists(output,LinkOption.NOFOLLOW_LINKS)) throw new IllegalStateException("preserve existing fixture");
    var git=new ProcessBuilder("git","-C",repo.toString(),"rev-parse","HEAD").start();
    String actual=new String(git.getInputStream().readAllBytes(),StandardCharsets.US_ASCII).trim();
    if(git.waitFor()!=0 || !actual.equals(args[2]))throw new IllegalStateException("source commit mismatch");
    var clean=new ProcessBuilder("git","-C",repo.toString(),"diff","--quiet","HEAD","--","src").start();
    if(clean.waitFor()!=0)throw new IllegalStateException("uncommitted production source");
    Files.createDirectory(output);
    var dependencies=new TreeMap<String,TreeSet<String>>();
    for(var role:List.of("api","web","operations")) {
      String module=role.equals("operations")?"batch":role;
      Path target=repo.resolve("src/schubert-nk-"+module+"/target");
      copy(target.resolve("schubert-nk-"+module+"-"+APP+".jar"),output.resolve(role+"/"+module+".jar"));
      var declared=new TreeSet<String>();
      for(String line:Files.readAllLines(target.resolve("runtime-dependencies.txt"),StandardCharsets.UTF_8)) {
        if(!line.startsWith("   "))continue;
        String coordinate=line.trim().split(" -- ",2)[0];
        String[] fields=coordinate.split(":",-1);
        if((fields.length!=5&&fields.length!=6)||!fields[2].equals("jar")
            ||!Set.of("compile","runtime").contains(fields[fields.length-1]))
          throw new IllegalStateException("unsupported resolved dependency");
        String version=fields[fields.length-2];
        String classifier=fields.length==6?"-"+fields[3]:"";
        String filename=fields[1]+"-"+version+classifier+".jar";
        if(!declared.add(filename))throw new IllegalStateException("duplicate artifact filename");
        String path=role+"/lib/"+filename;
        copy(target.resolve("runtime-dependencies/"+filename),output.resolve(path));
        dependencies.computeIfAbsent(fields[0]+":"+fields[1]+":"+version,k->new TreeSet<>()).add(path);
        if(fields[0].equals("dev.codex.schubert")) {
          Path built=repo.resolve("src/"+fields[1]+"/target/"+filename);
          if(!hash(built).equals(hash(output.resolve(path))))throw new IllegalStateException("stale shared artifact");
        }
      }
      try(var files=Files.list(target.resolve("runtime-dependencies"))) {
        var actualNames=new TreeSet<String>();
        for(var file:files.toList())actualNames.add(file.getFileName().toString());
        if(!declared.equals(actualNames))throw new IllegalStateException("resolved dependency directory mismatch");
      }
    }
    // SSC098: refuse before manifest/signature, preserving a partial fixture for diagnosis.
    var gas=new HashSet<String>();
    for(String coordinate:dependencies.keySet())
      if(!gas.add(coordinate.substring(0,coordinate.lastIndexOf(':'))))
        throw new IllegalStateException("cross-role dependency version mismatch");
    var migrations=new ArrayList<Map<String,Object>>();
    migrations.add(row(0,null,"SCHEMA","\"schubert_meta\"",null));
    Path sql=repo.resolve("src/schubert-nk-api/src/main/resources/db/migration");
    try(var files=Files.list(sql)) {
      int rank=0;
      for(var file:files.sorted().toList()) {
        String name=file.getFileName().toString();
        if(!name.matches("V[0-9]{3}__[a-z0-9_]+\\.sql"))throw new IllegalStateException("SQL profile");
        String version=name.substring(1,4);
        if(Integer.parseInt(version)!=++rank)throw new IllegalStateException("SQL gap");
        copy(file,output.resolve("db/migration/"+name));
        migrations.add(row(rank,version,"SQL",name,
            ChecksumCalculator.calculate(new StringResource(Files.readString(file,StandardCharsets.UTF_8)))));
      }
      if(rank!=25)throw new IllegalStateException("25 approved migrations required");
    }
    for(String name:List.of("common","api","web","batch"))
      copy(repo.resolve("src/deployment/config/"+name+".yml.template"),output.resolve("config/templates/"+name+".yml"));
    // SSC110: only the public, already operator-observed fixed profile and public recipient.
    // No private key/credential enters the release. This assembler still grants NO authority.
    if (args.length == 6) {
      byte[] profile=Files.readAllBytes(Path.of(args[4]));
      var claims=dev.codex.schubert.nk.batch.backup.BackupProfile.consume(profile);
      if(!claims.versions().app().equals(APP)||!claims.versions().schema().equals("025"))
        throw new IllegalStateException("effective backup profile version mismatch");
      byte[] recipient=Files.readAllBytes(Path.of(args[5]));
      if(!new String(recipient,StandardCharsets.US_ASCII).matches("age1[023456789acdefghjklmnpqrstuvwxyz]{58}\\n"))
        throw new IllegalStateException("public recipient required");
      copy(Path.of(args[4]),output.resolve("config/effective/backup-profile.json"));
      copy(Path.of(args[5]),output.resolve("config/effective/backup-age-recipient"));
    }
    try(var files=Files.list(repo.resolve("src/deployment/systemd"))) {
      for(var file:files.filter(Files::isRegularFile).toList()) {
        String name=file.getFileName().toString().replaceFirst("\\.template$","");
        if(!name.endsWith(".service")&&!name.endsWith(".target"))throw new IllegalStateException("Unit profile");
        copy(file,output.resolve("systemd/"+name));
      }
    }
    copy(repo.resolve("src/deployment/artemis/etc/broker.xml"),output.resolve("config/artemis/broker.xml.template"));
    String wrapper=Files.readString(repo.resolve("src/deployment/operations/inbox-inspector.sh.template"),StandardCharsets.UTF_8)
        .replace("@JAVA_BIN@","/usr/bin/java").replace("@API_JAR@","/opt/schubert-nk/current/api/api.jar")
        .replace("@LIB_DIR@","/opt/schubert-nk/current/api/lib");
    write(output.resolve("operations/bin/schubert-nk-inbox-inspector"),wrapper.getBytes(StandardCharsets.UTF_8));
    write(output.resolve("VERSION"),(args[3]+"\n").getBytes(StandardCharsets.US_ASCII));
    var artifacts=new ArrayList<Map<String,Object>>();
    var hashes=new TreeMap<String,String>();
    try(var files=Files.walk(output)) {
      for(var file:files.filter(Files::isRegularFile).sorted().toList()) {
        String path=output.relativize(file).toString();String sha=hash(file);
        artifacts.add(map("path",path,"size",Files.size(file),"sha256",sha));hashes.put(path,sha);
      }
    }
    var deps=new ArrayList<Map<String,Object>>();
    dependencies.forEach((coordinate,paths)->deps.add(map("coordinate",coordinate,"paths",List.copyOf(paths))));
    var manifest=map("format","NKRELEASE1","release",args[3],
        "versions",map("app",APP,"protocol",APP,"storage",APP,"bootstrap",APP,"schema","025","config","1"),
        "source",map("commit",args[2],"tag",args.length==6?"untagged-PGPT-candidate":"PG315-private-fixture"),
        "build",map("jdkVendor",System.getProperty("java.vendor"),"jdkVersion",System.getProperty("java.version"),"mavenVersion","3.9.12"),
        "platform",map("osId","ubuntu","osVersion","26.04","architecture",System.getProperty("os.arch"),"javaFeature",25),
        "dependencies",deps,"artifacts",artifacts,"migrations",migrations);
    byte[] original=new GsonBuilder().serializeNulls().disableHtmlEscaping().create().toJson(manifest).getBytes(StandardCharsets.UTF_8);
    if(original.length>1_048_576)throw new IllegalStateException("manifest limit");
    write(output.resolve("RELEASE-MANIFEST.json"),original);
    hashes.put("RELEASE-MANIFEST.json",hash(output.resolve("RELEASE-MANIFEST.json")));
    var sums=new StringBuilder();hashes.forEach((path,sha)->sums.append(sha).append("  ").append(path).append('\n'));
    write(output.resolve("SHA256SUMS"),sums.toString().getBytes(StandardCharsets.US_ASCII));
    System.out.println("PT-OPS-NATIVE-028 ASSEMBLED artifacts="+artifacts.size()+" dependencies="+deps.size()
        +" migrations=25 manifestBytes="+original.length+" manifestSha256="+hash(output.resolve("RELEASE-MANIFEST.json"))
        +" authorityIssued=false productionActivation=false");
  }
  private static Map<String,Object> row(int rank,String version,String type,String script,Integer checksum) {
    return map("installedRank",rank,"version",version,"type",type,"script",script,"checksum",checksum,"success",true);
  }
  private static LinkedHashMap<String,Object> map(Object... values) {
    var result=new LinkedHashMap<String,Object>();
    for(int i=0;i<values.length;i+=2)result.put((String)values[i],values[i+1]);return result;
  }
  private static void copy(Path source,Path target) throws Exception {
    if(!Files.isRegularFile(source,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("regular input required");
    Files.createDirectories(target.getParent());Files.copy(source,target);
  }
  private static void write(Path target,byte[] bytes) throws Exception {
    Files.createDirectories(target.getParent());Files.write(target,bytes,StandardOpenOption.CREATE_NEW);
  }
  private static String hash(Path file) throws Exception {
    var digest=MessageDigest.getInstance("SHA-256");
    try(var input=Files.newInputStream(file)){byte[] buffer=new byte[8192];for(int n;(n=input.read(buffer))!=-1;)digest.update(buffer,0,n);}
    return HexFormat.of().formatHex(digest.digest());
  }
}
