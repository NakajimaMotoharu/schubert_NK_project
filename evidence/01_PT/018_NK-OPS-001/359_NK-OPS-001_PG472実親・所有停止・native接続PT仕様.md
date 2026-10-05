# PG472実親・所有停止・native接続PT仕様

Program NK-OPS-001、関連RD:運用/監査/互換、UI241、SS342343355/SSC190191193194195、451品質条件。Production source=c8ad413437be409f70ec37bdba33c5e3cd21790b、署名digest8e6bc3c26c1d707b5873dd14c229d41fa129bf7e5547dacc2bbc3780a90df3f1。工具/PT sourceは保存commitへ別対応、旧717成果を新sourceへ混合しない。

|Test ID|対象/目的|fixture・操作・独立期待値|
|---|---|---|
|PT-OPS-PG472-PARENT001|observer/外部親|真正boot e07、保存済み停止後移行/全9actual native archive/同current c8、全9Unit kernel空、namespace49/intent0を事前認証。Root durable CREATE_NEW予約後に外部Morning一回。元07:47:24/30min期限、同親2370133/Invocation f2742b789183406d86fddf2f851a390f/job194353、Root→ordinary samePID/INV/tick、専用NSS/zeroCaps/socket/5INFO。API/Web/Caddyと真正PID1 DONEまで要求、client0だけでは合格にしない。|
|PT-OPS-PG472-READ001|Pg472CompletedReadback|保存旧371行全14列をSQLの独立順序で完全一致。新10task列挙はBACKUP_DB/CONFIG・CLEAN_NOTIFICATION/QUESTION/SESSION/INBOX_OUTBOX/LOG/BATCH_RUN/TRANSFER/EXPIRY、全SKIPPED、件数0。canonical集合は13epoch×4＋epoch.current=53、旧48歴史byte/metadata保持、intent0。原本DONE/全Backup/Transfer保持。許可技術table以外不変、auth保存5/context暗号・時刻・有効上限2、bootstrap旧credential退役維持。期待値はSSと保存before原値/独立literalから作成。|
|PT-OPS-PG472-READ002|readback異常/null/境界|独立396assert：snapshot envelope/重複/欠落・23table固定、Boolean81組、namespace53/foreign/missing/null、PID1 journal全field/元1800秒境界/違世代、auth5/unknown/null、close/suppressed/fatal保持。正常値をproduction getterから生成しない。|
|PT-OPS-PG472-TERM001|Pg472NativeStop/owned helper|親正規DONE/同4peer/原期限/同current/signedをM-A-DBで取得、現在全381/23business/原本Backup/startupを私有保存、8逆順所有stopを一回（依存停止へ再発行0）。API/Web143は同boot/UID/PIDINV/fulljournal/cleanup→stopped→native完了/全kernel空と合わせ停止データのみ。全原値/全newscope通常return。UNKNOWN/fatal/close故障は所有を保持し成功へ正規化しない。|
|PT-OPS-PG472-TERM002|停止異常/並行/再送|独立Java retain matrix24＋Python265のfixed8/4peer/全field/foreign/null/missing/normal/depstop/途中例外・no後段・durable予約先行。既generation-independent native TERM witness28を使用。再stop/start/期限更新は禁止。|
|PT-OPS-PG472-NATIVE001|NativeSessions472/NativeCoverage|全8fresh single stream=親/Backup/Cleanup/Expiry＋API/Web Root/ordinary。各新Invocationのrole ID、Root0/Backup992:977/API999:981/Web997:980、single link/nonempty0600。元親startと期限及び所有TERM時刻に束縛。同frozen6のclass byte NoMatch0、line/method/class/branch missを全module報告。未到達は未達のまま、除外/agent attach/reset0、全100未達なら正式更新しない。|
|PT-OPS-PG472-CHR001|Current共有A01|真正TLS/同APIWeb/Caddy socket/公開CAの後に固定Current driver・golden CHR-A01と比較。DIF001/QA045 titleだけ許可、Current baselineは不変更。L01はQA051比較承認範囲だけ保留、未受入をPASSへ算入しない。|

実行環境host Linux/JDK25.0.4/JaCoCo0.8.15、VM Ubuntu26.04。実command/日時/branch/source/exit/XML/static/coverage/hashは次実行結果とsafe manifestに記録。396/265/24/28工具assertはProductionPTへ加算0。未実行/失敗/中断/skipは合格へ加算0。Raw journal/exec/DB原値・秘密はWorkPG379及びRoot700/600のみ、通常Gitへは件数/hashだけ。
