# 2393 P005 同期失敗後回復・借用buffer独立PT

2026-10-28、群P005_COORDINATOR_FAILURE_RECOVERY_ORACLES_V1、着手前2/6/10pp cap10、NK-MSG-001/WBS-P005-02、RD MQ-003～005/UI212/231/SS312§3.2・321§6/9/411/451。元8client＋5registry＋新4cleanup=17/3suiteを同source一execで確認する。旧9成功の確認再演はせず、必要なcoordinator失敗後条件に接続する。Production Main不変更。

## 新規独立oracle

| Test ID / method | 入力/操作 | 独立期待値 |
|---|---|---|
| PT-JMS-RECOVERY-001 / everySendFailureKeepsIdentityAndReturnsBothCapacities | capacity1、senderが順に固定JMSException/IllegalStateException/AssertionErrorをthrow、各直後に正常exchange | 同一Throwable instance/1send/自動再送0/pending0、同一clientで即再利用成功・固定reply{31,32}。Errorを通常業務例外へ変えない |
| PT-JMS-RECOVERY-002 / registryFullDoesNotCancelAnotherWaiterAndRecovers | borrowed registryを別IDで満杯、coordinator capacity1でexchange→元ownerがcancel→再exchange | capacity理由、sender0、別IDのpending1/未完了保持。ownerがcancel後の再exchange正常・pending0。別ownerの解除をclientが代行しない |
| PT-JMS-RECOVERY-003 / clockFailureAndDeadlineOverflowReturnTheWaitPermit | Clock初回が固定RuntimeException又はInstant.MAX、二回目NOW | 例外同一又はDateTimeException/送信0/登録0、その後同client再exchange正常。Instant.MAX+2秒はInstant定義域外の独立境界 |
| PT-JMS-RECOVERY-004 / suppliedRequestAndReplyBuffersRemainBorrowed | 256byte手書きrequest先頭11/末尾22、callbackで渡されたclone改変、固定reply{31,32} | 元request全byteが独立配列と一致、reply/受取値は別object、replyの後続変更が返却goldenを変えない、1send/pending0 |

null/不正capacity/body256下限/1,000,000上限/1ns～2秒/timeout/interrupt/全registry境界は原whole13で担保。新Testのexpectedは固定literal/例外instance/独立状態後条件、Production生成0。新Test未実施段階はPASSでない。Main違反は修正前BUG/YKTへ。

## fixture是正と着手資格

BUG2009/YKT1757修正前起票済み。原client Test二methodの元bodyを保持し、finallyに同thread interrupt/join2000ms又は同latch countDownを加える。逆全tokenと非同値負例で旧全assertion/golden/timeoutを保持する。新Testにthread/待機latchなし。whole旧8/5と新4全文・Main JmsRequestReplyClient/例外とReason/PendingReply/Registry/BrokerTopology/JmsRequestSenderを確認する。JMSExceptionはJMS APIのメモリ例外だけでprovider/接続を作らない。固定/自己mutable clock、自己有限worker、memory callbackのみ。実Broker/HTTP/DB/VM/Root/FFM/native/鍵/権限/保留例外graphへの接続0、未知/拒否操作を試行しない。

六normal/format/null（PT0）→閉17method一exec/外JVM240秒→PMD/CS/六SB→独立XML/CRC/全Main/旧Test物理差・全六artifactcounterとmethod詳細→同期/Thread文脈/owner traceを保存する。対象の実測未達は未達、B0はN/A、旧source/exec合成/除外追加0。原本/stash七/Currentbaseline/鍵/Backup/両成功失敗を保持、正式1964/53/歴史17-190/工数null/QA051final/全安全HOLD不変更。command/環境/source/時刻/exit/path/hash/関連BUGは2394へ実結果として保存する。
