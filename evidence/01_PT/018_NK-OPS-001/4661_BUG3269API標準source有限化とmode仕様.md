# BUG-3269 API標準監視sourceの有限fixtureと固定mode

WBS-F03/2-2、P018-09、SS351／354、APIHOST001〜016、元1808/1809。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。016の実測待機・scrape＋close作業・元assertionを保持し、fixtureのexecutor暗黙closeを外す。release・shutdown・await10秒で終了を確定した後だけtest本体から登録ownerを再closeする。元2worker／二latch／全Future10秒を保持。004のDEBTfとSTANDAQcは許可modeと同hashの異値（PG39230独立値）で、固定CONFIG_INVALID、先行取得0。元bind/scrape別のnullと通常未知値も維持する。

Micrometer 1.17.1と元POM 1.7.0のPrometheus SDKに依存し、自分のregistryに限定。SDKの座標とローカルJARを実commandと一緒に保存。外部export先、HTTP、業務サービス、OS process、DB、保護型は使わない。JDK25.0.4／Maven3.9.12／dev-foundation、同試験commitで元16、独立XML・実終了・CRC・静的・生counter、PG39364に収録。旧API標準監視元13とJVM/System/GCの各試験は再演しない。0.4/1.5/3.5pp／上限5pp、元行価格追加0。
