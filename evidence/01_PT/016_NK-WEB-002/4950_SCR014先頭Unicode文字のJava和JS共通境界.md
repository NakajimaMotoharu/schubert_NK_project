# SCR014先頭Unicode文字のJava・JavaScript共通境界

WBS-P016-25.02/2／P016-14参照。FUN-008、UI225／235、SS313／352。既存PT-WEB-280とPT-SCR092-Eへ同じ独立固定値を追加。U+FEFFはUTF-8のEF BB BFで3 byte。先頭にあってもFieldの値であり、ASCII trim範囲に入らない。続くASCII aを253個にすると256 byte、254個にすると257 byte。Javaは256を受理し先頭文字も照会入力に保持、257はLENGTH。JavaScriptも256を受理、257は固定の長さエラーを表示して原入力を保持する。期待値を対象コードから計算しない。

PG43616、Core87927ea、試験fixture二つのみ変更。Java既存10件とNode既存8 subcaseが全成功、失敗・skip・未実行0。製品Java対象3 classの単一exec L109/M25/C3/B54は全到達。実script単体のNode line/function/branchは各100%。NodeのsubcaseをJava件数へ加えず、PG43614の旧試験結果は別保存。明示一Java fixtureのCheckstyle指摘0・formatter差分0。新規Test ID、製品動作変更、実Browser/HTTP/DB、正式451の追加0。

[実行と入力](../018_NK-OPS-001/evidence/PG43616-scr014-leading-bom-literal-contract/manifest.json)・[局所静的検査](../018_NK-OPS-001/evidence/PG43616-scr014-leading-bom-literal-contract/fixture-scoped-style.json)
