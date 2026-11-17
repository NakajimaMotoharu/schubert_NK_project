# Outbox保存値と宛先 単体実行結果

PT-OUTBOX-VALUE-RAW、SS312/331/351、WBS-P006-02/P018-10.03/F03。Core `47aeed19a157661363ffab5c4b5054f6b20230a1`、Unit `55847b1611d32bceeac0f5ee3a3254bb470f9547`、PG38282/84。旧whole4とprofile whole2、新2全8初回成功、失敗・エラー・skip・未実行0。対象はOutboxEntry 51L/19M/18B、OutboxRequest 27L/12M/2B、OutboxDestination 13L/9M/2Bの3class、全40 Code、416 instructions、四counterのmiss 0、除外0。実測は単一exec、全7物理CRC。

PG38278 Main7/Test3 compile、PG38280 static三種と整形すべて終了0。対象三classを測るため前群でも使ったprofile2を当一回へ含めた。別runの和や全製品品質へ転記しない。実DB・broker・監査永続化は未実行。

[PG38284 独立証跡](../018_NK-OPS-001/evidence/PG38284-outbox-retained-value-independent-v1/manifest.json) SHA-256 `d63f355fbf7333eb9e0018b835a1b7ffcefa75d37fdf8ab02017298ea26c65af`。
