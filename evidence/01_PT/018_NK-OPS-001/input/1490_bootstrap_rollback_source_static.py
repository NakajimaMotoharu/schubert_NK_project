"""Bootstrap owned TX source-only inverse and configured style; never compile/invoke Main."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27146-bootstrap-rollback-source-static-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists()
p=R/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain.java';old=subprocess.check_output(['git','show','c29e14a4470daf88727e3c4ea1f9359f1e9d5308:'+str(p.relative_to(R))],text=True);s=p.read_text()
before='''      connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      var metadata = new UserCommandMetadata(UUID.randomUUID(), UUID.randomUUID(), Instant.now());
      var outcome = new BootstrapAdminService().create(connection, username, password, metadata);
      connection.commit();
      return outcome == BootstrapAdminService.Outcome.CREATED ? 0 : 20;'''
after='''      try {
        connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        var metadata = new UserCommandMetadata(UUID.randomUUID(), UUID.randomUUID(), Instant.now());
        var outcome = new BootstrapAdminService().create(connection, username, password, metadata);
        connection.commit();
        return outcome == BootstrapAdminService.Outcome.CREATED ? 0 : 20;
      } catch (SQLException | RuntimeException | Error failure) {
        // BUG2697/YKT2371; SS343 SSC188/SS312: caller owns TX, outer TWR owns physical close.
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollbackFailure) {
          TemporaryInfrastructureException.attachSecondary(failure, rollbackFailure);
        }
        throw failure;
      }'''
imp='import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;\n';assert s.count(imp)==1 and s.count(after)==1 and old.count(before)==1
assert s.replace(imp,'').replace(after,before)==old
a=s.index('  static int createAndCommit(');z=s.index('\n  static void requireActor',a);body=s[a:z]
assert body.index('connection.setAutoCommit(false);')<body.index('      try {')<body.index('connection.setTransactionIsolation(')
assert body.count('connection.rollback();')==body.count('TemporaryInfrastructureException.attachSecondary(')==1
assert body.count('connection.commit();')==1 and 'connection.close(' not in body and "Arrays.fill(password, '\\0');" in body
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p)],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),str(p)],R))
passed=all(x['actualExit']==0 and not x['timedOut'] for x in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
v=dict(actualExit=0 if passed else 1,sourceBefore='c29e14a4470daf88727e3c4ea1f9359f1e9d5308',inputHashes={str(p.relative_to(R)):sha(p)},stages=stages,originalSourceInverseExact=True,ownedTransactionStartsAfterConfirmedManualMode=True,oneRollbackAttempt=True,existingSecondaryGraphPort=True,outerPhysicalResourceOwnershipAndEntryStatusesUnchanged=True,passwordWipeUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,actualHeldClassBinaryReadHashParseInit=False,actualDbCredentialNativeOrUnitOperations=0,coverage=None,nullAway=None,pmd=None,spotBugs=None,ptStatus='NOT_RUN_HOLD_NOT_PASS',bug='BUG-2697',horizontal='YKT-2371_RUNTIME_PENDING_OPEN',formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],stageExits={k:x['actualExit'] for k,x in stages.items()},productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
