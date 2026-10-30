# Batch cleanup 原whole5・当source単体テスト仕様

2026-10-30。群HOST_BATCH_CLEANUP_PURE5_V1、着手前0.5/2/4pp（共有枠と専有費は別）、主費用WBS-P017-07.01。Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c、通常compile14216固定。NK-BAT-001/DAT-009/OPS-009、UI251、SS331/332/341/352。

元1981仕様のPT-BAT-CLEANVALUE003～006と、cleanup.ExceptionValueContractTestのPT-F03-EXC003を全methodそのまま選択。全Test108+22行、Main六対象と依存BatchRun/CleanupCounts全body・initializer確認済み。前者の期待値表は1981を継承（手計算7/4/3、累積WARNING10、zero/最大値、各null/減少/不一致、固定理由3値）。後者は各既存理由の例外messageが固定`cleanup did not complete`、cause=null、reason同一、null入力NPE。期待messageはproductionから生成しない。理由列挙の互換性全域は本例外試験で推定しない。

対象六SourceはLogCleanupSummary、CleanupReason、CleanupChunk、LogCleanupProgress、CleanupStopReason、CleanupStoppedExceptionの完全closure。依存BatchRun/CleanupCountsの全域資格は加算しない。不変値型/固定例外で並行資源・再送処理なし、DB/cleanup service/Root/VM/実ファイル/鍵/permit/intent/ネットワークを呼ばない。Graph/停止境界を検証する試験ではない。

command: `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14676_batch_cleanup_pure_five_pt.py`（PYTHONPATH=tools/quality）。元5/2suite/一fresh JVM・XML F/E/S/not-run0、同一exec/session/CRCをshared pure post14678で独立照合。normal全input・六Jar・固定静的14224・実JVM環境を照合、全SourceのL/M/C/Bを実測、自然branch0はN/A。未達は未達のまま保存。hash/日時/終了code/環境/入力/case/coverageはraw/post manifest、結果は2742。正式1964/53、歴史17/190、工数null、全HOLDは本限定群で更新しない。
