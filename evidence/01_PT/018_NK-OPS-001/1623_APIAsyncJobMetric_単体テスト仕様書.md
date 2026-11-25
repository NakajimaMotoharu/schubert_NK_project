# 1623 API Async job metric 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS324§10・331§6.3・351§6/8/10/PG-D539。API AsyncJobMetricRecorder constructor/state/record/missing/snapshot/detail、Snapshot constructor/value/totalJobs、State enum。group1862、開始共有17/残83/reset1793306748・見積3/6/9pp上限10。実DB/JMS/HTTP/Root/VM/cohort/keys/配備操作なし。入力は固定state/count mapだけ、各TestがSDK registryを所有/最後にclose。

独立oracleはSS331/既V003.ck_async_jobs_stateの五literal RECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLEDと、SS351のGauge `nk_async_jobs{state}`。五状態すべてのknown countが必要、null/欠落を0へ補完しない。各非負long・総和long範囲内、immutable Snapshotで原精度保持、metricはSDKbinary64。未知はNaN、既知全zeroは0、STDは詳細登録/保持0。新業務状態・任意ID label・API→Batch依存を加えない。

| Test ID | fixture/入力・操作 | 独立期待値 |
|---|---|---|
| ASYNCGAUGE001 | DEBUG actual SimpleMeterRegistry/五state lookup/初期値 | 固定五gauge/一名一key、未知NaN/empty・借用先close0 |
| ASYNCGAUGE002 | literal count1/2/3/4/5、入力Mapを後変更 | 各gauge固定値/total15・immutable原値、state unknown alias/秘密canaryは固定拒否 |
| ASYNCGAUGE003 | 全zero→missing→新観測 | zero0と未知NaNを区別、snapshot/値の正しい復帰 |
| ASYNCGAUGE004 | STANDARD全操作/null/unknown mode | gauge/保持0、無効入力はdisabledでも隠さず拒否 |
| ASYNCGAUGE005 | null map/key/value/state、欠落key、負count | snapshot構築/境界例外、既record値不変、欠落を0補完しない |
| ASYNCGAUGE006 | Long.MAX_VALUE一状態/他0、総和overflow | 原long/total厳密・独立IEEE丸め値、overflow拒否 |
| ASYNCGAUGE007 | 64並行二immutable cohortと旧snapshot | complete snapshotは二cohortいずれかだけ、旧値不変・系列五のまま |
| ASYNCGAUGE008 | 二番目Gauge登録のRuntime/NPE/Error/合成OOM/非formatable故障、二owner | 同一Throwable・attempt2/partial caller所有・再送0、registry間値非共有 |

新8通常PTを独立API monitoring harnessで当source固定後にMaven verifyし、XML全case/終了/FES0、単一session/実CRC・実3class四counter100、annotation-only package-info一classは非実行metadataとして明示、lint/Werror/NullAway/SB/PMD/CSを確認する。五gaugeの3class分母に空scope/意味なしassert/除外で100%を作らない。PG7300/7302以降manifestへOS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashを保存予定。既Web/Batch同版SDK1.17.1四Jarをoffline再利用/取得なし、API POM一node以外の意味不変を検証する。

全六通常compile/Jar・旧1669byte/歴史Batch43/source743・歴史Web10/source19cの同byteだけと、当API4physical/3実行を別domainで照合する。当API8に旧Batch169/Web23/設定9を合算せず、全体451/正式の代替にしない。全65source差分と全1726physicalは予定値であり実測前は未確認。DB source/identity/finite collector/Root/exporter/native/CHRは未受入HOLD、formal1964/53・歴史17/別source新7・原190新受入0・工数null/QA051final/PTALT0を維持。障害は修正前915/916へ起票する。

## BUG-3879／YKT-2997 の並行fixture再試験

ASYNCGAUGE007の8 worker、64件、10秒、五つの独立期待とin-memory registryの所有順を維持。追加PT-OPS-ASYNCGAUGE009はJDK代理一つで一次例外と終了期限切れを重ね、一次同一・抑制一件・停止と待機が順に各一回。 [PG45482](evidence/PG45482-current-async-gauge-worker-ownership/manifest.json)
