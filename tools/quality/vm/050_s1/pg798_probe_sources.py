"""New-only readonly pair probe; no changes to the frozen797v3/v4 payload."""
import ast
from pg797_sources import java as previous_java,helper as previous_helper,SOURCE,DIGEST
__all__=['java','helper','SOURCE','DIGEST']


def bind(raw):
    return raw.replace('Pg797DatabaseProbe','Pg798DatabaseProbe').replace('pg797','pg798').replace('PG797','PG798').replace('pg798-liveness-tools-v1','pg798-scope-tools-v1').replace('pg798-liveness-probe-v1','pg798-scope-probe-v1')


HELPER_JAVA=r'''  static void helper(String action)throws Exception{
    pulse();
    var output=Files.createTempFile(Path.of("/var/lib/pgpt-s1-preservation"),"pg798-helper-",".private",java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
    var process=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg798_owned.py").toString(),action).redirectErrorStream(true).redirectOutput(output.toFile()).start();
    long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(120);
    while(!process.waitFor(250,java.util.concurrent.TimeUnit.MILLISECONDS)){pulse();require(System.nanoTime()<deadline);}
    pulse();require(process.exitValue()==0);
  }
'''


BUSINESS_JAVA=r'''  static Map<String,Pg456SignedMigration.Data> business(Connection db)throws Exception{
    var result=new TreeMap<String,Pg456SignedMigration.Data>();
    for(String table:new TreeSet<>(businessTableNames())){
      pulse();var digest=java.security.MessageDigest.getInstance("SHA-256");long count=0;
      try(var query=db.createStatement()){
        query.setQueryTimeout(5);
        try(var rows=query.executeQuery("select row_value from (select to_jsonb(t)::text collate \"C\" row_value from "+table+" t) snapshot order by row_value")){
          while(rows.next()){
            byte[] bytes=Objects.requireNonNull(rows.getString(1)).getBytes(StandardCharsets.UTF_8);
            digest.update(java.nio.ByteBuffer.allocate(4).putInt(bytes.length).array());digest.update(bytes);Arrays.fill(bytes,(byte)0);count++;if(count%256==0)pulse();
          }
        }
      }
      pulse();require(result.put(table,new Pg456SignedMigration.Data(count,HexFormat.of().formatHex(digest.digest())))==null);
    }
    return Map.copyOf(result);
  }
'''


def java():
    raw=bind(previous_java())
    raw=raw.replace('static long lastPulse;','static long lastPulse;\n  static Pg798DatabaseScope databaseScope;')
    raw=raw.replace('if(batchLease!=null)batchLease.verify();if(schemaLease!=null)schemaLease.verify();lastPulse=System.nanoTime();','if(databaseScope!=null)databaseScope.verify();lastPulse=System.nanoTime();')
    raw=raw.replace('phase="REFERENCE_ACQUIRE";refsHeld=true;', 'databaseScope=new Pg798DatabaseScope(batchLease,schemaLease);pulse();phase="REFERENCE_ACQUIRE";refsHeld=true;')
    start=raw.index('  static void retain(');end=raw.index('  static void parent()',start)
    raw=raw[:start]+r'''  static boolean retainPulse(){
    try{if(databaseScope!=null)databaseScope.verify();else require(batchLease==null&&schemaLease==null);return true;}
    catch(Exception|Error lost){return false;}
  }
  static void retain(String owners){
    System.err.println("PG798_UNKNOWN phase="+phase+" retained="+owners+" oldCloseNotInferred=true diagnosticsRedacted=true");
    boolean notified=false;
    for(;;){
      if(!notified&&!retainPulse()){System.err.println("PG798_DB_NOT_CONFIRMED ownershipNotInferred=true");notified=true;}
      try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
    }
  }
'''+raw[end:]
    start=raw.index('  static void helper(');end=raw.index('  static Set<String> businessTableNames()',start)
    raw=raw[:start]+HELPER_JAVA+BUSINESS_JAVA+raw[end:]
    # Each potentially expensive synchronous step is bounded by paired checkpoints.
    raw=raw.replace('helper("verify");parent();signed();','helper("verify");pulse();parent();pulse();signed();pulse();')
    raw=raw.replace('pending(invalid,db);','pulse();pending(invalid,db);pulse();')
    raw=raw.replace('var original=Pg428ColdBootPreparation.original();var backups=Pg481NativeStop.backup();','pulse();var original=Pg428ColdBootPreparation.original();pulse();var backups=Pg481NativeStop.backup();pulse();')
    raw=raw.replace('batchLease.verify();schemaLease.verify();','databaseScope.verify();')
    raw=raw.replace('&&original.equals(Pg428ColdBootPreparation.original())&&backups.equals(Pg481NativeStop.backup())&&rows.equals(business(schema))','&&original.equals(originalCheckpoint())&&backups.equals(backupCheckpoint())&&rows.equals(business(schema))')
    marker='  public static void main('
    assert raw.count(marker)==1
    raw=raw.replace(marker,r'''  static Map<String,String> originalCheckpoint()throws Exception{pulse();var value=Pg428ColdBootPreparation.original();pulse();return value;}
  static Map<String,String> backupCheckpoint()throws Exception{pulse();var value=Pg481NativeStop.backup();pulse();return value;}
'''+marker)
    raw=raw.replace('save("body-complete.private",','save("observations.private","count="+databaseScope.observations()+"\\nmaxGapNanos="+databaseScope.maxGapNanos()+"\\nmaxGapBoundNanos=30000000000\\n");save("body-complete.private",')
    return raw


def helper():
    raw=bind(previous_helper());tree=ast.parse(raw);lines=raw.splitlines(keepends=True)
    for node in reversed(tree.body):
        if isinstance(node,ast.FunctionDef)and node.name=='stop_one':del lines[node.lineno-1:node.end_lineno]
    result=''.join(lines);ast.parse(result)
    assert "'stop'"not in result and 'stop_one'not in result
    return result
