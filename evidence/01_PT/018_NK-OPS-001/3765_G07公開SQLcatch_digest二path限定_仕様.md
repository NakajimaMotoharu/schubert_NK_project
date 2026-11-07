# G07公開SQLcatch digest二path限定・仕様

WBS-G07、群4329原0.5/2/5pp cap7。元PG9888の4493 metadataと既9+2更新から残4482を維持、全scan/source/content/ruleは歴史値で固定。再scan/旧工具再演/実VM/DB/鍵/Root/私有raw/archive/old producer取得無し。public PG6542 sites.jsonの113 SQL catch metadataのうち、source witness読取をOwnedOutboxDispatcher.javaとWebLogReplayWorker.javaの現公開Main二pathに限定する。両sourceは同一byte pinが原sourceSha/current normal22084へ結合できる場合のみ。新しいSQL異常処理PT/PG修正や元例外型の動的検査は行わない。

対象artifact SHA/4493原metadata/現在sites inputSHA一致、JSON object位置・bodyTokenSha256の正確な一capture・原ruleを結合し、元113の公開token正規化を使ってcurrent sourceの同SQLcatch beginLineからderived digestを計算する。独立postは別の手書き字句走査・括弧対応でSQLcatch body token列を復元し同一性を確認。値/値hash/本文/code token列を新規出力せず、source/artifact hash・row番号/line・型役割・bool結果だけ保存。全capture不一致/源変化/未知/重複/型違いならUNCLASSIFIEDを維持。元9+2とのmultiset非重複、元4493から今回分だけ差し引き、actualSecretCount null/22binary限界/全G07未受入を維持。metadata否定はPT成功/coverageへ算入しない。

BUG2490/YKT2228：初ad hoc選定はartifact除外に比べsource path条件が不足し、今群scope外の公開auth/access等Main10file/13siteをchecksumだけ読取。分類/実行/受入0・値未出力・実auth/DB/鍵/私有raw無し。是正前起票し23524へ旧guard条件/件数を保存、以後二source exact whitelist先行・deny/symlink/resolve gateをproducer/post双方へ適用。offscopeの旧checksumは分類へ使わず、protected二工具/二RootTest含む未知pathはI-O前拒否。これは過去行為をなかったことにする訂正や安全HOLD解除ではない。

producer input448/独立449、PG23518/23520、仕様結果3765/3766、計測/close450451、公開23522予定。通常477継続、fresh残10%以下新規停止/5%保全、モデル/451/元見積/正式1964-53/newleaf0/工数null維持。Product Test0/coverage0・source資格0、472/whole93/候補111/pending9は不変。独立して型来歴を確定できた検出だけ限定false-positive分類、PG6542の当初catch品質/業務経路を成功へしない。
