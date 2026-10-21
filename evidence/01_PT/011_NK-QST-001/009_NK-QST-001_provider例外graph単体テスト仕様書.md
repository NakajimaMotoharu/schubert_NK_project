# NK-QST-001 / NK-ASY-001 provider failure graph PT specification

暫定PG/PT、正式認定/旧005～008を変更しない。WBS-P012-03、BUG1592/YKT1345/SSC329330、RD QST003/101・ASY001..009、UI213/224/236、SS312 §8.1/SS332 §8.1/SS324/354。対象QuestionWorkerService.processのprovider後処理、API共通fatal分類口。関連群1625/018の1441、012_NK-ASY-001/001。

## Fixtureと着手前判定

PT_DEFAULT。自己所有ApiLogDatabaseFixture（PG18/production Flyway DDL・合成行・一時directory）、既QuestionSubmissionServiceTest.Fixtureの入力/接続spyだけを再利用する。自己所有pool/codecはclose、PG fixtureはAfterAll stopする。質問本文は`Public fixture`、固定2026-10-01T00:00:00.123456Z・型付き合成ID。実credential/session/token/原本DB/Backup/鍵/VM/Root/外部AI/配備は使用しない。h.confirmOnSignalは自己DBのOutbox SENTを与える入力fixtureであり実JMS/ACK/native成功の証明ではない。期待値は下記literal SQL後条件/元Errorから独立に作り、Production methodでexpectedを生成しない。

|Test ID / method|入力・操作|独立期待|
|---|---|---|
|PT-QWK-GRAPH329001 providerBusinessMarkerFatalCannotBecomeBusinessError|受付fixture確立→delivery1、providerはAnswerBusinessException.suppressed→Runtime.causeの元Errorを含めてthrow|元Error identity。provider1回・provider実行中/帰還後live DB connection0。SS332 RECEIVED→PROCESSING commit後なのでjob/notificationはPROCESSING・error/completed時刻なし、answer0、Outboxは元work1のみ。通常ERROR/PROCESS_FAILEDへ変換しない|
|002 providerRuntimeFatalCannotBecomeFinalDlq|delivery4、provider Runtime.cause→SQL.next.causeに元Error|元Error identity、provider1/live0。job/notification PROCESSING、answer0/Outbox1のまま。ERROR/SYSTEM_UNAVAIL/DLQ追加をしない|
|003 nonFatalProviderCyclesKeepApprovedBusinessAndFinalRetryOutcomes|別fresh fixtureでBusiness又はRuntimeのcause/suppressed循環、Error無し。Business delivery1/Runtime delivery4|有限帰還。businessはERROR/PROCESS_FAILED/Outbox1、runtime最終はERROR/SYSTEM_UNAVAIL/Outbox2（SENT proof fixture）。answer0/provider1/live0、重複処理を発行しない|

PROCESSING期待はSS312 Workerのbegin commit→provider→完了transactionという順とSS332 §8.1 SQLから算出する。Errorにより後続完了/失敗transactionを実行せず、すでに確定したbeginをrollbackしたことにしない。既非fatal失敗の期待は005/AWORK005・最終retry/DLQ仕様から保持する。wire copy wipeはprocess finallyが両Error exitに到達するsource/JVM/当coverageへ結合し、private field reflectionや未観測memory値で実測を作らない。

赤は新3＋baseline12=15/8、API停止時9/5/F2を予測（Expected AssertionError but nothing thrown、後段6not-run）。新反例だけの赤→原XML照合→変換前guard・必要同群PG→同oracle/既業務domain・必要同source全体で確認する。Unknown/compile/timeout/errorを目的赤としない。

実行command/OS/JDK/version/branch/source/archive/終了code/XML/hash/当counter/障害/再試験は010と018の公開manifestへ真正回収後記録。現在は仕様だけで未実行、coverage/各domain/全品質/正式/native/IT/STは未受入。
