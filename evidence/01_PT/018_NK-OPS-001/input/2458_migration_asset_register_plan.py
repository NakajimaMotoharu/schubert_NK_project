"""Register missing production inventory artifact before manufacturing; keep full ETL unaccepted."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/AssetMigrationManifest.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assert not (r/main).exists() and not (r/test).exists();spec=r/'evidence/01_PT/019_NK-MIG-001/007_素材inventory純値製造・独立十二通常PT仕様.md';assert not spec.exists();spec.write_text('''# 素材inventory純値製造と独立12通常PT仕様

NK-MIG-001/WBS-P01903.02、FIL003005/MIG003006・MIG-DAT003006、UI254、SS343SSC342（main e48e393185/PR208）。Java25 bootstrap package migration/AssetMigrationManifest。実I/O・DB/原本・authorityなし。未実装機能TDDなのでBUG起票なし。元/2のETL/実master/DB/ID・表示順と受入は残す。

| Test ID | method / 独立期待値 |
|---|---|
| PT-MIG-ASSET001 | canonicalGolden: 五列/固定header/順序/UTF8LFを手書きtextblockと全byte比較。abc3/既知ba7816...15ad・empty0/既知e3b0...b855、input2/total3。production encoder/hashからexpected生成0 |
| 002 | validPathsAndKinds: 全4kind/NFC/supplementary/relativePOSIX名、境界0/LongMAX、emptyinventory。非authority値であること |
| 003 | invalidPaths: 空/absolute/backslash/空segment/`.`/`..`/全control/非NFC/未対応surrogate、source・target・observed双方拒否 |
| 004 | nullContracts: list/要素/kind/path/hashすべてのnullを明示拒否、NPEcatch正常化なし |
| 005 | invalidSizesAndHashes: 負byte/63・65桁/uppercase/nonhex拒否、lower64許容 |
| 006 | duplicatePaths: source/targetそれぞれの重複Entry・観測target重複を拒否、元list不変 |
| 007 | checkedAggregateOverflow: source/observed各MAX+1のoverflow拒否、MAX+0許容 |
| 008 | immutableOwnership: 元list変更・返却list書換・返却byte全消去でも元snapshot/golden不変 |
| 009 | identicalClaims: 観測順逆転でもmissing/extra/size/hash各0、observed2/3・metadataMatches true。constructor六負値は拒否。file/DB成功とはしない |
| 010 | missingClaim: missing1/extra0/他0、observed1/0、metadataMatches false |
| 011 | unexpectedClaim: missing0/extra1/他0、observed3/4、metadataMatches false |
| 012 | independentSizeAndHashDifferences: byteだけ/hashだけ/両方で各countを独立固定、metadataMatches false |

Source/Test全体をGJF/RootNullAway/lintWerror/PMD/CS/SB、固定source whole12一回、独立post全physical CRC/初期化/XML/FES/全四counterへ結合。到達不能・除外・無意味assert・旧exec合算なし。時刻/環境/JDK/tool/branch/source/command/終了/input/output/hash/coverageは各manifestと結果。返値は宣言metadata間の比較、実file/symlink/hash/原本/移行/Unit/Go/451/ITSTの成功ではない。

追加発見価格 .8/2.4/4.8の内、source+全12Test製造 .5/1.5/3（上限4）、normal .3/.9/1.8（上限3）。旧見積りの既存artifact前提がowned0で成立しなかった不足を明示して追加、元/2のETL/fullcriteria費用とS/V原枠は減らさず保持。専有実費/token不明null。
''')
old=next(d.glob('1648_*'));f=ld(old);estimate=dict(low=.8,base=2.4,high=4.8)
for k,v in estimate.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+v,3)
f.update(previousForecast=ref(old),revision='423-MISSING_MIGRATION_ASSET_COMPONENT_MANUFACTURE_AND_NORMAL_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='P01903_MISSING_ASSET_MANIFEST_COMPONENT',estimate=estimate,capByGroup=[4,3],sourceAndTest=dict(low=.5,base=1.5,high=3),normal=dict(low=.3,base=.9,high=1.8),reason='OriginalB-ownership artifact assumption false: currentowned0/no productioninventory. Add boundedofflinecomponent manufacture+ordinaryPT, preserve originalfullETL/actualmaster criteria budget, not repeat or acceptance from reduction.'))
br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp']);fp=d/'1650_WBS65予実・移行素材部品製造通常追加版423.json';wr(fp,f)
p=r/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json';a=ld(p);t=next(x for x in a['tasks'] if x['id']=='WBS-P019-03');assert t['ownedArtifacts']==[];t['historicalOwnedArtifactsBeforeSSC342']=[];t['ownedArtifacts']=[main];t['evidencePlan']['candidateTestFiles'].append(test);t['evidencePlan']['plannedSourceSSC342']=dict(state='REGISTERED_NOT_PRESENT',spec=ref(spec),actualRuntimeQualification=False);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
p=r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';a=ld(p);assert main not in {x['path'] for x in a['artifacts']};a['artifacts'].append(dict(kind='JAVA',path=main,owner='WBS-P019-03',costOwner='WBS-P019-03',sha256=None,acceptance='NOT_RUN',state='REGISTERED_PLANNED_NOT_PRESENT',relatedSsc='SSC-342',testIds='PT-MIG-ASSET001..012',historicalPath=None));a['plannedOfflineMigrationComponentSSC342']=dict(path=main,scope='DECLARED_METADATA_ONLY_NO_RUNTIME_AUTHORITY',formalAccepted=False);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');q=r/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';a=ld(q);a['inventorySha256']=sha(p);a['plannedOfflineMigrationComponentSSC342']=dict(path=main,sourceCreated=False,newAcceptance=0);q.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
c=ld(i/'2400_morning_typed_sql_source_start.json');c.update(groupId='PGPT-WBS65-SSC342-ASSET-MANIFEST-MANUFACTURE-AND-WHOLE12-SOURCE-20261114',recordPath=str((d/'1651_WBS65移行素材部品製造開始.json').relative_to(r)),category='IMPLEMENTATION',kind='ADDITIONAL_FINDING',scope='SSC342 approvedmaine48e: registerednewpurebootstrapAssetMigrationManifest and12independent Testdefinitions, GJF/CS/sourceclosure only. .5/1.5/3cap4 subset ofgross .8/2.4/4.8, normal .3/.9/1.8 remains. No I/O/DB/RootVMnativekeysdeployauthority, no partialMaster/ETL acceptance.',oracleRefs=[ref(spec),ref(b/'evidence/PG30152-ssc342-main-two-doc-publication-v1/manifest.json')],wbsLeafIds=['WBS-P019-03.02'],implementationArtifactPaths=[main],implementationOwnerLeafBindings={'WBS-P019-03':['WBS-P019-03.02']},implementationCanonicalPlans=[ref(r/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json'),ref(r/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json')],source='3f65cf67391b729feeca63f7b037e7c1f82db9e8',run='PG30158-ASSET-MANIFEST-MANUFACTURE',estimate=dict(low=.5,base=1.5,high=3),capPp=4,workIds=['P01903_SSC342_ASSET_MANIFEST_SOURCE_AND_WHOLE12_DEFINITIONS'],forecastRef=ref(fp),nextCommand='WriteonepureMain plusindependentwhole12 TestmatchingSS343SSC342. All5physical onlyJDK/JSpecify/JUnit, no file/DB/RootVMnativekeyauthority. GJF/CS/sourcecontractbeforepinnewMainGitandupdateinventories; no productPTclaim. Then alreadypricednormal.3/.9/1.8 fullstatic/fixedsource/onewhole12/independentpost. ContinueallowedPGPT beyondordinarygroup/report.');wr(i/'2459_migration_asset_source_start.json',c);print(json.dumps(dict(actualExit=0,registeredBeforeSource=main,additionalGross=estimate,currentRevisedRemaining=f['revisedRemainingPp'])))
