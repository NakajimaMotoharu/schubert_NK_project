# API/Web readiness generic20 現source用途レビュー仕様

2026-10-31 / PG-D995 / 群PG16142 / 主WBS-F03、開始0.5/2/5共有pp cap10、fresh16:22used54/rem46。先行ApiDependencyReadiness index3/Web2、1245/2511/2560を照合。候補14028型22と13964/76所有15は既接続で追加0・再演0。旧5960/288062のReadiness28は全28が現在とSource hash不一致であり、旧generic20理由を転用しない。

現API123行/Web76行の全199行を読み、origin/main SS342 SSC330/SS312/321/354を根拠に新20用途を点検する。NK-MSG-001002/NK-WEB-002、RD MQ001003006008/SYS004・UI212231252、既PT-JMS019022023025/PT-SCR113～116136137は参照だけで今回実行しない。SourceはAPI a9510db3...594e/Web bf5f3f63...35abでnormal14216同byte、Production変更なし。Graph9へのclassload/call・接続/closeの実行をしない。

対象は各10raw、全12catch header（各DB body/close/catalog、JMS body/close/catalog）。固定site表：API60/66/74/102/108/118、Web34/40/47/58/64/71。各bodyのRuntimeException/Errorはprimaryへ保持し同objectを再throw、closeの両型は全取得済資源のSource上close siteへ通してdirect Error優先又は一時secondary保持、outer RuntimeExceptionはfatal分類後だけ固定非成功診断へ移る意図。Errorをouterの通常catalog型へ混ぜず、DB非成功からJMSへ進む正常経路を持たせない。機械的catch削除/普通TWR化/未知を成功値へ補完しない。type operand20を20独立logic障害とは呼ばない。

各rowに元raw id/全attrs/診断/Source/正規span/catch型列・parameter・whole scopeと個別目的/riskを保存。実際のclose回数/型解決・任意Throwable graph/隠れError/DB/JMS/caller所有/時間上限は静的Source用途だけでは未証明であり、PG変更不要の当範囲判断をPT PASS/免除/全F03合格へ変換しない。Null factory/invalid admission等も失敗経路の意図でありNPE正常扱いではない。

16142→16144独立metadata26予定。既参照898不変、新用途96+20=116、合計1014/1491・当残497→477予定。current2133/285/四258-376・正式1964-53/歴史17/工数null/QA051final/G07/451/HOLD不変更、WBS不変更。BUGが確定すれば修正前起票、上位/期待値をcode都合で変更しない。
