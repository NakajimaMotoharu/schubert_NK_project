# Storage七資源・一catchの所有解放レビュー仕様

F03/411451/SS311333341343352354、原1/3/7pp cap9、CONTRACT_AUDIT/ADDITIONAL_FINDING。PG22904 current29 raw88/分類23/未分類65のCloseResource7/EmptyCatchBlock1を全件source reviewする。factory return wrapperへの所有移転とcaller ResourceScope、no-op DirectoryStream、手動close assertionの途中失敗、子寿命独立、worker closeの失敗前cleanup、Executor shutdownNowとjoin保証、procfs snapshotで消えるinodeを区別する。

取得/移転/明示close/例外時close/worker完了/所有に関する根拠をsource hashと完全methodへ対応。実違反は修正前にBUG/YKTへ登録。通常規約をTestであるだけで除外せず、所有移転と意図的catchは個別根拠がある場合だけ分類。未確定のexecutor終了は成功へ変更しない。

当群はsource/rule/fixtureの変更・元Test compile/run/native/Root/実FS/VM/process/DB0。現29hash/原88診断/既分類23を保ち、別metadata postで8site一意と分類/否定guardを確認する。静的source reviewを実PT/coverage/451へ算入しない。修正と独立静的確認は次の限定群へ。
