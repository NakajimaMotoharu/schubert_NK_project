# 1326 SS319 試行・正常rollbackの独立仕様

NK-MSG-001/NK-ASY-001、RD MQ003008010/UI213231/SS312321342354/SSC319、BUG1565/YKT1322/PG-D473。publiclistener/consumerの旧正常・exception identity/ACKcommitrollbackDLQ/既最大再送とnative UNKNOWN/親Unit期限を維持し、catch型から確認済rollbackを推定しない。

Main1baのままConfirmedRollbackCallbackTest三件を追加。予定PG6236 newonly15件/8suiteは既base12/7＋新3の実source宣言で確認した数で、成功数ではない。new class Testだけの差分をguardしMain/gates/Current byte不変更、全六format先行。有限の自前JMSContext/JMSConsumer/BytesMessage proxyだけで、socket/DB/VM/Root/credential/intent/permit操作0。preflight情報、同callbackの操作回数、ready/fatal/処理0、閉鎖した自前contextだけを独立検査。PTPRE041/PT_DEFAULTの安全条件内であり拒否境界を探る試行ではない。

| Test ID | 独立入力/観点 | SSに基づく固定期待 |
|---|---|---|
| rollback319001 | 三consumer × null message/session invalid/RTE/Error preflight | ready false/fatal1/commit0/processor0、通常preflight rollback0、直接Errorだけ既best-effort1、以後callback拒否 |
| rollback319002 | transport getterがJMSException→正常rollback、次配送null | 一回目ready true/fatal0/rollback1、次はready false/fatal1でrollback追加0。前配送confirmedを再利用しない |
| rollback319003 | transport getterがJMSException、rollback自体がError | 未確認の同rollbackを二重発行しない。一回/ready false/fatal1/commit0/processor0 |

一@Test内の三consumer/各入力loopは別PTへ算術加算しない。redで最初のassertが失敗した以降の入力は未実施として残す。fixtureのexpectedは上表のliteral回数/状態で、Productionを呼んで生成しない。MessageはSS電文の期待値生成ではなく、最初のgetterで決めたJMS transport faultをthrowするだけ。全自前contextはfinally一回close、実JMS native正常停止のreceiptとはしない。

予定command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:…/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6236_confirmed_rollback_red.py`。新only一回・真正失敗/未実施も保存、Main/Testは終端まで固定。定義15/8・pyflakes0、正規API Spotless apply元9647真正0。Sourceへのcode context patchは正規format後の行形と一致せず検証拒否された一回があり、その時点では書込なし、現fileを再読しOwner.closeをchecked Exception無しのRunnableへ修正してから正規formatした。工具の拒否をsecurity拒否/試験実行済みとはしない。

red後PGは同接続経路の七Mainを予定：三consumer、二実listener（Sync/TransactedEvent）、二Question/WebLog wrapper。context取得前にattempted/confirmedの独立AtomicBooleanと同期portを用意、配送ごとreset、Sync各context内で別state。listenerはrollback直前attempted・正常帰還後だけconfirmedを通知。ordinary catch未confirmedはhalt/terminal/fatal（追加rollback/ACK/commitなし）、direct Errorの既best-effortは未attemptedだけ一回。rollback Errorを別型へ包まず元Error identityを保つ。public既entryは観測無しportで互換のまま。

追加PTは同配送reset/別context並行、正常transport rollbackとrollback Runtime/Error、不確定DLQ/CommittedFatalと旧typed境界、通知port null/順序/例外・元public identityを検査する。全影響listener/consumer既suiteと現64を合わせて実source inventoryで数を確定、同source原資格/JVM・変更群の必要全回帰一回へ。中間whole4028未実施を合格にしない。actualRoot/VM/current/cohort/intent/permit・PTALT範囲不明・全native/CHR/全100/451/trace/QA051final/正式1964-53は別未完。

fresh29/残71/reset1793082865/券0、usage04c45505/N/T専有費工数null。1490開始1/4/10・今後1.5/7/17（既1565追加依存を含む未較正）と原v3v4を維持、試行/正常の内部補足を二重費用計上しない。通常red/小群/commitで停止せずPG/PTへ継続する。
