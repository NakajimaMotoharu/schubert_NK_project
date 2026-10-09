"""SSC239 new-only read-only host/VM comparison. No deployment, DB, start/stop or permit."""
import base64
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

T = Path(__file__).resolve().parents[4]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
JAVA = r'''
package dev.codex.schubert.nk.batch.platform;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;
public final class Pg824ManagerComparison {
  static final String FULL="Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup";
  static final String DEADLINE="Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic";
  static Map<String,String> fields(byte[] raw) {
    var result=new TreeMap<String,String>();
    for(String row:new String(raw,StandardCharsets.US_ASCII).split("\n")) {
      int split=row.indexOf('=');
      if(split<1||result.put(row.substring(0,split),row.substring(split+1))!=null)
        throw new AssertionError("literal property boundary");
    }
    return result;
  }
  static byte[] reference(RootStartupContext.Service service,String fields)throws Exception {
    var p=new ProcessBuilder("/usr/bin/systemctl","--system","--no-pager","--no-ask-password",
      "show","--property="+fields,service.unit()).start();
    p.getOutputStream().close();
    try(var input=p.getInputStream();var error=p.getErrorStream()) {
      if(!p.waitFor(5,TimeUnit.SECONDS)||p.exitValue()!=0)throw new AssertionError("reference not normal");
      byte[] value=input.readNBytes(4097);
      if(value.length>4096||error.read()!=-1)throw new AssertionError("reference boundary");
      return value;
    }
  }
  static long descriptors()throws Exception {
    try(var values=Files.list(Path.of("/proc/self/fd"))) {return values.count();}
  }
  public static void main(String[] args)throws Exception {
    var query=LinuxSystemdQuery.create();
    query.read(RootStartupContext.Service.API,FULL); // Warm immutable ABI/JAR handles, not reply cache.
    reference(RootStartupContext.Service.API,FULL);
    long before=descriptors(), children=ProcessHandle.current().descendants().count();
    var nativeTimes=new ArrayList<Long>();var referenceTimes=new ArrayList<Long>();
    int comparisons=0;
    for(int round=0;round<4;round++)for(var service:RootStartupContext.Service.values())
      for(String projection:List.of(FULL,DEADLINE)) {
        long started=System.nanoTime();var first=fields(reference(service,projection));
        referenceTimes.add(System.nanoTime()-started);
        started=System.nanoTime();var actual=fields(query.read(service,projection));
        long elapsed=System.nanoTime()-started;nativeTimes.add(elapsed);
        if(elapsed>=5000000000L)throw new AssertionError("whole query deadline");
        var second=fields(reference(service,projection));
        if(!first.equals(second)||!first.equals(actual))throw new AssertionError("independent literal map mismatch "+service+" "+projection);
        if(!actual.get("Id").equals(service.unit())||actual.size()!=projection.split(",").length)
          throw new AssertionError("fixed projection not complete");
        comparisons++;
      }
    long after=descriptors();
    if(before!=after||children!=0||ProcessHandle.current().descendants().count()!=0)
      throw new AssertionError("owned descriptor/child postcondition");
    Collections.sort(nativeTimes);Collections.sort(referenceTimes);
    System.out.println("{\"actualExit\":0,\"comparisons\":"+comparisons+
      ",\"nativeQueries\":"+(comparisons+1)+",\"referenceCommands\":"+(2*comparisons+1)+
      ",\"nativeMedianNanoseconds\":"+nativeTimes.get(nativeTimes.size()/2)+
      ",\"nativeMaximumNanoseconds\":"+nativeTimes.getLast()+
      ",\"referenceMedianNanoseconds\":"+referenceTimes.get(referenceTimes.size()/2)+
      ",\"fdBefore\":"+before+",\"fdAfter\":"+after+
      ",\"childBeforeAfter0\":true,\"serviceActions0\":true,\"formalAccepted\":false}");
  }
}
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selected', required=True, type=int)
    parser.add_argument('--run', required=True, type=int)
    args = parser.parse_args()
    assert args.selected >= 825 and args.run >= 824 and args.selected != args.run
    label = 'pg' + str(args.run) + '-manager-native-v1'
    os.umask(0o077)
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T)
    selected = W / ('pg'+str(args.selected)+'-manager-selected-v1')
    run = json.loads((selected / 'run.safe.json').read_text())
    assert (selected / 'exit').read_text() == '0\n' and run['actualExit'] == 0
    batch = selected / 'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    assert hashlib.sha256(batch.read_bytes()).hexdigest() == run['files']['batch/' + batch.name]
    root = W / label; root.mkdir(mode=0o700)
    source = root / 'Pg824ManagerComparison.java'; source.write_text(JAVA)
    classes = root / 'classes'; classes.mkdir(mode=0o700)
    libs = W / 'pg796-release-v1/operations/lib'
    annotations = Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp = str(batch) + ':' + str(libs / '*') + ':' + ':'.join(str(annotations / p) for p in (
        'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
        'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'))
    jdk = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/'
    with (root / 'compile.private.log').open('xb') as out:
        compiled = subprocess.run([jdk+'javac', '-Xlint:all', '-Werror', '-cp', cp, '-d', str(classes), str(source)], stdout=out, stderr=out)
    (root / 'compile.exit').write_text(str(compiled.returncode)+'\n')
    if compiled.returncode: raise SystemExit(compiled.returncode)
    with (root / 'host.private.log').open('xb') as out:
        host = subprocess.run([jdk+'java', '--enable-native-access=ALL-UNNAMED', '-cp', str(classes)+':'+cp,
                               'dev.codex.schubert.nk.batch.platform.Pg824ManagerComparison'], stdout=out, stderr=out, timeout=300)
    (root / 'host.exit').write_text(str(host.returncode)+'\n')
    if host.returncode: raise SystemExit(host.returncode)
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as archive:
        archive.add(batch, arcname='batch.jar')
        archive.add(classes, arcname='classes')
    encoded = base64.b64encode(stream.getvalue()).decode('ascii')
    payload = r'''
