from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));c=ld(B/'input/2218_signature9_pgpt_start.json');state=ld(R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json');assert state['ordinaryActiveGroup']==c['groupId'] and state['ordinaryGroupNotYetClosed'];assert '## BUG-2795' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();p=R/c['implementationArtifactPaths'][0];old=p.read_text();assert old==subprocess.check_output(['git','show',c['source']+':'+str(p.relative_to(R))],text=True);imp='import dev.codex.schubert.nk.storage.StorageIoException;\n';a='    } catch (GeneralSecurityException invalid) {\n';b=a+'      StorageIoException.preserveFatal(invalid);\n';assert old.count(a)==1 and imp not in old;new=old.replace(a,b).replace('import java.io.IOException;\n',imp+'import java.io.IOException;\n',1);assert new.replace(b,a).replace(imp,'')==old
T=R/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifierTest.java';oldT=T.read_text();assert oldT==subprocess.check_output(['git','show',c['source']+':'+str(T.relative_to(R))],text=True);assert len(re.findall(r'@Test\b',oldT))==8;assert not re.search(r'KeyPairGenerator|\.sign\(|PrivateKey|Files\.|ProcessBuilder|RootStartup|MaintenanceOwner',oldT)
addition='''  /** SIGN009/BUG2793: independent public provider fault graphs, never a private signing key. */
  @Test
  void sign009KnownProviderFatalGraphsKeepIdentityAndEraseAllOwnedClones() {
    for (int graph = 0; graph < 3; graph++) {
      var marker = new AssertionError("public fatal verification marker");
      var failure = new GeneralSecurityException("public provider fault");
      if (graph == 0) failure.initCause(marker);
      else if (graph == 1) failure.addSuppressed(marker);
      else {
        var cycle = new IllegalStateException("public cyclic provider fault");
        failure.initCause(cycle);
        cycle.initCause(failure);
        cycle.addSuppressed(marker);
      }
      byte[] key = hex(PREFIX + PUBLIC1);
      byte[] message = hex("72");
      byte[] signature = hex(SIGN2);
      var retained = new AtomicReference<List<byte[]>>();
      int[] calls = {0};
      var subject =
          new ReleaseSignatureVerifier(
              key,
              (k, m, s) -> {
                calls[0]++;
                assertTrue(k != key && m != message && s != signature);
                assertArrayEquals(hex(PREFIX + PUBLIC1), k);
                assertArrayEquals(hex("72"), m);
                assertArrayEquals(hex(SIGN2), s);
                retained.set(List.of(k, m, s));
                throw failure;
              });
      assertSame(marker, assertThrows(AssertionError.class, () -> subject.verify(message, signature)));
      assertEquals(1, calls[0]);
      assertEquals(0, marker.getSuppressed().length);
      assertEquals(3, retained.get().size());
      for (byte[] owned : retained.get()) assertArrayEquals(new byte[owned.length], owned);
      assertArrayEquals(hex(PREFIX + PUBLIC1), key);
      assertArrayEquals(hex("72"), message);
      assertArrayEquals(hex(SIGN2), signature);
    }
  }

''';anchor='  @Test\n  void sign008ConcurrentNativeProviderAndMalformedPoint()';assert oldT.count(anchor)==1;newT=oldT.replace(anchor,addition+anchor);aT='    try (var executor = Executors.newFixedThreadPool(4)) {\n';bT='    var executor = Executors.newFixedThreadPool(4);\n    try {\n';assert newT.count(aT)==1;newT=newT.replace(aT,bT);a2='      for (var future : futures) assertTrue(future.get(5, TimeUnit.SECONDS));\n    }\n';b2='      for (var future : futures) assertTrue(future.get(5, TimeUnit.SECONDS));\n    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }\n';assert newT.count(a2)==1;newT=newT.replace(a2,b2);assert newT.replace(addition,'').replace(bT,aT).replace(b2,a2)==oldT
O=B/'evidence/PG28912-signature-pg-whole9-source-closure-v1';assert not O.exists();O.mkdir();steps.SLOT=O;stages={}
for file,text in [(p,new),(T,newT)]:
 file.write_text(text);label='format-'+file.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(file)],R);assert stages[label]['actualExit']==0
assert p.read_text().replace(b,a).replace(imp,'')==old
text=T.read_text();start=text.index('  /** SIGN009/BUG2793:');end=text.index(anchor,start);actual=text[start:end];tokens=lambda s:re.findall(r'"(?:[^"\\]|\\.)*"|[A-Za-z0-9_$]+|[^\s]',s);assert tokens(actual)==tokens(addition);assert (text[:start]+text[end:]).replace(bT,aT).replace(b2,a2)==oldT;assert len(re.findall(r'@Test\b',text))==9
listing=O/'sources.txt';listing.write_text(str(p)+'\n'+str(T)+'\n');stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p),str(T)],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);assert all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');storage='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java';value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={str(p.relative_to(R)):sha(p)},mainInputHashes={str(p.relative_to(R)):sha(p),storage:sha(R/storage)},testInputHashes={str(T.relative_to(R)):sha(T)},originalSourceInverseExact=True,originalWhole8InverseExact=True,originalWhole8AssertionsPreserved=True,newIndependentDefinition=1,wholeTestCount=9,independentOracle='PublicRFC8032TEST1/2 only. Newliteral cause/suppressed/cycle3; originalErroridentity/supp0/providercall1/threeclonesnonaliases-allzero, originalpublickey/message/signaturebytesunchanged. NoProductionexpected or private signing.',workerLifecycle='Original4workers/barrier5s/Futureget5s; finallyshutdownNow-await10s asserted',wholeSourceReview='Signature78lines+currentStorage47whole/previousqualifiedsamebyte andoriginal171lineTest all reviewed; noRoot orunknownProducttypes',physicalPredictionCorrection='OriginalstartnextCommand3prediction retained; actual public Signature outer+Crypto+NativeCrypto andStorage+Reason => expected5 before firstcompile/profilefreeze.',stages=stages,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,actualKeySigningRootVmOrBackendActions=0,newAcceptance=0,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print('Main1 guard/sourceinverse andwhole8+new1/finiteworker inverse+GJF-CS0; ProductPT0')
