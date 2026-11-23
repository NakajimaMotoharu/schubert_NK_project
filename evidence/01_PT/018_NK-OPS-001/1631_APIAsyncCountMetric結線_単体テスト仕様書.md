# 1631 API Async count→metric 結線 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS331332351/PG-D541。AsyncJobMetricCollector.constructor/collect/snapshot、ASYNCCONN001～008。同ownerのreadonly Repositoryと実SDK五gaugeを結線する内部部品。自己所有JDBC proxy/SDKのみ、実DB/role/driver/Root/VM/cohort/鍵/permit/配備/ネットワーク操作なし。

| Test ID | 事前条件・入力・操作 | 独立期待値 |
|---|---|---|
| ASYNCCONN001 | DEBUG・五row1..5、初期→一collect | 初期全NaN、SQL一回/RS→PSclose後、五値1..5/total15/同Snapshotを返却保持、五seriesだけ |
| ASYNCCONN002 | 成功→SQL失敗→empty成功 | 失敗は同SQLException・snapshot空/全NaN、古い成功/0へ誤補完0、次真正emptyは全0 |
| ASYNCCONN003 | 全tx/getter/prepare/query/RS-PSclose故障 | 同一checked/Runtime/Error伝播・retry0・全失敗で未知、caller connection所有保持 |
| ASYNCCONN004 | STANDARD・getter失敗fixture/null | DB getter/prepare0/詳細登録保持0、nullは先行拒否、最小health停止は行わない |
| ASYNCCONN005 | null repository/registry/mode・未知mode/null conn | constructor副作用前のnull/invariant拒否、既正常snapshotはinvalid null入力で不変 |
| ASYNCCONN006 | 長時間待機を模擬する自己所有connection/二caller | private owner lockによりread→close→publishの順序が直列、一query中の二番目query開始0、後発成功値が最後 |
| ASYNCCONN007 | 64並行・owner独立row/registry | 全返値の固定owner count/total、五series固定・mixed snapshot0・別owner汚染0 |
| ASYNCCONN008 | 循環cause/非formatableRuntime/Error・closefailure | 元failureのidentity保持/原因走査・format・再送0、失敗をUNKNOWNにし次成功は回復 |

独立expectedはSQL literal/固定row/数値・全NaN/series名とlabel・資源call順。production methodからexpectedを生成しない。既Repository fixture二型をpackage共有にするだけでoracle変更なし、当sourceの必要既API16＋新8=24PT3suite予定（未実測）。全Java/CRC/session・四counter100/NullAway/SB/PMD/CS、normal六compile/Jar全byteとtraceを確認。未知原因のruntime権限/接続/外側有限期限を内部lock/timeoutで証明したとはしない。

実行command・OS/JDK/tool/branch/source/time/exit/XML/coverage/資源・BUG/SSC/path/hashは元PG7328/7330以降manifestへ保存予定。actual DB identity/role/driver/tx期限/collector起動/Root/exporter/native/CHR/全体451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0維持。PG/PT不具合は修正前915/916、TDD未実装は障害に算入しない。

## 2026-11-24 排他方式の是正

BUG-3743／YKT-2929。取得済み資源の解放から同ownerの完全値公開を私有ReentrantLockに保持し、正常・早期return・元Throwable再throwの全てでfinally解放。借用Connection、read-only契約、取得資源の順、公開後の値と既ASYNCCONN001～008の独立期待を維持する。PG43812の局所scopeで元指摘と生四指標を照合。実DBを使用しない。
