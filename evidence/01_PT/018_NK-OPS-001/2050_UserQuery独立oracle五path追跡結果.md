# User Query oracleを含む五pathのbatch追跡

2026-10-26 14:43 JST、source878866851、群2355→2356/G13.07（G03.01関連0）、開始.5/2/5 cap10。現10292の982行から、QuestionQuery二Testのsource4c定数化SHAと、UserQuery二Testのsource878独立profile SHAを更新、新UserQueryWireOracle一pathを追加した。元982中SHA以外の全fieldを保持し、未変更978行は全field同一。

|公開manifest|結果|SHA-256|
|---|---|---|
|PG10324-user-query-oracle-trace-v1/manifest.json|983行/候補975・四SHA＋新helper、原owner/cost/歴史runtime保持|7a7f15450a3c11638eb55b856f2cd9769d3617c1f00bab45a2c70c68e57fc71a|
|PG10326-user-query-oracle-trace-post-v1/manifest.json|所定audit実1→1HOLD・10metadata拒否/原941943・予算・受入保持|3a01bacd17f76a3b4f975a35c2064f8b41ea035dde4467b192e399b7cf663606|

pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 下。実command=tools/quality/pg10324_user_query_oracle_trace.py→--emit-patchをapply_patch→pg10326_user_query_oracle_trace_post.py、PYTHONPATH=tools/quality:tools/quality/vm/050_s1。実invocation/元registry/qualified proof/source hash/当inventory全rawとsnapshotのSHAをmanifestへ保存、製品実行0/外部操作0。

現Java1810中登録1808、Main965全件、Test843/845、UNKNOWN二不変更、legacy label749を実rowsから導出。新helperはPG-D679のG03.01候補、元User二TestはP01001、Question二TestはP01401/P01403の原担当/費用を保持。元10292の二bindingはhash付き歴史参照で保持、当四bindingは現source SHAと元proof sourceを別fieldに保存する。

Question二件のproofは10304/source4c（同値定数化/sourceメタ資格、メタvector数は未新実行なのでnull）、User二件は10320/source878（独立27メタ）。いずれも製品PT0/NOT_EXECUTED_HOLD/coverage未測定、共有27を54へ数えない。旧runtimeを当sourceの成功へ再束縛せず、source単位の証拠を分離する。

485現二section/486の485全raw hashだけ変更。原予算/acceptance/正式・元941logical943歴史physical不変、実全WBS監査は1/HOLDのまま。old-owner/new-cost/new-hash/current-hash/製品PT捏造/coverage捏造/source/UNKNOWN/legacy-count/受入の10変異を拒否。循環回避forward post SHA nullと実post側のraw束縛を保持。全G13/G03/F03/451未受入、正式1964-53/17-190/工数null/QA051final/全安全HOLD不変。
