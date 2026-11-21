# JDBC二資源closeと抑制例外順序の単体仕様

Program NK-DAT-001、WBS-P004-05/2、DAT-009／AUT-004、UI226／241、SS332のSSC-424／425。対象は `JdbcResourceCleanup.closeRows` と `closeStatement`。元のPT-JDBC-CLEANUP001～007は [既存試験の現候補証跡](../018_NK-OPS-001/evidence/PG41742-p00405-jdbc-cleanup-current-seven-v1/manifest.json) に記録する。

| Test ID | fixtureと操作 | 独立期待値 |
| --- | --- | --- |
| PT-JDBC-CLEANUP008 | 固定のSQLExceptionを主例外とし、別のRuntimeExceptionを抑制済みにする。JDK上のResultSet代理はcloseで別のSQLException、Statement代理はcloseで別のErrorを送出する。同一主例外を保持した呼出元のfinallyで、二つの型付きcloseを行→文の順で呼ぶ。 | 観測する主例外は入力の同一オブジェクト。呼出履歴は `rows, statement` の2件で各1回。抑制配列は入力の既存、行close失敗、文close失敗の順で、各要素の参照が入力と同一。 |

行と文を閉じる順序はこのfixtureで明示する。資源の取得・接続・実SQL・transaction・外部認証は実施せず、リポジトリや業務取引でのclose順序は個別試験に委ねる。本件は順序と同一性の観測。例外・null・成功の直交表は元001～007で維持し、各ケースの証拠を合算して全451の判定には用いない。

製品は既存の2物理クラスをSHA-256で固定し、試験classのみをJDK 25でコンパイルする。独立fixtureの書式、Checkstyle、SpotBugs、PMD、選択した1件のJUnit結果をPG41744のmanifestへ保存する。実行コマンド、入力と出力のSHA-256、終了コード、関連障害は同manifestから追跡する。
