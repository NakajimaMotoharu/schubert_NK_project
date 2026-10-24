# API/Web caller静的15指摘・個別PGレビュー結果

1831/group2061、Production28befbf2cac86840b6adef53b6c5f972e6f9610f不変更。**新製品PT0/Main0/coverage null/全品質合格false/PTALT0/正式受入0**。既8859/8873 staticのexit1/警告は原本のまま保持、静的再実行/旧試験確認再演0。

|公開artifact（provisional配下）|SHA256|
|---|---|
|PG8880-caller-static-manual-v1/decisions.json|b83db3d949a6ab3e44ad810e4b304b6aec0cc06ef7327dfd04858a0116a0addf|
|PG8884-caller-static-review-fixed-join-v1/manifest.json|0206bcdd8778cf6d33efd819e8dc97883d9cf8c5551ab1b051ed21e94f03a215|
|PG8883-caller-static-review-guards-v1/manifest.json|6c14c3d153c81ea791a1f258e86b9ae72fdcb796608aea704839773a8ced14ce|

各raw15のsource/path/hash/span/座標・規則・理由・反例を8880に個別保存。API2は原解析source0f065c63fの当API byte/sourceがcurrent28befでも同一、旧実行のsourceを書換えずsource/rule適用性レビューだけを結合した。公式PMD7.28 jar descriptionのJ2EE管理thread前提と、origin/main8b91944 SS342/同source Unitの直接Java launcherを照合し、この規則前提に限りCONTEXT_NOT_APPLICABLE_J2EE_RULE。実配備/handler成功や全F03受入ではない。

Web13はvolatile5/private同期2/retained resource6（新metrics含む）。sourceのreadiness snapshot/partial field捕捉/管理後metrics cleanup/同ownerLock/外側WebRuntimeExecution UNKNOWN frame保持をPGとして確認。各rowに必要Unit宣言・反例を付けたが、宣言やsourceだけではactual acquire/close/並行/停止のcurrent XMLを証明しないため、全13をREQUIRED_CONTRACT_DYNAMIC_JOIN_PENDINGとした。未レビュー0は未完0や静的PASSではない。抑制/規則変更/動的試験免除/実測coverage転用0。

8883は実validatorへ不足row/raw変更/source hash変更/偽PASS/偽runtime/XML/PT代替/誤分類/試験宣言欠落/sourceSpan改変/警告隠蔽11反例と、文書launcher欠落/Unit syntax欠落二反例を与え全拒否。13metadata checkは製品PTへ加算しない。command/UTC/source/tool/input/dependency/rule/設計/Unit/Test宣言hash・真正exitはmanifestに保存。

BUG1721/YKT1472：元8882はMarkdownにも設定syntax ExecStart=を要求して終了1（PG8882-caller-static-review-failed-v1/manifest.json/原tool保持）。SS342同byte/launcher実在は確認済みであり文書不足ではない。修正前起票後8884でSS本文の概念/固定java/shellなし・Unit側literal syntaxを分け、二反例と個別15結合へ確認。既8798は主体を分けていて非該当・再演なし。Main/手動期待/原static不変更、修正commitは1832と同commit、2026-10-25 tool限定CLOSED。

開始0.5/2/4pp/cap10、fresh46残54→fresh46残54/reset1793382075（共有丸め0≠専有0）。usage634ec24ecd4de782ee17fa2f0e2737fefc847f27ca321253512e380b5a8bbd6c/02:38:33→02:44:23JST、explicit新record0/完全性未証明、N/T/専有費/工数null、原-v4-v5/群開始値不変。source再認証・工具手戻り・reviewを製造/Test新実績へ付替えない。

own74991元0、8882元1/後段未実施保全、製品job/VM/native/DB/Root操作0。技術618TestIDs/33Main・正式1964-53/原190新受入0/QA051final/全actualHOLD/原本等不変。次8886scan/保存push→同C07 Batch custom+standard textの許可済み独立PG/PTを検討し、着手条件を確定して継続する。未確認の安全条件を必要とする操作は進めない。
