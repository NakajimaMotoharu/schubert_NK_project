# API cleanup確認済みOutbox公開接続・PG/PT仕様

2026-10-25/PG-D633/NK-OPS-001/WBS-P018-09、RD171/UI252/SS311332342351。開始HEAD71314afe98b79e0227edf93198c99c57d8affb8f/origin一致clean、製品e87ab6ec8、fresh53残47/reset1793382075、低2/基準5/高9pp・cap10固定。1854-59の同一API観測経路を継続、元/v4/v5・正式1964-53/原190新受入0/工数null/全actualHOLDを維持。

既ApiOutboxObservationSourceへ型付きobserve(ApiReadOnlyObservationAttempt)を追加する。resource-free一回ownerは将来callerが先に保持し、このメソッドはprivate writer lock内でfresh Entry pendingを置いてattempt.readを一度呼ぶ。TX/Connection close確認後の結果だけをCASで公開し、missing後の遅延結果は不採用。get/missingは非blocking/SQL・SDKなしを維持、STANDARDはattempt未読、nullは状態変更前拒否。既borrowed Connection/asOf overloadの保証/本文を変更せず、generic checked callbackや新worker/Clock/Pool取得は追加しない。失敗/UNKNOWN/fatalはmissingのまま同failureを伝播し、再利用された一回ownerも自動再試行しない。

新OUTBOXPUBLISH001～014（ApiOutboxCleanupPublicationTest）＋変更cacheの必要旧OUTBOXSOURCE001～020=34/2suite。null/STD/正常/empty0、acquire/query/rollback/close/diagnostic SQL-Error、UNKNOWN通知中はcache未公開、同attempt再利用拒否、更新/immutable旧値、inflight missing二回のABA防止、memory service renderがSQL待ちせずNaNを返すことを独立fake JDBC/Clock/policy・固定wireで試験する。旧ROATTEMPT32は必要fixture outer compile-onlyで確認再演/加点0、既cache20は変更classの必要回帰として同sourceで実施する。latchはbounded/finally解放、sleep同期0。

source固定→9104 normal六→9106 actual34→9107 private lock個別現source判断→9108 cache outer/Entry全二Mainの実四counter（Entry branch0/0はNA・除外0）/静的→9110全1839Main見込/変更outerだけ・既1838同byte/240owner見込/五arch→1861結果・計測・公開scan・保存push。実DB/worker/caller/native/全451資格を推定せず、成功小区切りで停止しない。
