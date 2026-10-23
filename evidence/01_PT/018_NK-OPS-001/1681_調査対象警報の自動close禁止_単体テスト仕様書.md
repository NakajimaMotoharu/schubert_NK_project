# 1681 調査対象警報の自動close禁止 単体テスト仕様書

2026-10-24追補（元予測を削除しない）：初回source9c087705c/7548は204/F2・原df3badf1、AlertRegistryTest.ALERTREG002とMonitoringMissingObservationTest.MONMISSING001にも旧全72自動close期待値を検出。BUG1667/YKT1418のoracle対象へ追加し、SS351§12から独立に保護二condition×6service=12保持/他60closeへ訂正。欠測301→600→601の元5分境界はそのまま、元epoch/count/first/lastも保持を確認。新ordinary件数は204のまま・失敗2を合格へ加算0。Main一/Test四の五編集anchorへ更新、初回六compile7552は9cのPT0正常で歴史保存、新sourceは7548-v2（工具7549）/7550/7553正常六compile/7554/7556/7558で別資格化。初回三編集/予測sourceと混同しない。

NK-OPS-001/P01809/C07/RD171/UI252/SS351§7・12/353/BUG1667-YKT1418/PG-D553/group1899。既共通normal回復より条件固有禁止を優先する。AlertLifecycle.normalのDLQ/INTEGRITY_CONFIGは供給正常・原因flagだけではactiveを退役しない。手動調査・明示退役の実運用/永続/権限経路は本限定修正で追加・受入しない。

| Test ID / method | fixture/操作/独立期待値 |
|---|---|
| PROTECTEDALERT001 / AlertLifecycleTest.protectedAlert001AllKeysHonorNoAutomaticCloseDespiteConfirmedCause | 全12condition×6service×warning/critical×両cause。0秒異常→1秒正常→1日正常。DLQ/INTEGRITY_CONFIGはCONFIRMEDでも同event/count1/first-last0を保持。その他warningは5分後close、criticalは10分後かつCONFIRMEDだけclose、未確認ならopen。独立固定閉集合で期待値を作りProduction判定を期待生成へ使わない |
| PROTECTEDALERT002 / AlertLifecycleTest.protectedAlert002ConcurrentNormalSamplesCannotRetireOrChangeProtectedEvent | protected二condition各critical0→64callerが同MAX elapsedと両causeを供給、全同一immutable event/open/count1/元時刻保持。private lock/別owner分離とoverflow非発生 |
| MONPIPE003 / MonitoringPolicyEngineTest.monPipe003EveryCriticalEndpointAndCauseAwareRecovery | 既全12criticalに0/600正常・未確認/確認を供給、保護二keyは残存、他10だけclose。最後のactive順はDLQ→INTEGRITY_CONFIGの2件。既count1/level固定期待値保持 |
| 既ALERT/ALERTCONT/MONPIPE/全monitor | 正常初期empty、重複/昇格/5分10分厳密境界、gap/null/逆行/clock jump/最大elapsed/並行、他10条件の正常復旧を変更しない必要回帰 |

当source新2＋必要既202→204普通PT/27suite・55Java予定。全正分母四counter/NullAway・lint/実静的/同source CRC/session、生成23型82methodは除外設定を変えず当独立ordinaryとbyteへ結合。全1750Main/元1669debug込み不変・全94sourceの三編集anchorとsource/runを検証予定。原202を新sourceへ転用せず各原manifestの環境/日時/OS/tool/branch/command/exit/XML/input/output/hashと1682へ結合する。

run7548/独立7550/正常六compile7552/全Jar7554/trace7556/review7558、失敗・未実行を合格へ加算0。原group3/5/9pp上限10/fresh25開始・元-v4-v5/窓0/reset1793306748不変更。実装とoracle手戻り・新case2/必要既202/toolを区分し元製造新規0/原190受入0。正式1964/53・工数null/QA051final/PTALT0/whole451-native-CHR/actual全HOLD不変更、実DB/VM/Root/通知/調査/退役操作0。
