# 2226 Batch二Repository96理由・現在source個別結果

2225/NK-OPS-001（品質）/影響NK-BAT-001/WBS-F03、source7f035ccfe89c46e8f4fae52099b1c0e4e890e66b、2026-10-27。Main/SQL/SS変更0、製品PT/全解析/coverage/実DB・VM・Root・private rawアクセス0。

## 先行想定の訂正と実績区分

96件はsource・座標・rule/priority・診断本文が旧個別recordと一致するが、本文まで点検すると旧6048のうち70件がreason/priorReason空欄だった。ラベルだけを理由再認証として計上せず、11560 v1はactual1/OUT前で拒否（BUG1923/YKT1672）。旧工具byte/失敗receiptを保持し新v2だけ使用した。

実際は旧6048 FP16/R6＋後続6354 R4＝**26件の既理由再認証**と、空欄70に対する**70件の新しいcurrent source個別点検**。全96を新規製造/新PTや既レビュー済み再利用とは呼ばない。新70はprimary記録/同identity再throw28、owned resource一回closeのsecondary順位28、nonnull guarded finallyの必須throw14。各実span・囲むmethod token SHA・具体resource/primary/secondary名・SQL/RTE/Error列・宣言IO保持を個別factへ記録した。単なるrule名だけの一律理由ではない。

## 原証拠と独立照合

| 処理 | provisional directory | manifest SHA256 | actual |
|---|---|---|---|
| 26再認証＋70source点検 | PG11560-batch-two-repository-reason-rebind-v2 | eee2f10894540f8516758a60c5c6fae0f92754f977db2f83cd2b0056cc32d879 | 0 |
| source/理由・誤実績15metadata負例 | PG11562-batch-two-repository-reason-rebind-post-v2 | b4a9d2e02875101f6c063227e56478747cd2ea6b569a0e0b77716ad313acc99a | 0 |
| 現在集合の理由参照結合 | PG11564-current-batch-repository-reason-delta-v1 | 7f74d22280372600bb6c8287e831f2759108756310473dc64c7caac364042a0a | 0 |
| 独立history/全ID/70実span照合・8反例 | PG11565-current-batch-repository-reason-delta-post-v1 | 5aae1fe97b17f27e846c37f3b7b979f5efdd148ecb3cce7f05526f38d4e00fb1 | 0 |

全48×二96はMain二class・JdbcResourceFailures/固定例外の旧source完全同byteを確認。現normal11536 input hash/原10690 row/旧6048及び6354の原manifest/inventory SHAへ一意対応、承認設計はorigin/main8b91944dfのSS332 SSC063/199/200・SQLとunknown順位。JDBC型解決は元normalのcompileに参照し、字句点検だけで新しい型解決/実行をしたとはしない。

結果はREQUIRED_CONTRACT80（generic catch64/finally16）、FALSE_POSITIVE16（presentによるnull拒否identity aliasで新資源でなく、実取得scopeのnonnull一回direct finally closeあり）。sourceのprovider SQL/RTE/NPE/Errorを成功や固定例外へ広く正常化せず、unknownのidentity/SQL順位とborrowed Connection非close/config/commit/rollbackを維持している。SS332のbatch契約をordinary APIのSSC320へ機械的に置換しない。元SQL/各scope・getter/純投影境界・返却前closeの具体箇所はreview.json/factに保持。

全96 rawは残しCURRENT_WHOLE_PENDING、現在sourceへの旧runtime/coverage転用0。現raw8896/原9409−是正521＋新八は不変、現在理由参照2841→2937/pending282→378/未参照6055→5959。真の全違反数null、全F03・451未受入。旧sourceの26理由を現Root/DB/lock/失敗cohort回収の所有証拠にしない。

開始見積.75/2/5cap10は不変更、37→38の同窓共有差は専有費としない。N/T/工数率null、正式1964-53/個別17-190/QA051final/全安全HOLD/原本等保持。次は旧非空理由のある未参照Mainを候補から絞り、現source及びhelper/契約前提の一致を確認して同じ方針で継続する。
