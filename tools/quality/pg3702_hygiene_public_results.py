"""Publish bounded source/static proof, preserving old failed/blank metadata and all open gates."""
import hashlib
import json
from pathlib import Path
from git_source_contract import last_main_source

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3702-hygiene-static-v1'


def main():
    slots={'imports':'pg3690-import-candidate-stage-v1','hygiene':'pg3692-hygiene-candidate-stage-v1','pmdOriginal':'pg3696-hygiene-pmd-diagnosis-v1','pmdRecovered':'pg3700-static-source-recovery-v1'}
    raw={k:(W/v/'manifest.safe.json').read_bytes()for k,v in slots.items()};v={k:json.loads(x)for k,x in raw.items()}
    if not all(x['actualExit']==0 for x in v.values()):raise ValueError('all actually successful stages required')
    r=v['pmdRecovered']['result'];h=v['hygiene']['result'];i=v['imports']['result']
    source=last_main_source(ROOT)
    if not(source==r['productionCandidateSource']=='5224dd641976df502f3d1f278d73ec55f5ff9711'and r['all849ByteJoinVerified']and not r['pmdReissued']and h['checkstyle']['actualExit']==h['checkstyle']['findings']==0 and i['wildcardImportsExpanded']==531 and h['declarationCounts']['groups']==113 and h['declarationCounts']['literalTabs']==2723):raise ValueError('all source/real counters required')
    applied=json.loads((W/'pg3694-hygiene-candidate-material-v1/apply.safe.json').read_bytes())
    if not(applied['actualExit']==0 and applied['all849Exact']and applied['candidateManifestSha256']==h['serverManifestSha256']==r['originalCandidateStageSha256']):raise ValueError('exact applied/proved source join')
    actual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if actual!=r['all849SourceSha256']:raise ValueError('every actually analyzed source byte still exact')
    PUBLIC.mkdir()
    outputs={'all849-source-sha256.json':actual,'applied214-sha256.json':h['candidateChanges'],'module-semantic-proofs.json':h['modules']}
    for name,value in outputs.items():
        with(PUBLIC/name).open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    data={'actualExit':0,'productionCandidateSource':source,'baseOperationalSource':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','kind':'APPLIED_SOURCE_STATIC_TECHNICAL_PROOF_NOT_RELEASE_ACCEPTANCE','originalReceipts':{k:{'slot':slots[k],'sha256':hashlib.sha256(x).hexdigest(),'actualExit':0}for k,x in raw.items()},'sourceFiles':849,'changedMainFiles':214,'wildcardImportsResolved':531,'multipleDeclarationsResolved':113,'variablesSeparated':282,'literalTabsEscaped':2723,'heldSyntaxCandidates':889,'heldMeaning':'Not transformed; all849 real fixed Checkstyle0 proves no unresolved Checkstyle declaration finding hidden in held candidates','allSixCompilerBindingsDeclarationsAndLiteralValuesIdentical':True,'checkstyle':h['checkstyle'],'pmd':r['pmd'],'originalBlankSourcePreserved':v['pmdOriginal']['result']['productionCandidateSource']=='','recoveryAll849ByteJoin':True,'pmdReissued':False,'seventyGeneratedArtifactsChanged':False,'staticRulesChanged':False,'suppressionAdded':False,'MainAppliedToFeatureBranch':True,'MainDeployed':False,'newMainBuildAndWholeRegressionPending':True,'newSourceNativePending':True,'oldSourceNativeImported':False,'canonicalWbsSourceRemainsBaseUntilQualification':True,'formalTests':1964,'formalScopes':53,'individualAccepted':17,'individualTotal':190,'newAcceptedLeafCredit':0,'effortCompletionRate':None,'QA051final':'HELD','F03Accepted':False,'formalAccepted':False,'files':{n:hashlib.sha256((PUBLIC/n).read_bytes()).hexdigest()for n in outputs},'vmActions':0}
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(data,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'publicManifestSha256':hashlib.sha256((PUBLIC/'manifest.json').read_bytes()).hexdigest(),'checkstyleFindings':0,'pmdRaw':data['pmd']['rawFindings'],'source':source,'F03Accepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
