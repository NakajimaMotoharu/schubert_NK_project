# 204 NK-OPS-001 停止client開始不明・限定実行結果

2026-09-28 JST、`dev-foundation`、Production source commit `42d419534`。対象`MaintenanceUnitStopClient.stop/Attempt.awaitClient`、`MorningStopPass.execute`。RD OPS-009、UI251/253、SS341/343・SSC102/105、BUG-315/YKT-248。Test IDと独立期待は166、200とMCLIENT012追補を正とする。

| 検証 | 実測 |
|---|---|
| 選択Batch PT | MCLIENT001～012の12件＋MPASS001～009の9件＝21件 F/E/S0、Batch SpotBugs0。post-start IOException/null/Runtime/Errorは原因非露出の`Attempt.UNKNOWN`で、同attemptのawaitもUNKNOWN。pre-start policy/root拒否はstop0を維持。MPASS006は既得UNKNOWNの間に親callbackが通常帰還しない |
| 変更class限定coverage | clean選択runで`MaintenanceUnitStopClient`本体 branch8/8、line43/43、method7/7、class1/1、`Attempt` branch24/24、line42/42、method6/6、class1/1。4指標missed0。`MorningStopPass`にはnative経路のbranch1/line6/method1 missedが残る |
| Production6 security回帰・初回失敗 | `/tmp/pg340-six-clean.log`はNode binをPATHへ入れ忘れ、Web555PTのうちE2、Batch未実行、exit1。合格・flakyへ加算しない。Productionコード・期待値は不変更 |
| 同source修正環境run | 固定Node24.19.0 PATH＋`-Dnk.pt.node`で6module reactor exit0。Protocol80、Storage149、Bootstrap175、API742、Web555、Batch655＝2,356PT/347suite F/E/S0。6module SpotBugs BugInstance0/Error0、JaCoCo report全6生成。これは既知coverage不足の正式`verify`合格ではない |
| Bundle coverage不足 | Protocol/Storage4指標missed0。Bootstrap branch37/line11/method4、API1/19/3、Web1/19/3、Batch6/124/48・class3（順にbranch/line/method）。除外なし、全4指標100%未達 |

Sanitized JUnit347 XML、coverage2、static6、run-summary1、計356fileのhash不一致0。manifest SHA-256 `92363fef129ddeb9a3373f43f2f2e3f5de6479b6e6ea8ca5a31f6281d4d2f775`、path `evidence/provisional/PG340-six-security/manifest.json`。実行時刻/tool/branch/commit/command/exit/input/期待/実際/BUG/SSCはmanifestに記録。原始log・raw DB/secret/sessionをGitへ格納しない。

限定修正により開始呼出後の不明を通常IOExceptionとしてM callbackへ返す経路は除去したが、handleなしUNKNOWNは自身でreap不能。実親Unit hard timeout後のM/Aとcgroup保全・再起動barrierを未実測で、BUG-315/YKT-248は継続対応とする。PG339候補Unit/既存PG323検証Unitは不変更。R2/R3、正式`PT-WEB-20260925-24`/source`858713c0bf310ae8bf62078b0a1cedbce4e968db`、1,964PT/53scope・全体中心48.3%は不変。
