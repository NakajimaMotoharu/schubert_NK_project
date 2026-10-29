# Async供給監視 元whole24：単体テスト仕様

2026-10-30 source6b53/dev-foundation/保存dc9c70082fc59bbdeab971cc9f4cbdeadda75a2d、PG-D895/群3051原0.5/3/6pp cap10。元AsyncJobMetricCollectorTest8/316行・AsyncJobCountRepositoryTest8/341行・AsyncJobMetricRecorderTest8/307行=24/3、全964Test/helper/FixtureとMain214行を確認。canonical候補P01809、RD171/UI252/SS331/332/342/351・既1623/1627/1631/2451、ASYNCGAUGE/ASYNCDB/ASYNCCONN001..008と元classname#methodをjoin。新Main/Test/fixture/input0。

## PT_DEFAULT・独立期待・所有
JDBC Connection/PS/RSは元FixtureのJDK Proxyだけ、SQL文字列と操作allowlistをTest literalで確認し実driver/DBへ接続しない。autoCommit=false/readonly=true/READ_COMMITTEDを事前確認、prepare一回/querytimeout1秒/execute一回、row/PS closeはRS→PS、borrowed connectionの設定変更・commit/rollback/closeは禁止されFixtureがAssertionErrorで拒否する。

固定SQLは `SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state`。五state固定表・shuffled1/2/3/4/5→total15、空/欠落groupの真0、null/未知/負/duplicate/wasNull不正、maxLong/合計overflowを独立literal/JDK整数で照合。例外は各12故障点の同一identityとJDK TWRのsuppression順序だけ、cause循環を走査・分類器呼出しなし。close完了前にはsnapshotを公開せず、観測失敗はmissingでNaN化し、次の真0/成功で回復する。nullの正常化や失敗の成功転換なし。

SDKは自分のSimpleMeterRegistry/MockClock、STDは収集/series0、DEBUG五series/state allowlist、型別label/禁止canary/immutable snapshot・LongMAX double固定値・partial factory failure/他ownerを確認。synthetic OutOfMemoryErrorは単なるTest Throwable一個でメモリ枯渇を発生させない。自己所有2/8thread・latch5秒/64taskは元bodyのまま、parallel戻り値はfixture ownerごとのcount+2など独立入力で確認。未完/flaky/timeoutをPASSへ数えない。

実DB/worker/broker/HTTP/VM/Root/cohort/鍵/permit/held操作/graph9は非依存、拒否操作の別fixtureへの置換ではない独立既存whole。業務再送は当scope非該当。MainはCollector45/Recorder100/Repository69=214行、三完全Source五physical（Recorder/State/Snapshot含む）、counterを依存先/実収集の受入へ拡張しない。

## command・証跡
`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14396_async_supplied_metric_whole_twenty_four_pt.py`。fixednormal14216六Jar/current input/SDK/selftested reporterでfresh元24を一JVM/session/exec一回実行、環境/branch/source/time/command/exit/XML/FESnotrun/fixture0/exec hashをPG14396へ。PG14398独立はactual API Jar/snapshot/全閉包・四counter・一CRC/八negative/原環境/候補ownerを照合。miss/branchN/Aがあれば保持、manual除外/人工assertion/exec合成/旧成功転用0。

結果2662、元262確認再演0、正式1964-53/歴史17-190/別source個別register/工数null/QA051final/全F03-451/HOLD/原本保全維持、通常区切り停止なし。

## BUG2100/YKT1847 工具是正追記（元指示/失敗保持）

原14396はcopyした非JDBC用import一律検査で工具1/製品JVM前・24not-run、元entry/SLOT無しと失敗観測14397を保持、platform拒否ではない。修正前台帳起票後、新14401は既三Testの固定hashと純JDBC Fixture操作契約のpositive1/negative25を非実行文字列copyだけで検証、SHA c968a2a5b50209f22907be283c0fe4937e438b4b6b7cc03d4c513ee23cc49582、Product0/工具0。DriverManager/DataSource/JNDI/直接getConnection等15禁止とProxy/型/独立SQL等6必須・null/未知shape4を全拒否、確認対象は実際の原三wholeだけ。安全HOLD/権限/承認範囲を解除しない。

初回の実製品commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14400_async_supplied_metric_whole_twenty_four_pt.py` とし、fixed proof/helper/sourcehashへ先行結合する。Main/Test/fixtureは元byte不変更・old14396再送なし、新only run14400と独立14402へ分離する。24/3とMain三Source五physical・原0.5/3/6ppは不変、tool手戻りを新製造出来高へ加算しない。
