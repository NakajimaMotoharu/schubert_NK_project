"""Fourteen explicitly reviewed Test-only null input/cleanup and Proxy identity sites."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
R=Path(__file__).resolve().parents[4]
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22418-null-identity14-sites-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
# Per-site purpose and independent existing assertion witness; no Production method generates expected.
VECTORS=[
 ('SessionIssueJdbcPortTest.java',403,'f.status = null;','infra(f);','Missing user status must fail infrastructure before session issuance; fixed SQL-order assertion follows.'),
 ('RunReferencePortTest.java',146,'fixture.values[column] = null;','fixture.assertClosed(1, 1);','Every required column missing is a deliberate negative vector; fixed failure catalog and both owned close assertions follow.'),
 ('DisplaySnapshotPortTest.java',62,'f.principal = null;','snapshot.topBar().getUsername()','Remove source principal after capture; retained display remains unchanged by an independent fixed username assertion.'),
 ('DisplaySnapshotPortTest.java',71,'f.principal = null;','assertTrue(WebDisplayContext.existing(f.request).isEmpty());','Anonymous capture intentionally removes prior snapshot and forbids token-property reads.'),
 ('DisplaySnapshotPortTest.java',161,'f.principal = null;','restore must not read principal','Restore uses retained projection even after principal replacement; explicit callback prohibition prevents re-reading.'),
 ('EncryptedSecurityContextPortTest.java',144,'frame.readFailure = null;','frame.session.failure = failure;','Clear the preceding read fault before injecting the distinct session-metadata failure; never a production null default.'),
 ('EncryptedSecurityContextPortTest.java',241,'frame.readFailure = null;','assertEquals(2, frame.sessionReads);','Retry the same deferred read after deliberate initial failure; ensure partial context was not cached and exactly two reads occurred.'),
 ('ErrorControllerPortTest.java',363,'principal = null;','preparingDisplay = false;','Own fixture finally releases its temporary display-preparation principal and phase marker; does not retain an authentication grant.'),
 ('ErrorDispatchRestorePortTest.java',114,'preparedPrincipal = null;','capturing = false;','Own fixture finally clears temporary captured principal/phase and operations before the error-dispatch vector.'),
 ('ErrorDispatchRouterPortTest.java',176,'missing.context = null;','assertThrows(','Explicit absent request-context vector must reject and clear only own thread; preserves original assertion without runtime replay.'),
 ('CaddyTransportPortTest.java',245,'case "equals" -> proxy == args[0];','case "hashCode" -> System.identityHashCode(proxy);','Own HttpServletRequest Proxy implements Object identity equality and matching identity hashCode; invoking equals would recurse into this handler.'),
 ('CaddyTransportPortTest.java',268,'case "equals" -> proxy == args[0];','case "hashCode" -> System.identityHashCode(proxy);','Own HttpServletResponse Proxy implements Object identity equality and matching identity hashCode; no domain value comparison.'),
 ('FormCsrfRequestPortTest.java',66,'case "equals" -> proxy == args[0];','case "hashCode" -> System.identityHashCode(proxy);','Own synthetic request Object.equals handler deliberately uses identity with matching hashCode; no value equality exemption.'),
 ('LoginFormConverterPortTest.java',116,'case "equals" -> proxy == args[0];','case "hashCode" -> System.identityHashCode(proxy);','Own synthetic Servlet request Object.equals implementation must not call itself recursively; identity-only port behavior.')]
def main():
    assert not OUT.exists();mp=BASE/'manifest.json';assert sha(mp)=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';m=load(mp);rows=load(BASE/'unclassified-sites.json');target=[x for x in rows if x['attributes']['rule'] in ['NullAssignment','CompareObjectsWithEquals']];assert len(target)==14;bykey={(Path(x['path']).name,int(x['attributes']['beginline'])):x for x in target};assert len(bykey)==14;sites=[];inputs={}
    for file,line,expected,witness,reason in VECTORS:
        row=bykey[(file,line)];path=row['path'];assert '/src/test/java/' in path and not any(x in path for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);text=(R/path).read_text();assert sha(R/path)==row['sourceSha256']==m['begin']['inputHashes'][path];lines=text.splitlines();assert lines[line-1].strip()==expected
        # The independently reviewed witness must occur in the local statement context, not an unrelated file.
        window='\n'.join(lines[max(0,line-5):line+30]);assert witness in window;inputs[path]=sha(R/path);sites.append(dict(original=row,classification='NOT_APPLICABLE',reason=reason,expectedSourceLine=expected,localWitness=witness,localWindowSha256=hashlib.sha256(window.encode()).hexdigest(),dynamicAssertionReexecuted=False))
    OUT.mkdir();(OUT/'site-classifications.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',originalManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),inputHashes=inputs,targetSites=14,newIndividualClassifications=14,originalRawSites=347,priorIndividualClassifications=251,subsetUnclassifiedBefore=96,subsetUnclassifiedAfter=82,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,dynamicBehaviourQualified=False,sourceBytesUnchanged=True,suppressionAdded=False,ruleConfigurationChanged=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files={'site-classifications.json':sha(OUT/'site-classifications.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
    (OUT/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=14,remaining=82,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
