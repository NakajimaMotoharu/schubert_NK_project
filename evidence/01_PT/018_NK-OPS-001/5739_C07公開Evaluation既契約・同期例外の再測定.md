# NK-OPS-001 C07公開Evaluation既契約・同期例外の再測定

SS351 §7/10、RD171、UI252、NK-OPS-001/P018-09、451 §5、元仕様2803 GENB006。PG42902の四系列と集約40件に、元GeneratedBatchValueContractTestのGENB006だけを加えて同一候補・同一execで実行した。41件すべて成功、エラー・失敗・skip・選択漏れ各0。GENB006のほか6件は選択範囲外。fixtureは5種類の公開Evaluationの固定presence、独立した空Optional/同一・相異event、等価性、独立primitiveとidentityによるhash、表示、null拒否。Transferの別業務経路は評価対象外。製品sourceおよび試験定義の変更0。

無フィルター実測は対象九物理で行188/192、method53/53、class9/9、branch84/84、instruction1031/1051。同じ四Evaluationの12生成methodと40命令が新たに到達。時系列四クラスのsnapshotには同期ブロックで例外が発生したときの解放命令が残り、各1行・5命令未計測（Filesystem 73、Heap 71、DB Pool 74、同期p95 72）。行の100%は未成立。公開APIの通常経路、現在の所有ロック、自然な例外契約を維持し、この結果には除外を設けていない。BUG-3642／YKT-2861を継続。F03全製品、C07運用設定、実endpointの正式受入は継続。

公開manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG42904-c07-direct-monitor-and-value-v1/manifest.json` SHA-256 `483584e9205d9674c70b1d05562a72387b72321fbc663e301283ad151a32255e`。
