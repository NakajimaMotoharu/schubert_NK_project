"""BUG2699 source-only guard, exact inverse and configured style; no compilation/runtime."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27192-question-collision-source-static-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists()
p=R/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java'
old=subprocess.check_output(['git','show','db9b88773a05ba7beaa7798bb6c2a571c55c734d:'+str(p.relative_to(R))],text=True);assert p.read_text()==old
before='''      } catch (SQLException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        if (!(failure instanceof PSQLException postgres) || !"23505".equals(failure.getSQLState()))'''
after='''      } catch (SQLException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        // BUG2699/YKT2373: a failed close cannot be recovered as a clean receipt collision.
        if (failure.getSuppressed().length != 0) throw failure;
        if (!(failure instanceof PSQLException postgres) || !"23505".equals(failure.getSQLState()))'''
assert old.count(before)==1;s=old.replace(before,after);assert s.replace(after,before)==old;p.write_text(s)
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p)],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),str(p)],R))
passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
v=dict(actualExit=0 if passed else 1,sourceBefore='db9b88773a05ba7beaa7798bb6c2a571c55c734d',inputHashes={str(p.relative_to(R)):sha(p)},stages=stages,originalSourceInverseExact=True,fatalBeforeSuppressedBeforeCollision=True,cleanCollisionConstraintAndBudgetUnchanged=True,originalSqlAndTransactionOwnershipUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_HOLD_NOT_PASS',bug='BUG-2699',horizontal='YKT-2373_RUNTIME_PENDING_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],stageExits={k:x['actualExit'] for k,x in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
