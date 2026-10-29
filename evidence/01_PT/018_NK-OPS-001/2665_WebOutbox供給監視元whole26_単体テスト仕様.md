# Web Outbox供給監視 元whole26：単体テスト仕様

2026-10-30 source6b53/dev-foundation/保存ef08721102143fcfa0c52f469629914baa17852a、PG-D897/群3055原0.5/3/6pp cap10。元CollectorTest8/379行・RecorderTest8/377行・ObservationRepositoryTest10/479行=26/3、全1235Test/helper/Fixtureと三Main234行を確認。P01809 canonical新logical候補、RD171/UI252/SS332/351・既1721、WEBOBXCONN/MET001..008/DB001..010と元classname#methodをjoin。

## PT_DEFAULTと独立oracle
実Connection/PS/RSではなく元Fixture JDK Proxyだけ。借用read-only transaction（autoCommitfalse/readOnlytrue/READ_COMMITTED）事前確認、独立SQL `SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at FROM schubert_web_session.web_log_outbox GROUP BY status` とquerytimeout1、prepare/execute一回、RS→PS close後だけ完全Observationを公開。borrowed connectionの変更/close/commit/rollbackはFixtureが拒否、実DB/driver/時計/worker/Root/VM/鍵/cohort/graph9なし。

固定count3/5/7・age2/4/11s、六row順序、空/疎status0/DurationZERO、typedOffsetDateTime JST→UTC1.5s、年0001→9999の315537897599秒999999000nano、LongMAX/double9.223372036854776E18、null/未知/重複/非正/SQLnull/未来+1ns/負年齢/ゼロ件に非ゼロageは異常。例外identity/suppression順序/partialResource close/後続getter未実行/retry0、STD収集series0/null事前拒否/失敗時missing/次成功回復を固定入力とJDK算術で照合。外部例外graph走査/分類器の再演0。

SDKは自分のSimpleMeterRegistry、六series（WEB×PENDING/SENT/ERROR×count-age）、immutable record独立polynomialhash90715647と全文literal、外国Counter非置換・借用registry未close/factory途中故障。所有2/8thread/5秒deadline/実BLOCKED/64taskは元body通り、owner別事前vectorからexpectedを作りProduction出力をexpectedに使わない。全体scrape跨metricの原子性/実DBソース資格をこのPTから主張しない。

## 工具の先行適格性（非実行）
非JDBC用import rejectを転用せず、reviewed_jdbc_fixture_scope_v2は固定hashで既レビュー済みのSource textだけを追加確認する（権限/操作allowlistではない）。PG14417/5994ad9f1211e5b51894d1bc596a2b4aaba7b54430e1a95ffb673447e245ef74はpositive1/negative61=62工具検査、直接接続API15×各三Source/必須12/shape4を非実行文字列copyで拒否、Product0。元三Test/Main/Fixture byte不変更、platform/安全HOLD解除0。

## command・coverage
`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14416_web_outbox_supplied_whole_twenty_six_pt.py`、fixednormal14216六Jar/全currentinput/SDK/selftestedReporterでfresh元26を一JVM/session/exec一回。原branch/source/time/command/exit/OSJDK/XML/FESnotrun/fixture0/exec hashはPG14416、独立PG14418は三完全Source五physical（Recorder+Observation+Status）と元XML/一CRC/八metadata反例/元環境・候補owner/先行profileを照合。四counterは実miss/N/A含めそのまま残し、手動除外/人工assertion/exec合成/旧source転用0。

結果2666、元286再演0・新Test/fixture/source0、正式1964-53/歴史17-190/別source受入register/工数null/QA051final/全F03-451/HOLD/原本保全維持、通常区切り停止なし。
