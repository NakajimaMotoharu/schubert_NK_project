"""Fresh owned readonly original IO timing; no proof caching or business mutation."""
import ast
from pg1478_partial_original_profile_sources import java as prior_java, BODY as prior_body
from pg1505_publication_recovery_sources_v3 import refs as recovery_refs

TOOLS='pg1512-original-component-tools-v1'
SAVE='pg1514-original-component-profile-v1'
CLASS='Pg1512OriginalComponentProfile'

def java():
    raw=prior_java().replace('Pg1478PartialOriginalProfile',CLASS).replace('pg1478-partial-original-tools-v1',TOOLS).replace('pg1481-partial-original-profile-v1',SAVE).replace('pg1478_partial_original_refs.py','pg1512_original_component_refs.py').replace('PG1481_','PG1514_').replace('PG266-readonly-profile','PG269-original-io-profile')
    marker='MaintenanceRunFiles.create().execute(session->'
    assert raw.count(marker)==1
    raw=raw.replace(marker,'dev.codex.schubert.nk.batch.file.Pg1512OriginalIoProfile.create().execute(session->')
    raw=raw.replace('    long begin=System.nanoTime();','    dev.codex.schubert.nk.batch.file.Pg1512OriginalIoProfile.reset();\n    long begin=System.nanoTime();',1)
    marker='    if(Pg983BootstrapExisting.lease!=null)Pg983BootstrapExisting.pulse();\n  }'
    assert raw.count(marker)==1
    raw=raw.replace(marker,'    Files.writeString(SAVE.resolve("components.safe.jsonl"),dev.codex.schubert.nk.batch.file.Pg1512OriginalIoProfile.report(duration)+"\\n",StandardCharsets.US_ASCII,StandardOpenOption.CREATE,StandardOpenOption.APPEND);\n'+marker)
    return raw

def refs():
    prefix=[]
    for node in ast.parse(recovery_refs()).body:
        if isinstance(node,ast.Try):break
        if isinstance(node,ast.FunctionDef)and node.name in {'stop_one','save','validate_current'}:continue
        prefix.append(node)
    raw=ast.unparse(ast.Module(body=prefix,type_ignores=[]))
    raw=raw.replace('Pg1505PublicationOnlyRecovery',CLASS).replace("b'recover'","b'profile'").replace('PG266-publication-recover','PG269-original-io-profile').replace('pg1505-publication-only-tools-v3',TOOLS).replace('pg1507-publication-only-recovery-v3',SAVE)
    body=prior_body.replace('expected_current','profile_expected').replace('expected_raw','profile_expected_raw').replace('/var/lib/pgpt-s1-preservation/pg1477-failed-publication-owner-v1/observed.private.json','/var/lib/pgpt-s1-preservation/pg1511-publication-gc-closing-v1/observed.private.json').replace('bcfd08285abe448ebe28c2adffc39acca0346e25b1769c44d72f43290da38cd5','7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5')
    raw+='\n'+SETUP+'\n'+body
    raw=raw.replace('PG266-readonly-profile','PG269-original-io-profile')
    compile(raw,'<fresh complete current owned readonly IO profile>','exec')
    return raw

SETUP=r'''
STOPPED[:]=ORDER;RETIRED=True
for unit in ORDER:
 path=BASE/'pg1507-publication-only-recovery-v3'/(unit+'.stopped.private')
 STOP_RECEIPTS[unit]=json.loads(path.read_bytes())
BROKER_LOCKS=[('POSIX',(253,1,503366)),('POSIX',(253,1,503372)),('FLOCK',(0,33,31))]
'''

PROFILE_JAVA=r'''package dev.codex.schubert.nk.batch.file;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.*;
import java.nio.channels.SeekableByteChannel;
import java.security.MessageDigest;
import java.util.*;
/** Tool-only transparent timing: original checks/FD/ACL/filesystem all delegate unchanged. */
public final class Pg1512OriginalIoProfile {
 private Pg1512OriginalIoProfile(){}
 private static final Map<String,long[]> METRICS=new TreeMap<>();
 private interface Work<T>{T run()throws IOException;}
 private static <T>T timed(String key,Work<T> work)throws IOException {
  long begin=System.nanoTime();try{return work.run();}finally{long[] m=METRICS.computeIfAbsent(key,k->new long[2]);m[0]++;m[1]+=System.nanoTime()-begin;}
 }
 public static void reset(){METRICS.clear();}
 public static String report(long total){
  StringJoiner values=new StringJoiner(",","{\"wholeTwoObserveNanos\":"+total+",\"components\":{","}}");
  for(var entry:METRICS.entrySet()){long[] a=entry.getValue();values.add("\""+entry.getKey()+"\":{\"calls\":"+a[0]+",\"nanos\":"+a[1]+"}");}
  return values.toString();
 }
 public static MaintenanceRunFiles create(){
  var actual=new MaintenanceRunFiles.NioIo();var sec=LinuxInodeSecurity.create();
  MaintenanceRunFiles.Io io=new MaintenanceRunFiles.Io(){
   public Map<String,Object> attributes(Path p)throws IOException{return timed("attributes",()->actual.attributes(p));}
   public String filesystem(Path p)throws IOException{return timed("filesystem",()->actual.filesystem(p));}
   public SeekableByteChannel open(Path p)throws IOException{return timed("open",()->actual.open(p));}
   public DirectoryStream<Path> openNames(Path p)throws IOException{return timed("openNames",()->actual.openNames(p));}
   public InspectorEnvironmentPublisher.Writer openWriter(Path p)throws IOException{throw new IOException("readonly profiler mutation refused");}
  };
  InodeSecurityCalls security=new InodeSecurityCalls(){
   public byte[] accessAcl(Path p,int limit)throws StorageIoException {
    try{return timed("acl",()->sec.accessAcl(p,limit));}catch(StorageIoException e){throw e;}catch(IOException e){throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);}
   }
   public boolean readOnlyFilesystem(Path p)throws StorageIoException {
    try{return timed("statvfs",()->sec.readOnlyFilesystem(p));}catch(StorageIoException e){throw e;}catch(IOException e){throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);}
   }
   public long effectiveUid(){return sec.effectiveUid();}
  };
  return new MaintenanceRunFiles(Path.of("/var"),LinuxDirectoryCalls.create(),security,io,
   ()->{throw new IllegalStateException("readonly profiler identity allocation refused");},
   ()->MessageDigest.getInstance("SHA-256"),Optional.of(LinuxHostDirectoryCalls.create()));
 }
}
'''
