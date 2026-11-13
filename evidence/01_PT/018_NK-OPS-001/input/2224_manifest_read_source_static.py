from pathlib import Path
import datetime,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));c=ld(B/'input/2223_manifest_read_source_start.json');state=ld(R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json');assert state['ordinaryActiveGroup']==c['groupId'] and state['ordinaryGroupNotYetClosed'];p=R/c['implementationArtifactPaths'][0];old=p.read_text();assert old==subprocess.check_output(['git','show',c['source']+':'+str(p.relative_to(R))],text=True);new=old;inverse=[]
def rep(a,b):
 global new
 assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a))
rep('                    require(channel.size() == before.size());\n','                    require(channel.size() == before.size() && channel.position() == 0);\n')
a='''                      if (count < 0) break;
                      require(count > 0);
                      total += count;
                      require(total <= MAX_BYTES);
''';b='''                      if (count < 0) {
                        require(
                            count == -1 && buffer.position() == 0 && channel.position() == total);
                        break;
                      }
                      // The retained file size is already admitted to MAX_BYTES.
                      require(
                          count > 0
                              && count == buffer.position()
                              && count <= before.size() - total);
                      total += count;
                      require(channel.position() == total);
''';rep(a,b);reverse=new
for a,b in reversed(inverse):assert reverse.count(a)==1;reverse=reverse.replace(a,b)
assert reverse==old;O=B/'evidence/PG28942-manifest-read-one-source-static-v1';assert not O.exists();O.mkdir();steps.SLOT=O;(O/'StartupReleaseManifest-before.txt').write_text(old);p.write_text(new);stages={};stages['format']=steps.step('format',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],R);assert stages['format']['actualExit']==0;reverse=p.read_text()
for a,b in reversed(inverse):assert reverse.count(a)==1;reverse=reverse.replace(a,b)
assert reverse==old;stages['format-after']=steps.step('format-after',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p)],R);stages['checkstyle']=steps.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),str(p)],R);assert all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');vectors=[dict(id='MANREAD001',scenario='size2, initialpos0, read2/bufferpos2/channelpos2, thenEOF-1/bufferpos0/channelpos2',expected='continuehashandunchangedexistingallclose/inoderecheck'),dict(id='MANREAD002',scenario='initialposition1',expected='rejectbeforefirstread/ownedchannelclose'),dict(id='MANREAD003',scenario='size2, read2/bufferpos1/channelpos2',expected='rejectcount-versus-bufferbeforehash'),dict(id='MANREAD004',scenario='size2, read1/bufferpos1/channelpos2',expected='rejectchannelpositionbeforedigestupdate'),dict(id='MANREAD005',scenario='size2, read3/bufferpos3/channelpos3',expected='rejectdeclaredsizeoverrunbeforehash'),dict(id='MANREAD006',scenario='size2, read0/bufferpos0/channelpos0',expected='rejectzeroprogressnoinfiniteretry'),dict(id='MANREAD007',scenario='size2 fullyread thenEOF-2/bufferpos0/channelpos2',expected='rejectnoncanonicalEOF'),dict(id='MANREAD008',scenario='size2 fullyread thenEOF-1/bufferpos1/channelpos2',expected='rejectEOFwithbufferadvance'),dict(id='MANREAD009',scenario='size2 fullyread thenEOF-1/bufferpos0/channelpos3',expected='rejectEOFwithchanneldrift'),dict(id='MANREAD010',scenario='size2 read1thenEOF-1 withconsistentpositions',expected='existingexactsizepostconditionrejects; no publishedhash')];v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],inputHashes={str(p.relative_to(R)):sha(p)},originalSourceInverseExact=True,stages=stages,originalNormalIoAndOwnedCloseRootSelectorAuthorityUnchanged=True,declaredSizePrecheckedByExistingCheckedMax1MiB=True,oldTotalMaxAssertionReplacedByStrongerPreincrementRemainingSize=True,independentLiteralPendingVectors=vectors,vectorExecutionStatus='SPEC_ONLY_NOT_PRODUCT_TEST_OR_EXECUTED_PASS',productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG2794',ykt='YKT2399',actualRootNativeVmKeyOrReleaseActions=0,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print('manifest strictread sourceinverse/GJF-CS0; ten independent vectors SPEC_ONLY, ProductPT0')
