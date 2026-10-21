# Ordinary JMS secondary・duplicate前fatal PT仕様（実装前）

485実物のcost owner：OutboxJmsSender=WBS-P006-02、WebLogMessageSender=WBS-P006-04、ArtemisRequestSender=WBS-P005-02、共通口P018-05/06は既製造の参照費0。開始fresh used62残38/window10080/reset1793082864/secondarynull/券0、指定model維持・実設定未確認、token N/T/専有費null。

新群ORDINARY_JMS_SECONDARY、BUG1598/YKT1351、SS312321324354/SSC320～323/330。既WBS内の追加発見・製造手戻りであり新業務要求ではない。着手前見積低.3/標準1/高3共有週次pp（PROVISIONAL_UNCALIBRATED）、SQL1625の.5/1.5/4・原-v4とは別に保持し、同common portの再製造費を加算0。個別実配賦/N/T null、各cost ownerは485実物でTest具体化前に確定する。

PT_DEFAULT：pure JMSContext/BytesMessage/JMSProducer proxyと公開合成wire/暗号入力のみ、broker/DB/VM/Root/failed cohort/認証・鍵取得/外部通信なし。旧sender domainsの自己所有embedded Artemis/DBは別判定を継承、実MQ/native/CHRの受入と混同しない。wire fixtureの入力組立に既codecを再利用する場合も、expected Error identity/順序/counter/duplicate条件はSSの独立literalから作り、Production duplicate predicateをexpected生成へ呼ばない。

## 予定九観点（具体class/method/hash/runは実Test宣言後、実行前に固定）

- API Outbox送信：001 suppression無効primary＋rollback wrappedError、closeは一回。002 primaryがcause/linkedで確定duplicate、rollback suppressedにErrorがある時も成功に戻らない。003 nonfatal循環/通常duplicate、suppressedだけのduplicateは未確認のまま、直接primary/close Errorの既優先。
- Web WLG送信：004/005/006は上記と同じ分類、さらにraw primary＋close wrappedErrorを失わずplain wire wipeを保持する。
- Web request送信：007 rollback wrappedError保持、008 close wrappedError保持（close後に元Errorへ伝播）、009 nonfatal/直接primary-close優先・body/TTL/metadata不変更。

API closeのprimaryはstandard typed wrapper又はprimaryErrorなので、単語だけで一括置換しない。API/WLGのduplicate predicateはcause/linkedだけを確定根拠とし、suppressedをduplicate根拠へ拡張しない。fatalはその成功判定より先に排除する。ただし分類Errorをclose前に直接throwして既direct-close優先を変えないよう、必要な内部transport carrierでdeferし、全owned close後・ordinary mapperへ渡す前に必ず元Errorへ戻す。carrierはbusiness catalogや成功/通常retryへ到達させない。

正常/境界/null/各取得段・send/commit/rollback/close/同一Throwable・alias/cycle/duplicate＋Error・直接closeError合成を独立counter/固定objectで確認。原反例を保存→必要三Mainの最小PG→全新/旧Test bytes固定のgreen/既domain→原source/Jar/XML/counter/static→まとめ必要全体/F03/trace/PGPTへ。品質・HOLD/正式/QA051final/原-v4は緩和しない。
