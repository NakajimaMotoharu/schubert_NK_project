# Scenario/Media 14query振分け・限定静的PT設計結果

主P008-01・関連P009-01追加0、原1/3/7pp cap9。Main7aed/既Source不変更。PG23912 source静的レビューとPG23914独立照合は終了0。STATIC_PT_DESIGN_REVIEW_COMPLETE（六Scenario/八Media）、動的14ケースはすべてNOT_EXECUTED_HOLD。新Product PT/PASS/実測coverage/PT免除/正式受入は0、工数率null。

SS323§9.1/9.2から独立した14layout・canonical field順/Optional・DTO・query先・応答形を固定。六ScenarioのInline五/Detail一、八Mediaのdescriptor直返Optional三/通常一覧present五を対応。query三null前提の先行、同じ内部kind/valuesの利用、actor外側認証責任、借用Connection/transaction所有、commit/rollback/close/file/JMS権限を当Requestに追加しないことを確認。例外補完catch無しのsource制御を確認し、実SQL/driver/整合/資源close故障/DB null/並行/再送/配信結果の動的証明とは区別する。

独立postは別line-based method parser、origin/main承認SSの14canonical表を別に解析。metadata誤layout/DTO/query先/応答形/fields/所有/動的PASS/実DB証明/欠落/重複の13否定と、六indent変形・四methodのbranch内容保持を確認。以前のSource27寄与hashは全Source byteと一致しclass hashでないことも有限横展開で確認した。

工具手戻り: BUG2510/YKT2248=physical index classSHAをSourceSHAと同視し起動前guard1。23916に修正前byte/終了1を保全しSourceはGit7aed+事前pin、physicalはmembership/CRC metadataに分離。BUG2511/YKT2249=4space終端仮定でcanonical parser1、23918before保存、indentに依存しないswitch終端へ。BUG2512/YKT2250=indent反例のslice末尾triviaを意味差と誤認、23920before保存、前後stripのみで内部textを保持。元失敗は合格にせず、手戻り3と元計画14静的レビューを分離する。Product不具合/試験失敗ではない。共通原因はmetadata意味/構文schemaの観測不足であり、以後は新parserを広げず固定入力のfield役割・終端形を先に確認する。

公開証跡: evidence/PG23912-request-dispatch14-static-design-v1/{static-case-designs,manifest}.json、evidence/PG23914-request-dispatch14-static-independent-v1/manifest.json、失敗before PG23916/23918/23920。独立manifest SHA-256 710bc1a1d03ec793ed00d9a073c7eb76f5d1f73696dde1b2cb5f5dd5a31baa97

残: repository内preserveFatal/保留例外を含む実経路、SQL/DB/TX/原本/署名/配信/native/CHR/451はHOLDを維持。旧10原成功とpartial counterを当14の成功へ転用しない。517unique/正式1964PT53scope/全actualHOLD/七stash/原本/Current baseline/保護pathsを保持。
