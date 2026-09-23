# NK-WEB-002 Log経路親起動実行結果

PG231/PT-SCR127～131は正式`PT-WEB-20260924-22`/source`74bd4fcf`で限定認定。全1797PT（CHR41/Protocol80/Storage82/API710/Web512/Batch372）、failed/error/skipped0、Java6 module instruction/line/method/class/branch missed0、Production SpotBugs0、93負canary、46scope/hash・保存manifest再照合PASS。root manifest SHA-256 `ee6a7eb976e5abe7e82dc70527364c585a8f7b822e7e09dd427bedc714be962a`。隔離PostgreSQL/Artemis/実TomcatでWeb返信consumer1、Log worker、Login HTTP200/承認済みtitle、close後consumer0を確認。不正replyはDLQ1/terminal通知1で全体ready false。worker/DB起動失敗時の先行consumer解放、3資源の停止順・二次故障suppressed、10依存nullを検証。追加class instruction376/376・line71/71・method9/9・class1/1・branch22/22。Test ID/日時・環境・command・exit・input/expected/actual・coverage・file hashは`evidence/manifest.json`を正とする。実API dispatcher/credential/full broker readiness/実NK CHR-L01は未完了。

不認定履歴: 正式`PT-WEB-20260924-21`/source`fe760c18`はWeb PT-SCR128で1 failure（DLQ受信後、非同期terminal callback完了前に通知数を即時assert）、Batch未実行となり全体不合格。production仕様逸脱は確認されず、PT観測時点の競合と分類する。DLQ1と通知1の独立期待は維持し、両完了を上限5秒で待つ同期だけを追加した。run21を合格数へ算入しない。

同期修正後、PT-SCR128のみを3連続実行して3/3 PASS、追加class全5件の選択再実行も5/5 PASS。これらは正式全reactor/保存証跡の代替にはしない。
