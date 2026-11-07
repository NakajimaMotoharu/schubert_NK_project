"""Reconstruct current ordinary85 subset from unchanged84 and fresh changed-Test raw7; no engine replay."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
R=Path(__file__).resolve().parents[4]
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1'
OUT=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22444-user-audit-static-source-rebinding-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserCriticalAuditPortTest.java'
def main():
    assert not OUT.exists();old=load(BASE/'manifest.json');assert sha(BASE/'manifest.json')=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';rows=load(BASE/'unclassified-sites.json');assert len(rows)==347
    newp=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22432-user-audit-cleanup-static-applicability-v1/manifest.json';new=load(newp);assert new['pmdRaw']==7 and new['applicableViolations']==0 and new['checkstyle']==0;fresh=load(Path(new['staticManifest']['path']));assert sha(Path(new['staticManifest']['path']))==new['staticManifest']['sha256'];newrows=fresh['reports']['pmd']['items'];assert len(newrows)==7
    inputs=old['begin']['inputHashes'];assert len(inputs)==85;current={}
    for name,h in inputs.items():
        assert not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and '/src/test/java/' in name
        current[name]=sha(R/name)
        if name==TEST:assert current[name]==new['inputHashes'][name] and current[name]!=h
        else:assert current[name]==h
    prior=[];priorrefs=[]
    for folder in ['PG22392-ordinary-proxy-loader93-v1','PG22408-ordinary-thread158-scope-v1','PG22418-null-identity14-sites-v1']:
        p=R/'evidence/01_PT/018_NK-OPS-001/evidence'/folder/'manifest.json';v=load(p);priorrefs.append(dict(path=str(p.relative_to(R)),sha256=sha(p)));data=load(p.parent/'site-classifications.json');assert sha(p.parent/'site-classifications.json')==v['files']['site-classifications.json']
        for site in data:
            row=site['original'];assert row in rows;assessment=site.get('assessment',site);assert assessment['classification']=='NOT_APPLICABLE';prior.append(row['ordinal'])
    assert len(prior)==len(set(prior))==265
    was=[x for x in rows if x['path']==TEST];assert len(was)==8;closed=[x for x in was if x['attributes']['rule']=='CloseResource'];assert len(closed)==1;remaining=[x for x in was if x not in closed];bindings=[]
    for item in newrows:
        attrs={k:v for k,v in item.items() if k!='message'};matches=[]
        for x in remaining:
            oldattrs=dict(x['attributes']);oldattrs['beginline']=str(int(oldattrs['beginline'])+4);oldattrs['endline']=str(int(oldattrs['endline'])+4)
            if oldattrs==attrs and x['message']==item['message']:matches.append(x)
        assert len(matches)==1;row=matches[0];qualified=row['ordinal'] in prior;assert qualified==(item['rule'] in ['DoNotUseThreads','UseProperClassLoader']);bindings.append(dict(originalOrdinal=row['ordinal'],oldSourceSha256=row['sourceSha256'],newSourceSha256=current[TEST],currentAttributes=attrs,priorReasonRequalified=qualified,currentSubsetClassification='NOT_APPLICABLE' if qualified else 'UNCLASSIFIED_MAP_GROUP_DEFERRED',localChangedTestStaticAssessment='NOT_APPLICABLE',note='Map thread-confinement reason is available in local Test static receipt, but original planned global Map62 review remains pending; no automatic global credit.'))
    assert len({x['originalOrdinal'] for x in bindings})==7 and sum(x['priorReasonRequalified'] for x in bindings)==6
    otherclassified=[n for n in prior if next(x for x in rows if x['ordinal']==n)['path']!=TEST];assert len(otherclassified)==259
    unitpost=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22438-user-audit-cleanup-independent-v1/manifest.json';u=load(unitpost);assert sha(unitpost)=='48d5f83b00ebb47bc4adf700b198c6bb5246344b32a4552d139bbf165097ff12' and u['actualExit']==0 and u['requalifiedExistingTests']==20 and u['finallyRecoveryPresent']
    OUT.mkdir();(OUT/'rebindings.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n');value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=u['source'],productionCoreMain=u['productionCoreMain'],originalRawManifest=dict(path=str((BASE/'manifest.json').relative_to(R)),sha256=sha(BASE/'manifest.json')),freshChangedTestStaticManifest=dict(path=str(newp.relative_to(R)),sha256=sha(newp)),priorClassificationManifests=priorrefs,unitPost=dict(path=str(unitpost.relative_to(R)),sha256=sha(unitpost)),inputHashes=current,unchangedSources=84,changedSources=1,originalRawSites=347,reconstructedCurrentRawSites=346,originalClassifiedSites=265,retainedOtherSourceClassifications=259,requalifiedKnownSites=6,currentSubsetClassifiedSites=265,originalUnclassified=82,currentSubsetUnclassified=81,removedApplicableFinding=closed[0],bug='BUG-2431',ykt='YKT-2176',otherCloseResourceSitesRemainPending=6,globalMapSitesRemainUnclassified=62,globalF03Accepted=False,whole451Accepted=False,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,reconstructedNotFreshAll85EngineRun=True,files={'rebindings.json':sha(OUT/'rebindings.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,currentRaw=346,requalifiedKnownSites=6,remaining=81,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
