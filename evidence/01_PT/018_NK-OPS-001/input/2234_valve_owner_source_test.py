from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';root=R/'src/schubert-nk-web/src';p=root/'main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpAdmissionValve.java';t=root/'test/java/dev/codex/schubert/nk/web/bootstrap/WebHttpAdmissionValveTest.java';old=p.read_text();ot=t.read_text();assert len(re.findall(r'@Test\b',ot))==2
changes=[('    void complete() {','    boolean ownedBy(WebHttpAdmission candidate) {\n      return admission == candidate;\n    }\n\n    void complete() {'),('    } else if (!(lease instanceof WebHttpAdmissionValve.Lease)) {','    } else if (!(lease instanceof WebHttpAdmissionValve.Lease owned) || !owned.ownedBy(admission)) {'),('    if (lease instanceof WebHttpAdmissionValve.Lease owned) owned.complete();','    if (lease instanceof WebHttpAdmissionValve.Lease owned && owned.ownedBy(admission))\n      owned.complete();')]
s=old
for a,b in changes:assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)
new='''
  @Test
  void httpLease003ForeignGateCannotDispatchOrCompleteButSameGateAdaptersCan() throws Exception {
    var gateA = new WebHttpAdmission();
    var gateB = new WebHttpAdmission();
    var valveA = new WebHttpAdmissionValve(gateA);
    var valveB = new WebHttpAdmissionValve(gateB);
    var sameGate = new WebHttpAdmissionValve(gateA);
    var callsA = new AtomicInteger();
    var callsB = new AtomicInteger();
    valveA.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request req, Response res) {
            callsA.incrementAndGet();
          }
        });
    valveB.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request req, Response res) {
            callsB.incrementAndGet();
          }
        });
    sameGate.setNext(valveA.getNext());
    var request = new Request(new Connector(), new org.apache.coyote.Request());
    var response = new Response(new org.apache.coyote.Response());
    String attribute = WebHttpAdmissionValve.class.getName() + ".lease";
    gateA.admit();
    gateB.admit();
    valveA.invoke(request, response);
    Object originalLease = request.getAttribute(attribute);
    var rejected = assertThrows(jakarta.servlet.ServletException.class,
        () -> valveB.invoke(request, response));
    assertEquals("Web HTTP lease unavailable", rejected.getMessage());
    assertEquals(1, callsA.get());
    assertEquals(0, callsB.get());
    assertSame(originalLease, request.getAttribute(attribute));
    valveB.log(request, response, 0);
    assertThrows(IOException.class, () -> gateA.drain(Duration.ZERO));
    gateB.drain(Duration.ZERO);
    sameGate.invoke(request, response);
    assertEquals(2, callsA.get());
    assertSame(originalLease, request.getAttribute(attribute));
    assertThrows(IOException.class, () -> gateA.drain(Duration.ZERO));
    sameGate.log(request, response, 0);
    gateA.drain(Duration.ZERO);
    valveA.log(request, response, 0);
    sameGate.log(request, response, 0);
    gateA.drain(Duration.ZERO);
  }
'''
assert ot.endswith('}\n');t.write_text(ot[:-2]+new+'}\n')
subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'-i',str(p),str(t)],check=True)
s=p.read_text();inv=s
# GJF only wraps the new log line, which the replacement already has.
for a,b in reversed(changes):assert inv.count(b)==1;inv=inv.replace(b,a)
assert inv==old
nt=t.read_text();idx=nt.index('  @Test\n  void httpLease003');assert nt[:idx].rstrip()+'\n}\n'==ot.rstrip()+'\n'
main=[p,root/'main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpAdmission.java'];O=B/'evidence/PG28988-valve-owner-source-whole3-closure-v1';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));sdk=B/'evidence/PG28986-tomcat-sdk-constructor-metadata-v1'
(sdk/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),provenance=ref(sdk/'provenance.json'),metadata=[ref(x) for x in sorted(sdk.glob('*.txt'))],qualification='Connector default HTTP/1.1 -> ProtocolHandler exact Http11NioProtocol -> NioEndpoint constructors allocate state only. Endpoint serverSock/poller null; AbstractProtocol binds handler and properties only. LifecycleBase NEW; no init/start/bind/selector-open/poller/startInternal invoked. Connector clinit APR status uses resource lookup only not native init. Coyote Request/Response and Catalina wrappers allocate maps/buffers/metadata. ValveBase only lifecycle fields. Product tests invoke no init/start/network/Root or private files.',productClassMetadataRead=0,actualHttpOrBackendOperations=0),ensure_ascii=False,indent=2)+'\n')
(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalSourceInverseExact=True,originalWhole2InverseExact=True,oldSourceSha256=hashlib.sha256(old.encode()).hexdigest(),oldWholeTestSha256=hashlib.sha256(ot.encode()).hexdigest(),mainInputHashes={str(x.relative_to(R)):sha(x) for x in main},testInputHashes={str(t.relative_to(R)):sha(t)},wholeTestCount=3,newDefinitions=1,sdkConstructorQualification=ref(sdk/'manifest.json'),independentOracle='Foreign gate ServletException exact message, nextB=0/A=1, same original attribute; foreign log leaves A.drain(ZERO) IOException while B drains; same gate adapter dispatch increments A=2 and only its terminal permits A drain; duplicate logs no underflow. No production method generates expected.',productTestsExecuted=0,newAcceptance=0),ensure_ascii=False,indent=2)+'\n');print('BUG2799 Main1 + originalwhole2/new1, oldsource and old2 exact inverse; no ProductPT executed')
