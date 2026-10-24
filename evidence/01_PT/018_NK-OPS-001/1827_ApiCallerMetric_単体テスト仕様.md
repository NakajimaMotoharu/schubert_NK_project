# API caller metric context PG・独立単体テスト仕様

NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D622、group2057、主P018-09/C07追加費0。開始fresh46/残54/reset1793382075、開始見積3/6/10pp・一群上限10。既承認metrics/owner契約のAPI同経路接続であり仕様変更なし。

ApiDbPoolMetricBinding.prepareContextはresource-free factory。STDは借用bean supplierも未読、DEBUGの明示initializeだけでpool→config参照を取得、getter四値はrender時だけ。factory返却ownerをApiProcessMain既ResourceScopeが捕捉後initializeし、内側Managementへ借用する。既consumer/promote/lifetime/readyの権限は変更せず、管理の正規終了確認後にcontextをclose、外側のoutbox等とpoolは最後。unknown所有の既native keeperを変更しない。実DataSource取得やcastは当PGの動的受入ではない。

|新Test ID|fixture/操作|独立期待|
|---|---|---|
|APIPOOLB011|STD・読まれるとErrorのsupplier|取得0、空bindings、固定readyだけ|
|APIPOOLB012|null/未知mode|入力拒否・provider/getter0|
|APIPOOLB013|owner捕捉→init→render二回|pool/config各一回、init時getter0、3/5/2/8→0/0/4/8 literal|
|APIPOOLB014|pool supplier Runtime/Error/null|primary identity/後続config0/再init拒否、caller partial cleanup|
|APIPOOLB015|config supplier Runtime/Error/null|pool→config順各一回、getter0/再init拒否、primary保持|
|APIMHTTP021|deferred factory→context→memory HttpExchange二GET|200/ready1、3→0/max8、UTF8 byte長/content-type/no-store/close1、参照再取得0|

必要既Binding10＋HTTP20と新6をactual36/2として実行する。既Fixture outer testsはcompileだけ、pool/DB/HTTP socket/Main/main/run/default/startは一切実行しない。独立期待はSS名/tag、literal/order/例外identity/headerから作り、production methodでexpectedを作らない。

8854 normal六module skipTests compile/NullAway→8856新selected36→8857旧collector三raw rationaleのsource/rules/currentXML join→8858 Binding/collector/HTTP三Main同source四counter100/静的解析/CRC/session→8859 caller source/静的PGレビュー→8860全physical/owner/差分→1828/scan/push。caller actual/native coverageはUNRUN_HOLD/null、適用範囲不明の拒否をPT免除へ変換しない。全451/実経路/CHR/正式1964-53/原190新受入0/工数null/QA051final/全actual HOLDは別未完。時刻/環境/command/source/exit/XML/coverage/証跡hashを原manifestと1828に保存する。
