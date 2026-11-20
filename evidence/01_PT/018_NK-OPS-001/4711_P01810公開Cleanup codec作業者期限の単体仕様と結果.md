# P018-10 公開Cleanup codec作業者の期限

NK-OPS-001、元PT-OPS-CREQ001〜007、SS341/342/343、SS351、451、BUG-3363。純メモリの二virtual taskだけを所有し、各futureを5秒待つ。成功・失敗いずれでもshutdownNow、最大5秒の期限内停止を確認する。既独立ASCII golden、入力消去、例外、再送時の同値、固定診断は維持。実Cleanup、file、認証、JMS、DB、Rootを起動しない。

PG40408は現製品Coreで既7件成功、F/E/S/未実行各0（選択範囲内）。新規の製品試験定義は0。製品クラスの変更は0。PG40410で元JUnitと現class CRC、唯一のsession、原Checkstyle/整形0とPMD生6件の全個別非該当を照合。PG40412は現byte 3物理に対し、対象外側 `CleanupWorkerRequest` の無除外で行40、method 12、class 1、branch 36、命令257すべて実測到達。補助 `CleanupProfile` と `BatchRun` の不足は残す。元別sourceのExpiry九件を合算しない。正式・全P018-10・451は別。

[単体](evidence/PG40408-p01810-creq-worker-bound-seven-v1/manifest.json) [独立](evidence/PG40410-p01810-creq-worker-bound-independent-v1/manifest.json) [生coverage](evidence/PG40412-p01810-creq-worker-bound-unfiltered-v1/manifest.json)
