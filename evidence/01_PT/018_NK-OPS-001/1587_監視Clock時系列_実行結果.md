# 1587 監視Clock時系列 実行結果

source `3b2ef576cf46763d67a9e2914dc547afd2f93ef6`、1586/group1842。PG7166-observation-clock-host-v1原SHA `14d1f4480673564e5d542b936339bd424e9f08b8c9dae713506aa5fec8b94238`、真正verify0/91PT13suite/FES・rerun/flaky0/六format0。新clock8＋必要同package83であり、旧83を当sourceへ加算した数ではない。実Clock/LongSupplierは固定port fixture、OS時刻の変更・実Root等操作0。

PG7168-observation-clock-post-v1原SHA `580abe8ff4eea75f6f2fda9fbd45c787f16b468a2536f16590705734f23bdcc5` は全27Java source/実22class＋metadata1・単一session/CRC差0、**L447/M101/C22/B207全miss0**。親Enforcer/Spotless/lint/Werror/NullAway/SpotBugs/Checkstyle0。原点の符号と通常Long wrapを許し、逆行/epoch超過は拒否・UTC未読/状態未commitを実assert。UTC rollbackを値どおり保存しmonotonic elapsedで閾値期間を制御、constructor/null/Runtime/Error/非formatable/64並行の全固定vectorを確認した。

OBSCLOCK008はClock/FileStoreそれぞれRuntime/NPE/Errorの六複合fixtureで元故障同一再throw・資源閉鎖0・失敗時event不変を確認。次の正常観測では欠測flagを新旧両APIで消費し、critical回復を662秒から再開始、1261では未close/1262でclose。新時刻入力故障を正常観測やNPE正常処理へ変換しない。既context逆行拒否だけでは欠測flagを変更せず、旧FSINPUT010の直後64観測count65も維持した。

PMD raw21/exit4/processing0は、旧14の全source/指摘/個別理由が同byteのまま。残七行は次へ分類し、未知0/抑制0とする。

| 対象行 | 個別適用性とTest |
|---|---|
| FilesystemHealthMonitor.observe / AvoidSynchronizedStatement | CONTRACT_REQUIRED：既private lock・read→状態遷移の直列化、FSINPUT010。実provider有限性は未認定。 |
| FilesystemHealthMonitor.observeNow / 同rule | CONTRACT_REQUIRED：同ownerでclock採取と入力/状態を一pollに連結。OBSCLOCK008、新旧APIの欠測消費。 |
| MonitoringObservationClock.context / 同rule | CONTRACT_REQUIRED：tick/UTC採取成功とlast commitを一原子のprivate critical sectionにする。OBSCLOCK004005007。 |
| FilesystemHealthMonitor.observeNow / AvoidCatchingGenericException RuntimeException | CONTRACT_REQUIRED：欠測flagだけを残して同一再throw、正常returnしない。Clock欠測を次回回復へ橋渡し0、OBSCLOCK008。 |
| 同method / 同rule Error | CONTRACT_REQUIRED：同一Errorを失わず欠測flag、fatal抑止/原文処理0、OBSCLOCK008。 |
| FilesystemHealthMonitor.observeLocked / 同rule RuntimeException | CONTRACT_REQUIRED：unchecked入力失敗時の同一再throwと欠測flag、NPEを正常化0、OBSCLOCK008/FSINPUT004。 |
| 同method / 同rule Error | CONTRACT_REQUIRED：同一Errorと既eventを保存し、外側の失敗処理へそのまま返す。OBSCLOCK008。 |

lock順序はHealth→Clock（採取後解放）→TimedMonitor、逆向きcall0。固定fixtureの成功を実FileStore/Clockのdeadline保証にしない。実source/clock所有・polling・finite停止・制御/標準Micrometer exporter・全体451/native/CHR/当Web実行/正式認定は未受入。原4222/common44の確認再演0、新障害/上位QA等0、工数null/QA051final/PTALT0を維持。全command/時刻/環境/branch/source/input/XML/終了/counter/static/hashは元7166/7168へ保存する。
