# 通知明細参照HTTP単体テスト仕様書

2026-10-03、NK-WEB-002/SCR021参照部分/PG-D349、RD FUN010/NTF001～012/QST/AUT、UI222/224 §5/236 §9、SS313/314/323/332。NotificationController.detail/NotificationDetailViewModel/notifications/detail、NotificationMvcConfiguration/WebMvcConfiguration明示構成、既存固定NotificationWireClient NTDREQ01と独立NotificationControllerTestを対象とする。PG437 sourcef4a0全回帰・classes/exec/XML保存後に実装を開始し、旧source結果を流用しない。

| Test ID | 入力・事前条件・操作 | 独立期待値と観点 |
|---|---|---|
| PT-NTF-DETAIL001 | USER/ADMIN、ID1/N12最大、0000/0200、全5state | UI236 literalのNTDREQ12/NTDRSP8896、独立header全byte/現在context/要求target。正常type/時刻/本文/Question ID条件はUI224236の表から固定しProductionでexpectedを生成しない |
| PT-NTF-DETAIL002 | RECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLED、deleted/空回答 | JST秒、受付中/処理中/完了/error/取消済みの状態表示、COMPLETED＋非削除だけ質問明細link。非削除COMPLETEDのall-space answerは空回答あり、削除済みは両本文なし・固定caption/質問linkなし |
| PT-NTF-DETAIL003 | 異なるtarget/0/N12超/null actor/id/data/unknown principal・immutable表示 | 同ID不一致を503またはfactory拒否、入力nullは契約fail-fast、表示Map変更拒否/TopBar current actor/診断redacted、owner/context/bodyをsessionへ保持しない |
| PT-NTF-DETAIL004 | 全承認error code/JMS/timeout/correlation/context/layout/Reserved破損 | API0102 terminal Cookie/session、不存在/他owner404、固定HTTP分類/503、wire buffer0/pending0、unknown Error原identity、test timeoutを正常扱いしない |
| PT-NTF-DETAIL005 | 全5state×削除有無/Unicode特殊本文/空回答、MVC GET HEAD/POST | title/明示safe DOM/escape/JST/state別時刻、両削除本文非返却、非削除完了のみ固定question link、HEAD body0。取消未承認部分は実装しないため本参照PTはPOST機能完了を主張しない |
| PT-NTF-DETAIL006 | 実Jetty/encrypted session USER/ADMIN/匿名・API0102 | 各GET HEAD再API/current context、両role本人参照、匿名302/no-store/0102 Cookie失効・DB後条件、Native ordinary Web fullReadyとは別scope |
| PT-NTF-DETAIL007 | 8thread100要求target/context/UUIDを独立設定 | 100別MessageID/target/contextと応答を照合、混線0・元buffer0/pending0、shared mutable viewなし |
| PT-NTF-DETAIL008 | BUG562破損deleted=true＋質問/IDspace＋回答あり、同vector encode/decode/semantic | UI224削除仕様から独立拒否oracle。正常deleted/COMPLETED空回答はPASS、不正回答はcodec拒否＋HTTP503。API実DB NOTICE SQLはdeleted時両本文NULL、QSS/QDT削除対象外/404、YKT406全対象の根拠・再発防止testを確認 |

公開factoryは既存PayloadSemanticValidatorを再利用してcross-field契約を検証し、Production methodをexpected生成へ使わない。取消form/token/POST・質問受付参照QA048・完成token履歴QA049は別未承認、RECEIVEDを含むSCR021全機能完了/全Web readyを参照部分の合格へ混同しない。line/method/class/branch100%、null/negative/並行、strict compile/静的6zero、codec共通変更後は他機能前に同Source全6回帰。実行環境/日時/command/source/exit/FES/coverage/BUG/YKT/証跡hashは016062/manifestへ実測後保存する。

BUG564/565の試験境界補足：NTD error profileのN12 ID/N17受付日時は全0、B flagはSS322 §4.3どおりspace（false0へ変えない）。DETAIL008の意味拒否はCatalog.encode→raw Codec.encode、raw Codec.decode→Catalog.decodeというProduction既存のvalidated pipelineとHTTPで確認する。raw Codecだけのfield container返却をcross-field業務受入とは扱わず、誤った単体層oracleを直す。期待する削除回答拒否・正常deleted/空回答の意味は変更しない。
