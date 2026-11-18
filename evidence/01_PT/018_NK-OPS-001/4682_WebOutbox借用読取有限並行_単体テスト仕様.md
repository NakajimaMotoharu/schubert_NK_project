# Web Outbox借用読取と有限並行

BUG-3288、YKT-2387/2691、P004-05、P018-09、F03/2-2。1721／2665の元DB10・Collector8・Recorder8と、SS332/351/354、RD171・UI252の既期待を使用する。固定SQL、元2/8 worker、元64操作、先後のclose・borrowed Connectionの無変更、メモリ公開順は既試験どおり。

WEBOBXCONN006/007、WEBOBXDB010は元Futureを維持し、明示finallyでshutdownNow、5秒のawait結果を要求する。WEBOBXCONN006は元latchを閉じてから停止確認し、既方針どおりRegistryは所有workerの生存中に保持する。WEBOBXCONN004／WEBOBXMET004は固定した同hash二異値の拒否を、SQL・登録の副作用0と独立に確認する。

既whole26の合成JDK Proxy、自有SimpleMeterRegistry、JUnit/Java25。実DB、driver、JMS、Root、serviceの活動を含めない。原二fixtureの閉包を保ち、当source・ABI・静的・一exec・合否・生不足をPG39554へ保存する。
