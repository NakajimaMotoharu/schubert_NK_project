# 管理metric接続・所有の限定照合

group2043、主P018-09/C07追加費0、開始fresh42残58/reset1793382075/0.5-1-3pp/cap10。Production3613b2742不変更、管理文書/工具だけ、製品Test0/Main0/新受入0。PG8734-management-metric-owner-audit-v1/manifest.json SHA `854af6f7a3f4845f2c2dbb65765da97956a1cd9dc0609f5d989085e143ba5060` に固定11public source/正式SS3docのhash/限定行番号/事実を保存した。origin/mainはfetch後 `8b91944df5820535e23ba2469740f1c0aa94c447`、SS正本は同commitのgit showから読み、branch設計を正本と読み替えない。

|対象|確認できたpublic source事実|後続依存|
|---|---|---|
|API/Web NonSecretConfig|共用bootstrap内の互換binary名、nk.monitoring.mode=STANDARD default・strict STANDARD/DEBUG検証済み、common.ymlにも同値|新設定key/共用framework/credential配布は不要、起動側が既valueを渡す|
|ApiManagementServer/WebManagementServer|既GET /actuator/prometheusはlegacy ready gauge、当2managerと限定2callerにCustomMetricPayload/StandardMetricSource consumerなし|full payload供給とmode受渡し、失敗応答・ownerを後続PG/PTで接続。これは限定source検索で全動的実行不在を証明したものではない|
|API普通起動|既ResourceScope/ownedReleaseでmanagement bind後の所有捕捉→start→consumer、SS342 SSC158/316も同契約|metric context ownerをmanagerの外側・applicationの内側で先に捕捉し、明示SDK初期化後にmanagerへ供給する必要依存|
|WebNativeRuntime|managementを保持してからstart/promote、close phasesはHTTP/retry/replay/replies→management→assets/transfer/codecs/broker|新metric contextはmanager終了確認後・外側借用資源解放前に閉じる。未確認closeを成功にする/timeoutを無視する変更はしない|
|SS311/342/351|bootstrapは非秘密parse/固定role credential領域、業務HTTP/JMS禁止。管理port非proxy loopback。詳細はDEBUGだけ、STANDARDは最小health、外部通知追加なし|role内metric実装を維持。Ops credentialをAPI/Webへ渡したり、新transport/監視target/権限を推測追加しない|

次の許可済みPGはAPI/Web各roleのMetricContext<T>。constructorはresource-freeで、callerが保持してからinitializeを明示実行、固定custom registryと既standard ownerを内部に保持する。custom initializerは既にcallerが所有する入力を使った非resource bindings登録だけを行い、返されたbindingsを強参照で保持してGaugeの弱参照脱落を防ぐ。initializerでDB/JMS/worker等の新資源を取得しない。STANDARDは両SDK/initializer未読、DEBUGはcustom設定後に標準をbind、部分失敗時は再initialize/成功renderを拒否してcaller closeまで所有を残す。renderは既full overloadへ借用供給し、closeはstandard→custom registry・失敗未確認保持、private ReentrantLockで直列化する。

このcontextは構造的初期化だけを表し、全custom観測の取得/鮮度/全catalog充足・service readinessの証拠にしない。missingを0や成功へ補完せず、実観測collector/producer hook/管理handler供給は別未完として残す。bindings参照はcaller-owned metadataであり、contextがDataSource/credential等を暗黙closeしない。実endpoint/default socket/Root/VM/native/DB/Backup/鍵/intent/permit/配置/権限・拒否対象未特定操作HOLDを解除せず、既current/runtime生存や過去成功も推測しない。

終了fresh42残58/同marker、共有丸め差0≠専有費0・N/T工数null、usage9c2eab81 cursor継承/明示usage完全性未証明。技術累計480Test/27Main/正式1964-53/原190新受入0/QA051final/PTALT0/whole451・元-v4-v5/欠測/原本stash等を不変維持。監査完了や報告だけで停止せず、次群の着手見積とfresh枠を固定して上記PG/PTへ進む。
