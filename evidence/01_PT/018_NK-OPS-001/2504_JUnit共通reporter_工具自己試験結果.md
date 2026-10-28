# 2504 JUnit共通reporter 工具自己試験結果

2026-10-29、2503/PG-D817/START2882→END2883、Production source17ab52b253282ce45016f0586c0167a22029fd8c/Main/Test非変更。開始0.5/2/4pp cap10、fresh27→28/残72/reset1793774153の丸め共有差1pp・専有N-T/配賦/工数null。工具改善費であり、原機能PG/新Product PT/coverage/WBS受入へ計上0。

|真正証拠|結果・SHA256|
|---|---|
|PG13726/entry206a7ed3/session26396|javac0、工具専用12観点を予定どおり確認。positive child二件exit0/intended negative十件exit1・timeout0を保持、本体0。0a43e2c2ffa463f9475ca6b0158189a030eb2f3ca4fac80812da3bcf4d869f1c。|
|PG13728/entry4dddeec9|独立private receipt/public XML/全源・七JUnit jar/一意case・planned exit/安全summaryを再実行なしで確認、actual0。32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c。|

新共通SharedSelectedJunitReporterV1 SHA c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515。Callerの固定Mapからtotalを一度Math.addExactで導出し、各suite件数と一意caseも検査する。source/driver/fixture三Javaのhashは元manifest、12compiled tool classのhashは**post時に初めて記録**したもので、元run前後にcapture済みと偽らない。元compile command/各JVM command/UTC/OS-JDK/tool/exit/timeout/XML/hash・7jar pinは各manifest/SLOT。JDK25.0.4実runtime情報もown stdoutの許可四行だけpostへ記録。

2/1の二class正常、期待総数違い、総数は同じだがsuite配分違い、failure、skip、abort、container失敗/not-started、empty test/not-run、empty map、count0、非法class名を全て仕様2503どおり確認。negative childのexit1をexit0へ変更しない。failure message sentinelは公開XML/summaryへ出ず、型/限定own source frameのみ。これらは新工具のテスト入力であり、意図的failureや空fixtureをProduction成功・flaky/skipの合格算入・意味のないcoverage加点に使用0。Product jar/class/method/DB/MQ/HTTP/Root/VM/鍵/Graph9実行0、ToolChecks12/ProductPT0/coverage null。

旧具体reporter166行に対し新共通186行は一つだけ共有し、今後の選択callerは固定Mapを渡す小さいwrapperにする。四つの件数literalの更新漏れを構造的に避けるが、実週次token削減率は未測定で、LOC減を費用/工数完成率へ変換しない。原hostや実行済reporter/source/runは不変更・元2075/JVM1を保持。現在の共通版は既定のordinary whole @Test/MethodSourceの固定選択向けで、dynamic/parameterized/未知sourceを暗黙に成功化しない。source/whole/fixture/副作用の着手前判定と独立postは従来どおり必要。

YKT1823の限定是正は履歴として保持し、この共通化はコピー起因再発防止の追加実装。新たなProduct受入や全過去工具の再資格ではない。次はMorningExpiryObservationInvariant全4のdata-only到達性を確認後、新工具を必要な新しい普通PTだけへ適用する（未実施、旧成功の確認再演0）。Root/permit/実サービスに触れる経路は保留のまま。正式1964-53/17-190/工数null/QA051final・全actualHOLD/全保全物を維持し、工具だけの区切りで停止しない。
