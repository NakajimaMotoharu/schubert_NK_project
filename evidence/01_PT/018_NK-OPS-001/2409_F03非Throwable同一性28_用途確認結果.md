# F03 非Throwable同一性28・用途確認結果

仕様2408/PG-D771/event2773、source2f4290e7e511ea30224d087f78d44964d3488919不変更、先行save45aef62bb229aad51935f29795160b06e8f89c59/push57926真正0。元13036型56を再解析せず、13038で未分類だった28だけをsource/hash/元位置/型・保持元へ静的に追跡した。製品/Main/Test変更0、製品PT・coverage・新規個別受入0。

| 静的用途 | 元diagnostic数 | 根拠・未証明 |
| --- | ---: | --- |
| 保存結果と元request scope | 5 | private Snapshot constructorがrequestを保持しreplyで同referenceを要求、owner照合は別検査。暗号/DB実行の正常性は未証明 |
| 所有Thread/自己join回避 | 9 | currentThreadと捕捉owner又は生成したworkerの同一性。実競合/期限内停止/資源帰還は未証明 |
| opaque発行gate/元baseline | 7 | private Intent/Baseline/TerminalReceiptのissuer/frameを比較。現物/権限/世代/原本の実認証ではない |
| 同一terminal receipt継続 | 4 | 停止再検証のadapterはbeforeそのものを返し、handoffは観測済み同receiptを保持。実stop/DONE成功ではない |
| ThreadLocal stack順序 | 1 | pushしたScope自身だけがtopをpopしpreviousを復元。実dispatch成功ではない |
| current repository instance | 2 | 注入したsession repositoryとrequest属性の同instanceを要求。実session/Logoutは未実行 |

SS324 line92のowner/layout/fingerprint・保存応答条件、SS313 line137のcurrent repository・314 line48、SS343 line448同producer receipt、SS351 line93 request lifetimeと矛盾しない内部実装意図を記録した。上位仕様が28の各演算子を個別規定しているとの主張はしない。式/捕捉/注入の行と各source SHAは公開reviewへ一意保存。全siteはSTATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLDで、false positive断定・PT免除・全実行正常へ変換しない。

## 公開証拠・結果

provisional/PG13044-reference-identity-context-v2/manifest.json SHA256 `f7345a09e4b83152111b83b56a48534a9223f66f6704df8a6d870adefe5e8d06`、checked entry lint0/body0・28用途/誤計上反例8。独立PG13048-reference-identity-post-v2/manifest.json SHA256 `a690dd5687adb85051ee630599702f82ecf24dd147eb9a6d492632eb2aef2dc4`、lint0/body0・元28全fieldのうちmanualPurposeReviewComplete false→trueだけ許可/他field完全一致、source・位置・型・未reviewの独立反例4。全source/current型metadata/目的周辺/元ownerは不変。実時刻/OS/工具・依存SHAは各invocation、既JDK型取得環境は2407/13036を不変更参照する。新compiler/製品classロード/生成/PT0。

BUG2021/YKT1769は未使用Path importによるbody前lint1、元13042entry fea88a79・failure.safe.jsonを保持し別13044でimport一つとOUTのみ変更。BUG2022/YKT1770は独立postがレビュー済flagの正当遷移まで不変を要求した前提不備、元13046 entry4a640cf9/actual1保持・全28差分は当flag一つだけ。新13048で元false/新trueを明示し他metadata不変＋四反例まで確認した。製品失敗ではなく工具不備2、型解析や元28レビューの再実行0、以後新entryはbind前明示pyflakesを先行する。両障害/横展開当工具範囲のみ完了、完了日2026-10-28・修正保存commitは456参照。

raw8472/既是正953・Main1504/Test6968・introduced16不変、参照3231→3259(+28)、現source参照付き保留913→941、未参照5241→5213。先行28と合わせ原未参照比較56の用途根拠が揃っただけでraw減算0、actualViolationCount=null。正式1964PT/53scope・歴史個別17/190・工数null/QA051final・全F03/451・実Root/VM/DB/native/実例外graph・保留二工具は維持する。

原1/2/4pp cap10・共有開始85、専有費/実N/T/残予測の実費較正は不明を維持。元型/既PTの確認再演0、次は本当に未対応の安全な既Program不足を原diagnostic/既試験索引から選定する。通常保存/小群で終了しない。
