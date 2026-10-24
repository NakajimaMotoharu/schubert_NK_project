# Canonical owner／変更群の分離・照合結果

1839/PG-D627/group2070、主WBS-G13.07・P018-09/C07参照0加算。Production sourcefb9fce0f91de3d9fdfa634fe277592700f915e45不変更。**製品Main/新Test0・coverage null・正式受入0/全G13未完**。8952の全1835physical/232source行を再実行せず読み、source現hash/normal2bb0684f・raw85aac967と485の論理ownerを結合した。

|公開artifact（provisional配下）|SHA256|
|---|---|
|PG8958-canonical-owner-join-v1/manifest.json|208fa4cd2ecb4ca62631fae6cc60ebaef39abd410edd64da00f4d3a29f244755|
|PG8960-canonical-owner-guards-v1/manifest.json|782eb932795dc6a037dd377296a2c91f34e3c1ec7b199a3cf6ea39e227b95ba4|

|canonical owner/costOwner|当232行|根拠|
|---|---:|---|
|P018-05|2|485既ApiProcessMain/ApiManagementServer|
|P018-06|3|485既WebNativeRuntime/HttpServer/ManagementServer|
|P018-09|213|新monitoring code/PT/明示した独立fixture、RD171/UI252/SS312351|
|C07|8|monitoring配置artifact、SS351|
|F02|4|API/Web/Batch/Bootstrap POM、module build依存入力|
|C02|1|SupplementaryUnitTemplateTest、1553～1555の既主担当|
|C06|1|ConfigurationTemplateContractTest、1556～1557の既主担当|

旧sourceRows.owner一律P018-09からcanonical表示が異なるのは19行。既主担当5件は485とhistorical physicalのowner/costOwnerが一致することを確認し、変更担当P018-09と分離した。新規227件は明示ruleに基づくlogical候補であり、WBS受入や実行済み証拠の資格を意味しない。対応はowner/canonicalOwner/canonicalCostOwnerとchangeOwnerを別記、旧owner literal/変更群という意味・原hashを保存し、費用配分/原event/開始見積を変更しない。

初回新rule TDDはnested persistence二pathと独立fixture二pathをUNKNOWNとして保持しdriver終了1/補正未発行（PG8958-canonical-owner-unresolved-v1/manifest.json、初案commit2fda93c76）。未知を変更群から既知化していない。public sourceのAsyncJobCountRepository（PG-D540/1627）・OutboxObservationRepository（PG-D547/1664）がSS351 monitoring projectionであること、metric-catalog.tsv/http-route-labels.txtがSS351/312独立fixtureであることを確認して明示ruleを補完した。SQL/DB処理やfixture試験を実行せず全232行を解決し、任意unknown/private/outside pathは引続きUNKNOWN/拒否へ残す。

8960は独立golden7件と、主担当上書き/費用owner変更/変更担当付替え/歴史費用再配分/専有費捏造/旧PT資格化/旧run付替え/誤hash/欠落/重複/候補の偽受入/config二重割当/module owner変更/unknown推定/unsafe path二つの**16metadata反例**を実validatorへ与え全拒否した。metadata checkを製品PT/成功件数/coverageへ加算しない。

485はcurrentIncrementalHostOwnership参照だけ追加、元論理941件のdataset SHA256 ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99、旧e7d64 physical943件dataset SHA256 38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01aを編集前後で保持。旧byte/成功はcurrentへ移植せず、whole source/runtime受入false。原ファイル全hash a067663bはAtJoin時点の記録であり追加参照後の現ファイルhashとは区別する。旧8938の231行・8916の229行は最新232path集合の部分集合と確認、元tool/証拠を編集・再実行せず補正参照で横展開した。今後はtrace_owner_joinのexplicit canonical/change ownerを使い477/411へ再発防止を反映した。

BUG1725/YKT1476は当232行の意味分離・19label補正、原5主担当保持/全新候補根拠/unknown扱い・反例/485履歴不変まで限定CLOSED、修正commitは本1840と同commit、完了2026-10-25。既source byte/44試験/coverageを変更しないので再compile/全回帰は実行していない。全941/current全classの要求-TestID-実行trace完成を宣言しない。

開始0.5/1.5/4pp cap10、fresh48残52→fresh48残52/reset1793382075、共有丸め0≠専有0。usageae44df6a5e61b4abadb690c5ae24da87440f50a78dfd72bf0d28386ca890bb63/03:27:05→03:51:16JST、explicit新record0/完全性未証明、N/T/工数/専有費null。原-v4-v5/群開始値/追加発見1725/初回rule補完/再認証/tool費を分離、技術653TestIDs/34Main・正式1964-53/原190新受入0/QA051final/PTALT0/全actualHOLD不変。

全metadata tool真正終端回収済/製品jobなし。次8962公開scan/保存push→G07秘密情報scan又はC07残観測hook等の最新後続成果・実command/安全条件を限定確認し、可能な独立PG/PTへ継続。実VM/Root/native/DB/Backup/鍵/intent/permit/配備/拒否未特定操作は保留、原本等を保全し通常小区切りで停止しない。
