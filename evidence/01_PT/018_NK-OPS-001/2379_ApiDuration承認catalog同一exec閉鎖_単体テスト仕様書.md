# ApiDuration承認catalog 同一exec閉鎖 単体テスト仕様書

2026-10-28 / PG-D758 / 2377-2378の残6L1M1B / NK-OPS-001・RD171 MON010..013・UI252/SS351・411・451。source639bbc777593cd98d95db1b0316e8113b40b886b、save802dc3bd1e0bf0ee45fc092fd66e4e60db85e5d4/push64732真正0・origin同一。Main/Test/設定/SDK byteは不変更、normal12766/39678a3cの成功を確認だけで再compileしない。

着手前見積2/5/8週次共有枠pp・cap10。主費WBS-F03、canonical source owner/costは実12774 registry rowで照合してから固定、P01809参照追加費0/専有null。原計画/v3-v5/元費不変更。対象は原ApiDurationMetricExporterTest全24＋必要ApiMetricScrapeTest全14＝38/二suite。先行456/460の次予定40は足し算の誤りで、実行/見積凍結前にevent2741で追記訂正、原記述/元2740は保全・40実行へ加算0。実PTの独立結果24を38へ算術合算しない。

PG追加変更が不要な根拠：既Mainのapproved APIとそのcaller policyは実装済み、今回のgapは当24にgeneric APIだけを選択したことによる未実行path。Main全本文/必要recorder・固定Protocolのclosureを確認し、変更要否と既独立oracleを審査する。問題が判明すれば修正前BUG/YKT/必要設計台帳を起票し、無根拠な期待値変更をしない。予定はcode差0の製造レビュー＋通常PT接続でありPGを無条件省略するのではない。

ApiMetricScrapeTest全569行を読取済み。014はapproved Summaryを直接呼び、001..013もpolicy経由でapproved Gauge/Counter/Summaryを呼ぶ。全14の既helper/Fixture Bundle・独立literal/元有限4worker64task/10秒Future/TWRを保持し、Main純値/SDK recorder全closureが確認できてからPT_DEFAULTを確定する。DB/JMS名のrecordersは自己Registryへsynthetic Counts/Durationを入れるのみで、実connection/resourceを取得しないことを本文で確認するまで未資格。部分抽出/拒否範囲の言換えやSnapshot key-close/Root/実VM/nativeへの接続はしない。

SUMENC001..024は2377表全件、APIPOL001..014は既仕様を継承。001STDはsource/value0read、002全16family/900sample/51NaN、003供給値3/3.5/1ns/1.5秒とCDF literal、004mode非破壊、005空compatible、006非対応sourceの固定拒否、007null/未知modeのread0、008closed非再開、009Runtime/Error identity、010後続label失敗でpartial返却0、011未知provider未読、01264並行callbackの同literal/非close、013三codecのpoisoned synthetic labels拒否/別owner回復、014name/tag/value各一回・捕捉後のfake mutation非反映/3・2・.1固定値。期待はTest手書き数値/SS label閉集合で、Production methodから生成しない。

前24の成功を単に確認する再演ではない。全scope同source/同run条件でgeneric24とapproved14の両枝を一fresh JVM/一execに含む正規38を一回実行するための必要回帰。旧24exec＋新14execのcoverage unionは禁止。normalの全input/全jar/全Test/SDK同byteと唯一定義を着手前後に検査し、immutable snapshot内の全38methodだけを選ぶ。外240秒/自己空CWD/extensions autodetectfalse、failed/flaky/skipped/notrunを成功へ含めない。

新38→独立全XML/CRC/全1843Main/1962Test同byte・完全六artifact counter/ApiDuration method別miss0を確認し、全artifactや他Mainが未達なら保持する。必要な当2Test PMD/CS/同sourceSB（元六SpotBugs0のinput不変は参照可能、code変化時は再検証）・Thread文脈/原owner/trace/終了依存を結合する。immutable工具/証拠の新only保存、2390等の先回り完成宣言はしない。実source/run/日時/環境/終了/command/期待実際/coverage/hash/BUGはPG12784以降と2380へ。

正式1964-53/17-190/工数null/QA051final/全F03-451/CHR/HOLDは維持。全scope品質の限定達成を全PGPTにせず、群終了後も現行477の通常停止条件まで独立PG/PTへ継続する。
