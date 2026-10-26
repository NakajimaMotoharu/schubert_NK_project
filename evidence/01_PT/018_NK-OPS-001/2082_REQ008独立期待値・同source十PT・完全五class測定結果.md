# 2082 REQ008独立期待値・同source十PT・完全五class測定結果

2026-10-26、群2420/2421（開始1/3/7pp cap10、quota開始はfresh8。元2420の7は2421へ追記訂正済み）。source `36c8d53dae2a333fe97ba8beef1a9c7f100033b2`。Main21d不変更/全1843 class byte一致。BUG1841の固定fallback一式＋追加1842の同値String三/十二参照だけ、全他source token/assertion/fixture保持。原一式plan10530とraw八行10532は歴史として保持する。

2081のSS312「§4.21」は手入力した節番号の誤記。今回照合したorigin/main8b91944dfの正しい箇所は**SS312 §11 Web REQUEST log投影、295行相当**。規則文そのもの・原UI235/252参照・期待UUIDには変更なし。2081はpreflightでhash固定済みの原文として改変せず、本追記で訂正する。上位設計修正ではない。

|段階|結果/公開manifest SHA256|
|10530 原一式plan|actual0、de7b0431f5b6e65d1b23c487eb7701ab7837f8a5f99db7708541406c604ff8b9|
|10532 原static|actual1、PMD8/CS0/処理0、c2b90fc0c18abfea0f37d1ca50e0da3f17d30941e09c5254ed66746a881c22ff|
|10534 最終plan|actual0、六metadata反例/全token逆展開、1d240b682738bc78d9c7ae95f3d7384f052ef5209ee5dcbd81c467f9dd3379bf|
|10536 static|raw actual1、PMD5/CS0/処理0、f7489316458b98966b2f3d13bf0e5de6cc112c8095a52a8969bbeacc866cd622|
|10538 正常六module compile/package|actual0/PT0、56ed79534c2426ccd7ee115b0c11cf093b2ce74b72c46f655bda40d40872f28e|
|10540 事前判定|PT_DEFAULT、固定十method/二physical Test/五完全Main/原SHA、398e8db7c6dedb0895dfed836962e1f618753e4ba6fe739d0033cfc4c66c0b1a|
|10542 当十PT一suite|actual0、F/E/S/aborted/container failure0、287c9d3c3d680505ca3d7b7b4b08cab137a3441de46b8537e69f6ea42ad3c4c4|
|10544 独立post|actual0、XML/session/CRC/classload/source、8e15d3e78666c879515e96b45513aeb1d72af7da8df7eeec117afb8757f25033|

各manifestは `evidence/provisional/PG<上記番号>-.../manifest.json`。実commandは各同番号の`tools/quality/pg105xx_*.py`とmanifestのstages/beginへ固定。全新Python工具は前置pyflakes0。JDK25.0.4、Maven3.9.12、JUnit1.13.4、JaCoCo0.8.15、PMD7.28/record-fix1298、Checkstyle14.3、OS/versionは当run stdoutとmanifest参照。class/source/spec/dependency/helper/XMLのhashは各manifestへ記録。raw HTML/credential/session/token/鍵は公開していない。

残PMD五行は二並行@Testの専用try-resource executor/5秒Future待ちに全対応し、J2EE production thread禁止の当Test文脈非該当。原五行/終了1は保存、抑制・ルール除外0。static rawを成功0へ書き換えず、当文脈の適用指摘0と分離する。十methodを全実行し、scope所有/別thread拒否/100並行も当run実績へ結合した。

## 同runの五完全Main counter（covered/total）

|Main class|Line|Method|Class|Branch|
|RequestLogMvcConfiguration|3/3|2/2|1/1|0/0 非適用|
|WebRequestRouteInterceptor|9/9|3/3|1/1|4/4|
|WebRequestTrace|58/58|17/17|1/1|14/14|
|WebRequestTrace$Scope|15/15|2/2|1/1|8/8|
|WebRequestContext|33/38|7/9|1/1|11/14|

四classは適用counter未網羅0。全五合計Line118/123、Method31/33、Class5/5、Branch37/40。0/0は非適用で数値100への補完ではない。残Contextは3branch/5line/2methodを保持し、全Java100/451としない。旧exec・歴史view15class・template等を合成していない。

単一session `PG10542-TRACE-FALLBACK`、start1793017259575/end1793017260566。全Main1843 byte不変、変更physical Test二（outer/匿名class）のSourceFileは当Test一sourceだけ、他1960 Test同byte/総1962不変。禁止/未選択API/batch/bootstrap/storage/実startup/JDBC等のclassload/probe0。Mock filterとnumeric literal parserだけでDNS/socket/DB/VM/Caddy/Root/鍵操作0、公開snapshot controller source読取はTestの既操作として明記。

原trace registry10512はまだsource661であり、一最終SHA/当十methodのsource36資格は未反映。元主責P006-03/費用/歴史runtime/UNKNOWN二を保ち、Context不足を補完する次sourceの検証後にまとめてtraceへ結合する予定。それまでBUG1841/1842の全終了とWBS受入は宣言しない。

新Test ID/個別受入増0、正式1964PT/53scope・17/190・工数null・QA051final/全安全HOLD不変。次はContextの実測不足だけを修正前起票し、Mock入力の欠落/既context再利用/不整合/安全診断を追加する。同sourceへの旧成功転用・成功確認だけの再実行はしない。
