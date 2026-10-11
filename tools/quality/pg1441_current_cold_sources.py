"""SSC264 source-only current completed-cold preparation; no VM actions."""
import ast
from pathlib import Path
import sys

R=Path(__file__).resolve().parent/'vm/050_s1'
sys.path.insert(0,str(R))
from pg1062_cold_preparation_sources_v2 import files as prior

ROLE_USERS={
    'backup':'schubert-backup','inspector':'schubert-inbox-inspector',
    'ordinary-inspector196':'schubert-inbox-inspector','ordinary-api193':'schubert-api',
    'ordinary-bootstrap196':'schubert-api','ordinary-web193':'schubert-web',
}
ROOT_ROLES=['cleanup','expiry','parent','root-api','root-api193','root-web193']


def java():
    values=prior()
    raw=values['Pg1062ColdOwnedPreparation.java']
    for old,new in [
        ('Pg1062ColdOwnedPreparation','Pg1441CurrentColdPreparation'),
        ('pg1062-cold-tools-v1','pg1441-current-cold-tools-v1'),
        ('pg1062-cold-prepared-v1','pg1441-current-cold-prepared-v1'),
        ('pg1062_cold_refs.py','pg1441_current_cold_refs.py'),('PG1062_','PG1441_'),
        ('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),
        ('eeae04ea-713c-4f2d-888d-358fb4bed274','d2e3a86f-27a4-4c2a-be21-b512eebf1216'),
        ('091663ce-1cf4-47e7-8311-218ebb0c8653','841b507c-2713-4ffe-8882-68f5fb3f87f5'),
        ('2026-10-09T23:31:22.087768Z','2026-10-10T23:30:23.481632Z'),
        ('2026-10-09T23:56:48.112404Z','2026-10-10T23:54:39.918039Z'),
        ('"PG932"','"PG1292"'),('"pg932"','"pg1292"'),
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97','769ddb15cd735c25fef581b5f9850ef9d0053c0f'),
        ('/opt/schubert-nk/releases/0.1.0-PG932','/opt/schubert-nk/releases/0.1.0-PG1292'),
        ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'),
    ]:
        if old not in raw:raise ValueError('explicit current cold binding absent: '+old)
        raw=raw.replace(old,new)
    start=raw.index('  static void environment()throws Exception {')
    end=raw.index('  public static void main',start)
    raw=raw[:start]+ENVIRONMENT+'\n'+raw[end:]
    return raw


ENVIRONMENT=r'''
  static void initialChild(dev.codex.schubert.nk.storage.OwnedTransferDirectory parent,
      String name,int uid,int gid,boolean publicParent)throws Exception {
    try(var child=parent.createPrivateChild(name)) {
      child.atDirectory(held->{
        try {
          var initial=Pg428ColdBootPreparation.heldAttributes(held);
          require(((Integer)initial.get("uid"))==0 && ((Integer)initial.get("gid"))==0
              && ((Integer)initial.get("mode"))==0040700 && ((Integer)initial.get("nlink"))==2
              && Pg428ColdBootPreparation.names(held).isEmpty());
          // Following this /proc/self/fd capability targets the retained inode.
          Files.setAttribute(held,"unix:uid",uid);
          Files.setAttribute(held,"unix:gid",gid);
          if(publicParent)Files.setPosixFilePermissions(held,java.nio.file.attribute.PosixFilePermissions.fromString("rwxr-xr-x"));
          var after=Pg428ColdBootPreparation.heldAttributes(held);
          require(initial.get("dev").equals(after.get("dev")) && initial.get("ino").equals(after.get("ino"))
              && ((Integer)after.get("uid"))==uid && ((Integer)after.get("gid"))==gid
              && ((Integer)after.get("mode"))==(publicParent?0040755:0040700)
              && ((Integer)after.get("nlink"))==2 && Pg428ColdBootPreparation.names(held).isEmpty());
          return Boolean.TRUE;
        }catch(Exception problem){throw new java.io.IOException("new cold child initialization refused",problem);}
      });
      child.sync();parent.sync();
    }
  }
  static void environment()throws Exception {
    Path run=Path.of("/run/schubert-nk");
    var names=List.of("startup","backup-request","cleanup-request","expiry-request","pt-coverage");
    for(String name:names)require(!Files.exists(run.resolve(name),LinkOption.NOFOLLOW_LINKS));
    var calls=dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create();
    try(var held=dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(calls,run)) {
      for(String name:names)initialChild(held,name,0,0,name.equals("pt-coverage"));
      try(var coverage=held.openExistingChild("pt-coverage")) {
        for(String name:List.of("cleanup","expiry","parent","root-api","root-api193","root-web193"))
          initialChild(coverage,name,0,0,false);
        var users=Map.of("backup","schubert-backup","inspector","schubert-inbox-inspector",
            "ordinary-inspector196","schubert-inbox-inspector","ordinary-api193","schubert-api",
            "ordinary-bootstrap196","schubert-api","ordinary-web193","schubert-web");
        for(var entry:users.entrySet()) {
          var uid=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-u",entry.getValue());
          var gid=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-g",entry.getValue());
          initialChild(coverage,entry.getKey(),Integer.parseInt(new String(uid,StandardCharsets.US_ASCII).strip()),
              Integer.parseInt(new String(gid,StandardCharsets.US_ASCII).strip()),false);
        }
        coverage.sync();
      }
      held.sync();
    }
  }
'''


if __name__=='__main__':
    print('CURRENT_COLD_SOURCE_BUILT_NO_ACTION',len(java()))
