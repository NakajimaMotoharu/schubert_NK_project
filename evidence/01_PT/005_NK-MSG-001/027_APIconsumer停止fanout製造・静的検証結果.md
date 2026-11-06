# API consumer停止fanout製造・静的検証結果

BUG-2407/YKT-2152はPG是正済み・動的再試験未完のOPEN。正本SS321SSC314の内部実装として、4既存Mainを修正し、package-local InboundConsumerGroupを1件追加した。3 childの新stopDeliveryは既AtomicBooleanをtrueにするだけ。親は既所有リストの全子へ通知してから、既順序のblocking closeへ進む。子単独closeも同じ通知を使う。取得/ACK/rollback/既処理/成功phase/再close/UNKNOWNの契約を維持する。新resource/worker/権限/外部操作を追加しない。

固定Production candidateは56720d75714f60d7e31da59c3da8c02baf05de52。配備済み・全体資格済みではない。新規Production methodは3、独立PT仕様026の6 Test IDはすべてNOT_RUN/HOLD。新Test実行・new source四counter資格・leaf受入は0。

| 検証 | 結果・証拠 |
|---|---|
| 変更5Main format | PG21918、GJF1.36.1終了0 |
| 通常Main-only six build | PG21922終了0、1036入力、1845 physical。元20990から4 class変更・1 interface追加・1840 class同byte。Testは内容読取前にsnapshotから除外 |
| 同source六module SpotBugs | PG21924終了0、各module bug/missing/errorすべて0、全Jar/入力不変 |
| 変更5Main PMD/Checkstyle | PG21926、PMD raw101/終了4を保持、全101は旧20154で個別判断された同一のrule/message/equal-code anchor。既取得資源所有・例外順位・identity・private lockの理由を現在の差分で再点検し適用違反0。新stop/interface/fanoutに新規指摘なし。Checkstyle0。抑制/ルール変更なし、全F03合格にはしない |
| 通常classの独立bytecode読取 | PG21928 javap終了0、5classだけ。親の全child stopループ完了後にcloseGroupsを呼ぶこと、child三methodがflag setだけ、単独closeが先にstopを呼ぶことを照合。interface二methodはabstract/no Codeのmetadataでcoverage成功/除外にしない。Product初期化/呼出し0 |
| 独立結合 | PG21930終了0、normal/六静的の原終端・入力/source・全Jar/physical・原101判断・bytecode順を確認。元run/execの転用なし |

公開証跡はevidence/PG21930-consumer-stop-static-independent-post-v1/manifest.json。checkerの実行時は私有工具であり、同一byteをinput027へ保全した。checkerHeadは実行時repo contextで、事前Git固定済みのcheckerと誤認しない。原manifestと後付けsource対応はchecker-source-binding.jsonで別々にpinし、元実行結果を改変/再演しない。

残る必須確認は026の並行停止・既callback保持・partial start/close phase・UNKNOWNの動的回帰、現在sourceの全scope実行/native/CHR/四coverage100/451/trace/QA051final。旧4217の正常38等を新56720へ合算しない。再発防止PTと全横展開が未実行なのでBUG/YKTを閉じず、coverageは未測定null。正式1964PT/53scope・unique Test387・whole Source88・工数率nullは変わらない。
