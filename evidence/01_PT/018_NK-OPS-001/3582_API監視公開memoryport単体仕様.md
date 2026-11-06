# API監視公開 memory JDBC port 単体仕様

Program NK-OPS-001 / WBS-P018-09、ApiOutboxObservationSource ctor/observe/get/missing・nested Entry。RD171/MON系、UI252、SS311/332/342/351・PG-D631/633。原部分sourceのwhole physical2を測定する。Production Main D8、変更なし、normal PG20112/SB PG20114をbyte/hash再利用。

|TestID|method|独立期待値|
|---|---|---|
|PT-OPS-OBS001|constructorsAndNullContracts|DEBUG/STANDARD以外と欠落を拒否。null呼出前の観測値を保持|
|PT-OPS-OBS002|standardDoesNotAcquire|両observeでempty、prepare/checkout/close0|
|PT-OPS-OBS003|borrowedPublicationAndMissing|固定PENDING3/SENT5/ERROR7とage2/4/6秒、getは同じOptional、missing後empty、借用close0|
|PT-OPS-OBS004|borrowedFailureClearsPriorValue|prepare SQL故障は同一例外、古い値を再公開せずempty|
|PT-OPS-OBS005|borrowedInvalidationRaces|PS close前に別threadでmissing、解放後も古いreadのCASはfalse、bounded待機|
|PT-OPS-OBS006|ownedPublicationAfterClose|新規自己所有proxy一つ、readonly/readcommitted/rollback/close後だけpublish。未確認callback0|
|PT-OPS-OBS007|ownedInvalidationSuppressesPublication|close hookでmissing、正常readでもCAS false、再公開なし|
|PT-OPS-OBS008|ownedOneShotFailureClearsValue|成功済み同attemptの2回目は公開入口のone-shot IllegalStateException、checkout追加0/観測empty|

FixtureはJDK proxyの合成行・固定Instant.EPOCH、SQLはSS351由来の独立literal。expectedをProductionから生成しない。実DB/SQL送信/SDK registry/clock thread/OS/Root/VM/credentialなし。新Test全8を一度に実行し、F/E/S/abort0、正常Main JARとのCRC/入力hash一致、単一JaCoCo session/四counterを独立postで検証する。Coverage未達は未達のまま。nullを正常扱いするProduct変更なし。

ApiReadOnlyObservationAttempt内部の失敗回復はheld TemporaryInfrastructureExceptionへ到達するためNOT_RUN_HOLDとし、その例外・実環境・pool障害の動的資格は本8へ含めない。成功read/一回用入口の既使用拒否は別独立経路であり、held failureの代替実行ではない。元20Testや他SDK試験は変更/合算/成功再演しない。8件のPASSを監視工程全体の完了としない。

Command/environment/source/run/終了code/hashとcoverageはshared012/profile052のmanifestおよび結果3583へ保存予定。障害発見時は修正前にBUG/YKT起票。正式1964/53・工数null・新leaf0維持。
