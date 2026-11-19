# NK-OPS-001 Artemis起動前観測単体テスト仕様書

SSC-461／BUG-3233のPT-OPS-MQ-OBS-GRAPH-001／002は、それぞれ `inspect` の注入済みtopology口と `inspectEvidence` のローカルCore interface proxyが対象。独立した例外チェーンから同じError参照を返し、後続観測0回または先頭 `addressQuery` だけ1回で止まることを期待する。方法は新規2と既存029〜031をJava 25で同一source実行。実session取得、embedded broker、外部照会は使わない。対象commit、実結果、部分coverageはPG40320〜324を参照。

Program `NK-OPS-001`、PG267、class `ArtemisStartupObservation`、method `inspect`。RD MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §10/13・342 §4。既存の実Broker個別検査 PT-OPS-MQ-001～021 を、caller所有のOps Core sessionの上で順番に呼ぶ境界である。Productionは順に全6組Topology、Broker実効値、6 Address設定、loopback acceptor、role、6 Queue pressureを照会する。運用のgo/no-go決定、journal復旧エラー、credential出自、Expiry maintenanceは別の必須gateである。

| Test ID / method | fixture・入力・操作 | 独立した期待値と根拠 |
|---|---|---|
| PT-OPS-MQ-029 / `opsMq029OrderedReadOnlyObservation` | 6段階の公開Core session proxyと独立step記録、固定6 Addressの合成NORMAL/DLQ ALERTを渡す | SS321 §13の検査順0→5。戻り値は6件の変更不能snapshotで、呼出側map変更は反映されない。ALERTを勝手に起動可/不可と判断しない。default結線は最初にAddress queryを呼び、test-only proxyのfatalを隠さない |
| PT-OPS-MQ-030 / `opsMq030FailClosedAndNoLaterChecks` | 各6段階の任意1段で秘密を模した通常Runtimeを注入。null sessionも入力 | 失敗段より後の検査0件、固定redacted例外・causeなし。caller sessionの所有権を奪わない。nullはfail-fast。独立step記録を期待値とする |
| PT-OPS-MQ-031 / `opsMq031MalformedPressureAndFatalContracts` | pressureの空/1欠落/1超過/null要素/null map、最初の検査にfatal Error、6依存の各null | 固定6 Address集合以外は拒否し未完成観測を返さない。fatalは元identityのまま伝播し後続0件。各constructor nullは拒否。SS321固定6組とJava所有例外契約をoracleとする |

正常・欠落・空・未知・null・通常例外・fatal・後続停止を網羅。並行安全はimmutable構成であり、各低位clientの並行PTを参照する。選択commandはJava25/Maven3.9.12 `-pl src/schubert-nk-batch -Dtest=ArtemisStartupObservationTest test jacoco:report`。正式全reactor、commit、line/method/class/branch/instruction coverage、実行日時/環境/結果、関連障害、sanitized input/期待/actual/hashは039と`evidence/manifest.json`へ固定する。Production methodからexpectedを生成しない。失敗・flaky・skipped・not-runは合格に算入しない。
