from pathlib import Path
import datetime,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));c=ld(B/'input/2255_native_source_start.json');state=ld(R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json');assert state['ordinaryActiveGroup']==c['groupId'] and state['ordinaryGroupNotYetClosed'];changes=[]
for name in c['implementationArtifactPaths']:
 p=R/name;old=p.read_text();assert old==subprocess.check_output(['git','show',c['source']+':'+name],text=True);new=old;replacements=[]
 if p.stem=='FixedNativeCoverageCheckpoint':
  a='import dev.codex.schubert.nk.storage.ServiceConfigFiles;\n';b=a+'import dev.codex.schubert.nk.storage.StorageIoException;\n';replacements.append((a,b,1))
  a='      } catch (ReflectiveOperationException | java.net.URISyntaxException | IOException failure) {\n';replacements.append((a,a+'        StorageIoException.preserveFatal(failure);\n',1))
  a='      } catch (ReflectiveOperationException failure) {\n';replacements.append((a,a+'        StorageIoException.preserveFatal(failure);\n',2))
 else:
  assert p.stem=='NativeCoveragePrivateFile'
  a='''              try (var channel = channel(channels.write(held))) {
                var buffer = ByteBuffer.wrap(bytes);
                while (buffer.hasRemaining()) require(channel.write(buffer) > 0);
                channel.force(true);
                require(channel.size() == bytes.length);
'''
  b='''              try (var channel = channel(channels.write(held))) {
                require(channel.position() == 0);
                var buffer = ByteBuffer.wrap(bytes);
                while (buffer.hasRemaining()) {
                  int positionBefore = buffer.position();
                  int written = channel.write(buffer);
                  require(
                      written > 0
                          && written == buffer.position() - positionBefore
                          && channel.position() == buffer.position());
                }
                channel.force(true);
                require(channel.size() == bytes.length && channel.position() == bytes.length);
''';replacements.append((a,b,1))
  a='''      require(channel.size() == size);
      var buffer = ByteBuffer.allocate(8192);
''';b='''      require(channel.size() == size && channel.position() == 0);
      var buffer = ByteBuffer.allocate(8192);
''';replacements.append((a,b,1))
  a='''        if (n < 0) break;
        // PG-D804/2476: retain the original short-circuit update and one require call.
        boolean withinSize = n > 0;
        if (withinSize) {
          count += n;
          withinSize = count <= size;
        }
        require(withinSize);
''';b='''        if (n < 0) {
          require(n == -1 && buffer.position() == 0 && channel.position() == count);
          break;
        }
        require(n > 0 && n == buffer.position() && n <= size - count);
        count += n;
        require(channel.position() == count);
''';replacements.append((a,b,1))
 for a,b,n in replacements:assert new.count(a)==n;new=new.replace(a,b)
 inv=new
 for a,b,n in reversed(replacements):assert inv.count(b)==n;inv=inv.replace(b,a)
 assert inv==old;changes.append((p,old,new,replacements))
O=B/'evidence/PG29112-native-two-main-source-static-v1';assert not O.exists();O.mkdir();steps.SLOT=O;stages={};proof=[]
for p,old,new,replacements in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(new);label='format-'+p.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages[label]['actualExit']==0
 inv=p.read_text()
 for a,b,n in reversed(replacements):assert inv.count(b)==n;inv=inv.replace(b,a)
 assert inv==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),originalByteInverseExactAfterFormat=True))
paths=c['implementationArtifactPaths'];listing=O/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in paths));stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(R/p) for p in paths]],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),'@'+str(listing)],R);assert all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
vectors=[dict(id='CHANNEL-SPEC-'+str(i),input=x,expected='REJECT_FIXED_NON_SUCCESS',executionStatus='SPEC_ONLY_NOT_RUN') for i,x in enumerate(['initial read position nonzero','positive read count with buffer position0','positive read count different from buffer.position','read count exceeds declared remaining size','channel position differs from accumulated count','EOF -2','EOF -1 with data in buffer','EOF -1 with mismatched channel position','initial write position nonzero','positive write count with unchanged buffer','write count differs from buffer delta','write channel position differs from buffer.position','force changes final position'],1)]
(O/'independent-negative-vector-spec.json').write_text(json.dumps(dict(status='SPEC_ONLY_NOT_PRODUCT_PT',vectors=vectors,normalExpected='Valid FileChannel partial reads/writes advance count-buffer-channel equally, initial0, EOF-1 only, force preserves endposition, same original bytes/SHA256 and all resource closes. Positive implementation execution notperformed.'),indent=2)+'\n')
(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={p:sha(R/p) for p in paths},originalSourceInverseExact=True,proof=proof,stages=stages,knownCatalogFatalGuards=3,strictReadWriteChannelProtocol=True,normalPinAttemptNewonlyRootIdentityMetadataHashAndOwnedClosePriorityUnchanged=True,independentNegativeSpec=ref(O/'independent-negative-vector-spec.json'),bugs=['BUG2803','BUG2804'],productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',actualAgentNativeCaptureRootPrivateFdFileVmActions=0,verifier=ref(Path(__file__).resolve())),ensure_ascii=False,indent=2)+'\n');print('twoMain originalsource inverse/GJF-CS0; 3catalog guards/channel protocol; spec13 not ProductPT')
