# Root反復読取の費用測定・共通化候補

2026-10-16、NK-OPS-001/OPS009/SYS002/UI251/SS311/343/353/451、SSC295/BUG1332/YKT1098。配備7bb/PG3976/BOM0a409301/guest79aは不変更。候補Main **964e96e45bb588e7e75798b5adf425cbd9985427**。正式1964PT/53scope・工数null・QA051final保留。以下は限定診断/試作でありProduction PT追加0、Root/PGPT又はIT/ST完了ではない。

## 固定観点と実測

Linux/JDK25.0.4の同VM、固定7fieldのreadonly data読取、各相20warmup＋200反復。Root/Child capture/認可・DB/Unit/permit/start/stop/reload/VM操作0。実装の観測値を独立expectedへ流用せず、相内raw安定性を測るだけの比較と全7propertyの独立cross-process比較を区別した。全相は新私有namespace、元process結果だけを回収し再演していない。

| Test/元job | 結果・解釈 |
|---|---|
| COST4392/4040 | /proc型取得200回、JDK20.5～24.3ms対fresh statfs2.59～5.67ms。単独では32秒級の合成費用を説明しない |
| COST4394/43301 | 実Root NativeIo7field200回715.7ms、proc24.4ms。capture/Root資格は未実行 |
| COST4396/51077 | immutable binding200構築=Directory51.0ms/security12.1ms/FS3.59ms、regex200000回409.7ms対compiled29.2ms。どれも主因と断定せずMain不採用 |
| COST4400/71731 | exact ABI adapter候補ABBAの7field200回:旧665.1/549.1ms対候補599.6/558.8ms。順序ドリフトと区別できず不採用、Mainへ反映0 |
| COST4402/21442 | 実Child NativeIoのsystemctl7field200回5621.3ms。既in-processとの差が明瞭 |
| COST4404/19338 | 候補共通読取ABBA:旧5851.6/5620.0ms対候補585.7/665.8ms。速度の限定証拠だけ、全7値同値受入は後続 |
| COST4406/13383 | 四child全0後、raw行順を値差と誤判定し工具1。BUG1354/YKT1120、旧失敗を保持 |
| COST4408/87255 | 全7property/key/valueの独立canonical digest **333c00d79716cfb56db7f910a2b76c299e57aa60d8b26eddf68d2a914ce21ff0** がABBA全相同一。旧5547.8/5496.1ms対候補593.4/502.5ms、約9～11倍。候補3source hashは公開manifestに記載 |

4406の独立原因確認：systemctl rawのInvocationID/MainPID順と要求順の入替だけで、旧rawSHAd5b7c3d5・要求順SHA83a4e786を説明できた。外部固定長/HTTP/署名/原本のbyte順oracleは変更しない。4408は全7keyの欠落/未知/重複/ASCIIを独立検査して比較し、各相rawの200回同値を残す。Production Childの前後raw二読/全kernel/NSS/所有条件も維持する。

静的call-countの補正：BrokerのreadObservations成功一回にはparent guard201回・全scan804回以上。これは実Root時間ではない。また988のgraph-first/secondはそれぞれobserveStartup内部で二scanするので、合計431824112nsは**四scan**であり、二scanとする過去説明は訂正する。MorningDB recheckへ全BOM reload費用を加算する根拠もない。現UnitのCPUQuotaはinfinity/system.slice cpu.max=maxで、quota絞り込みを主因と決めつけない。

## 候補の実装と独立PT

SSC295/PG-D422：旧batch LinuxSystemdQuery/Session及び独立試験をbootstrapのSystemManagerObservation/Sessionへ移動。RootNativeIoは固定Service名対応、ChildNativeIoは既五固定observerから同readerを使う。各readの新bus/arena・固定local socket・owner PID1/euid0/unique前後・全7/4field・元5秒・全RPC/handshake期限/unknown close保持・owner threadを維持。全graph二読/境界回数・NSS/kernel/世代・元1800を削減していない。公開窓口は固定enumの非秘密data読取のみ。

PT-OPS-MANAGER4404-001=八Unit literal/全field/各二新Session・前後owner/close、002=五Child route/null/全fresh、003=両内部行順で同parent二読/byte消去、004=同一操作中の行順driftは依然拒否。既MANAGER817全method/例外/null/thread/timeout/UNKNOWNを所属変更だけで保持。old→new class名の一対一対応を全体資格で確認する。

PG4412（元73479）はstorageのliteral NoTests gateでMaven1、対象0/0suite。BUG1356/YKT1122、試験未実行のまま保持。gateを無効化せず、必要な新source六module全体 **PG4420/元79478**（3721/545/1644予定）を一回実行中。完走/全XML・Main inventory・静的・同source独立資格前は成功へ算入しない。BUG1355/YKT1121のhost/emitted静的分離も工具独立試験で是正し、工具4件をProduction PTへ加点しない。

## 証跡・次工程

公開 `evidence/provisional/PG4410-root-cost-components-v1/manifest.json` SHA **b25fa5f57005b87c7543e6f4fa9c58953114d5ea08ee4e2d614c455a6a2984fc**。元全8manifest/実測/候補hash/旧4406actual1を非秘密fieldだけで保全。全private stdout/stderr/class/owner/実入力はWorkPG379とguest同名new-only保存先に残す。秘密scanの正式0を主張しない。

設計only PR141/main **48b3856c01326ebecb9224733a4905d458ba2381** を通常merge/remote確認。実施design5860fc6e7、隔離201c842c4。添付toolは既100件上限で拒否、旧添付削除せずURLを台帳に保存。未受入Main/code/tools/evidenceをmainへ混入0。

次=元4420真正結果/独立source・全旧ID/物理差資格→必要新source署名/正規unused・RO・有限公開/独立post→新一回通常Root・当source native/Browser/CHR/F03/四100/451/trace/引継ぎ。限定9～11倍をRoot全体の短縮率や30分達成見積りへ換算しない。旧Root143/旧close UNKNOWN/全原本・DBBackup・鍵・native58・37startupを保持し、既4384回収及び旧全3717を再実行しない。
