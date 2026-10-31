# BatchRun 現48診断・所有八scopeレビュー 結果

2026-10-31 / PG-D980 / event3395。3066の静的PGレビューのみ実施し、Main/Test/設定変更なし。

PG16004 checked entry f702b9/body0/lint0、manifest `evidence/provisional/PG16004-batch-run-current-static-review-v1/manifest.json` SHA256 `2e6c4240a6749477bf58ade99bb44701c382f0d4adb3c8cb0a5b0ad66348976d`。PG16006 cd7234/body0/lint0、manifest `evidence/provisional/PG16006-batch-run-static-review-post-v1/manifest.json` SHA256 `11b92206d5f124165a86be099f1ab92219be860f14dbfa9868527d61a602dc56`、別line/token走査で全48IDと8scopeを再構成し、独立metadata変異25を拒否した。これらは管理検査でProduct PT件数0。

| method | owned resource | alias/body catch/finally/close catch/end line | 診断数 |
|---|---|---|---:|
| finish | statement | 142/147/150/154/158 | 6 |
| history | rows | 245/280/283/287/291 | 6 |
| history | statement | 238/292/295/299/303 | 6 |
| abandon | statement | 314/323/326/330/334 | 6 |
| insert | rows | 368/377/380/384/388 | 6 |
| insert | statement | 354/389/392/396/400 | 6 |
| replayed | rows | 424/428/431/435/439 | 6 |
| replayed | statement | 417/440/443/447/451 | 6 |

CloseResource8は取得済み資源のidentity aliasへ付く。nullならSQLDataException、nonnullは同変数を一度直接finally closeする。汎用catch32はbodyの同一primary記録/rethrowとcleanupの閉じたSQL/RTE/Error順位処理であり、未知例外の正常化ではない。finally8の条件付きthrowはSS332/SSC063のSQL-primary/未知cleanup優先を実現するため必要。helperはprimaryなし・SQL primary＋未知cleanupだけを置換し、未知primaryのsecondaryには新しい固定例外を付ける。同一Throwableを直接自身へsuppressed追加しない。全八scopeを個別照合した現ソースの用途判断として変更不要。

BatchRunSource SHA256 `47d12d03590932d7df11681d0c663cd1a75e59b4b32cff72ee5c7aea8318d876`、helper `f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a`、SS332 `bf35de0b4d24a253eb75808f0280fa92eb3f02f8ba3a988a227f96c7213781a5`（origin/main同byte）。review.jsonに全指摘のID/元属性/byte/span/hash/方法/資源/primary/理由/未検証事項を格納し、旧queue/rawは不変更。

選択1491rawの既562参照を保持し、新規用途レビュー48、合計「用途レビュー又は参照接続」610、当選択未接続/未用途レビュー929→881。48を新PT・新coverage・旧PT再認証・適用違反0・全F03受入へ換算しない。現八scopeの動的close回数/SQL後条件/型解析は本群で未実施。旧957/1266の別source成功を移植0、scanner/compiler再演0。新BUG/工具実行失敗/プラットフォーム拒否0。

現registry2094/278・四252/366・正式1964/53・歴史17/190・工数null・QA051final・G07/451/外部Graph HOLD不変更。WBS正本は本群で変更なし。着手0.5/2/5共有pp cap10固定、fresh14:14 JST used51/rem49、共有整数差0は専有費0を意味せずN/T/専有費null。次は残881の別Sourceについて既存レビューと現在byte/全依存を照合し、必要なPG/通常PTを継続する。
