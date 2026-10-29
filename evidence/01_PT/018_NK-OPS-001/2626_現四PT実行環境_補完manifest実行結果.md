# 2626 現四PT実行環境 補完manifest実行結果

2026-10-30 JST、branch dev-foundation、Production source 6b53efeec87f3ec36a840dd8e7759656cb4aee5c、作業HEAD ae9557ac47090e580b614c9542bc58872c0f5b48。2625の開始見積0.25/1/2pp cap10を保持。PG-D877、BUG2096/2097・YKT1843/1844。

## 実行と独立検証

- 初版14276は実resultとspecのbranch記録roleを取り違えて終了1・OUTなし。失敗工具を非改変保全し、BUG2097を是正前起票。2625の予定14276/14278は履歴のまま、実際の成功版は14280/14282。
- command: `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14280_current_pt_environment_envelope_v2.py`。実終了0、失われた応答後は出力manifestを回収し再演0。
- 独立command: `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14282_current_pt_environment_post.py`。実終了0、元四parent/各own log hash/最大32行4096byteの四prefix/SDK hash/元期間・command・exit・source・元result branchを別に照合、metadata負例12拒否。
- 補完manifest: `evidence/provisional/PG14280-current-four-pt-environment-v2/manifest.json` SHA-256 `feb59b693a1a74ba53c88323343888c9dd13a8cf3fc90fd7c9c1a5dfbfa56260`。
- 独立post: `evidence/provisional/PG14282-current-four-pt-environment-post-v1/manifest.json` SHA-256 `f15f909d6e872c24c73a08d6ac914ee50f8f40d50a096b3706b913f8c5c5efbf`。

## 元証拠との一意対応

|元run / 原結果|原manifest SHA-256|
|---|---|
|PG14242 / 2616|053ae4ab0d09af0eb25f711d58c00d5bb54cd88343be9d50e54fcf85b7377171|
|PG14252 / 2618|5b49c990cb01281ea26f7860256b7a09a0ea14becf1419cfce85e33cfc4ba888|
|PG14256 / 2620|90bb7c8ff1b76cb6ae5fc78bf4766bc6fb65702a53923c56e6ecd6b5ab83ef71|
|PG14270 / 2624|b86d3cc5ef5309104d8dfc85e215c193ac04ae7d054deca89da61e7c2520cadd|

全四実測=Linux / amd64 / 7.0.0-38-generic / JDK runtime 25.0.4+7-1-26.04-Ubuntu、JUnit Platform Launcher1.13.4、JaCoCo agent0.8.15。現在hostのuname/java -versionから代入していない。branchは当時の元結果本文に明示されたdev-foundation、qualification HEAD/元時刻/実command/SDK path/hashは各parentに束縛。原resultのhashもenvelope入力なので2616/18/20/24へ追記せず、この対応表を補完参照正本とする。

## 是正範囲・未証明

当四実行の環境再現リンク不足と新工具branch role不整合だけを限定完了。原manifest・元PT・元ログ・SDK・Source/Test・過去失敗工具は不変、製品PT追加0/JVM再起動0/外部操作0/新受入0。今後同runnerで原manifestに四fieldが未構造化なら新-only補完envelopeと独立postを実行結果から参照する。旧source履歴の全環境保証・whole451/動的HOLDの解除ではない。正式1964PT/53scope、17/190、工数null、QA051final、全F03・451未受入を維持。

保存前check追記：最初のexact保存はgit diff --cached --checkのEOF空行警告でcommit前に停止。2626文書末尾は整えたが、実行済み14282工具末尾の空行1件は実行来歴hashを保持するため非改変保存する。full whitespace checkの当警告を成功へ読み替えず、当工具以外は追加警告0で照合して保存する。Production format/静的解析条件を変更しない。pushの一回は未commit時点のEverything up-to-dateであり、成果反映と認定しない。
