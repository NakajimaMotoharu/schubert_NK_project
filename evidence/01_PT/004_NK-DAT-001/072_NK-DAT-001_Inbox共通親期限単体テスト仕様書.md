# 072 Inbox共通親期限 単体テスト仕様書

Program NK-DAT-001 / `InboxCleanup.owned/boundTransaction/delete`、`MaintenanceOwnerFrame.Guard`。関連 OPS009/DAT009/MQ008、UI212/241/251、SS324/331/341§7.3/343§6.17、SSC119、BUG357。Production Inspector callerの結線/真正Unit受入は018の289、これだけではS2を認定しない。

| Test ID | 入力・事前条件・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-DB-INBOX-269 | 実PostgreSQL、既存LOGIN fixture1行、同親残6,123,456,789ns、restricted Inspector接続でinspectNext | 行0/DELETED、commit1/rollback0/close1/delete1。削除直前に別SQLでcurrent_setting=5s。5秒は残ns整数秒を切り下げ上限5秒から独立算出。接続前後/timeout設定前後/DELETE前後/commit前後の8観測 |
| PT-DB-INBOX-270 | 同fixtureを各回初期化、8境界各位置で既知IO失敗 | 1～7失敗は行1/commit0、8は既に行0/commit1でrollback0（確認済commitを取消済と捏造しない）。位置3～7だけrollback1、接続前はclose0。他はclose1。DELETE前までdelete0。診断を秘密provider文字列で置換しない |
| PT-DB-INBOX-271 | timeout SQL返値不一致/結果欠落/複数/SQL例外 | 行1、commit/delete0、rollback/close1、固定InboxMaintenanceException。expectedをProduction codecから作らない |

実行環境・command・Source・coverage・F/E/Sは073と後続manifestへ記録する。初回F1/E1は合格に含めない。Guardなし既存低位部品はnative actor承認の代用にせず、普通Inspector入口はprivate owner＋実kernel/managerを接続してから受入する。null/未知IO境界、CLOCK_MONOTONIC独立vectorは018/289 COWNER001～004も参照。新deadline境界の全網羅/真Unitは未認定。
