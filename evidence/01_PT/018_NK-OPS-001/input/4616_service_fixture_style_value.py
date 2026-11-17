"""Reversible original fixture syntax plus a new independently specified immutable HTTP response value contract."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';prefix='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/';names=['MorningServiceReadinessTest.java','RootStartupContextTest.java'];old={name:(r/prefix/name).read_text() for name in names};out=b/'evidence/PG37150-service-fixture-before-v1';assert not out.exists();out.mkdir()
for name,s in old.items():(out/(name+'.before.txt')).write_text(s)
edits=[('String status = STATUS;','String statusText = STATUS;'),('String command =','String commandValue ='),('int sockets;','int socketReads;'),(' : status)',' : statusText)'),('null : command.getBytes','null : commandValue.getBytes'),('if (++guards == failGuard)','guards++;\n      if (guards == failGuard)'),('if (++requests == failIo)','requests++;\n      if (requests == failIo)'),('return nullSockets ? null : (++sockets == 1 ? before : after);','if (nullSockets) return null;\n      socketReads++;\n      return socketReads == 1 ? before : after;')]
s=old[names[0]]
for a,z in edits:assert a in s;s=s.replace(a,z)
s=re.sub(r'\bf\.(status|command|sockets)\b(?!\s*\()',lambda m:'f.'+dict(status='statusText',command='commandValue',sockets='socketReads')[m[1]],s)
inverse=re.sub(r'\bf\.(statusText|commandValue|socketReads)\b',lambda m:'f.'+dict(statusText='status',commandValue='command',socketReads='sockets')[m[1]],s)
for a,z in reversed(edits):inverse=inverse.replace(z,a)
assert inverse==old[names[0]]
root=old[names[1]];redits=[('final class RootStartupContextTest {','final class RootStartupContextTest {\n  private static final int FIRST_FIXTURE_SLOT = 1;\n  private static final int SECOND_FIXTURE_SLOT = 2;\n  private static final int THIRD_FIXTURE_SLOT = 3;\n  private static final int NOT_DONE_FIXTURE = 1;\n  private static final int NONZERO_EXIT_FIXTURE = 2;\n  private static final int INTERRUPTED_WAIT_FIXTURE = 3;'),('long pid = 42;','long processId = 42;'),('String boot = BOOT;','String bootValue = BOOT;'),('unit = RootStartupContextTest.unit(','unitValues = RootStartupContextTest.unit('),('return pid;','return processId;'),('return bytes(boot);','return bytes(bootValue);'),('assertEquals(pid, p);','assertEquals(processId, p);'),('unit.replace(INV, "2".repeat(32)) : unit','unitValues.replace(INV, "2".repeat(32)) : unitValues')]
for var in ['at','position']:
 for i,constant in [(1,'FIRST_FIXTURE_SLOT'),(2,'SECOND_FIXTURE_SLOT'),(3,'THIRD_FIXTURE_SLOT')]:redits.append((var+' == '+str(i),var+' == '+constant))
for i,constant in [(1,'NOT_DONE_FIXTURE'),(2,'NONZERO_EXIT_FIXTURE'),(3,'INTERRUPTED_WAIT_FIXTURE')]:redits.append(('bad == '+str(i),'bad == '+constant))
for a,z in redits:assert a in root;root=root.replace(a,z)
root=re.sub(r'\b(f|max|unavailable)\.(pid|boot|unit)\b(?!\s*\()',lambda m:m[1]+'.'+dict(pid='processId',boot='bootValue',unit='unitValues')[m[2]],root)
inverse=re.sub(r'\b(f|max|unavailable)\.(processId|bootValue|unitValues)\b',lambda m:m[1]+'.'+dict(processId='pid',bootValue='boot',unitValues='unit')[m[2]],root)
for a,z in reversed(redits):inverse=inverse.replace(z,a)
assert inverse==old[names[1]]
body='{"status":"UP"}';h=0
for c in body:h=(31*h+ord(c))&0xffffffff
signed=lambda n:n if n<2**31 else n-2**32
recordhash=signed((31*200+h)&0xffffffff)
method='''
  /** READYVALUE001: literal independent record identity, never a live HTTP response. */
  @Test
  void readyValue001ResponseRetainsBothIndependentValueComponents() {
    var first = new MorningServiceReadiness.Response(200, "{\\"status\\":\\"UP\\"}");
    var same = new MorningServiceReadiness.Response(200, "{\\"status\\":\\"UP\\"}");
    assertEquals(200, first.status());
    assertEquals("{\\"status\\":\\"UP\\"}", first.body());
    assertTrue(first.equals(first));
    assertTrue(first.equals(same));
    assertFalse(first.equals(null));
    assertFalse(first.equals(new Object()));
    assertFalse(first.equals(new MorningServiceReadiness.Response(201, "{\\"status\\":\\"UP\\"}")));
    assertFalse(first.equals(new MorningServiceReadiness.Response(200, "{\\"status\\":\\"DOWN\\"}")));
    assertEquals(HASH_LITERAL, first.hashCode());
    assertEquals("Response[status=200, body={\\"status\\":\\"UP\\"}]", first.toString());
  }
'''.replace('HASH_LITERAL',str(recordhash))
assert s.endswith('}\n');withoutnew=s;s=s[:-2]+method+'}\n';assert s.replace(method,'',1)==withoutnew
# Fixed body used four times: a named independent fixture value avoids duplicate-literal noise.
s=s.replace('  private static final String FIXTURE_12345_AFC21EDA', '  private static final String READY_VALUE_UP = "{\\"status\\":\\"UP\\"}";\n  private static final String FIXTURE_12345_AFC21EDA',1)
# Restrict substitution to new method, preserve the eight original methods exactly.
start=s.index('  /** READYVALUE001:');s=s[:start]+s[start:].replace('"{\\"status\\":\\"UP\\"}"','READY_VALUE_UP')
assert len(re.findall(r'@Test\s+void',s))==9
candidate={names[0]:s,names[1]:root};post=b/'evidence/PG37152-service-style-and-value-source-v1';assert not post.exists();post.mkdir()
def signature(text):
 values=[]
 for word,at in lexical(text):
  if word!='LITERAL':values.append(word);continue
  if text.startswith('"""',at):stop=text.index('"""',at+3)+3
  else:
   quote=text[at];stop=at+1
   while text[stop]!=quote:stop+=2 if text[stop]=='\\' else 1
   stop+=1
  values.append(('LITERAL',text[at:stop]))
 return values
for name,value in candidate.items():
 tmp=post/(name+'.unformatted.txt');tmp.write_text(value);cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings',str(tmp)]
 result=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert result.returncode==0 and not result.stderr and signature(value)==signature(result.stdout)
 (r/prefix/name).write_text(result.stdout)
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputHashesBefore={prefix+n:hashlib.sha256(old[n].encode()).hexdigest() for n in names},inputHashesAfter={prefix+n:hashlib.sha256((r/prefix/n).read_bytes()).hexdigest() for n in names},originalEightOraclesInverseExactBeforeFormat=True,wholeRootTestInverseExactBeforeFormat=True,formatLiteralAndTokenSignatureExact=True,originalSelectedTests=8,newSelectedValueContract=1,expectedWholeSelected=9,sharedRootTestsSelected=0,newResponseVector=dict(body=body,status=200,javaStringHashSigned=signed(h),recordHashSigned=recordhash,basis='independent 31-fold UTF16 string hash then31*status+bodyHash; no Product invocation'),sourceMainChanged=False,productTestsExecuted=0,bug='BUG3156',horizontal='YKT2625')
(post/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');(out/'manifest.json').write_text(json.dumps(dict(actualExit=0,sourceHashesBefore=v['inputHashesBefore'],originalWholeSelected=8,rootSharedOnly=True,productTestsExecuted=0),indent=2)+'\n');print(json.dumps(dict(actualExit=0,original8Preserved=True,sharedRootWholePreserved=True,newValue1=True,expected=9,independentHash=recordhash,productTests=0)))
