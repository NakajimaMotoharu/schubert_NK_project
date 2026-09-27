import java.nio.file.*;
import java.nio.file.attribute.*;

/** Disposable VM-only public abc release selector fixture; NOT a valid release BOM. */
public final class NativeReleaseFixture {
  private static void directory(Path path,String owner,String group,String mode)throws Exception {
    if(Files.exists(path,LinkOption.NOFOLLOW_LINKS)) {
      var a=Files.readAttributes(path,PosixFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
      if(!a.isDirectory()||!a.owner().getName().equals(owner)||!a.group().getName().equals(group)||!a.permissions().equals(PosixFilePermissions.fromString(mode)))throw new AssertionError("existing namespace differs; do not repair");
      return;
    }
    Files.createDirectory(path,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString(mode)));
    var view=Files.getFileAttributeView(path,PosixFileAttributeView.class,LinkOption.NOFOLLOW_LINKS);
    var lookup=path.getFileSystem().getUserPrincipalLookupService();
    view.setOwner(lookup.lookupPrincipalByName(owner));view.setGroup(lookup.lookupPrincipalByGroupName(group));
  }
  public static void main(String[] args)throws Exception {
    if(args.length!=0||!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated fixture required");
    Path app=Path.of("/opt/schubert-nk"),releases=app.resolve("releases"),release=releases.resolve("pgpt-native-301");
    for(Path p:new Path[]{app,releases,release})directory(p,"root","schubert","rwxr-x---");
    Path manifest=release.resolve("RELEASE-MANIFEST.json");
    if(Files.exists(manifest,LinkOption.NOFOLLOW_LINKS)) {
      if(!Files.isRegularFile(manifest,LinkOption.NOFOLLOW_LINKS)||!Files.readString(manifest).equals("abc"))throw new AssertionError("existing manifest differs; do not overwrite");
    } else {
      Files.createFile(manifest,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-r-----")));
      Files.getFileAttributeView(manifest,PosixFileAttributeView.class,LinkOption.NOFOLLOW_LINKS).setGroup(manifest.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByGroupName("schubert"));
      Files.writeString(manifest,"abc",StandardOpenOption.WRITE);
    }
    Path current=app.resolve("current");
    if(Files.exists(current,LinkOption.NOFOLLOW_LINKS)) {
      if(!Files.isSymbolicLink(current)||!Files.readSymbolicLink(current).equals(release))throw new AssertionError("existing selector differs; do not overwrite");
    }else Files.createSymbolicLink(current,release);
    for(String service:new String[]{"api","web"})directory(Path.of("/var/lib/schubert-nk/pgpt-native-"+service),"schubert-"+service,"schubert-"+service,"rwx------");
    System.out.println("isolated public release fixture prepared; BOM=false; no production acceptance");
  }
}
