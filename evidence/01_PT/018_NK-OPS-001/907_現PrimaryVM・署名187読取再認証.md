# PG3428 現Primary読取再認証・Morning Unit補足

目的=後続候補native前の現在地確認のみ。開始前にLAN pinned host鍵・QEMU4599/t101242/argvf765c39c・専用active.qcow2・hostbootc7964823と、local forward20445/t104194/argvfd6ff71bをfreshで照合。既存管理22222へ接続し、SSC275のcurrent-management-critical.lockを非blocking所有、strict SSH host key/既private identity、guest sudoの読取のみ。二重VM/forward起動・旧authority復元なし。

PG3428/exec4230 actual0、guestboot79a3260a-e16d-42bf-942a-b914ed144c28・専用instanceid一致、現配備**a9/PG2802/BOM37bfe01a**の全187artifact size/hashと原manifest、固定別配備pinによる署名verify0を再認証。新4856候補は未配備。公開 `PG3428-primary-readonly/manifest.json` SHA256 **8b61f1e0cdf7f28f0b07a6920f8b306eeef460211deb8dd53dc27ba79af59dd3**。鍵実体/署名実体/credential/DB内容は出力せずhashだけ。DB全24/原本/Backupを今回再認証したという主張はしない。

API/Webはloaded/failed/各MainPID0/Job空を観測し、そのまま保全。Backup/Cleanup/Expiry/Inspector/Caddy/Artemisはloaded/inactive/dead/MainPID0/Job空。failedを自動resetしたりstop/startしない。probeに含まれたlegacy名schubert-nk-morning.serviceは**not-found**であり、Morningの停止証拠へ読み替えない。

直後に正規名**schubert-nk-morning-controller.service**を同管理gateで別の読取補完。結果=loaded/inactive/dead/MainPID0/Job空/Invocation空（空hashe3b0c442）。この補足は元3428結果を上書きせず、原not-foundも保持する。Unit/VM/DB/配置/公開/権限発行の変更操作は全0。所有・生存は当時点の観測で、後続の変異直前には必要なfresh再認証/正規admissionを行う。旧native/Root真正DONEの再実行・新bootへのauthority移植0。
