# CHR-L01の残る二操作の具体化

S-POST、同じS10ppの範囲。QA051の承認は有効で、再承認待ちへ戻さない。本資料は実装・実測・受入ではない。

CurrentのSearchController.menuはGET `/`でAppLogService.logAction("menu", ...)を一度呼ぶ。LogController.logsはAppLogService.searchで検索結果を取得してModelへ格納した**後**にlogAction("log_search", ...)を呼ぶ（14074f、参照sourceはCurrent側の既存コードだけ）。このため、検索後DB配列と当該応答DOMの件数が同じ観測時点とは限らない。時刻・最大IDだけで行を切り出す計画にはしない。

NKのMenuController.showはPrincipal/Model検証とMenuViewModel生成、LogController.searchはADMIN検証・form・LGSREQ01交換・結果描画を行う。両controllerの当該bodyにはmenu/log_search専用action出力がない（01e276）。共通REQUEST hook、API受信/MQ等の別責務まで存在しないとの断定ではない。SS351のaction catalogにはこの旧二名称を直接置換するcatalog名がなく、QA051の「対応を示し未対応は合格にしない」を適用する。

残作業は①CurrentのAppLogServiceとNKのcaller/REQUEST/API監査を、同じ論理操作ごとの記録先・category・件数に対応付ける、②UI252/SS351の範囲内で確定できる内部比較仕様を補足し、設計誤りならSSCへ先行起票する、③新しい業務差分が必要ならUIC/RDF/QAの適切な分類を先行する、④before/afterと検索の読取時点を分けた独立期待表を固定し、比較artifact/oracleへ実装する、である。

REQUESTへの一律置換、Current ACTION行の除外、categoryごとの包括免除、期待件数を実測から作ることは行わない。552の二行はnullのまま保持し、実CHR-L01、native、最終source資格・451は後続の開始/終了条件として残す。現時点で新QAの要否は未確定であり、単なる調査不足を利用者承認待ちとしない。

Product実行・DBアクセス・fixture reset・Current baseline変更・新規受入は全て0。引用した操作名・routeはコード上の定数で、実ログ・秘密・sessionは保存していない。
