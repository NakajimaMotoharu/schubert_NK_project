"""Independent method AST, ownership witnesses and corrected seventh-site closure; metadata only."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22456-close-resource-six-ownership-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22458-close-resource-six-independent-v1';SLOT=RUNS/'pg22458-close-resource-six-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def profile_valid(site,text,body):
    a=site['original']['attributes'];line=int(a['beginline']);lines=text.splitlines()
    if not 0<line<=len(lines) or lines[line-1].strip()!=site['declaration'] or site['ownerWitness'] not in text or site['assertionWitness'] not in body:return False
    profile=site['profile']
    if profile=='ALIAS_ALREADY_OWNED_BY_TWR':
        segment=body[body.index('QuestionSubmitForm form;'):body.index('assertThrows(IllegalStateException.class, form::operationToken);')+len('assertThrows(IllegalStateException.class, form::operationToken);')]
        return 'try (var ownedForm =' in segment and 'form = ownedForm;' in segment and re.search(r'\}\s*assertThrows\(IllegalStateException.class, form::operationToken\);',segment) is not None
    if profile in ['TEST_PROXY_TRANSFERRED_TO_CALLEE_TWR','BORROWED_CONNECTION_PROXY']:
        if 'Proxy.newProxyInstance' not in text:return False
        if 'Fixture' in site['original']['path']:return False
        return 'Connection.class' in text and ('PreparedStatement.class' in text or 'f.connection()' in body)
    if profile=='BORROWED_RESULT_MAPPER_PROXY':return 'ResultSet.class' in body and 'Proxy.newProxyInstance' in body and 'throw expected;' in body
    return False

def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='06caab4775f5650dae53cae6a97e2b3011743121cec6cb41866c00b43e252735' and m['actualExit']==0 and m['source']=='367dc439776bdfb9b36d5fc1bba0c10ad684c0a3';sites=load(P/'site-classifications.json');assert len(sites)==6 and sha(P/'site-classifications.json')==m['files']['site-classifications.json'];base=R/m['originalRawManifest']['path'];assert sha(base)==m['originalRawManifest']['sha256'];raw=load(base.parent/'unclassified-sites.json');oldseven=[x for x in raw if x['attributes']['rule']=='CloseResource'];assert len(oldseven)==7 and [x['original'] for x in sites]==[x for x in oldseven if Path(x['path']).name!='UserCriticalAuditPortTest.java']
    for name,h in m['inputHashes'].items():
        assert '/src/test/java/' in name and not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json')
    for name,h in m['mainSourceHashes'].items():assert sha(R/name)==h==normal['begin']['inputHashes'][name]
    prior=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22410-ordinary-thread158-independent-v1/manifest.json';assert sha(prior)=='b7a9022920798dd9c82e80a3e5165fca4a19a82de4d700568c46382c86f929f4';tool=load(prior)['tool'];owned=RUNS/'pg22410-ordinary-thread158-independent-v1';assert sha(R/tool['path'])==tool['sha256']==sha(owned/'source/TestMethodScopeAstCheck.java');classes={p.name:sha(p) for p in (owned/'classes').glob('*.class')};assert set(classes)=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};SLOT.mkdir();c.SLOT=SLOT;stage=c.step('parse',[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',str(owned/'classes'),'TestMethodScopeAstCheck',str(R),*sorted(m['inputHashes'])],R,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];methods={}
    for line in (SLOT/'parse.stdout').read_text().splitlines():
        path,cl,method,start,end=line.split('\t');methods.setdefault((path,cl,method),[]).append((int(start),int(end)))
    evidence=[]
    for site in sites:
        row=site['original'];a=row['attributes'];path=row['path'];text=(R/path).read_text();matches=[(lo,hi) for lo,hi in methods.get((path,a['class'],a['method']),[]) if lo<=int(a['beginline'])<=int(a['endline'])<=hi];assert len(matches)==1;lo,hi=matches[0];body='\n'.join(text.splitlines()[lo-1:hi]);assert profile_valid(site,text,body)
        if Path(path).name in ['AdminPreludeJdbcPortTest.java','SessionRevocationJdbcPortTest.java']:
            owners=methods[(path,Path(path).stem+'.Fixture','connection')];assert len(owners)==1;start,end=owners[0];ownbody='\n'.join(text.splitlines()[start-1:end]);assert site['ownerWitness'] in ownbody and '"commit", "rollback", "close", "setAutoCommit", "setReadOnly"' in ownbody
        evidence.append(dict(originalOrdinal=row['ordinal'],profile=site['profile'],methodRange=[lo,hi],ownershipWitnessVerified=True,dynamicBehaviourRequalified=False))
    outbox=(R/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.java').read_text();assert 'try (PreparedStatement statement = connection.prepareStatement(sql))' in outbox and 'try (ResultSet result = statement.executeQuery())' in outbox
    mapper=(R/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BackupStepRepository.java').read_text();assert 'readTerminal(ResultSet row' in mapper and 'row.close(' not in mapper
    fixed=R/m['correctedSitePost']['path'];assert sha(fixed)==m['correctedSitePost']['sha256'];f=load(fixed);assert f['actualExit']==0 and f['finallyRecoveryPresent'] and f['requalifiedExistingTests']==20;assert all(sha(R/p)==h for p,h in f['inputHashes'].items() if p.endswith('.java'))
    # Negative metadata guards reject wrong declaration, absent ownership, unrelated assertion and profile.
    sample=sites[0];path=sample['original']['path'];text=(R/path).read_text();a=sample['original']['attributes'];lo,hi=methods[(path,a['class'],a['method'])][0];body='\n'.join(text.splitlines()[lo-1:hi]);negative=[]
    for key,value in [('declaration','missing declaration'),('ownerWitness','missing owner witness'),('assertionWitness','missing assertion witness'),('profile','UNKNOWN')]:
        bad=json.loads(json.dumps(sample));bad[key]=value;negative.append(not profile_valid(bad,text,body))
    assert all(negative);assert m['currentRawSitesRetained']==346 and m['subsetUnclassifiedAfter']==75;assert classes=={p.name:sha(p) for p in (owned/'classes').glob('*.class')};OUT.mkdir();files={}
    for name in ['parse.stdout','parse.stderr','parse-exit.safe.json']:(OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),targetSites=6,originalLateralSites=7,correctedOriginalSites=1,newIndividualClassifications=6,currentRawSitesRetained=346,subsetClassifiedBefore=265,subsetClassifiedAfter=271,subsetUnclassifiedBefore=81,subsetUnclassifiedAfter=75,verifiedOwnershipSites=evidence,negativeMetadataGuards=len(negative),sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,dynamicBehaviourRequalified=False,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stage=stage,files=files,reusedToolPhysical=classes,correctedSitePost=m['correctedSitePost'],bug='BUG-2431',ykt='YKT-2176',finiteLateralClosureSatisfied=True,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=6,remaining=75,lateralClosure=True,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
