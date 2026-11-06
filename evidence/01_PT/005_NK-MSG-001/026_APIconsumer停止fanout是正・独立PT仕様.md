# API consumer停止fanout是正・独立PT仕様

NK-MSG-001、WBS-P005-03、SS321SSC314、BUG-2407/YKT-2152。対象はApiMessagingRuntime.close、SyncRequestConsumers/WebLogConsumers/QuestionWorkConsumers.stopDelivery/close、およびpackage-local InboundConsumerGroup。既取得owner集合をこの内部契約へ型付けし、全childの既halted flagを先にtrueにしてから既逆順closeを行う。新規owner/port/workerを取得後に作らない。

これは既承認の「停止後は新callback非受理」を満たす内部是正で、上位仕様変更や新QAを必要としない。要求根拠はorigin/main SS321SSC314。親ready停止、子callback非受理、子close完了を別の後条件とする。close順/成功phase/再close範囲・エラー順位/UNKNOWN・進行中処理のACKrollbackを維持する。

| Test ID | 事前条件・操作 | 独立期待・根拠 | 現状態 |
|---|---|---|---|
| PT-JMS-STOP-GROUP001 | complete4+1+1正常起動、ASYNCのcloseが既処理完了を待つ位置で、SYNC/WEB_LOGへ新callback entry | parent close開始後の業務processor呼出し増分0、全6contextの新entryがguardで止まる。SS321SSC314に由来しProductionからexpectedを作らない | NOT_RUN/HOLD。新fixtureや選択抜粋でheld graphを再演しない |
| PT-JMS-STOP-GROUP002 | legacy4+1、最初のWEB_LOG close待機中にSYNC callback entry | 新業務処理増分0。completeだけへ是正を限定しない | NOT_RUN/HOLD |
| PT-JMS-STOP-GROUP003 | callbackがguard通過済みの状態で親close | 既listenerのACK/rollback規約を維持し途中打切り/新rollback/commitを発行しない。新entryだけを拒否 | NOT_RUN/HOLD |
| PT-JMS-STOP-GROUP004 | child close失敗/UNKNOWN、明示close再確認、成功子を含む | 全子の停止flagを維持。正常帰還済みchild/contextを再closeしない。逆順group/既context順/元failure順位を維持しUNKNOWNを成功にしない | NOT_RUN/HOLD |
| PT-JMS-STOP-GROUP005 | 単独child.close、繰返しstopDelivery/close、親closeの同時要求 | flag通知はidempotent、既close lock/成功phaseが直列化、完了後no-op。新terminal failure通知を正常stopから発生させない | NOT_RUN/HOLD |
| PT-JMS-STOP-GROUP006 | resource acquire/設定/起動途中の失敗、部分owner集合0/1/2/3、null/未知callback入力 | 所有済み集合だけを停止し既cleanupを維持。停止済みcallbackは入力/processorに触れない。元null契約と早期拒否を維持 | NOT_RUN/HOLD |

実装の静的確認は全3stopDeliveryがAtomicBoolean.set(true)だけで、resource/queue/context/DB/権限へ作用しないこと、親は最初のblocking closeより前に既owner集合へ全通知すること、closeから同通知を呼ぶことを独立の順序表から確認する。Java type/null検査・format・通常Mainコンパイル・六module静的解析は新sourceで行う。Test contentはsnapshot作成前に除外し、四heldの初期化/実行や元RootFailed二Testの読取/compileをしない。

動的再現・回帰・line/method/class/branch coverageは未測定nullである。コンパイル/静的解析の成功をこの6TestのPASSに換算しない。BUG/YKTは修正sourceと静的結果を記録しても、必要な再試験/横展開の受入までOPENのままとする。旧source4217/normal20990の成功を新source全体へ輸入しない。
