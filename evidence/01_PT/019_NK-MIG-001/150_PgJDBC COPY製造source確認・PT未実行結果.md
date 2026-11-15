# PgJDBC COPY 製造source確認結果・PT未実行

2026-11-15、dev-foundation、source前HEAD7b2f17f40bfff283913a30a6fe4ab8329d9d8031。実行環境/時刻/command/exit/hashはPG33710/source-only-checks-v2.json、独立source判断はsource-only-review-v2.json。整形GJF1.36.1とCheckstyle14.3のJava source parseは終了0・指摘0。旧途中結果も保存し、新24Testを一度も起動していない。

SDK ABI/compile、NullAway、SpotBugs、semantic PMD、全体build、動的PT24、実Driver/DB/nativeはNOT_RUN_HOLD。line/method/class/branch/instruction coverageはすべてnull、PASS数0。旧Coreef461eba/Unita48eec60の全1050は新POM変更前の歴史資格として保持し、新port・新POMへ流用しない。旧105Java source byte不変はレビュー済みだが、新依存グラフ全体の受入を意味しない。

BUG3001/YKT2530は表示escape誤読による誤検知取り下げ、source修正実績0。BUG3002/YKT2531はfuture fixture初期化順をsource是正し型compile/PT待ち。BUG3003/YKT2532はowned capture後の幅検査へsource是正、未来PGCOPY005を追加し、既4Mainの非該当根拠をsource-only水平確認、動的未完OPEN。BUG3004/YKT2533の誤った旧vector異常前提は原・現同値正例と独立合成負例で是正、metadata source review限定で閉鎖し製品PT成功に数えない。

価格1/3/8pp cap9はこのsource製造・PT source・強化レビュー段のみ。未実行SDK/PTの残工数を0としない。後続費用は元P019/全451費用に含む未確定内訳として保留、追加二重課金0、今回段完了を工程完了/工数完成率に換算しない。正式1964PT/53scope、正本184/625、元190新0、工数率nullを維持。
