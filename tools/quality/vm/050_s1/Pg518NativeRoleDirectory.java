package dev.codex.schubert.nk.batch.file;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
/** SS343/SSC193196209211; PT-OPS-PG518: fixed missing6, held-inode new-only. */
public final class Pg518NativeRoleDirectory {
  private Pg518NativeRoleDirectory() {}
  static final Set<String> ROLES=Set.of("root-api193","root-web193","ordinary-api193","ordinary-web193","ordinary-inspector196","ordinary-bootstrap196");
  public interface Io {
    Map<String,Object> metadata(Path held)throws IOException;
    void owner(Path held,int uid,int gid)throws IOException;
    boolean cleanTmpfs(Path held)throws IOException;
  }
  static void require(boolean v)throws IOException {if(!v)throw new IOException("fixed native role unavailable");}
  public static void prepare(OwnedTransferDirectory common,String role,int uid,int gid)throws IOException {
    prepare(common,role,uid,gid,new Io(){
      public Map<String,Object> metadata(Path p)throws IOException{return Map.copyOf(Files.readAttributes(p,"unix:dev,ino,uid,gid,mode,nlink,size,lastModifiedTime,ctime"));}
      public void owner(Path p,int u,int g)throws IOException{Files.setAttribute(p,"unix:uid",u);Files.setAttribute(p,"unix:gid",g);}
      public boolean cleanTmpfs(Path p)throws IOException {var s=LinuxInodeSecurity.create();return s.effectiveUid()==0 && s.accessAcl(p,4096).length==0 && !s.readOnlyFilesystem(p) && Files.getFileStore(p).type().equals("tmpfs");}
    });
  }
  static boolean fixedRole(String role,int uid,int gid) {
    return role!=null && ROLES.contains(role) && uid>=0 && gid>=0 && (!role.startsWith("root-") || uid==0 && gid==0);
  }
  static boolean directory(Map<String,Object> v,int uid,int gid,int mode)throws IOException {
    return v!=null && Set.of("dev","ino","uid","gid","mode","nlink","size","lastModifiedTime","ctime").equals(v.keySet())
      && Integer.valueOf(uid).equals(v.get("uid")) && Integer.valueOf(gid).equals(v.get("gid")) && Integer.valueOf(0040000|mode).equals(v.get("mode"))
      && v.get("dev") instanceof Long && v.get("ino") instanceof Long ino && ino>0 && v.get("nlink") instanceof Integer links && links>=2
      && v.get("size") instanceof Long size && size>=0 && v.get("lastModifiedTime") instanceof java.nio.file.attribute.FileTime
      && v.get("ctime") instanceof java.nio.file.attribute.FileTime;
  }
  static Set<String> names(Path root)throws IOException {
    var names=new HashSet<String>();try(var entries=Files.newDirectoryStream(root)){for(var p:entries)require(names.add(p.getFileName().toString()));}return Set.copyOf(names);
  }
  static void prepare(OwnedTransferDirectory common,String role,int uid,int gid,Io io)throws IOException {
    require(common!=null && io!=null && fixedRole(role,uid,gid));
    var before=common.atDirectory(p->{var v=io.metadata(p);require(directory(v,0,0,0755) && io.cleanTmpfs(p) && !names(p).contains(role));return v;});
    // createPrivateChild uses mkdirat0700 and held NOFOLLOW FD; no path-based existing repair.
    try(var child=common.createPrivateChild(role)){
      child.atDirectory(p->{
        var initial=io.metadata(p);require(directory(initial,0,0,0700) && names(p).isEmpty() && io.cleanTmpfs(p));
        io.owner(p,uid,gid);
        var after=io.metadata(p);require(directory(after,uid,gid,0700) && names(p).isEmpty() && io.cleanTmpfs(p)
          && initial.get("dev").equals(after.get("dev")) && initial.get("ino").equals(after.get("ino")));
        require(after.equals(io.metadata(p)));return Boolean.TRUE;
      });
      child.sync();common.sync();
      common.atDirectory(p->{
        var after=io.metadata(p);require(directory(after,0,0,0755) && io.cleanTmpfs(p) && names(p).contains(role));
        for(String k:List.of("dev","ino","uid","gid","mode"))require(before.get(k).equals(after.get(k)));
        require(((Integer)before.get("nlink"))+1==(Integer)after.get("nlink"));return Boolean.TRUE;
      });
    }
  }
}
