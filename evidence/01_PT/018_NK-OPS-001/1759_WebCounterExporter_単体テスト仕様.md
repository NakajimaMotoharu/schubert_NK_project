# Web Counter標準text PG/PT仕様（group1986）

NK-OPS-001/RD171/UI252/SS351 §metric・SS311 app責務/411、WBS-P018-09（C07参照、追加予算0）。開始source3968abacec2052b9e7b803702a3a9231f9209f26。見積2/4/8pp・群上限10pp、fresh25使用/75残はPG8332/event1986に固定。正式受入・工数・451全体を更新する群ではない。

## 実装・所有

WebCounterMetricExporterが借用registryのapproved `_total` Counterを公式Prometheus SDK model/textへ変換する。Web内だけのWebMetricTextへnamespace深いcopy・exact tag検査・UTF8 writerを集約し、既WebDurationのAPI/秒変換/例外messageを維持する。Bootstrap追加なし、API/POM不変更。値は単一count読取、有限非負（汎用Counter小数可、HTTP producerは整数）。sourceを閉じずprovider failureを隠さない。暗黙config/clock/HTTP/endpoint/VM/DB/サービス/実networkなし。

## 固定matrixと独立oracle

| Test ID | class/method prefix | 入力・期待・根拠 |
|---|---|---|
| COUNTENC001 | WebCounterMetricExporterTest.countenc001 | literal2.5、`nk_http_requests_total`一系列、TYPE counter・suffix重複なし・createdなし。SS351名とSDK形式 |
| COUNTENC002 | countenc002 | 0/MAX_VALUE/MIN_VALUEを変換せず有限値として出力、負/非有限を003で拒否 |
| COUNTENC003 | countenc003 | -MIN/-1/NaN/±InfはIAE、0へ正常化しない |
| COUNTENC004 | countenc004 | 二系列とquote/backslash/newlineのwire escaping、明示literal |
| COUNTENC005 | countenc005 | 同名Gauge/Timer/SummaryはIAE |
| COUNTENC006 | countenc006 | source/map/name/keys/要素nullはNPE契約違反、catch正常化なし |
| COUNTENC007 | countenc007 | 不正suffix/label/leとlabel欠落・過剰はIAE |
| COUNTENC008 | countenc008 | provider duplicate tagはIAE |
| COUNTENC009 | countenc009 | unknown meter無視・空namespace/registryは空text |
| COUNTENC010 | countenc010 | borrow source保持、閉鎖済みはISE |
| COUNTENC011 | countenc011 | count()一回だけ、書込・別scalar呼出なし |
| COUNTENC012 | countenc012 | provider RTE identity保持、borrow owner保持 |
| COUNTENC013 | countenc013 | provider Error identity保持、成功へ変換なし |
| COUNTENC014 | countenc014 | namespace/label setをproviderより前にcopy、入力変異に非影響 |
| COUNTENC015 | countenc015 | writer IOException→UncheckedIOException、同cause/固定message/source未close |
| COUNTENC016 | countenc016 | writer null/不正namespaceをprovider読取前に拒否 |
| HTTPCOUNT001 | WebCounterExporterContractTest.httpcount001 | real Web registry/HttpMetricRecorder DEBUG、35×10×5=1750ゼロ系列・TYPE1、helper/timer漏出なし |
| HTTPCOUNT002 | httpcount002 | GET200二回/POST404一回/GET503一回を独立固定2/1/1、他0 |
| HTTPCOUNT003 | httpcount003 | 未知route/methodを`/**`/OTHER/5xxへ1、raw不在 |
| HTTPCOUNT004 | httpcount004 | MockClock一日経過しても件数1、durationと独立 |
| HTTPCOUNT005 | httpcount005 | 有限64worker完了後64、別owner/STANDARD空、borrow保持 |
| HTTPCOUNT006 | httpcount006 | 全10method×5statusの固定入力各1、route外0、合計50 |
| TIMERENC001～016 | WebDurationMetricExporterTest | 1757の既独立literal/ns/negative/checkedIO全16を必要回帰（新成果へ数えない） |
| HTTPEXP001～006 | WebTimerExporterContractTest | 1757実Web memory接続6を必要回帰、fixtureそのまま |

新22＋必要既22＝44/4、一回の真正JUnit、F/E/S/aborted0必須。独立oracleはliteral、固定50/1750・closed catalog fixture、production expected生成なし。並行は有限future join10sec、sleepなし。

## 品質・証跡（未実行）

source固定後、正常六module package/NullAway/Spotless→当44の一exec→WebCounter/WebDuration/WebMetricTextの実line/method/class/branch各100・CRC/session/static→全physical/source/所有traceを新sourceに束縛。必要なら未網羅条件を意味あるnegativeで補完して新source結果を保存、旧成功流用なし。API/旧全4222を確認目的で再演しない。PG83xxの再現工具/manifest/入力hash/exit/XML/exec/coverage/staticを1760へ列挙する。Failed/未実行は合格0、実装済み違反は修正前915/916へ。

現在実行結果/coverageはUNRUN。実Root/VM/native/DB/endpoint・whole451/CHR/final受入はHOLD。formal1964PT/53scope・原190新受入0・工数nullを維持、IT/ST完了宣言なし。
