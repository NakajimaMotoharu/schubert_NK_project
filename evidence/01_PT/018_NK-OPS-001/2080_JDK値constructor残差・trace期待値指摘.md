# 2080 JDK値constructor残差・trace期待値指摘

2026-10-26、G03.01、群2418、開始.5/2/5週次枠pp/cap10。source6612747b7、原10252から2078の128箇所をpath/method/line/expectedExpressionSha256の四要素完全keyで差し引いた。同じ式hashでも別source/pathの箇所は除外しない。元source SHAと現byteが一致するものに限る。

JDKだけのconstructor(UUID/HashSet/TreeSet/String/BigInteger/ArrayList)を含む117式/34sourceが候補。内訳UUID102、HashSet7、String2、java.math.BigInteger2、BigInteger1、TreeSet2、ArrayList1。型出現数と式数は別（複数型併存あり）。38式は既PG10330/10362/10364の同keyに既レビューがあり、新成果へ数えず元文脈を参照する。残79式は本群だけで全独立性を判定しない。

既golden/response helperは2058/2059を参照し再試験しない。追加読取したLoginInboxService.expectedはTestのLoginReplayService.goldenと固定offset補正だけ、QuestionSubmissionService.work/headerは固定320byte/offsetとJDK整形。LogQueryApplicationService.brokerBodyのString二は受信bodyとJMS propertyの相関確認であり、独立golden全体の代用ではない。こうした追加相関を無条件に「期待値不正」としない。

WebRequestTraceTest原398行は `same ? new UUID(2,91) : first.eventId()` を期待にしている。trace helperは固定供給順UUID(0,id)/UUID(1,id)で、first=trace(...,90)。このcase内にeventIdを固定UUIDへ比較する独立基点がないため、BUG1841/YKT1592を修正前起票した。not-same期待をUUID(1,90)へ一箇所是正する。req006の同種相関は直前に固定event UUID(1,3)比較があるため非該当で、元assertionを保持する。

状態はSTATIC_CANDIDATE_REVIEW_PARTIAL_WITH_ONE_ORACLE_GAP。構文候補117/新候補79をPT/PASS/受入件数にしない。本群で元Test/fixture/Java/DB/VM/Root/鍵の実行0、元検査/署名/compile/成功PTの再演0。正式1964/53・個別17/190・工数null・QA051final/全安全HOLD維持。次は別PG/PT群で当一式を独立固定入力へ是正し、対象req008がpure mock/ThreadLocalだけであることと実commandを事前確認して通常PTを行う。
