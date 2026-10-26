# Query Test二変更＋独立oracle補助一path追跡

2026-10-26 14:18 JST、source21228608b、群2347→2348/G13.07（G03.01関連0）、開始.5/2/5 cap10。Query009010/PG-D678/10287の当三source hashだけを登録。元Application/Replay TestはP01401/P01403の担当・費用・全historical fieldを保持しSHAだけ更新、新helperは明示PG-D678によるG03.01責任候補。新helperは@Testなし/製品TestIDなし、24vector等はoracleメタIDとして区別。

|証拠|結果|SHA-256|
|---|---|---|
|PG10290-remaining-shared-context-v1/manifest.json|残62site/36不変sourceの文脈レビュー、製品PT0/新欠陥認定0|581fd767bae699fbbb70a66eedfb866445d5e07c2bfe5d09f98e2c0b658c016a|
|PG10292-query-oracle-trace-v1/manifest.json|旧981中二SHAだけ更新/他979全field不変＋新helper一→982行、候補974|9a00d5ede29463b85a6cedd23f8c851741530f94ed7ea53bbd4c6b0e1de741e2|
|PG10294-query-oracle-trace-post-v1/manifest.json|実guard10metadata拒否、原941/943・予算/受入保持、所定audit前後1HOLD|12e9aaabfd4fb4be5fbb3d61809888a106c50a21a3709394655347748fe8d0aa|

各pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 下。実command=PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg10292_query_oracle_trace.py、--emit-patchをapply_patchへ、pg10294_query_oracle_trace_post.py。製品実行0/外部操作0、工具invocation/原source/manifest hash・raw inventoryとsnapshot hashはpostに保存。

現Java1809中登録1807、Main965全件、Test842/844、UNKNOWN二は不変。legacy label相違748は実rows導出。原registry/原code/runtime/費用とPG-D673の既六補助規則を保持し、当helper一件の責任を過去へ一般化しない。変更二Testのproofはsource212の「製品PT0/coverage未測定/元PT NOT_EXECUTED_HOLD」メタ資格、旧成功を新sourceの実行へ結合しない。共有24vectorは二参照でも48へ加算しない。

485は現二sectionの参照/導出counter/当二binding参照だけ変更、486は485全raw hash再束縛。forward post SHA nullは循環回避として維持し、独立postが実raw hashを束縛する。旧owner/newcost/newhash/currenthash/実PT捏造/coverage捏造/source/UNKNOWN/legacycount/受入の10変異を拒否。全WBS監査HOLD/全G13/G03/F03/451/native/CHRは未受入。正式1964-53/既17-190/工数null/QA051final/全安全HOLD不変。
