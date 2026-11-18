# BUG-3250 Webのmetric catalog有限fixtureの実行結果

Core `29f3b433952ad19d4ad34c4e1a31ed310bebde6a`、固定試験source `ca4c4e370fc31be35b04304a78f223487ada4f9a`。PG38992は独立WEBCAT001～014初回14合格、失敗／エラー／skip／未実行0。PG38994／PG38996で所有4worker、64task、各get10sと必須await10sの逆変換、全7物理・CRC陽性3・対象49/50行、10/11method、1/1class、14/14分岐、260/265命令を同execで照合。Mainと固定route入力は不変。

静的NullAway／Checkstyle／SpotBugs 0、PMD6を個別non-applicableと判定。製品や運用metricsを起動しない。BUG3250のfinite fixture完了。独立生計測でpackage-privateの名前取得済み `labels(String,List<Tag>)` 1method/1行/5命令が未到達。歴史的なScrape結合のroot evidenceは保持し、このexecとの合算なし。BUG3251に起票して追補の単体結果を得る。

注記。4628のゲージ／byteの合計数は記述が不正確。固定期待はWEBCAT004のゲージ13組とWEBCAT005のbyte36組で、試験本体と独立データを変更していない。601/378の次工程にあるpublicは可視性の記述誤りで、対象overloadはpackage-private。環境・実コマンド・hashは[独立manifest](evidence/PG38996-f03-web-metric-catalog-independent-v1/manifest.json) SHA256 `888828298ea363f99f27ddeb9313daaee70db00d54523638f1781242f95e2406`。
