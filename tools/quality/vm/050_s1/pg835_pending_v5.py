"""BUG964: fixed existing bind mount proof; no second freeze/place/activation."""
import ast
from pathlib import Path
import sys
import pg835_pending_sources as profile
from pg835_pending_v4 import source as previous

R=Path(__file__).resolve().parent
METHOD=r'''
  static boolean readOnlyMount(String table,String target){
    if(table==null || target==null || table.length()>1048576 || !target.equals("/opt/schubert-nk/releases/0.1.0-PG832"))return false;
    String[] root=null, candidate=null;
    var ids=new HashSet<String>();
    for(String row:table.split("\\n",-1)){
      if(row.isEmpty())continue;
      String[] f=row.split(" ",-1);int sep=-1;
      for(int i=6;i<f.length;i++)if(f[i].equals("-")){if(sep!=-1)return false;sep=i;}
      if(f.length<10 || sep<6 || f.length!=sep+4 || !f[0].matches("[1-9][0-9]*") || !f[1].matches("[1-9][0-9]*") || !f[2].matches("[0-9]+:[0-9]+") || !ids.add(f[0]))return false;
      for(String s:f)if(s.isEmpty())return false;
      if(f[4].startsWith(target+"/"))return false;
      if(f[4].equals("/")){if(root!=null)return false;root=f;}
      if(f[4].equals(target)){if(candidate!=null)return false;candidate=f;}
    }
    if(root==null || candidate==null)return false;
    int cs=Arrays.asList(candidate).indexOf("-"),rs=Arrays.asList(root).indexOf("-");
    return candidate[1].equals(root[0]) && candidate[2].equals(root[2]) && candidate[3].equals(target) && candidate[5].equals("ro,relatime") && candidate[cs+1].equals("ext4") && candidate[cs+2].equals("/dev/vda1") && root[rs+1].equals("ext4") && root[rs+2].equals("/dev/vda1") && candidate[cs+3].equals(root[rs+3]);
  }
'''
# Literal independently specified root+bind oracle, not read from Production.
ORACLE=r'''
    String target="/opt/schubert-nk/releases/0.1.0-PG832";
    String root="46 1 253:1 / / rw,relatime shared:1 - ext4 /dev/vda1 rw,discard,errors=remount-ro,commit=30\\n";
    String mount="249 46 253:1 "+target+" "+target+" ro,relatime shared:1 - ext4 /dev/vda1 rw,discard,errors=remount-ro,commit=30\\n";
    String good=root+mount;
    if(!Pg835PendingDeployment.readOnlyMount(good,target))throw new AssertionError("bind ro on rw superblock rejected");
    String[] invalid={null,"",root,mount,good+mount,good.replace("249 46","249 99"),good.replace("249 46","46 46"),good.replace("ro,relatime","rw,relatime"),good.replace("ro,relatime","ro,relatime,nosuid"),good.replace("249 46 253:1","249 46 253:2"),good.replace("249 46 253:1 "+target,"249 46 253:1 /foreign"),good.replace("ext4 /dev/vda1","xfs /dev/vda1"),good.replace("ext4 /dev/vda1","ext4 /dev/vdb1"),good.replace("249 46","invalid 46"),good.replace("shared:1 - ext4","shared:1 - - ext4"),good+"250 249 253:1 /foreign "+target+"/api ro,relatime - ext4 /dev/vda1 rw\\n",good.replace("249 46","249  46"),good.replace("ro,relatime shared:1 - ext4 /dev/vda1 rw,discard,errors=remount-ro,commit=30","ro,relatime shared:1 - ext4 /dev/vda1 rw"),good+root};
    for(String bad:invalid)if(Pg835PendingDeployment.readOnlyMount(bad,target))throw new AssertionError("foreign mount accepted");
    for(String badTarget:new String[]{null,"/foreign",target+"/"})if(Pg835PendingDeployment.readOnlyMount(good,badTarget))throw new AssertionError("foreign target accepted");
    System.out.println("PG835_FIXED_MOUNT_ORACLE independentAssertions=23 mutation0=true");
'''

def bind(raw):
    return raw.replace('pg835-pending-tools-v1','pg835-pending-tools-v5').replace('pg835-pending-codeonly','pg835-pending-codeonly-v5')

def java(raw):
    marker='phase="FIXED_FREEZE";Pg387TrustedDeployment.freezeCandidate();'
    assert raw.count(marker)==1
    raw=bind(raw).replace(marker,'phase="EXISTING_FIXED_FREEZE";require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))) && readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),NEXT.toString()));')
    return raw.replace('  static String SOURCE,DIGEST;',METHOD.replace('\\\\n','\\n')+'\n  static String SOURCE,DIGEST;')

def source(mode):
    raw=previous(mode).replace('-v4','-v5')
    if mode=='compile':
        marker='    for old in(W/'
        assert raw.count(marker)==1
        raw=raw.replace(marker,"    original_sources=sources\n    def sources():\n        value=original_sources()\n        value['Pg835PendingDeploymentTest.java']=value['Pg835PendingDeploymentTest.java'].replace('    System.out.println(',MOUNT_ORACLE+'\\n    System.out.println(')\n        return value\n"+marker)
    ast.parse(raw);return raw

def assembled_sources():
    import pg835_pending_compile as compiler
    old=profile.java;old_refs=profile.refs;old_before=profile.before_freeze
    try:
        profile.java=lambda old=old:java(old())
        profile.refs=lambda old_refs=old_refs:bind(old_refs())
        profile.before_freeze=lambda old_before=old_before:bind(old_before())
        values=compiler.sources()
        values['Pg835PendingDeploymentTest.java']=values['Pg835PendingDeploymentTest.java'].replace('    System.out.println(',ORACLE.replace('\\\\n','\\n')+'\n    System.out.println(')
        return values
    finally:profile.java=old;profile.refs=old_refs;profile.before_freeze=old_before

if __name__=='__main__':
    mode=sys.argv[1];assert mode in('compile','stage','activate')
    if mode=='compile':
        old=profile.java;profile.java=lambda old=old:java(old())
        for name in ('refs','before_freeze'):
            old=getattr(profile,name);setattr(profile,name,lambda old=old:bind(old()))
    exec(compile(source(mode),'<835 bind mount fixed new-only v5>','exec'),{'__file__':str(R/'pg835_pending_v5.py'),'__name__':'__main__','MOUNT_ORACLE':ORACLE.replace('\\\\n','\\n')})
