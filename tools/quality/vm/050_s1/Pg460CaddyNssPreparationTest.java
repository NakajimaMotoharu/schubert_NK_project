import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** Independent literal group/member oracle; optional real shadow-utils isolated chroot. */
public final class Pg460CaddyNssPreparationTest {
  static int assertions;
  static byte[] bytes(String s){return s.getBytes(StandardCharsets.US_ASCII);}
  static void check(boolean b){if(!b)throw new AssertionError("independent NSS oracle differs");assertions++;}
  static final String GROUP="root:x:0:\nwww-data:x:33:caddy,other\ncaddy:x:978:\nother:x:1000:\n";
  static final String GROUP_AFTER="root:x:0:\nwww-data:x:33:other\ncaddy:x:978:\nother:x:1000:\n";
  static final String SHADOW="root:!::\nwww-data:!::caddy,other\ncaddy:!::\nother:!::\n";
  static final String SHADOW_AFTER="root:!::\nwww-data:!::other\ncaddy:!::\nother:!::\n";
  public static void main(String[] args) throws Exception {
    check(Arrays.equals(bytes(GROUP_AFTER),Pg460CaddyNssPreparation.removeMember(bytes(GROUP),false)));
    check(Arrays.equals(bytes(SHADOW_AFTER),Pg460CaddyNssPreparation.removeMember(bytes(SHADOW),true)));
    check(Arrays.equals(bytes(SHADOW_AFTER),Pg460CaddyNssPreparation.removeMember(bytes(SHADOW_AFTER),true)));
    for(String bad:List.of(GROUP.replace("33:","34:"),GROUP.replace("caddy,other","other"),GROUP.replace("caddy,other","caddy,caddy"),GROUP.replace("caddy,other","caddy,"),GROUP+"www-data:x:33:caddy\n",GROUP.replace("\n","\r\n"),GROUP.substring(0,GROUP.length()-1),"",GROUP.replace("www-data","other-data"),GROUP.replace("other:x:1000:","other:invalid"))) {
      try{Pg460CaddyNssPreparation.removeMember(bytes(bad),false);throw new AssertionError("bad independent literal accepted");}catch(IllegalStateException rejected){assertions++;}
    }
    for(String good:List.of("978 33\n","33 978\n"))check(Pg460CaddyNssPreparation.groupIds(bytes(good)).equals(Set.of("33","978")));
    check(Pg460CaddyNssPreparation.groupIds(bytes("978\n")).equals(Set.of("978")));
    for(String bad:List.of("978 978\n","0\n","0978\n","978","978\r\n","978  33\n","","-1\n","978 \n")) {
      try{Pg460CaddyNssPreparation.groupIds(bytes(bad));throw new AssertionError("bad id literal accepted");}catch(IllegalStateException rejected){assertions++;}
    }
    if(args.length==1 && args[0].equals("native-fixture")) {
      check(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
      byte[] actualBefore=Pg460CaddyNssPreparation.query("/usr/bin/id","-G","caddy");
      Path fixture=Files.createTempDirectory(Path.of("/var/lib/pgpt-s1-preservation"),"pg460-nss-shadow-fixture-");
      Files.setPosixFilePermissions(fixture,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
      Path etc=Files.createDirectory(fixture.resolve("etc"));
      Files.writeString(etc.resolve("group"),GROUP,StandardOpenOption.CREATE_NEW);
      Files.writeString(etc.resolve("gshadow"),SHADOW,StandardOpenOption.CREATE_NEW);
      Files.writeString(etc.resolve("passwd"),"root:x:0:0:root:/root:/bin/sh\ncaddy:x:993:978:fixture:/nonexistent:/usr/sbin/nologin\nother:x:1000:1000:fixture:/nonexistent:/usr/sbin/nologin\n",StandardOpenOption.CREATE_NEW);
      Files.writeString(etc.resolve("nsswitch.conf"),"passwd: files\ngroup: files\nshadow: files\n",StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(etc.resolve("gshadow"),java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));
      var p=new ProcessBuilder("/usr/bin/gpasswd","--root",fixture.toString(),"-d","caddy","www-data").redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.DISCARD).start();
      check(p.waitFor(5,TimeUnit.SECONDS) && p.exitValue()==0);
      check(Files.readString(etc.resolve("group")).equals(GROUP_AFTER));check(Files.readString(etc.resolve("gshadow")).equals(SHADOW_AFTER));
      check(Files.readString(etc.resolve("group-")).equals(GROUP));check(Files.readString(etc.resolve("gshadow-")).equals(SHADOW));
      check(Arrays.equals(actualBefore,Pg460CaddyNssPreparation.query("/usr/bin/id","-G","caddy")));
      System.out.println("PG460_NSS_NATIVE_FIXTURE_PASS literalGroupShadowOtherMemberBackupPreserved=true actualCaddyNssUnchanged=true fixtureRetainedPrivate=true productionPt0=true");
    }else if(args.length!=0)throw new IllegalArgumentException("no args or native-fixture only");
    System.out.println("PG460_NSS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true");
  }
}
