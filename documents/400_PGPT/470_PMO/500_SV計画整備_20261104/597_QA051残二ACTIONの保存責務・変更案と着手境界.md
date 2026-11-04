# QA051残二ACTIONの保存責務

同じPGPT-SV-20261104-01/S10内の設計不足調査。着手時fresh週次used5/rem95、共有S6/10（準備1含む）、残4内POST2を確保。今回の調査・起票・独立期待表草案の技術判断見積0.2/0.5/1.0ppは追加予算ではなく、元S開始見積1.5/5/10を変更しない。Production 6b53efeec87f3ec36a840dd8e7759656cb4aee5cは不変更・未配備。

## 確認できた制約

553/567のCurrent caller照合では、menu/log_searchはACTIONであり、単なるREQUESTの旧名称ではない。UI225 §2.1・UI264 §5.1は両記録を落とさないとする。一方、UI235 §12.1のWLGEVT01 Log typeは固定REQUEST、SS351 §3.3は他categoryをREQUESTとして受理することを禁止する。SS312 §11・SS324 §12相当のWeb log outbox/ingest責務もREQUEST投影であり、既存枠をそのままACTIONへ読み替えられない。SS351 §4 catalogには二操作の個別actionが未定義で、§4.1は未対応のまま合格にしない。

現Main MenuController.showはPrincipal/Modelを検証してviewを返すだけで、別の業務APIを呼ばない。LogQueryAuditWriterの四EventはSESSION_INVALID/ROLE_DENIED/MESSAGE_MISMATCH/REPLAYで、初回成功のlog_search用ACTIONではない。WebLogIngestServiceはHTTP_REQUEST_COMPLETED以外を拒否しINSERT categoryもREQUEST固定。WebLogEventDataもLog typeを呼出側指定するrecord項目を持たない。これらはc93e62/6aef70/d5e0fa/f35b8fの読取結果であり、実ログ/DB/稼働環境の観測ではない。独立した別生成元が絶対に存在しないという全体保証もしない。

## 未承認の具体案

QA-054/UIC-011/SSC-336へ先行起票する。RDのログ閲覧・互換・監視要件を変えず、記録欠落を許す選択肢は提案しない。

1. メニュー閲覧はACTION/MENU_VIEWEDとしてWebが一つのeventを発行し、既存technical outbox→APIの冪等投影を使う。WLGEVT01の物理byte位置・長さ・layout数・既存REQUESTの意味は維持するが、Log type固定REQUESTを、厳密に定義したACTION/MENU_VIEWEDの組合せも扱えるよう基本設計へ拡張する。任意category/action、critical監査の置換、未検証actorによる認可には使わない。
2. ログ検索はACTION/LOG_SEARCHEDをAPI側の初回成功確定transactionで一度保存する。保存済み結果の再送では当ACTIONを再発行しない。読取snapshotの後で当検索auditを保存するという観測時点を明記し、検索応答に自分の後発auditが含まれないことと、DBから欠落していることを区別する。既存INBOX_REPLAYEDは別eventとして必要性を検証し、初回ACTIONの代用にしない。
3. SS351 catalog、UI235/252/264、SS312/323/324/351/355、固定長codecとsemantic validation、Web/APIの生成・送達・SQL、独立期待表・再送・CHRを横断更新する。schema/DDL変更が必要かは制約を確認してから確定し、現段階で不要と断定しない。

固定REQUESTという基本設計上の制約に触れるため、承認済みQA051の名称統一・安全比較だけから実装許可を推測しない。QA-054の具体判断が必要なのはこの拡張範囲であり、QA051を未回答へ戻すものではない。承認前はUI/SS正本・Production・Current baseline・test oracleを変更しない。mainへ未承認案を確定設計として反映しない。

## 承認後に固定する独立期待表

| 論理操作 | 必須記録 | 再送・時点の期待 | 残る動的資格 |
|---|---|---|---|
| 正常メニューGET | MENU_VIEWED/ACTION 1、HTTP_REQUEST_COMPLETED/REQUEST 1を別eventとして相関 | 同一ACTIONのlocal/outbox/DB重複0、ACK前後再送でもDB1。HTTP結果/表示/既存ログ不変 | 正規Web/API/JMS・障害/再送/所有・CHR/同source品質 |
| ADMIN初回ログ検索 | LOG_SEARCHED/ACTION 1、HTTP_REQUEST_COMPLETED/REQUEST 1、既承認の必要MQ記録は別に検証 | 検索snapshotと後発auditを分離。保存結果再送でLOG_SEARCHED再追加0 | 読取/確定transaction・rollback/commit不明・再送・実L01 |
| 入力不正/未認証/権限拒否 | 成功ACTIONを偽造しない | 既定HTTP/認可監査を保持。成功・失敗各catalogと件数は承認後の閉表に固定 | 全異常/null/例外/競合・四coverage/451 |

上表は未承認案の設計入力で、実行oracleでも新規PTでもない。未実装部分の不足を既実装障害と断定せず、現時点ではBUGの成功/再試験や実測結果を生成しない。承認後に実装済み違反を確認したら修正前BUG/YKTを別途起票する。

費用主担当は既WBS-P020-01群のQA051契約参照とし、Web/API共通変更を画面ごとや親子に重複課金しない。具体leafへの費用配賦・将来修理/再資格/受入総額・解決日は未確定null。この調査費はSのみ、将来PG/PTを今回Vの成功へ付け替えない。判断待ちはこの変更案に限り、独立Sレビューと既承認PG/PTは継続する。
