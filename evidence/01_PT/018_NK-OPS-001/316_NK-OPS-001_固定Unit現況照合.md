# 316 NK-OPS-001 固定Unit現況照合

2026-10-03、BUG538/YKT382、SS343 MaintenanceUnit/451。手動の非定義名を正式Unitの不在へ読み替えた診断を訂正する。Production起動/停止/observerは正式名で実施済、Source変更0。これは工具/観測是正でありProduction PTの増加ではない。

固定対象は `caddy.service`、`schubert-nk-web.service`、`schubert-nk-api.service`、`schubert-nk-cleanup.service`、`schubert-nk-inbox-inspector.service`、`schubert-nk-expiry-cleanup.service`、`schubert-nk-backup.service`、`artemis.service`、`schubert-nk-morning-controller.service` の9。各 `Id` 完全一致と `LoadState=loaded` を必須とする。not-found/null/未知名/IO失敗は稼働証拠にしない。

当回Source91/boot58006280で全9 loadedを再照合。最新の真正終端は親334c正常30、API61b650正常143＋cleanup、Weba3437正常50であり、3者PID/control/job=0。Cleanup4c4f・Expiry8c1819はactive/exited・worker0、Broker084098fa/PID57990はactive/running。この時点で全8coldと記載しない。既存observer terminalとprivate actual full18（SHA701943c75adebf51e5ca41e3e48f52b874c2f62ce2933111a4d4e8f98fb26e2b）、PG430-native-parent-api-ready-web50 manifest56c5cb1598be2e66e4dcc1ae89b5c461c3f87f0fea2588514057c11a03e1b008へ連結する。非定義名照会の過去結果も破棄せず履歴として保全する。

次操作は最新Unit/Invocationを再照会し、SSC168のM下保存→正式8停止→全tree/manager二読→A/DB同原本で固定3intent退役する。現在状態は変化し得るのでこの記録を生存保証にせず、同start/配備/stop/migrationの二重発行を避ける。原byteはprivate、Gitにはhashと非秘密結論のみ保存、Production試験数/正式認定増分0。
