package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermission;
import java.security.*;
import java.util.*;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/** PT-ADM-BOOT008; UI225226/SS313314343: actual signed NK login/self-reset/relogin.
 * Shared Current login driver, independent HTTP/DOM/SQL/JCA oracle; NOT CHR-L01 acceptance.
 * Never emits cookies/tokens/password/hash or stores page/network bodies in Git evidence.
 */
public final class NativeNkBootstrapAuthentication {
  static final Path PRIVATE=Path.of("/home/mini/codex/project1/work/pgpt-vm/private");
  static final String BASE="https://10.0.2.15:55160";
  static final ObjectMapper JSON=new ObjectMapper();
  static void require(boolean b){if(!b)throw new IllegalStateException("fixed authentication oracle failed");}
  static com.fasterxml.jackson.databind.JsonNode query(String sql)throws Exception{
    var p=new ProcessBuilder("ssh","-i",PRIVATE.resolve("vm-access").toString(),"-p","22222","-oBatchMode=yes","-oIdentitiesOnly=yes","-oStrictHostKeyChecking=yes","-oUserKnownHostsFile="+PRIVATE.resolve("known_hosts"),"ubuntu@127.0.0.1","sudo -n -u postgres /usr/bin/psql -X -qAt -v ON_ERROR_STOP=1 -d schubert_nk").redirectError(ProcessBuilder.Redirect.DISCARD).start();
    try(var in=p.getOutputStream()){in.write(("BEGIN READ ONLY; SET LOCAL statement_timeout='5s';\n"+sql+";\nCOMMIT;\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));}
    byte[] bytes=p.getInputStream().readNBytes(8193);require(p.waitFor(10,java.util.concurrent.TimeUnit.SECONDS) && p.exitValue()==0 && bytes.length<=8192);
    try{return JSON.readTree(bytes);}finally{Arrays.fill(bytes,(byte)0);}
  }
  static void independentPassword(String encoded,String password)throws Exception{
    require(encoded!=null && password!=null && encoded.matches("\\{pbkdf2-v1}[0-9a-f]{96}"));byte[] all=HexFormat.of().parseHex(encoded.substring(11));
    byte[] salt=Arrays.copyOfRange(all,0,16),expected=Arrays.copyOfRange(all,16,48);var spec=new PBEKeySpec(password.toCharArray(),salt,310000,256);
    try{byte[] actual=SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();try{require(MessageDigest.isEqual(expected,actual));}finally{Arrays.fill(actual,(byte)0);}}finally{spec.clearPassword();Arrays.fill(all,(byte)0);Arrays.fill(salt,(byte)0);Arrays.fill(expected,(byte)0);}
  }
  public static void main(String[] args){
    try{run(args);System.out.println("NK_BOOTSTRAP_AUTH_ACCEPTED login=true adminHttpDom=true selfPasswordReset=true oldSessionsRevoked=true newLogin=true independentJca=true credentialRetirementPending=true chrL01Pass=false secretsPrinted=false");}
    catch(Throwable failure){System.err.println("NK_BOOTSTRAP_AUTH_FAILED diagnosticsRedacted=true pass=false");System.exit(1);}
  }
  static void run(String[] args)throws Exception{
    require(args.length==1 && args[0].equals("bbb244e5191e68adee2f6251dfdbbba53e9b64b4"));
    Path input=PRIVATE.resolve("pg467-bootstrap-account.private.json"),updated=PRIVATE.resolve("pg468-active-account.private.json");require(!Files.exists(updated));
    require(!Files.isSymbolicLink(input) && Files.getPosixFilePermissions(input).equals(Set.of(PosixFilePermission.OWNER_READ,PosixFilePermission.OWNER_WRITE)));
    byte[] raw=Files.readAllBytes(input);require(raw.length<=4096);com.fasterxml.jackson.databind.JsonNode account;
    try{account=JSON.readTree(raw);}finally{Arrays.fill(raw,(byte)0);}
    require(account.size()==2 && account.path("username").isTextual() && account.path("password").isTextual());String username=account.path("username").textValue(),oldPassword=account.path("password").textValue();require(username.matches("[a-z0-9_]{1,64}"));
    var before=query("select json_build_object('count',count(*),'id',max(id),'role',max(role),'hash',max(password_hash),'version',max(version)) from schubert.app_users where username='"+username+"'");require(before.path("count").intValue()==1 && before.path("role").asText().equals("ADMIN"));independentPassword(before.path("hash").textValue(),oldPassword);
    byte[] random=new byte[32];new SecureRandom().nextBytes(random);String password=Base64.getUrlEncoder().withoutPadding().encodeToString(random);Arrays.fill(random,(byte)0);
    try(Playwright pw=Playwright.create();Browser browser=pw.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));BrowserContext context=browser.newContext(CurrentCharacterizationTest.desktopOptions(false).setProxy("socks5://127.0.0.1:55169"))){
      var info=context.request().get(BASE+"/actuator/info");require(info.status()==200);
      var information=JSON.readTree(info.body());require(information.size()==5 && information.path("commit").asText().equals(args[0]) && information.path("app").asText().equals("0.1.0-SNAPSHOT") && information.path("config").asText().equals("1") && information.path("schema").asText().equals("027") && information.path("protocol").asText().equals("0.1.0-SNAPSHOT"));info.dispose();
      byte[] candidate=JSON.writeValueAsBytes(Map.of("username",username,"password",password));
      try(var file=java.nio.channels.FileChannel.open(updated,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
        var buffer=java.nio.ByteBuffer.wrap(candidate);while(buffer.hasRemaining())file.write(buffer);file.force(true);
      }finally{Arrays.fill(candidate,(byte)0);}
      try(var directory=java.nio.channels.FileChannel.open(PRIVATE,StandardOpenOption.READ)){directory.force(true);}
      Page page=CurrentCharacterizationTest.login(context,BASE,new CharacterizationEnvironment.Credential(username,oldPassword));require(page.url().equals(BASE+"/"));
      require(context.cookies().stream().anyMatch(c->c.secure && c.httpOnly && c.path.equals("/") && String.valueOf(c.sameSite).equalsIgnoreCase("LAX")));
      var response=page.navigate(BASE+"/admin/users");require(response!=null && response.status()==200);var row=page.locator("tr.user-row").filter(new Locator.FilterOptions().setHasText(username));require(row.count()==1 && row.locator("td.role").innerText().equals("ADMIN"));row.locator("a.detail").click();page.waitForLoadState();
      require(page.url().equals(BASE+"/admin/users/"+before.path("id").longValue()) && page.locator("dd.role").innerText().equals("ADMIN"));
      var form=page.locator("form[data-operation=PASSWORD]");require(form.count()==1 && form.locator("input[name=operation_token]").inputValue().matches("[0-9a-f-]{36}"));
      form.locator("input[name=password]").fill(password);form.locator("input[name=password_confirmation]").fill(password);form.locator("input[name=confirm]").check();form.locator("button[type=submit]").click();page.waitForLoadState();require(page.url().startsWith(BASE+"/login"));
      var changed=query("select json_build_object('hash',password_hash,'version',version,'revoked',(select count(*) from schubert.auth_sessions where user_id=u.id and revoked=false)) from schubert.app_users u where id="+before.path("id").longValue());require(changed.path("version").longValue()==before.path("version").longValue()+1 && changed.path("revoked").intValue()==0 && !changed.path("hash").textValue().equals(before.path("hash").textValue()));independentPassword(changed.path("hash").textValue(),password);
      Page relogin=CurrentCharacterizationTest.login(context,BASE,new CharacterizationEnvironment.Credential(username,password));require(relogin.url().equals(BASE+"/"));
      var after=query("select json_build_object('count',count(*),'active',(select count(*) from schubert.auth_sessions where user_id=max(u.id) and revoked=false)) from schubert.app_users u where username='"+username+"'");require(after.path("count").intValue()==1 && after.path("active").intValue()==1);
    }
  }
}
