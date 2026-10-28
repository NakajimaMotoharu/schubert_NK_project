# 2486 API二Repository 四資源診断文脈仕様

2026-10-29、PG-D809予定、event2865/開始0.5/2/3pp/cap10/fresh24残76/reset1793774153、主F03・元P01809担当費参照内数。source17ab52b25/save396e70084（push38653真正0）、対象Main AsyncJobCountRepository.read/OutboxObservationRepository.read、PMD00386～00389。結果2487予定。

両Main全文と現13596 sourceを確認し、statement/rowsは取得直後null guard→Java9 try(variable)に入り、RS→PSを逆順closeする。借用Connectionの作成/config変更/commit/rollback/closeは行わず、正常return/Snapshot計算は資源解放後。null取得時にcloseすべき実体はなく、取得・timeout・読取・checked/unchecked/fatal・RS/PS close失敗はJava TWRの同identity/抑制規則で処理される。Mainコード上の資源漏れは確認しておらず、inline宣言へ書き換えるPGは不要と判断する。PMD内部の検出原因は未解明で、一般にJava9非対応とは断定しない。

PG13253/751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdfの実測findingは当二Main SHAと現13596に完全一致する。古いdb33という全sourceを現資格へ転用せず、固定同byte対象の診断根拠としてだけ使用する。既13384/86の18PTはsourcea75の歴史証拠のまま、当sourceのPT/coverageとして再計上しない。変わっていないMain/Testについて成功確認目的の再実行や全回帰は行わない。

13632は元global IDと当四findingの属性/順序/source/span/read method、取得→null guard→TWRの連続token/二所有域の入れ子/借用Connection無変異を照合。現normal型/null/compileと全1843静的は13596/99を参照する。四resourceを保持rawでCONTEXT_NOT_APPLICABLEへ分類し、suppressionや品質条件緩和0。13634は独立の固定四map/元診断位置/sourceと正常token・期待を変えた有限反例を確認する。レビュー/metadata検証以外の製品・JUnit・SQL/DB/JDBC呼出・VM/Root/native/鍵/実broker/資源操作0。

新refs四は個別source文脈の補完であって全F03 join完了ではなく、pendingも四追加して元未知を保持する。raw6247/Main1491/Test4756/corr3194、refs3349→3353、pending2488→2492・noRef2898→2894を区別。全995旧runtime/責任費/原941943/予算受入/正式1964-53/17-190/工数null/QA051final・全actualHOLD/原本保全は非変更。通常小群/報告/commitで止まらず、fresh残10以下/取得不能で保全。
