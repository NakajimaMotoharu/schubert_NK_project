# 2799 BatchStepValues原八件仕様

event3192/primary leaf P017-02.01、着手見積.5/3/7pp、source6b53/normal14216固定。初回親P017-02のevent validationは拒否しguardで後段全停止、job/event未発行。実leaf確定後に3192を発行し0を確認、失敗を合格とせず見積不変。artifact正本ownerはStep/Result P017-02、Attempt P017-12、工程費用groupから推定しない。

関連NK-BAT-001/OPS009/UI251/SS331§8.3/SS341/SSC055/PG163、原PT-BAT-130～137。対象BatchStep/BatchStepAttempt/BatchStepResultの完全3Source/5physical（Result outer+Status+Reason）。原Test全288行、必要Main Step/Attempt/Result/BatchRun/MaintenanceActivation全bodyを読了。

|Test ID|原method・独立期待値|
|---|---|
|PT-BAT-130|closedStepsAndBackupPolicy: 閉10stepと固定BACKUP policy/未知名拒否|
|131|attemptIdentityAndBounds: id1～999999999999/attempt1～99/skip両値・範囲外拒否|
|132|terminalStatesAndReasonMatrix: 固定4status×11reason、独立code/summary/allowed matrix|
|133|counterAndStatusBoundaries: 四counter負/極値/skip0/success failure0、存在しないsum制約を作らない|
|134|temporalContractAndBusinessDay: 固定cutoff/歴史1582 LMT/境界microsecond/9999年とJST civil date|
|135|nullContractsAndRedaction: null拒否/固定redaction、private Historyは公開合成引数だけ|
|136|immutableValueSemantics: record値等価/hash/差分|
|137|independentConcurrentValues: own virtual64tasks、各future5秒/親JVM180秒、固定date/id/attempt|

## PT着手判定

NORMAL_PT、純値/固定literalとown threadのみ。原nullContracts内のreflectionは `BatchRunRepository$History` 一型のprivate record constructor/toStringだけ。Source496～502全bodyおよび外側のfields/constructorを読取、classfile全9methodにclinitなし、JDK javapの受動読取actual0でconstructorがRecord.super+field storesだけ/toString固定literalを確認。Repository instance/Connection/実DB/Rootを構築しない。外側502行全体のDB機能を読了・試験・Source資格化したとは主張せず、当private recordの部分測定も親全Sourceへ昇格しない。

fixtureはTest内公開UUID/time/status/counter literalのみ。期待値をproduction呼出から生成せず、全原8を保持して分割・除外しない。actualFiles/native/VM/DB/鍵/Graph/外部接続0。既BatchRun/MaintenanceActivationは旧資格を保持し新三Sourceへcounter合算0。既926の確認再演0。

command checked entry pg14910_batch_step_values_eight_pt.py、JDK25.0.4/proc:none/Werror/JaCoCo0.8.15。原Test hash4f6c9eca、Main Step f736e4cf/Attempt a37a929c/Result d4d8f244。新一exec/session/CRC/全closureの四counterと実不足/N/Aを独立記録し、四100・451・正式を捏造しない。実環境/source/command/exit/時刻/coverage/hash/関連障害は2800・PG14910～14へ。
