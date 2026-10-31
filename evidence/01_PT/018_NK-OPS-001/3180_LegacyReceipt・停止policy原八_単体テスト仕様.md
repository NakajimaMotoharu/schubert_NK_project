# LegacyReceipt・停止policy 原八 単体テスト仕様

2026-10-31/PG-D1024/event3496、主・計測WBS-F03、元artifact/cost ownerは481/485の既担当を保持し追加配賦0。HEAD77e4d3278fb882a7551e5374b00a3d999b7178ca/push64532終端c2ae98真正0、Production6b53/normal14216不変更。開始1/4/8共有pp cap10、freshused59/rem41/reset1793774153/短期null/券0、専有費・N/T・工数null。

PGは既実装Main/Testを保持し、今回原whole `LegacyReceiptValueTest` 一＋`MaintenanceUnitStopPolicyTest` 七を当sourceで初資格する。先行1511/197/199/203/2758と公開catalog15950・現2174casesを照合し重複無しを確認。Test全二・Main/関連caller・元InspectorUnitProbeFixture全体を読取った。後者はJava Process subclass/メモリstreamのfakeで、`mpol005`は元callbackが固定query文字列をassertして同Childを返す。`create()`はdefault reader/callbackの構築のみで、そのcallbackを実行しない。`InspectorUnitSnapshotTest.GOLDEN`はコンパイル時String定数、同Test fileはfixtureの型解決のためcompile-only・JUnit非選択とする。既HOLD Testからの新fixture抽出/差替えはしない。

|Test ID・method|目的・fixture/操作|独立期待・根拠|
|---|---|---|
|PT-OPS-RETDATA-001 / retdata001|baseline Object一、boolean false/true、freshZero counter、captureはAssertionError|observed空/typed不足・stopped不足は各固定IOException、cause/suppressed無し。terminalだけfreshZero一回、trueだけSUCCESS・typed実証無し。1511/SS341343|
|PT-OPS-MPOL001 / mpol001|手書き八Unit名/四行ASCII policy・並び替え|既enum順と完全一致、各入力wipe。Productionから名前期待を作らない。SS341342 SSC101|
|002 / mpol002|欠落/重複/未知/等号/末尾LF異常|MALFORMED_STATE・元配列全wipe|
|003 / mpol003|0/512/513byte・各byte値異常・null constructor/Source/unit|異常policy拒否/wipe、null契約の例外。NPEをcatchして正常扱いしない|
|004 / mpol004|Id/LoadState/KillMode/SendSIGKILLの各違反literal|拒否、stop命令を発行しない|
|005 / mpol005|既Child fake/NativeReaderへ固定八queryを渡す|systemctl showのargvだけ一致、stdin/stdout/stderr各一回close/wipe、実process取得0|
|006 / mpol006|前後IRQ/既知・未知exception identity|IRQ保持、前IRQでsource0、後IRQでwipe、例外identity保持|
|007 / mpol007|private pool8/64tasks・factory構築だけ|全独立policy入力wipe・閉じたPROPERTIES literal、actual thread数は未計測null。factory構築を権限・実query/停止成功にしない|

個別正常/境界/null/異常・IRQ/並行の原oracleを変更しない。既関係の再送/真receipt/Unit停止/世代/所有/DB/Backup/permit/鍵/nativeは範囲外HOLD。独立期待はSS/固定literal/identity/counterで、Production methodからexpectedを生成しない。既6910等・旧source成功やexecは合算しない。

PT_DEFAULT。JDK25.0.4/Maven3.9.12 normal14216の同六Jar/SDK/JUnit/JaCoCo0.8.15、own fresh javac/JVM上限各180秒、一session append=false、原二Testとcompile-only二fixture/SharedReporter/新launcherだけ。新Product/Test実装0・新TestID0。private JVM内のIRQ/own platform workersのみ、実VM/既process/サービス/DB/JMS/network/鍵/Graph9/Root/permit/失敗cohort操作なし。Toolのjavac/java子と、製品の外部process発行を区別する。

全六Source（MorningBackupUnitCycle/MaintenanceUnitStopPolicy/MaintenanceUnit/InspectorUnitProbe/ProcessResourceScope/SystemctlStateSource）40physical=Code19/真正NoCode21を凍結。CodeのうちCycle outer/anonymous1..3/Started/Unresolved、Inspector outer、Systemctl全Code三の計十は未実行予定であり、欠落・全missを保持する。Systemctl cold Sourceはfactory callback未発行の照合対象で、正常稼働/stop証明ではない。private空ctor等は公式既定filterだけ、除外・人工呼出しでwhole100にしない。六Source whole coverage未達ならstrict gate1のまま、全PT成功と分離する。

16398 raw→16400同session/CRC/全Source四counter/四held六native absence→16402独立期待/異常metadata→現registry/WBSを予定。元StopGateException/Failureの同source proofは依存参照として保持し、今回execと合算/上書きしない。3181に実command/時刻/環境/source/終了・XML/coverage・hash/BUGを記録する。正式1964/53・歴史17/190・工数null・QA051final/全HOLD維持、通常小群停止0。
