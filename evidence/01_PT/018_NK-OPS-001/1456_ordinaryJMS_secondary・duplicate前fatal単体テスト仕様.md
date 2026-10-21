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

## 実行前固定（2026-10-22、管理三検査0）

独立TestはAPI `OutboxSecondary330Test`三method（001..003）SHA256 `5137af76ddf50588a1ca2f12aac06e16546c86cc1cac1cc4a88303188a78680f`、Web logging `JmsSecondary330Test`六method（004..009）SHA256 `640c6d71223b113e5967fcb6a5ff3736f17755ca63fa64776cd52be48cf000ed`。全旧Test/Main d25f固定。formatter19613終了0。request TTLのexpectedはSS321の5秒を直接5000とし、実行前レビューで草稿の30000を是正、Productionから期待値生成0。Goldenは明示byte位置（API320/request256）、WLG inputだけ既qualified golden/codecを再利用、expectedは固定Error object・操作回数・配列0/不変・metadata literal。

API/WLGのtyped transport例外は既SSC322/323の実final receiver `OutboxDispatcher.preserveFatal` / `WebLogDispatcher.preserveFatal`で実際に分類した結果をactualとする。これは期待値生成ではなく既send→ordinary mark/retry直前の実処理接続。sender内部のtyped carrierは許容、final receiverで元Errorになることを独立identityで検査する。requestはそのような最終分類口がなく、senderのowned close後の公開boundaryでError identityを要求。後処理前に分類してdirect-close優先を変更しない。

driver `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6626_jms_secondary_selected.py PHASE`。同Main/Test sourceを固定して`red-api`=PG6626（計画15/8、実際停止予測9/5/F2、後段6未実行）、`read-api`で予定001002のboolean assertionだけを原XML/終了1/phase0,0,1と照合。続いて`red-web`=PG6628（18/8、実16/6/F4、後段2未実行）、`read-web`で予定004005007008の同assertionを照合。残003006009は既非fatal・duplicate範囲・direct優先・metadata/wipe controlで合格予測。fixture unknown method数0と操作回数をidentityより先にassertし、準備失敗を目的反例に算入しない。実行/合否はまだ未確定。

必要三Main PG後は全新/旧Test bytesを固定し、`green`=PG6630/86件17suite（六baseline12/7＋API39/5＋Web35/5、各既sender/dispatcher/helper domain）、真正終了0後だけ`qualify-green`=PG6632で原source/archive/XML/Jar/851Main/1667physical・三sender family差分・四counter・静的原証拠を照合する。新nine/二suiteが増えた全体の宣言は4158/635見込みであり、後続の実宣言検査で確定するまで数値もPASSも認定しない。別source/選択結果の合算0、formal/accepted17-190/工数null/F03/全HOLD不変。
