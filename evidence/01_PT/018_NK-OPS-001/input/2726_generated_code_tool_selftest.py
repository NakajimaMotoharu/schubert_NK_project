"""Independently exercise supplemental byte measurement on owned toy artifacts; never App PT."""
from pathlib import Path
import datetime, hashlib, json, math, subprocess, xml.etree.ElementTree as ET
r=Path.cwd();tc=r.parent/'toolchain';b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1';e=b/'evidence/PG31434-generated-code-tool-selftest-v1';assert not e.exists();e.mkdir();src=w/'toysrc/measurementfixture';src.mkdir(parents=True);classes=w/'toyclasses';classes.mkdir()
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
compile_record=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert compile_record['actualExit']==0
for pin in compile_record['dependencies']+[dict(path=str(r/compile_record['source']['path']),sha256=compile_record['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
java=tc/'jdk-25.0.4/bin/java';javac=java.with_name('javac');agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';cp=':'.join([str(w/'toolclasses'),*[p['path'] for p in compile_record['dependencies']]])
commands=[]
def run(name,cmd,zero=True):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();v=subprocess.run(list(map(str,cmd)),capture_output=True,timeout=60);out=e/(name+'.stdout');err=e/(name+'.stderr');out.write_bytes(v.stdout);err.write_bytes(v.stderr);row=dict(name=name,command=list(map(str,cmd)),startUTC=now,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=v.returncode,expectedZero=zero,stdout=ref(out),stderr=ref(err));commands.append(row);(e/(name+'.json')).open('x').write(json.dumps(row,indent=2)+'\n');assert (v.returncode==0)==zero,(name,v.returncode,v.stderr.decode()[:900]);return v.stdout.decode()
contents={'Point.java':'package measurementfixture; public record Point(int x, int y) {}\n','Tone.java':'package measurementfixture; public enum Tone { ONE, TWO }\n','NoCode.java':'package measurementfixture; public interface NoCode { void unused(); }\n','RunFixture.java':'''package measurementfixture;
public final class RunFixture {
  private RunFixture() {}
  private static void require(boolean value) { if (!value) throw new AssertionError("tool fixture"); }
  public static void main(String[] args) {
    Point point=new Point(7,11); require(point.x()==7); require(Tone.ONE!=null);
    if (args[0].equals("full")) {
      require(point.y()==11); require(point.hashCode()==228);
      require(point.toString().equals("Point[x=7, y=11]"));
      require(point.equals(point));require(point.equals(new Point(7,11)));
      require(!point.equals(new Point(8,11)));require(!point.equals(null));require(!point.equals("other"));
      require(Tone.values().length==2);require(Tone.values()[0]==Tone.ONE);require(Tone.values()[1]==Tone.TWO);
      require(Tone.valueOf("ONE")==Tone.ONE);require(Tone.valueOf("TWO")==Tone.TWO);
    }
  }
}\n'''}
for name,text in contents.items():(src/name).open('x').write(text);(e/(name+'.txt')).open('x').write(text)
run('compile-fixture',[javac,'-Xlint:all','-Werror','--release','25','-g','-d',classes,*[src/n for n in contents]])
targets=[classes/'measurementfixture'/n for n in ['Point.class','Tone.class','NoCode.class']];before={str(p):sha(p) for p in targets}
for mode in ['full','partial']:
 run('execute-fixture-'+mode,[java,f'-javaagent:{agent}=destfile={w}/{mode}.exec,append=false,output=file,sessionid=TOOL-31434-{mode.upper()},dumponexit=true','-cp',classes,'measurementfixture.RunFixture',mode])
 full=w/'full.exec';partial=w/'partial.exec'
def parse(text):
 values={};methods=[]
 for line in text.splitlines():
  fields=line.split('\t')
  if fields[0]=='CLASS':
   assert len(fields)==12,fields
   name=fields[1];assert name not in values;values[name]=dict(id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={})
   counter_start=6;target=values[name]
  else:
   assert fields[0]=='METHOD' and len(fields)==11,fields
   target=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(target);counter_start=5
  for item in fields[counter_start:]:
   key,miss,covered=item.split(':');target['counters'][key]=dict(missed=int(miss),covered=int(covered))
 return dict(classes=values,methods=methods)
def measure(name,execpath,paths=targets,zero=True):
 text=run(name,[java,'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',execpath,*paths],zero)
 return parse(text) if zero else None
all_=measure('measure-full',full);some=measure('measure-partial',partial);checks=[]
def check(identity,condition,detail):
 assert condition,(identity,detail);checks.append(dict(testId=identity,result='PASS_TOOL_ONLY',detail=detail))
def total(value,kind,field):return sum(c['counters'][kind][field] for c in value['classes'].values())
check('TOOL-CODEMEASURE001',total(all_,'METHOD','covered')==11 and total(all_,'METHOD','missed')==0 and total(all_,'BRANCH','missed')==0 and total(all_,'BRANCH','covered')==0,dict(expectedRawCodeMethods=11,expectedRawBranches=0,actual=all_))
check('TOOL-CODEMEASURE002',total(some,'METHOD','covered')==5 and total(some,'METHOD','missed')==6 and total(some,'INSTRUCTION','missed')>0,dict(expectedCoveredMethods=5,expectedMissedMethods=6,actual=some))
no=all_['classes']['measurementfixture/NoCode'];check('TOOL-CODEMEASURE003',not no['dataPresent'] and no['probes']==0 and all(sum(v.values())==0 for v in no['counters'].values()),dict(naturalNoCodeNotExecutedOrClaimedAsCovered=no))
# Bit-at-a-time CRC64/ISO polynomial, independent of JaCoCo's table lookup. Java25 major69 needs no Java9 normalization.
def crc64(blob):
 assert int.from_bytes(blob[6:8],'big')==69
 value=0
 for byte in blob:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
crc={p.stem:crc64(p.read_bytes()) for p in targets};check('TOOL-CODEMEASURE004',all(all_['classes']['measurementfixture/'+name]['id']==value for name,value in crc.items()),dict(independentBitwiseCrc=crc))
empty=w/'empty.exec';empty.open('xb').close();missing=measure('measure-missing-execution',empty);check('TOOL-CODEMEASURE005',total(missing,'METHOD','missed')==11 and total(missing,'METHOD','covered')==0 and total(missing,'CLASS','covered')==0,dict(actual=missing,missingNeverPasses=True))
mismatch=w/'mismatch/measurementfixture';mismatch.mkdir(parents=True);wrong=mismatch/'Point.java';wrong.write_text('package measurementfixture; public record Point(long x, int y) {}\n');wrongclasses=w/'mismatchclasses';wrongclasses.mkdir();run('compile-mismatch',[javac,'--release','25','-g','-d',wrongclasses,wrong]);measure('reject-class-crc-mismatch',full,[wrongclasses/'measurementfixture/Point.class'],False);check('TOOL-CODEMEASURE006',True,dict(expectedNonzero='same class name/different CRC',actualCommand='reject-class-crc-mismatch'))
blob=full.read_bytes();name=b'measurementfixture/Point';assert blob.count(name)==1;renamed=w/'renamed.exec';renamed.write_bytes(blob.replace(name,b'measurementfixture/Poins',1));measure('reject-exec-name-mismatch',renamed,[targets[0]],False);check('TOOL-CODEMEASURE007',True,dict(expectedNonzero='same CRC/different name',actualCommand='reject-exec-name-mismatch'))
# Independent compact-exec parser only locates the toy Point probe length; never edits a product exec.
def locate(data,wanted):
 position=0
 while position<len(data):
  block=data[position];position+=1
  if block==1:position+=4
  elif block==0x10:
   size=int.from_bytes(data[position:position+2],'big');position+=2+size+16
  elif block==0x11:
   position+=8;size=int.from_bytes(data[position:position+2],'big');position+=2;current=data[position:position+size];position+=size;start=position;count=0;shift=0
   while True:
    byte=data[position];position+=1;count|=(byte&127)<<shift;shift+=7
    if not byte&128:break
   end=position+math.ceil(count/8)
   if current==wanted:return start,position,end,count
   position=end
  else:raise AssertionError(('unrecognized toy exec block',block,position))
 raise AssertionError('toy class absent')
start,payload,end,count=locate(blob,name);assert count<126 and payload==start+1
extra=(count+1+7)//8-(count+7)//8;bad=w/'wrong-probes.exec';bad.write_bytes(blob[:start]+bytes([count+1])+blob[payload:end]+b'\0'*extra+blob[end:]);measure('reject-probe-length-mismatch',bad,[targets[0]],False);check('TOOL-CODEMEASURE008',True,dict(expectedNonzero='probe count differs',oldProbes=count,newProbes=count+1))
badmagic=w/'badmagic.exec';badmagic.write_bytes(b'\x01\x00\x00\x00\x00');measure('reject-invalid-exec',badmagic,[targets[0]],False);check('TOOL-CODEMEASURE009',True,dict(expectedNonzero='invalid exec magic'))
invalid=w/'invalid.class';invalid.write_bytes(b'not-a-class');measure('reject-invalid-class',full,[invalid],False);check('TOOL-CODEMEASURE010',True,dict(expectedNonzero='invalid class bytes'))
run('reject-missing-arguments',[java,'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',full],False);check('TOOL-CODEMEASURE011',True,dict(expectedNonzero='no explicit class list'))
xml=e/'default-toy.xml';run('reference-default-report',[java,'-jar',cli,'report',full,*sum([['--classfiles',p] for p in targets],[]),'--xml',xml]);root=ET.parse(xml).getroot();default={c.attrib['type']:dict(missed=int(c.attrib['missed']),covered=int(c.attrib['covered'])) for c in root.findall('counter')};check('TOOL-CODEMEASURE012',default['METHOD']==dict(missed=0,covered=2) and before=={str(p):sha(p) for p in targets} and sha(full)==hashlib.sha256(blob).hexdigest(),dict(expectedDefaultMethods=2,actualDefault=default,rawMethods=11,allOriginalClassAndExecBytesUnchanged=True,defaultFilterUnchanged=True))
assert len(checks)==12
(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolTests=12,tests=checks,commands=commands,source=ref(r/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'),compile=ref(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json'),fixtureClassHashes=before,originalExecSha256=sha(full),agent=dict(path=str(agent),sha256=sha(agent)),referenceCli=dict(path=str(cli),sha256=sha(cli)),applicationTestsExecuted=0,applicationAcceptance=0,actualDbNativeRootHeldClassActions=0,formalUpdated=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolTests=12,newAppTests=0,defaultMethods=2,unfilteredMethods=11,partialMissed=6)))
