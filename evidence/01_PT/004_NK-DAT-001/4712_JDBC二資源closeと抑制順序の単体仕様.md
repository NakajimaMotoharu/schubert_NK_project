# JDBC二資源closeと抑制例外順序の単体仕様

Program NK-DAT-001、WBS-P004-05/2、DAT-009／AUT-004、UI226／241、SS332のSSC-424／425。対象は `JdbcResourceCleanup.closeRows` と `closeStatement`。元のPT-JDBC-CLEANUP001～007は [既存試験の現候補証跡](../018_NK-OPS-001/evidence/PG41742-p00405-jdbc-cleanup-current-seven-v1/manifest.json) に記録する。

| Test ID | fixtureと操作 | 独立期待値 |
| --- | --- | --- |
| PT-JDBC-CLEANUP008 | 固定のSQLExceptionを主例外とし、別のRuntimeExceptionを抑制済みにする。JDK上のResultSet代理はcloseで別のSQLException、Statement代理はcloseで別のErrorを送出する。同一主例外を保持した呼出元のfinallyで、二つの型付きcloseを行→文の順で呼ぶ。 | 観測する主例外は入力の同一オブジェクト。呼出履歴は `rows, statement` の2件で各1回。抑制配列は入力の既存、行close失敗、文close失敗の順で、各要素の参照が入力と同一。 |

行と文を閉じる順序はこのfixtureで明示する。資源の取得・接続・実SQL・transaction・外部認証は実施せず、リポジトリや業務取引でのclose順序は個別試験に委ねる。本件は順序と同一性の観測。例外・null・成功の直交表は元001～007で維持し、各ケースの証拠を合算して全451の判定には用いない。

製品は既存の2物理クラスをSHA-256で固定し、試験classのみをJDK 25でコンパイルする。独立fixtureの書式、Checkstyle、SpotBugs、PMD、選択した1件のJUnit結果をPG41744のmanifestへ保存する。実行コマンド、入力と出力のSHA-256、終了コード、関連障害は同manifestから追跡する。

## PG43052 現候補の001～008同一実行

2026-11-23 JST。現Core `7698011f52`、検証source `046ffeb75a`。元001～007の独立期待を維持し、008のStatement→ResultSetの各一回close、既抑制→Statement失敗→ResultSet失敗の順と同一性を同一JUnitに含めた。現sourceの対象二物理は既許可のSHAと一致。8件すべて成功、F/E/S各0。同一JaCoCo原記録で生L21/M3/C1/B6全数、SqlCloseは抽象宣言のみ。実接続・トランザクション・実SQLと全451は別の未成立条件。[PG43052 manifest](../018_NK-OPS-001/evidence/PG43052-jdbc-close-001-008-one-current-exec-v1/manifest.json)
