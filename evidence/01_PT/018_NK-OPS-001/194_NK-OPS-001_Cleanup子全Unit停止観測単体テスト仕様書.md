# 194 NK-OPS-001 Cleanup子全Unit停止観測単体テスト仕様書

Program ID NK-OPS-001。対象`MaintenanceUnitTermination.createCleanup`、`CleanupNativePreflight.requireApplicationsStopped`/native前後接続。RD OPS-009、UI251、SS341/343、SSC-104/PG335。Test ID PT-OPS-MTERM009、NCLEAN002～004。親`MORNING`の既存8 Unit observerは変更せず、子の固定`CLEANUP` actorはWEB/APIの読取だけを許す。

| Test ID | 事前条件・fixture、入力/操作 | 独立期待値 |
|---|---|---|
| MTERM009 | 公開literal root CLEANUP cgroup/unit/boot/invocation、固定8 Unit各target、null/wrong actor | WEB/APIのみfactoryが作成可能。その他6/null/wrong actorはmanager照会前に拒否。host UID1000の実whole-Unit呼出しは成功扱いしない。SS341§5/7の固定対象 |
| NCLEAN002 | 独立観測portへWEB/API両方true | WEB→APIを各1回・この順で照会。既存8停止のうち子が要求する2対象とSS341§7の順から作る期待値 |
| NCLEAN003 | WEB false、API false | WEB busyならAPI照会0、API busyなら両観測後固定非成功。対象を初期inactiveやnot-foundへ補完しない |
| NCLEAN004 | port null、各観測の既知IOException/未知Runtime | nullは契約違反、既知/未知は成功へ正常化されず後続対象へ進まない。raw値/secretは証跡へ出さない |
| NCLEAN005 | 独立literal WEB not-found projectionを既存parserで固定`StopGateException`にし、子境界へ注入 | 固定原因非露出IOException、次API照会0。外部mainはこれを安全失敗30へ分類する。BUG313/YKT246。parserをexpected生成には使わず、期待コードはSS341から導く |

実装の前後`applicationsStopped`は同root snapshotでprivate/DB前と全close後に呼ぶ。ただし注入portの試験は真正systemd/親M/Aの証明ではない。実Unitのloaded/全nested空/前後同一、後段DELETE直前のfresh再観測、子root成功経路、Production全4coverage100%、全正式runは別必須。環境/command/commit、F/E/S/static、変更class4指標、BUG/SSC、sanitized evidence path/hashを195へ記録。TDD初期失敗は障害扱いせず、実装済み違反は915へ修正前起票する。除外なし。
