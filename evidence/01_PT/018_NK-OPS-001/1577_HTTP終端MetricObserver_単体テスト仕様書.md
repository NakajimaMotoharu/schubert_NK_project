# 1577 HTTP終端MetricObserver 単体テスト仕様書

NK-OPS-001/P018-09、RD171 MON005..013/UI252/SS312・351、PG-D528。対象HttpMetricValve constructor/invoke/log/signalFailure/attribute契約/Completion.claim。既WebRequestTrace/WebStartupException・Micrometerの公的契約を利用し、実ネットワーク/HTTP/DB/VM/Root/鍵は起動しない。実起動順/owner assembly/exporterは未受入。群1836見積1/3/7pp、上限10pp、追加費の重複計上0。

| Test ID | 目的・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| HTTPTERM001 | 既traceの/login GET200、terminal250ms、二callback | 固定counter1、timer count1/250ms、HTTPstatus/body変更0。SS351の二metricとTomcat terminal ns。 |
| HTTPTERM002 | ASYNC/ERROR相当再invoke、64並行terminal、別request | request属性に一回claim、同request1/別request各1、registry借用close0。Servlet再配信と終端を分離。 |
| HTTPTERM003 | unknown URI/query/method、error/redirect/HEAD、正常0/Long.MAX | 既trace閉route/**とmethodOTHER、実status class、入力nsをそのまま記録。raw値label追加0。 |
| HTTPTERM004 | null/missing/型不正/負nanos/範囲外status/欠method/欠trace | 未観測を成功補正0、metric0、所有者terminal signal。NPEをcatchして正常扱いしない。 |
| HTTPTERM005 | 自己所有Requestの属性/getMethod/status故障 | metadataのIAE/ISEだけを固定失敗信号、graph内Errorは既helperで同一fatal。provider故障と混同0。 |
| HTTPTERM006 | 実registry Counter/TimerがRuntime/Error/循環graphをthrow | 元例外/fatal同一伝播、terminal1、再送/再記録0、partial sampleを完全成功化0。provider原文のformat/log0。 |
| HTTPTERM007 | 上記にowner signal故障/同一例外/抑制無効を重ねる | 元故障優先、既graph helperでfatal保存、借用資源close0。 |
| HTTPTERM008 | constructor/invoke null、next不在/checked例外、attribute override | 明示境界拒否/元HTTP例外同一、観測を早期成功化0、HTTP処理/認可の変更0。 |

fixtureは自己所有の未起動Tomcat Request/Response/ConnectorとSimpleMeterRegistry、固定UUID、固定ns/明示literal meter値。expectedのproduction method生成は禁止。実DB fixtureの旧Producer/ValveTestは選択しない。新sourceの正常六Main/Test compileと選択ordinary JVM PTを原snapshot/runへ固定し、元XML/終了/CRC・新クラス四counter/静的適用性を独立確認する。全体451/正式認定へは加算しない。実行command/環境/commit/hash/BUGは実行結果へ追記する。
