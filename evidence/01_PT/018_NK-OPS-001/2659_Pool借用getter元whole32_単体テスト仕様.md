# Pool借用getter 元whole32：単体テスト仕様

2026-10-30 source6b53/dev-foundation/保存ac26843682955bb481c95c8b6d290c4f1c0bc79c、PG-D894。群3048原0.5/3/6pp cap10。元API/Web各Collector8/Observation8=32/4、全948Test行とFixture・targetMain136行/依存recorder全bodyを確認。新Test/入力/Source/fixture0。NK-OPS-001/P01809候補、RD171/UI252/SS351・既1639/1728、POOLCONN/POOLREAD/WEBPOOLCONN/WEBPOOLREAD001..008とclassname#methodを元XMLへjoin。

## PT_DEFAULT・独立期待
HikariPoolMXBean/HikariConfigMXBeanは元Test Fixtureが作るJDK Proxyだけ。呼出可能なのはactive/idle/pending/maxの四getter、その他の管理/control/config/credential操作はAssertionError。実Hikari pool/config/DB/JMX/ネットワーク/Root/VM/鍵/cohort/graph9起動なし。観測失敗Throwableは同一性のみを比較、元の循環cause例も走査や分類器を呼ばず同一例外再throwの確認であり、保留classifierの迂回実行ではない。SDKは自分のSimpleMeterRegistry、自己所有2/8thread/latch5秒・100ms非進入/WEB実BLOCKED/64task・100回だけ、外部processへ触れない。

独立値はactive3/idle5/pending2/max8、真0/正max1、負四位置とmax0は未知Optional.empty/NaN、全IntegerMAX→各long2147483647（合算・wrapなし）。getter順序四literal、fault位置以降未読/retry0/同identity、STDはgetter0/series0、nullは事前拒否して旧snapshotを変えない。collectorはread→publication直列化/別owner111と99/4series固定を確認し、実poolの跨getter同時刻一貫性や接続資格へ拡張しない。expectedはFixture入力・literalでProduction observation methodから算出しない。

## 実行・coverage・証跡
`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14390_pool_borrowed_getter_whole_thirty_two_pt.py`。固定normal14216/全sixJar/current input/SDK/reporter資格に結合しfresh元32を一回のJVM/session/execで実行、原OS/JDK/branch/source/time/command/exit/XML/case32/FESnotrun/exec hash/fixture0をPG14390へ。

PG14392独立はAPI DbPoolMetricCollector/Observation・Web WebDbPoolMetricCollector/Observationの完全四Source四physicalをmodule別Jar/snapshot/CRC/実四counter、XML32と八negative/元環境/候補ownerへ結合。依存DbPoolMetricRecorder二つ/Counts/State等はこのtarget counterだけで受入へ数えず、不明/branchN/A/missを保持、manual除外/人工呼出/exec union0。2653監視raw14の二collector関連四理由と関係するが、他collector・全F03/451の合格へ拡張しない。

元230/旧sourceの成功確認再演0、実DB等0。結果2660、正式1964-53/歴史17-190/別source個別register/工数null/QA051final/全HOLD/原本/二held工具metadata前除外保全。群開始markerの依存recorder行201は確認前の転記値で、実wcを別checkpointへ訂正し判定や費用を水増ししない。