import pathlib,subprocess,json,os,base64,tarfile,io,hashlib
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796')
units=('caddy','schubert-nk-api','schubert-nk-web','schubert-nk-cleanup','schubert-nk-inbox-inspector','schubert-nk-expiry-cleanup','schubert-nk-backup','artemis','schubert-nk-morning-controller','schubert-nk-bootstrap-admin')
def units_now():
 result={}
 for unit in units:
  raw=subprocess.check_output(['/usr/bin/systemctl','show',unit+'.service','--property=MainPID,ControlPID,Job,ActiveState,SubState,InvocationID,ControlGroup'],timeout=5)
  value=dict(row.split('=',1)for row in raw.decode().splitlines())
  assert value['MainPID']==value['ControlPID']=='0'and not value['Job']and value['ActiveState']in('inactive','failed')
  result[unit]=raw
 return result
before=units_now();root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg824-manager-native-v1');root.mkdir(mode=0o700)
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(ENCODED)),mode='r:gz')as archive:archive.extractall(root,filter='data')
assert hashlib.sha256((root/'batch.jar').read_bytes()).hexdigest()==EXPECTED
command=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',str(root/'classes')+':'+str(root/'batch.jar')+':/opt/schubert-nk/releases/0.1.0-PG796/operations/lib/*','dev.codex.schubert.nk.batch.platform.Pg824ManagerComparison']
with(root/'native.private.log').open('xb')as out:r=subprocess.run(command,stdout=out,stderr=out,timeout=300);out.flush();os.fsync(out.fileno())
(root/'native.exit').write_text(str(r.returncode)+'\n')
assert units_now()==before
if r.returncode:print(json.dumps({'actualExit':r.returncode,'privateLogSha256':hashlib.sha256((root/'native.private.log').read_bytes()).hexdigest()}));raise SystemExit(r.returncode)
value=json.loads((root/'native.private.log').read_text());value.update(allTenStoppedUnchanged=True,candidateDeployed=False,privateLogSha256=hashlib.sha256((root/'native.private.log').read_bytes()).hexdigest())
print(json.dumps(value))
'''
    payload = payload.replace('pg824-manager-native-v1', label)
    payload = 'ENCODED='+repr(encoded)+'\nEXPECTED='+repr(hashlib.sha256(batch.read_bytes()).hexdigest())+'\n'+payload
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes', '-oStrictHostKeyChecking=yes',
           '-oUserKnownHostsFile='+str(P/'known_hosts'), '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    with (root / 'transport.private.stderr').open('xb') as out:
        result = subprocess.run(ssh, input=payload.encode(), stdout=subprocess.PIPE, stderr=out, timeout=360)
    (root / 'native.exit').write_text(str(result.returncode)+'\n')
    if result.returncode:
        print(json.dumps({'actualExit':result.returncode,'phase':'NATIVE','privateOutputSha256':hashlib.sha256(result.stdout).hexdigest()}))
        raise SystemExit(result.returncode)
    value = {'actualExit':0,'run':label,'selectedRun':args.selected,'source':run['source'],'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
             'host':json.loads((root/'host.private.log').read_text()),'vm':json.loads(result.stdout),
             'batchJarSha256':hashlib.sha256(batch.read_bytes()).hexdigest(),'helperSha256':hashlib.sha256(JAVA.encode()).hexdigest(),
             'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidateDeployed':False,'formalAccepted':False,'productionPTAdded':0}
    (root/'result.safe.json').write_text(json.dumps(value,sort_keys=True))
    print(json.dumps(value))

if __name__ == '__main__': main()
