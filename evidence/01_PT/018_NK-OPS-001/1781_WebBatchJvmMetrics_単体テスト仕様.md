# Web/Batch standard non-resource JVM wiring PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411/451、PG-D606/group2008、WBS-P018-09/C07参照0加算。fresh32残68/reset1793382075/2-4-8pp/cap10はPG8502/event2008固定。両class/SDK導入の後続索引一致0・src未導入を確認済み。既API1779/1780の14は確認再演しない。

## 製造・独立性
WebJvmMetrics（固定WEB/既HttpMetricContract mode）とBatchJvmMetrics（固定BATCH/既MonitoringModePolicy mode）を各roleへcomposeする。四標準SDK ClassLoader/Memory/Thread/Uptimeだけを直接呼び、shared business helper/Bootstrap責務拡大/相互app依存/既classの同名module複製を作らない。共通化するのは外部SDK自体で、role固有compositionの固定tagと既mode契約は別々。Webの未知mode診断は既契約literal `invalid monitoring mode`、Batchは既 `CONFIG_INVALID` を維持し、コード都合で統一しない。

STDはfactory/JMX/source未読、DEBUGはborrowed source閉鎖確認→factory一回/List.copyOfでexact四要素/順序bind。途中factory/binder失敗のRuntime/Errorを同identityで伝播し、partial sourceはcaller所有、暗黙rollback/close/再試行をしない。自身のinstance field0（固定BINDER_COUNT定数1）。GC listener/CPU-FD/標準text/実endpoint/actualownerは別未完、SDK4binder≠wire4family。POM/API/Bootstrap/旧全Main-Unit/上位不変更。二role追加だがshared protocol/interface/security/DDL/POMを変更せず、開発中の局所28/両新2Mainを検証する。正式機能受入/全451は行わない。

## 新WEBJVM001～014・BATCHJVM001～014（計28/2）
両roleに独立literal tag WEB/BATCHと既mode診断を固定し、各14の入力/期待は1779の番号に対応：
1. actual own host JVMの四SDK namespace/型/tag、独立RuntimeMXBean start/time範囲、動的値は存在/非負契約（性能合格ではない）。
2. STD factory0/source読取0、lazy初期化。
3. 四port順1-2-3-4/同source/factory一回、最初のportが元listをclearしても事前copyを完走。
4. source/mode/factory null。
5. 空/小文字/末尾空白/未知modeは既role診断で拒否、factory/source0。
6. closed DEBUG拒否/factory0。
7. factory list/要素nullを全bind前拒否。
8. count0/1/3/5を全bind前拒否。
9. factory Runtime/Error同identity。
10. 各位置binder Runtimeで後続未実行、partial registry caller所有。
11. 各位置binder Error同様、成功化なし。
12. closed STD未読/暗黙再closeなし。
13. 同instanceの二owner再利用、片方close後も他方保持。
14. 有限64並行×4port/独立owner、join10sec/sleep0。

SDK名/typeは固定core1.17.1/SHA9ca47dfa、8493原69266176公開bytecode（classloader累積FunctionCounterとcurrent Gauge/TimeGauge ms）をbyte依存として参照し、expectedをproduction methodから生成しない。literal/固定port記録/独立Java公開management APIがoracle。Java25 own fresh JVMだけ、対象VM/Root/他process/DB/Backup/鍵/permission/network/services/拒否操作0。normal六/NullAway/format→original28一exec→新2Main実四100/CRC0/session1/PMD-CS-SB-missing0→全physical/owner/role/instance fields0→1782。元command/環境/OS-JDK/branch/source/時刻/exit/input/expected/actual/XML/exec/counter/static/log/hash/BUG-YKTを新only公開manifestへ。

現在PT/coverage UNRUN。fail/skip/unrunはPASSにしない、実装済み違反は修正前915/916へ。原4222/API14の確認再演/別source coverage合算0、formal1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/F03Root11/actual VM-Root-DB-native-Backup-鍵-intent-permit-配備/拒否未特定HOLD、元-v4-v5/欠測不変、通常停止なし。

