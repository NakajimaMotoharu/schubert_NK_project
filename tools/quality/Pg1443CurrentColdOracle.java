import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.util.*;

/** Independent SSC264 real FD oracle, dedicated temporary tree, no VM authority. */
public final class Pg1443CurrentColdOracle {
  static int checks;
  static void check(boolean value) {
    checks++;
    if(!value)throw new AssertionError("current cold independent FD oracle refused");
  }
  static Map<String,Object> attrs(Path p)throws Exception {
    return Files.readAttributes(p,"unix:uid,gid,mode,nlink,dev,ino,size,ctime,lastModifiedTime");
  }
  public static void main(String[] args)throws Exception {
    check(args.length==1 && args[0].equals("/dev/shm/pgpt-SSC264-oracle-1443"));
    Path root=Path.of(args[0]);
    check(Files.isDirectory(root,LinkOption.NOFOLLOW_LINKS) && !Files.isSymbolicLink(root)
        && ((Integer)attrs(root).get("uid"))==0 && ((Integer)attrs(root).get("mode"))==0040700);
    try(var held=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),root)) {
      Pg1441CurrentColdPreparation.initialChild(held,"root-private",0,0,false);
      var first=attrs(root.resolve("root-private"));
      check(((Integer)first.get("mode"))==0040700 && ((Integer)first.get("nlink"))==2
          && ((Integer)first.get("uid"))==0 && ((Integer)first.get("gid"))==0);
      Pg1441CurrentColdPreparation.initialChild(held,"public-parent",0,0,true);
      check(((Integer)attrs(root.resolve("public-parent")).get("mode"))==0040755);
      Pg1441CurrentColdPreparation.initialChild(held,"fixed-api",999,981,false);
      var api=attrs(root.resolve("fixed-api"));
      check(((Integer)api.get("mode"))==0040700 && ((Integer)api.get("uid"))==999
          && ((Integer)api.get("gid"))==981 && ((Integer)api.get("nlink"))==2);
      boolean duplicate=false;
      try {Pg1441CurrentColdPreparation.initialChild(held,"root-private",999,981,false);}
      catch(StorageIoException rejected){duplicate=true;}
      check(duplicate && first.equals(attrs(root.resolve("root-private"))));
      for(String name:Arrays.asList("..","a/b",null)) {
        boolean invalid=false;
        try {Pg1441CurrentColdPreparation.initialChild(held,name,0,0,false);}
        catch(IllegalArgumentException|IllegalStateException rejected){invalid=true;}
        check(invalid);
      }
    }
    try(var entries=Files.list(root)) {
      check(entries.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet())
          .equals(Set.of("root-private","public-parent","fixed-api")));
    }
    System.out.println("PG1443_REAL_FD_ORACLE checks="+checks+" unchangedDuplicate=true noVm=true");
  }
}
