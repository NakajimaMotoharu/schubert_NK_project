# 2437 JMS受信三owner・未分類72のPG強化レビュー仕様

2026-10-28、source db33c6a371d3dbc8e84f70462e0e56351bbb18b4、保存c795452aa07451133a89d7b4717fe61e1cf3d641/push25858真正0/origin一致。群JMS_CONSUMER_THREE_OWNER_PURPOSE72_PG_REVIEW_V1、開始見積低1/基準3/高6pp・cap10、共有used9残91/reset1793774153/secondaryなし、専有費/N/Tnull。候補選定で三Main全文と既Testの宣言/一部assertを既に閲覧した事実を記録し、群着手後の新規実績に遡及算入しない。原/v3/v4/v5の見積・担当費不変更。

対象は`src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/`のQuestionWorkConsumers.java、SyncRequestConsumers.java、WebLogConsumers.java。原catalogで現存かつ目的未参照の各24=72を対象にし、他診断や旧分類を変更しない。関連RD MQ003/006/008/010・MON003/005/ASY001～009、UI212/213/231/251、SS311/312/321/342、既PT-JMS-013/015/CORE-001～008・SSC314/316/319/332/333。元owner/costはQuestion=P01201、Sync=P00503、WebLog=P00605、F03は参照のみ追加費用配賦0。

## 確認方法と期待

- 固定normal13242/current全1821静的13253・旧原catalog10690・13258 stateのhashを照合し、当三Main＋既三Testのcurrent SHAを束縛する。新PMD/六build/動的PTは不要なため起動しない。
- 72=CloseResource7/Generic catch39/instanceof23/synchronized3。各IDをcurrent診断へ位置以外の全attributes/message multisetで照合し、enclosing method/当source行/目的分類/具体的source anchor/既Test期待参照/残存リスクを保存する。重複signatureは個別発生位置IDを推測しない。
- 長命contextは返却ownerのcloseが担当しconsumerはcontextに従属する意図、部分起動失敗の停止通知→close、Error優先/同一Throwable自己suppression防止、有限四contextの全close試行/成功flag、close lockとhalted可視化を全文で確認する。provider契約や任意Throwable graph/未確認close/外部process停止を動的に証明したとはしない。
- catchの目的確認は握潰し合格/禁止解除でない。rollback失敗時はHALT/owner非zero前提を記録し、通知callback失敗・graph accessor・closeの局所期限がないリスクを明示する。既Testのassertはsource期待の根拠であり当sourceの実行成功ではない。
- 独立postは元diagnostic集合/72各lineとsource hash/ルール別件数/元責任費/旧runtimeを再照合し、sourceすり替え・ID欠落/重複・分類漏れ・PT/coverage/品質PASS捏造等を反例で拒否する。

目的参照+72候補以外の是正/新TestID/新受入0。raw8022/corr1419は不変更、全F03/451未受入、正式1964PT/53scope・個別17/190・工数null/QA051final保持。実JMS/DB/VM/Root/Graph9/保留二工具/私有rawは非アクセス・非実行、通常群/commit/報告/PMO待ちで停止しない。結果2438/PG-D786へ保存し、freshused10で定期点検（停止でない）、残10以下又は取得不能時に新規停止・保全する。
