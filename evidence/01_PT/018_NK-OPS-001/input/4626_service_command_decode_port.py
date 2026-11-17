"""PG-D363: existing internal Io owns pure conversion, existing ordinary owner always erases bytes."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';before=b/'evidence/PG37176-service-command-cleanup-before-v1';p=json.loads((before/'manifest.json').read_text());main=r/p['mainPath'];test=r/p['testPath'];oldmain=main.read_text();oldtest=test.read_text();assert hashlib.sha256(main.read_bytes()).hexdigest()==p['mainShaBefore'] and hashlib.sha256(test.read_bytes()).hexdigest()==p['testShaBefore']
added='''
    /**
     * Pure command conversion; the caller retains byte ownership and erases on every exit.
     * SS342/343/354, PG-D363, READYDATA001..003: this port grants no process authority.
     */
    default String decodeCommand(byte[] command) throws IOException {
      return new String(command, StandardCharsets.US_ASCII);
    }
'''
anchor='    Response get(String path) throws IOException;';oldline='String text = new String(command, StandardCharsets.US_ASCII);';newline='String text = Objects.requireNonNull(io.decodeCommand(command), "service command text");';assert oldmain.count(anchor)==oldmain.count(oldline)==1
newmain=oldmain.replace(anchor,anchor+'\n'+added).replace(oldline,newline);assert newmain.replace(anchor+'\n'+added,anchor).replace(newline,oldline)==oldmain
newtest=oldtest.replace('import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;','import static org.junit.jupiter.api.Assertions.assertArrayEquals;\nimport static org.junit.jupiter.api.Assertions.assertDoesNotThrow;').replace('import static org.junit.jupiter.api.Assertions.assertThrows;','import static org.junit.jupiter.api.Assertions.assertNotSame;\nimport static org.junit.jupiter.api.Assertions.assertSame;\nimport static org.junit.jupiter.api.Assertions.assertThrows;').replace('import java.util.Arrays;','import java.util.ArrayList;\nimport java.util.Arrays;').replace('static final class Fixture implements MorningServiceReadiness.Io','static class Fixture implements MorningServiceReadiness.Io')
methods='''
  /** READYDATA001: each independent successful sample discards its own command bytes. */
  @Test
  void readyData001DefaultConversionErasesBothIndependentCommandSamples() throws Exception {
    var captured = new ArrayList<byte[]>();
    var fixture = new Fixture() {
      @Override
      public byte[] command() throws IOException {
        byte[] bytes = super.command();
        captured.add(bytes);
        return bytes;
      }
    };
    assertTrue(fixture.observer().ready());
    assertEquals(2, captured.size());
    assertNotSame(captured.get(0), captured.get(1));
    for (byte[] bytes : captured) assertArrayEquals(new byte[bytes.length], bytes);
    assertEquals(8, fixture.requests);
    assertEquals(3, fixture.guards);
  }

  /** READYDATA002: independent checked, runtime and fatal providers retain identity after erase. */
  @Test
  void readyData002DecoderFailureErasesCapturedCommandBeforePropagation() {
    for (Throwable failure : List.of(new IOException("PUBLIC_DECODE"),
        new IllegalStateException("PUBLIC_DECODE"), new AssertionError("PUBLIC_DECODE"))) {
      var captured = new ArrayList<byte[]>();
      var fixture = new Fixture() {
        @Override
        public byte[] command() throws IOException {
          byte[] bytes = super.command();
          captured.add(bytes);
          return bytes;
        }
        @Override
        public String decodeCommand(byte[] bytes) throws IOException {
          assertSame(captured.get(0), bytes);
          if (failure instanceof IOException io) throw io;
          if (failure instanceof RuntimeException runtime) throw runtime;
          throw (Error) failure;
        }
      };
      assertSame(failure, assertThrows(Throwable.class, fixture.observer()::ready));
      assertEquals(1, captured.size());
      assertArrayEquals(new byte[captured.get(0).length], captured.get(0));
      assertEquals(0, fixture.socketReads);
      assertEquals(2, fixture.requests);
    }
  }

  /** READYDATA003: a missing converter result cannot skip owner erase or become ready. */
  @Test
  void readyData003MissingCommandTextFailsAndErasesBeforeAnySocketOrHttp() {
    var captured = new ArrayList<byte[]>();
    var fixture = new Fixture() {
      @Override
      public byte[] command() throws IOException {
        byte[] bytes = super.command();
        captured.add(bytes);
        return bytes;
      }
      @Override
      public String decodeCommand(byte[] bytes) {
        assertSame(captured.get(0), bytes);
        return null;
      }
    };
    var failure = assertThrows(NullPointerException.class, fixture.observer()::ready);
    assertEquals("service command text", failure.getMessage());
    assertEquals(1, captured.size());
    assertArrayEquals(new byte[captured.get(0).length], captured.get(0));
    assertEquals(0, fixture.socketReads);
    assertEquals(2, fixture.requests);
  }
'''
assert newtest.endswith('}\n');newtest=newtest[:-2]+methods+'}\n'
inverse=newtest.replace(methods,'').replace('import static org.junit.jupiter.api.Assertions.assertArrayEquals;\n','').replace('import static org.junit.jupiter.api.Assertions.assertNotSame;\n','').replace('import static org.junit.jupiter.api.Assertions.assertSame;\n','').replace('import java.util.ArrayList;\n','').replace('static class Fixture implements MorningServiceReadiness.Io','static final class Fixture implements MorningServiceReadiness.Io');assert inverse==oldtest and len(re.findall(r'@Test\s+void',newtest))==12
out=b/'evidence/PG37178-service-command-port-source-v1';assert not out.exists();out.mkdir()
def signature(text):
 result=[]
 for word,at in lexical(text):
  if word!='LITERAL':result.append(word);continue
  if text.startswith('"""',at):end=text.index('"""',at+3)+3
  else:
   end=at+1
   while text[end]!=text[at]:end+=2 if text[end]=='\\' else 1
   end+=1
  result.append(('LITERAL',text[at:end]))
 return result
for path,value in [(main,newmain),(test,newtest)]:
 cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',path.name,'-'];start=datetime.datetime.now(datetime.timezone.utc).isoformat();c=subprocess.run(cmd,input=value,text=True,capture_output=True,timeout=120)
 (out/(path.name+'.format.stdout')).write_text(c.stdout);(out/(path.name+'.format.stderr')).write_text(c.stderr);(out/(path.name+'.format.result.json')).write_text(json.dumps(dict(actualExit=c.returncode,command=cmd,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))+'\n');assert c.returncode==0 and not c.stderr and signature(value)==signature(c.stdout);path.write_text(c.stdout)
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainPath=p['mainPath'],mainShaBefore=p['mainShaBefore'],mainShaAfter=hashlib.sha256(main.read_bytes()).hexdigest(),testPath=p['testPath'],testShaBefore=p['testShaBefore'],testShaAfter=hashlib.sha256(test.read_bytes()).hexdigest(),originalMainInverseWholeByteExactBeforeFormat=True,originalNineTestsInverseWholeByteExactBeforeFormat=True,formatAllTokensAndLiteralsExact=True,newSelectedTests=3,expectedWholeSelectedTests=12,defaultConversionUnchanged='new String(command, StandardCharsets.US_ASCII)',publicOuterApiUnchanged=True,ioAddition='package-private existing Io.default decodeCommand; nonnull borrowed input/result, checkedIOException/unchecked propagate',RootOrNativePermissionChanged=False,additionalPricePp=0,originalGroupBasePp=3,originalGroupCapPp=8,mainCompile='NOT_RUN',whole12='NOT_RUN',productTestsExecuted=0,bug='BUG3160',horizontal='YKT2629')
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,original9Preserved=True,expected12=True,mainSourcesChanged=1,productTests=0)))
