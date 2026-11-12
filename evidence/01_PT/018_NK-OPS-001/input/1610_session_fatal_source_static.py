"""Four existing module-local calls only, no Main compilation/runtime/held payload."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27380-session-fatal4-source-static-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists();paths=[];inverse={};base='de781be6be4b2c515ee067847f2efc208dc3bf6f'
patterns={'SessionAttributeCodec.java':[('''        | DateTimeException failure) {
      throw new SessionAttributeException();''','''        | DateTimeException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionAttributeException();''')], 'SessionPayloadCodec.java':[('''      } catch (GeneralSecurityException | ProviderException failure) {
        throw new SessionPayloadException''','''      } catch (GeneralSecurityException | ProviderException failure) {
        SessionStoreException.preserveFatal(failure);
        throw new SessionPayloadException'''),('''      } catch (GeneralSecurityException | ProviderException | SessionAttributeException failure) {
        throw invalid();''','''      } catch (GeneralSecurityException | ProviderException | SessionAttributeException failure) {
        SessionStoreException.preserveFatal(failure);
        throw invalid();''')], 'EncryptedWebSessionRepository.java':[('''    } catch (GeneralSecurityException failure) {
      throw new SessionStoreException();''','''    } catch (GeneralSecurityException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();''')]}
for name,changes in patterns.items():
 p=R/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session'/name;old=subprocess.check_output(['git','show',base+':'+str(p.relative_to(R))],text=True);assert p.read_text()==old;s=old
 for a,z in changes:assert s.count(a)==1;s=s.replace(a,z)
 check=s
 for a,z in reversed(changes):assert check.count(z)==1;check=check.replace(z,a)
 assert check==old;p.write_text(s);paths.append(p);inverse[str(p.relative_to(R))]=dict(beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),callCount=len(changes),exactInverse=True)
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*map(str,paths)],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*map(str,paths)],R));passed=all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error');v=dict(actualExit=0 if passed else 1,sourceBefore=base,inputHashes={str(p.relative_to(R)):sha(p) for p in paths},stages=stages,originalSourceInverseExact=True,fourExistingModuleLocalFatalCallsOnly=True,inverse=inverse,wireCryptoSchemaKeyHashTransactionNullAndCleanupUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2704',horizontal='YKT-2359_41_LIMITED_SITES_RUNTIME_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],stageExits={k:x['actualExit'] for k,x in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
