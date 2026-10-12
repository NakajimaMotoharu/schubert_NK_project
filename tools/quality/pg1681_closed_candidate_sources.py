"""BUG1150 new-only inputs plus pre-M/A/DB/Ref exact dependency qualification."""
import inspect
import pg1659_completed_candidate_identity_sources as previous
import pg1681_input_closure_contract as contract

TOOLS = 'pg1681-completed-unused-tools-v4'
REMOTE = '/home/ubuntu/pg1683-candidate-input-v4'
ARCHIVE_NAME = 'pg1683-release-v4.tar'

PREFLIGHT = r'''
import hashlib,json,os,pathlib,stat,subprocess
def require(v):
 if not v:raise ValueError('fixed input dependency closure refused')
require(os.geteuid()==0)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1681-completed-unused-tools-v4')
stage=pathlib.Path('/home/ubuntu/pg1683-candidate-input-v4')
def private_file(p,uid,mode,max_size):
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(uid,uid,mode,1)and s.st_size<=max_size and not os.listxattr(p))
 raw=p.read_bytes();t=p.lstat();require((s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_uid,t.st_gid,t.st_mode,t.st_nlink,t.st_size,t.st_mtime_ns,t.st_ctime_ns))
 return raw
for p,uid in [(root,0),(stage,1000)]:
 s=p.lstat();require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(uid,uid,0o700)and not os.listxattr(p))
pins=json.loads(private_file(root/'payload-sha256.json',0,0o400,1048576))
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(pins)|{'payload-sha256.json'})
directories={str(p)for name in pins for p in pathlib.PurePosixPath(name).parents if str(p)!='.'}
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_dir()}==directories)
for p in root.rglob('*'):
 s=p.lstat();require(not p.is_symlink())
 if p.is_dir():require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700)and not os.listxattr(p))
text={}
for name,digest in pins.items():
 canonical(name);raw=private_file(root/name,0,0o400,2097152);require(hashlib.sha256(raw).hexdigest()==digest)
 if name.endswith('.py'):text[name]=raw.decode('utf-8')
names={p.name for p in stage.iterdir()};validate_graph(pins,text,'pg1683-release-v4.tar',names)
bundle_raw=private_file(stage/'bundle.safe.json',1000,0o400,1024);require(hashlib.sha256(bundle_raw).hexdigest()==BUNDLE_HASH)
bundle=json.loads(bundle_raw);require(set(bundle)=={'archiveSha256','signatureSha256'})
archive=private_file(stage/'pg1683-release-v4.tar',1000,0o400,536870912)
signature=private_file(stage/'pg1638-manifest-v1.sig',1000,0o600,64)
require(len(signature)==64 and hashlib.sha256(archive).hexdigest()==bundle['archiveSha256']and hashlib.sha256(signature).hexdigest()==bundle['signatureSha256'])
for name,digest in [('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py','0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'),('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py','b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')]:
 p=pathlib.Path(name);require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')
manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c')
data=json.loads(manifest);require(data['source']['commit']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'and len(data['artifacts'])==187)
for row in data['artifacts']:
 canonical(row['path']);p=release/row['path'];require(p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile','/var/lib/pgpt-s1-preservation/pg1544-manifest.sig'],check=True,timeout=5,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
require(not pathlib.Path('/var/lib/pgpt-s1-preservation/pg1684-completed-unused-placement-v4').exists()and not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists())
print('PG1681_INPUT_CLOSURE_READY',flush=True)
'''

JAVA_PREFLIGHT = r'''
  @FunctionalInterface interface InputVerifier {void verify()throws Exception;}
  static void beforeOwnership(InputVerifier verifier)throws Exception{require(verifier!=null);verifier.verify();}
  static void verifyInputClosure()throws Exception{
    var probe=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg1681_input_preflight.py").toString()).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!probe.waitFor(15,TimeUnit.SECONDS)){probe.destroy();require(probe.waitFor(5,TimeUnit.SECONDS));throw new IOException("input preflight unconfirmed");}
    try(var input=probe.getInputStream()){
      require(probe.exitValue()==0 &&Arrays.equals(input.readNBytes(129),"PG1681_INPUT_CLOSURE_READY\n".getBytes(StandardCharsets.US_ASCII))&&input.read()==-1);
    }finally{probe.getOutputStream().close();probe.getErrorStream().close();}
  }
'''


def sources(bom):
    result={}
    for name,raw in previous.sources(bom).items():
        raw=raw.replace(previous.TOOLS,TOOLS).replace('/home/ubuntu/pg1661-candidate-input-v1',REMOTE).replace('pg1662-completed-unused-placement-v3','pg1684-completed-unused-placement-v4')
        raw=raw.replace("archive=stage/'pg1661-release-v1.tar'", "archive=stage/'pg1683-release-v4.tar'")
        if name=='pg1640_native_owned_stop.py':
            raw=raw.replace('import hashlib, json, os, pathlib, stat, subprocess, sys','import os, pathlib, stat')
        if name=='Pg1640UnusedStage.java':
            marker='    require(MaintenanceFileLock.create().tryExclusive('
            if raw.count(marker)!=1:raise ValueError('one pre-ownership closure boundary required')
            raw=raw.replace(marker,'    beforeOwnership(Pg1640UnusedStage::verifyInputClosure);\n'+marker)
            raw=raw.replace('  public static void main',JAVA_PREFLIGHT+'\n  public static void main')
        result[name]=raw
    definitions='import ast,re\nfrom pathlib import PurePosixPath\nSTANDARD=frozenset('+repr(tuple(sorted(contract.STANDARD)))+')\n'
    definitions+=inspect.getsource(contract.canonical)+'\n'+inspect.getsource(contract.validate_graph)+'\n'
    result['pg1681_input_preflight.py']=definitions+PREFLIGHT
    result['Pg1681InputBoundaryTest.java']=INPUT_TEST
    return result


INPUT_TEST=r'''
import java.io.IOException;
public final class Pg1681InputBoundaryTest {
 private Pg1681InputBoundaryTest(){}
 public static void main(String[]args)throws Exception{
  int[]count={0};Pg1640UnusedStage.beforeOwnership(()->count[0]++);if(count[0]!=1)throw new AssertionError("single probe");
  try{Pg1640UnusedStage.beforeOwnership(null);throw new AssertionError("null admitted");}catch(IllegalStateException expected){}
  var io=new IOException("fixed");try{Pg1640UnusedStage.beforeOwnership(()->{throw io;});throw new AssertionError("IO swallowed");}catch(IOException expected){if(expected!=io)throw new AssertionError("IO identity");}
  var runtime=new IllegalArgumentException("fixed");try{Pg1640UnusedStage.beforeOwnership(()->{throw runtime;});throw new AssertionError("runtime swallowed");}catch(IllegalArgumentException expected){if(expected!=runtime)throw new AssertionError("runtime identity");}
  var error=new AssertionError("fixed");try{Pg1640UnusedStage.beforeOwnership(()->{throw error;});throw new AssertionError("fatal swallowed");}catch(AssertionError expected){if(expected!=error)throw new AssertionError("fatal identity");}
  System.out.println("PG1681_INPUT_BOUNDARY independentChecks=5 actualMethod=true nullNpe0=true ownerIO0=true");
 }
}
'''
