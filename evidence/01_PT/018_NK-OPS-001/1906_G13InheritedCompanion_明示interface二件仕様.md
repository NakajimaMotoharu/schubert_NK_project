# G13.07・継承scope未確定二件の明示interface責任確認

2026-10-25 13:35 JST、G13_INHERITED_COMPANION2_INTERFACE_V1/WBS-G13.07、開始 .25/1/3pp・群cap10。fresh65残35/reset1793382075、停止はfresh現在窓残10%以下/取得不能。元予実・過去群費を現在残量から減じず、旧累計90抑制/小cap不使用。

対象は前ASTでINHERITANCE_UNRESOLVEDだったMorningCurrentInvalidationTestとMorningPreviousBrokerTestのみ。src/schubert-nk-batch/src/test/java/配下の同package/同Main責任を確認する。根拠をmapper実装前に凍結する。

|Test source|Main interfaceと明示fixture|canonical owner/cost|既Test ID/設計|
|---|---|---|---|
|dev/codex/schubert/nk/batch/file/MorningCurrentInvalidationTest.java|MorningCurrentInvalidation.Store / class Store implements MorningCurrentInvalidation.Store|WBS-P018-03|PT-OPS-MINVALID001..006 / OPS009 UI251 SS341343 SSC089105|
|dev/codex/schubert/nk/batch/platform/MorningPreviousBrokerTest.java|MorningPreviousBroker.Query / class Fixture implements MorningPreviousBroker.Query|WBS-P017-10|ISSSTOP001..004 / SSC131、closed generation/anchor/byte契約|

AST汎用検査が型の継承scopeを保守的に保留したことを不具合や誤判定としない。上記sourceのexact interface実装/static対象呼出し、元485 Main責任、正常9246 snapshot/current hashを照合し、同source既batch Jarのnested interface宣言をjavap -pで読み取る。Root/Morning/Artemis/journal/DB/Testメソッド/JUnit/VM/credential操作は行わず、追加target compileも行わない。既normal/原PT/先行337parseの確認再演なし。javapは宣言metadataだけでclass初期化/実行なし。

二つのexpected ownerは本literal表を独立oracleとし、旧624canonicalと元941/943/予算/acceptanceを保持。正規shape成功→cost一field等のmetadata反例・近傍規則不変/論理owner優先を確認できた場合だけexact候補を登録する。Expected source登録1449→1451/1789/test484→486/824、残340→338。これを動作PT/coverage/正式受入や全method/要求/TestID trace完了へ変換しない。終了後も未対応293複合/45helper等の独立PG/PTへ継続する。
