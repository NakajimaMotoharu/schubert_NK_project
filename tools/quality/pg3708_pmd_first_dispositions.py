"""Exact source-bound J2EE context and already-proven label FP; raw2217 remains intact."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
import xml.etree.ElementTree as E
from git_source_contract import last_main_source,POM_PATHSPEC
from lan_server import copy,run
from pmd_context_disposition import standalone_thread_context

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE='/home/mini/schubert-nk-pgpt'


def require(value,reason):
    if not value:raise ValueError(reason)


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');prior=b/'runs/PG3706-pmd-inventory-v1';out=b/'runs/PG3708-pmd-disposition-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require(sha(prior/'manifest.safe.json')==data['inventoryManifestSha256'],'actual all2217 source-bound index')
    meta=json.loads((prior/'manifest.safe.json').read_bytes());require(sha(prior/'findings.private.json')==meta['findingsSha256']and sha(prior/'vendor-rules.private.json')==meta['vendorRulesSha256'],'all original findings and vendor scope immutable')
    rows=json.loads((prior/'findings.private.json').read_bytes());rules=json.loads((prior/'vendor-rules.private.json').read_bytes());require('J2EE specification'in rules['DoNotUseThreads']['description']and 'J2EE server'in rules['DoNotUseThreads']['description'],'actual primary context premise')
    context=data['architecture'];context['ruleExplicitlyJ2EE']=True;changed=[]
    for row in rows:
        disposition=standalone_thread_context(row,context)
        if disposition is not None:row.update(disposition);row['testOrDesignEvidence']=['origin/main:SS311 module jar table','origin/main:SS342 direct Java process/Unit entrypoints',data['architectureProofSha256']];changed.append(row['id'])
    require(len(changed)==238,'all238 exact vendor-context findings, no other rule removed')
    label=[r for r in rows if r['rule']=='HardCodedCryptoKey'];require(len(label)==1,'exact known label finding')
    row=label[0];proof=data['priorLabelProof'];require(row['path']==proof['finding']['file']and row['sourceSha256']==proof['sourceSha256']and int(row['coordinates']['beginline'])==proof['finding']['beginline'],'same exact source/label coordinate as independent existing canary/JCE witness')
    row.update(disposition='FALSE_POSITIVE_VALIDATION_LABEL_NOT_KEY',basis=proof['basis'],testOrDesignEvidence=[data['priorLabelProofSha256'],proof['sameRuleCanaryManifestSha256']],qualityGatePass=False)
    counts=dict(Counter(x['disposition']for x in rows));require(counts=={'UNCLASSIFIED':1978,'CONTEXT_NOT_APPLICABLE_J2EE_RULE':238,'FALSE_POSITIVE_VALIDATION_LABEL_NOT_KEY':1},'raw2217 preserved and exact partition')
    out.mkdir();(out/'dispositions.private.json').write_text(json.dumps(rows,sort_keys=True))
    result={'actualExit':0,'productionCandidateSource':data['source'],'rawFindings':2217,'dispositions':counts,'newContextDispositions':238,'historicalLabelFalsePositiveRevalidatedWithoutReplay':1,'unclassified':1978,'applicableViolationCount':None,'remainingRawWarningCount':2217,'allFindingIdsAndSourceCoordinatesPreserved':True,'dispositionSha256':sha(out/'dispositions.private.json'),'architectureProofSha256':data['architectureProofSha256'],'priorLabelProofSha256':data['priorLabelProofSha256'],'rulesChanged':False,'suppressionAdded':False,'sourceExcluded':False,'MainChanged':False,'pmdReissued':False,'businessOrVmReplay':False,'qualityGateAccepted':False,'F03Accepted':False,'formalAccepted':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed source/context evidence')
    source=last_main_source(ROOT);require(source=='5224dd641976df502f3d1f278d73ec55f5ff9711','exact source still current')
    docs=['documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md','documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md']
    require(not subprocess.check_output(['git','diff','origin/main','HEAD','--',*docs],cwd=ROOT),'approved design originals equal origin/main')
    text={p:subprocess.check_output(['git','show','origin/main:'+p],cwd=ROOT).decode()for p in docs}
    require('Executable jar'in text[docs[0]]and 'Java processを直接ExecStart'in text[docs[1]],'explicit normative standalone Java launch, not inference from packaging alone')
    require(not subprocess.check_output(['git','diff','4856b3fcaeb4cae983d77757a38dc0bf56a693e2',source,'--','src/deployment','pom.xml',POM_PATHSPEC],cwd=ROOT),'approved process/dependency configuration unchanged')
    modules=['protocol','storage','bootstrap','api','web','batch'];roles={}
    for m in modules:
        p=ROOT/f'src/schubert-nk-{m}/pom.xml';node=E.fromstring(p.read_bytes());ns={'m':'http://maven.apache.org/POM/4.0.0'}
        require(node.findtext('m:packaging','jar',ns)=='jar','only standalone/library jar, never WAR/EJB deployment')
        deps=[x.findtext('m:groupId','',ns)+':'+x.findtext('m:artifactId','',ns)for x in node.findall('m:dependencies/m:dependency',ns)]
        require(not any(x.startswith(('jakarta.platform:','jakarta.ejb:','javax.ejb:','javax:javaee'))for x in deps),'no managed JavaEE platform dependency')
        roles['schubert-nk-'+m]='STANDALONE_JAVA_SERVICE'if m in ['api','web','batch']else'LIBRARY_ONLY_IN_STANDALONE_GRAPH'
    require(not any(p.name in {'ejb-jar.xml','application.xml'}for p in(ROOT/'src').rglob('*.xml')),'no managed container deployment descriptor')
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';label_path=public/'PG3426-crypto-finding-disposition/manifest.json';label=json.loads(label_path.read_bytes());codec=ROOT/label['finding']['file'];test=ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodecTest.java'
    require(hashlib.sha256(codec.read_bytes()).hexdigest()==label['sourceSha256']and hashlib.sha256(test.read_bytes()).hexdigest()==label['testSourceSha256'],'exact unchanged code and independent JCE witness Test, no rerun')
    canary=public/'PG3424-crypto-rule-canary/manifest.json';require(hashlib.sha256(canary.read_bytes()).hexdigest()==label['sameRuleCanaryManifestSha256'],'original true unsafe vs dynamic-label sensitivity unchanged')
    binding=json.loads((public/'PG3702-hygiene-static-v1/all849-source-sha256.json').read_bytes());require(binding=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'all exact current849 files')
    architecture={'source':source,'sourceSha256':binding,'approvedDirectJavaProcess':True,'externalJavaEEManaged':False,'noManagedDeploymentDescriptors':True,'moduleRoles':roles,'approvedDocumentSha256':{p:hashlib.sha256(v.encode()).hexdigest()for p,v in text.items()},'originMain':subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),'qualityGatePass':False}
    inventory=json.loads((W/'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes());require(inventory['actualExit']==0,'actual all23/index0')
    data={'source':source,'architecture':architecture,'architectureProofSha256':hashlib.sha256(json.dumps(architecture,sort_keys=True).encode()).hexdigest(),'priorLabelProof':label,'priorLabelProofSha256':hashlib.sha256(label_path.read_bytes()).hexdigest(),'inventoryManifestSha256':inventory['result']['serverManifestSha256']}
    os.umask(0o077);out=W/'pg3708-pmd-first-dispositions-v1';out.mkdir();(out/'architecture.safe.json').write_text(json.dumps(architecture,sort_keys=True));payload=inspect.getsource(require)+'\n'+inspect.getsource(standalone_thread_context)+'\n'+inspect.getsource(server)+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';script=out/'disposition.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3708-pmd-disposition-v1 && mkdir -m700 '+BASE+'/transfer/PG3708-pmd-disposition-v1',timeout=30);require(rc==0,'new-only independent dispositions')
    rc,_=copy(script,BASE+'/transfer/PG3708-pmd-disposition-v1/',timeout=60);require(rc==0,'fixed context evidence payload')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3708-pmd-disposition-v1/disposition.private.py'),timeout=45);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionCandidateSource':source,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return rc


if __name__=='__main__':raise SystemExit(main())
