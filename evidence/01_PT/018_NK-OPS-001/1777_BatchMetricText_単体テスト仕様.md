# Batch closed six-family text接続 PG/PT仕様

NK-OPS-001/RD171/UI252/SS311341351/411/451、1775～1776/PG-D604/group2004、主WBS-P018-09/C07参照0加算。開始31残69/reset1793382075/3-6-10pp/cap10はPG8460/event2004固定。既label policyの同返却Mapを直接line modelへ使用し、name/key/value一回capture、借用source非保持/非close、STANDARD詳細未読、DEBUG closed六familyだけ。counter有限非負、gaugeは明示NaN未知と±Inf/負の標準double、duplicate series/型不一致/null/未知field/値は失敗。source/既POM/API-Web-Bootstrap/旧全Mainは変更しない。

BatchにはProduction text SDK依存がないため、固定ASCII enum/suffixだけの専用text codecをBatch role内に実装する。汎用label escape API/暗黙SDK loader/反射/他app依存を作らず、未知quote/backslash/newline/非ASCIIはlabel policyで拒否する。name/label順はTreeMap、HELP/TYPE/number spellingsを固定し、whole scrape時点性/実endpoint/owner/actualmodeを保証しない。STDは既MonitoringModePolicyのexact parse、sourceを一切読まない。

## 新BATCHTEXT001～024（unit24）
literal Counter/Gauge golden、Gauge NaN/±Inf/負/±0・finite extrema/小数、Counter有限非負境界/負/NaN/±Inf、unknown未読/空、両型不一致、null source/mode/list/meter/id/name/tag/key/value、閉鎖/借用、name/tag/valueの各一回capture、mutable provider変更でも承認copyだけ、全六family順/同family複数series/duplicate series、provider Runtime/Errorの元identity/後段failureで部分成功なし、mode不正/STD未読、別source/有限64並行、固定ASCII外値/余剰/欠落を検証する。期待はSS literal/固定double表記/独立line setで作り、production methodからexpected生成なし。

## 新BATCHWIRE001～008（actual Simple registry接続8）
1. 実SimpleMeterRegistry(SimpleConfig.DEFAULT,MockClock)＋既Batch/Transfer/Integrity/Restart Recorder、六family/108sample、初期Gauge14 NaN/Counter94 zero。
2. supplied Counts(3/100,5/200)、BACKUP_DB SUCCESS at epoch10.5、Integrity HASH/BACKUP_DB、API OOMを二回→literal値。
3. STD空/DEBUG同観測、source非close/reset。
4. Transfer missing→known zero、unknownと0を分離。
5. WARNING/FAILED/SKIPPEDのcountとlast-success保持、後続古いSUCCESSも最大時刻維持（業務成功を推定しない）。
6. 有限64workerの供給Counterと同source scrape、元期待64。
7. 二owner/unknown provider未読、Map/旧sourceの状態非保持。
8. 当source実六family textを固定公式promtool3.13.5 `check metrics` のstdinだけでparse/lint、成功0と独立malformed literal拒否をJUnit内数で確認。binary SHA256 **4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff**、元PG8162 manifest ca3c93186503b91ff14183b1759b7c8b1e0e33fc73d16685974a8ebd2a01ecaeを照合、版再実行/再取得0、設定/SD/scrape/query/server/network操作0。own parser childはbounded30秒/失敗時本人だけ回収、timeout非PASS。

## 実施条件・証拠
ホスト通常JUnit/公開fixed tool/供給memory fixtureだけ、原本DB/Backup/鍵/VM/services/拒否対象未特定操作へアクセスしない。新32/2→追加Main1実line-method-class-branch100/CRC0/session1/PMD-CS-SB-missing0→全physical/owner/role→1778。parser内数は全32へ算術追加しない。source/branch/OS-JDK/command/時刻/exit/input/expected/actual/XML/exec/counter/static/log/hash/BUG-YKTを新only公開manifestに結合。既label14/旧4222の確認再演0、既成功はbyte依存のみ、coverage合算0。

現在新PT/coverage UNRUN。actual endpoint/全451/CHR/F03Root11/実VM-Root-DB-native-Backup-鍵-intent-permit-配備/拒否未特定HOLD、formal1964-53/原190新受入0/工数null/QA051final/PTALT0・元-v4-v5/欠測不変。未実行/失敗/skipをPASSへ加算せず、実装済み違反は修正前915/916へ。

