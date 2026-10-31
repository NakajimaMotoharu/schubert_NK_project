# Expiry成功監査・JDBC資源scope原whole24 単体テスト仕様

2026-10-31 / PG-D977 / 群3389 / 主WBS-P017-11、共有BatchRepositoryException担当P01702は追加費0。開始1/3/7共有pp cap10固定。現Production6b53/normal14216、原ExpirySuccessfulScopeTest全24（PT-EXP-4956-001～024）を変更・抽出せず現在sourceで初回実行する。旧4972/59は別source歴史で転用/再演しない。

関連NK-BAT-001/DAT-009/OPS-009/UI251/SS331§8.2-8.3/SS341§9/SS343/SSC304。Test全548行・Main ExpiryAuditRepository全459行とBatchRepositoryException全文を読取照合。呼出はstatic verifySuccessfulAudit/usingJdbc/required、Snapshot immutable valueと固定例外だけ。実Repository constructor/SQL/Connection/DB/run owner/expiry削除/原本/Backup/鍵/Graph9/Root/native/外部は呼ばない。JDK Throwableのsuppressed/TWR oracleは二held例外classifierの再実行とは異なり、当二classを一切呼ばない。

正常・境界・異常期待は原Testの固定SUCCESS、観測時刻2026-10-17T00:00:02Z、同値/±1ns、独立status六値、空でも非nullのcode/summary拒否、null audit/observed/三port、取得null/取得失敗・callback構築失敗時の未所有/未呼出を使う。JDBC portは自己Object/lambda/AtomicInteger/Listだけで実接続なし。取得→body→closeの順、元failure identity、12組合せの抑制、nested reverse close、同一secondary重複・self-suppressionのIllegalArgumentException/causeを、**production helperを使わないcompiler-generated Java TWR**と明示assertionで確認する。

8physical全SourceFile=ExpiryAuditRepository七（outer/Stage/Prior/Snapshotと三NoCode接口）＋BatchRepositoryException一を分母に保持。outer/staticとSnapshot/固定例外だけ実行想定、Stage/PriorはCodeを持つ未実行、SQL/成功原本取得など全未実行methodも分母へ残す。正常24成功でもwhole repository/DB/削除業務を完成扱いにしない。NoCode実flag/全methodを独立検証し、自然branch0と厳密四100を区別する。

元Test class/method・入力hash・日時/JDK/OS/branch/command/終了code/XML/exec/session/CRC/全source counter・関連BUG/SSCをmanifestへ保存。期待値は原固定literal/TWR参照、今回新fixture/production methodでexpected生成なし。四held/六nativeの当session true probe不在を独立読取確認する。失敗/skip/未実行/別sourceをPASSへ加算しない。新障害は修正前915/916、未受入は維持し、正式1964-53/工数null/451/QA051final/HOLDは変更しない。

選定時：BackupManifestReaderTestはwhole24内1003～1020が実native adapterを呼ぶためNOT_STARTED_HOLD・部分抽出0。QuestionControllerTestは実security/API等の全依存未照合のため未実行。最大件数を理由にHOLDへ進めない。
