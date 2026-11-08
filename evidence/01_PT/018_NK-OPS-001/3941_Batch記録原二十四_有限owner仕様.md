# 3941 Batch/Integrity/Restart原24 有限owner仕様

G03.05主/P01809関連、REWORK着手前見積1/4/8pp・上限10pp。既2819/2820のwhole38は歴史値として保全し確認再演しない。Label14は25132/34で別sourceの限定再試験済み。今回は残る原whole3・24を、実在する無期限invokeAll/Executor TWR終了の是正後に一度だけ再試験する。Main7aed・元Test全body/literalを固定し、変更は待機と所有終了のみ。

|原whole/Test ID|件数|独立期待値・異常/境界/null/例外/並行|
|---|---:|---|
|BatchMetricRecorderTest/BATCHREC001..008|8|40counter+10gauge、4状態×10step、NaN、10.25/11.5最大、UTC0001/9999とmicro精度、invalid副作用0、provider同一例外・再送0、64件=64/max64、別owner1000/0|
|IntegrityFailureMetricRecorderTest/INTEGRITYMET001..008|8|3area×10step=30、4×30+1=121、閉enum/unknown/null、STANDARD0、partial factory1、失敗前後0/1・補償0、64事前入力を独立集計、foreign gauge7保持|
|ProcessRestartMetricRecorderTest/RESTARTMET001..008|8|4reason×6service=24、4×24+1=97、閉enum/unknown/null、STANDARD0、partial factory1、失敗前後0/1、64事前入力を独立集計、foreign gauge7保持|

実装前BUG2576を915へ起票し同因YKT2177を継承。pool/executor3 ownerをregistryの内側で単一finally shutdownNow/await10へ、3 invokeAllを10秒化。既Integrity/Restart Futureget5を保持。Batch getはtimed invokeAllの終端Futureのみ取得する既bodyを保持。registryは従来TWR所有・workerより後で終了。追加仕様/QAは不要。

NORMAL_PT: 全Main/Test/必要helperの全文レビューとSDK graph確認を条件とする。所有SimpleMeterRegistry、固定/MockClock、counter/gaugeと固定入力だけ。SDK内部Clockは計測SDKの通常実装で実health/OS/JMX収集ではない。実Batch/DB/JMS/Root/VM/OS/process制御/backup/鍵/FFM/外部export/network0、held4 compile/init/probe0、二RootTest/保護工具二名はIO対象外。BatchMetricContractTest全文は定数compile-only、選択5件再演0。

現在Consoleプロフィールを既1.17.1 Micrometer必要Jarだけへ拡張し、Jar/Source/class CRCを固定。元whole24一JVM・独立post・同source/case/XML/終了/CRC/coverage/静的分類とSS351固定oracleで確認。対象は3Source5Code全体、非空四counter100と自然B0=N-Aを区別、別run exec/coverage合算0。新unique/leaf/正式受入0、1964/53・工数null・全HOLD維持。失敗は再演で隠さず元before/exitを保全する。証跡はPG25144/46/48/50/52/54、実command/環境/hashはmanifest、結果は3942。動的証拠前は未実行。

着手記録の初回呼出はPYTHONPATHにvm/050_s1がなくModuleNotFoundErrorでevent生成前停止。製品未実行、同一helperへ正規module pathを設定して4525を一度記録。工具本文/原event不変更、開始準備失敗1として残し成功0へ隠さない。
