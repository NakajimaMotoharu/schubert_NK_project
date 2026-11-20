# InspectionSummaryRepositoryの単独SQL例外

Program NK-DAT-001、NK-BAT-001参照、WBS-P004-02/2、P004-05/2共有。DAT009／OPS009、UI251、SS331 §3.13、SS332 SSC063、SS311 SSC461、BUG-3416／YKT-2359、同原因BUG-2775。

INSPPORT011。実DBに代えて既 `InspectionSummaryPortTest` の借用JDBCインタフェースfixtureを使用。statement準備、query、必須値completeの読取、row.close、statement.closeの各1点でのみ、合成SQLExceptionを返す。元Errorはcause、suppressed、nextの先のcause各1経路に置く。計15 fixtureを1 Test IDの独立assertとして扱う。

期待は元Errorと同じインスタンス、Errorへのsuppressed追加0。準備失敗ではclose 0、query失敗はstatement.close 1、他3点ではrow.close→statement.close 各1。借用Connectionへのcommit/rollback/config変更/closeは禁止。正常SQL/UTC bindingは元INSPPORT001、SQL pair・null・不正値・同時観測・割込みは既suiteの独立期待を保持する。非fatal SQLは従来の固定診断を維持。再送やDB実行の確認は当fixtureの対象外。

未修正候補で新規1件のみを実行し、修正後に新規1と既Port全件、共通の非fatal循環を同sourceで検証する。JDK25、JUnit Console1.13.4、実JDBC・DB・原本操作0。Coverage／コマンド／source／成否・hashは実行manifestへ記録する。
