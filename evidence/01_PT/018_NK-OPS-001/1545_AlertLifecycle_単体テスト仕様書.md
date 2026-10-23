# 1545 AlertLifecycle 単体テスト仕様書

2026-10-23、NK-OPS-001/P018-09、C07共有参照、PG-D519。SS351§7/10・SS-D044、RD MON005～009/013、UI252§6を正とする。着手見積1/3/6pp、工程上限10pp、共有使用6/reset1793306748（開始0継承）。未実装の元計画内alert状態責務を補完し、C07監査費や元受入数へ混入しない。

AlertLifecycleは一つの閉condition/service keyの純粋state owner。AlertRegistryは固定12condition×6serviceを一つずつ所有し、同keyの多重openを防ぐ。入力は既判定Severity NORMAL/WARNING/CRITICAL、明示CauseClearance、UTC Instant表示時刻と同owner起点のmonotonic経過Duration。実metricからseverityへの閾値計算/実時刻採取/外部通知/制御/永続化は本工程の能力に含めず未完。壁時計jumpで回復時間を短縮しない。欠落/負/逆行tickは拒否し、未知を成功へ補正しない。

alert中の違反観測を一回としてcount(BigInteger、overflowなし)とlastSeenを更新し、正常観測は違反countを増やさず連続正常期間を進める。CRITICALはWARNINGへ自動降格せず、連続正常10分かつ明示原因撤去確認まで保持する。WARNINGは5分正常でclose。再違反で正常期間はリセット、close後の次違反だけ新event/count1。NORMALのみではopenしない。閉snapshotは呼出側へ返すがactive状態から退役し、操作対象/condition/service/level/count/時刻だけの不変値とする。これは新しい外部仕様でなくSS351の内部状態遷移の具体化である。

PT_DEFAULT：純粋な閉enum/数値/時刻と自己所有executorだけ、実VM/DB/鍵/Root/native/monitoring service操作0。全状態/正常期間は独立literalで操作し、Productionの戻り値からexpectedを生成しない。既mode7/catalog6は同packageの必要回帰13、元4222/common44確認再演0。

| Test ID | 入力/操作と独立期待値 |
|---|---|
|PT-OPS-ALERT-001|初期NORMALは空、初WARNINGは同key・level/first/last/count1/open=true、全getterとsnapshot不変 |
|002|同違反反復は同key/first維持/count2、CRITICALへの昇格と後続WARNINGでもCRITICAL維持、lastSeen更新 |
|003|WARNING連続正常0/299.999999999秒/300秒、直前open・到達close、原因未確認でもWARNINGは回復可 |
|004|CRITICAL正常599.999999999秒/600秒、原因確認のみ又は時間のみは不十分、両方成立だけclose |
|005|正常中の再違反で期間リセット、両levelの境界を再確認 |
|006|close後のNORMALは空、次の違反は新first/count1。過去snapshot不変 |
|007|constructor/null4引数/負Duration/逆行tickは契約違反、例外固定で既state不変 |
|008|UTC壁時計の前後jumpは正常期間へ不使用、monotonic Durationだけで判定。極大Durationもoverflowせず正判定 |
|009|同tick64並行の返却countが2～65一意、最終65・first同一、callerがthis monitorを保持してもprivate lockで進行、finally全executor終了 |
|010|閉12×6全組合せのidentity保持、unknown/free文字列を受け付けるAPIなし |
|PT-OPS-ALERTREG-001|同key反復は一active/count2、他keyの初回は独立count1、active一覧immutable/順序固定 |
|002|全72keyでopen・一覧72、全回復後一覧0、過去snapshot一覧72は不変 |
|003|null key/service/観測引数を拒否、他key/既state不変 |
|004|64並行同keyは一active/count64、異key不変、finally全executor終了 |

要求coverageは当package全実行class/method/line/branch100%、null静的解析/通常負試験、PMD/Checkstyle/SpotBugsと個別適用性、原XML/CRC/単一session、source/fixture/hashを保存する。副作用を持たないためDB TX/再送/rollback/実I/O故障は非該当。真のlive条件や原因撤去の権威をこの型の成功から推測しない。実行command/source/結果は後続1546、未実行/失敗/skipをPASSへ算入しない。F03/actual全HOLD・正式1964/53・工数nullを維持。
