# Web四JS資源・原wrapper5/Node30 実行結果

2026-10-30、Production source `6b53efeec87f3ec36a840dd8e7759656cb4aee5c`、dev-foundation、normal14216。同仕様2767の変更なし原Java wrapper5件/4suiteと子Node30件を初回実行、各F/E/S/todo/cancelled0。PG14778/own session97351は真正終了0。PG14780と追加独立PG14782も真正終了0、製品の再実行0。

|scope|原試験|独立検証した実結果|
|---|---:|---|
|log-search-validation.js|Node8|line/function/branch各100%、欠落・境界・NFC/byte・修正送信|
|operation-post-submit.js|Node6＋Java template照合1|各100%、不正修正・二重submit・独立form・承認update画面の属性|
|search-speaker-submit.js|Node8|各100%、必須DOM・全不正停止・Unicode/byte・game変更|
|question-input-validation.js|Node8|各100%、必須DOM・1～4096 byte・残数・元文字非変更・送信再検査|

独立oracleは固定CJSのliteral ID/message/上限/DOM呼出し回数と手計算byte。production関数からexpectedを生成していない。Java wrapper5とNode30は親子の異なる階層であり35 Java試験とは数えない。Node resource coverageはJava Main Source四counterへ転記しない。新Java Source資格0、JavaScript class counterは非該当。実Browser/HTTP/業務再送/CHRは未実施・未受入。

## 証跡

すべて `evidence/provisional/` 配下。manifest自身のSHA-256は次のとおり。

|run|manifest SHA-256|
|---|---|
|PG14778-web-four-script-resources-pt-v1|5f4205513895cd2ea19ca369d5bffe6d1a752cc959a5ed04913a028ab247d7f8|
|PG14780-web-four-script-resources-post-v1|93523a10ae49e619195a4a228a528a822c32184adb218cb78268eb998752ef05|
|PG14782-web-four-script-resources-independent-v1|e9e6bb114098d6d02d38b502822916dd350b1db70c4de1f0e81d0e8775a5a70d|

14778は全normal input/原Test/15コピー/Main11資源のJar byte/固定Nodeのhash/command/原JVM環境/終了/全XMLを保持。14780は返却XML4とNode出力12のhash/内容を保全し、8 metadata＋4 TAP負例を拒否。14782は元宣言とXML/TAPを再結合し、14 semantic＋5 TAP負例を拒否。Java source/class/oldSource成功/実Browser/新受入への誤昇格を拒否する。両postはProduct・Nodeの再実行なし。

実環境は原JVMからLinux amd64、kernel7.0.0-38-generic、JDK25.0.4、Node24.19.0（絶対binary/hashを固定）。PG14782初回checked-entryはunused importのlint終了1、body未着手。未実行draftから未使用importだけ除去後、lint0/body0。Productの再実行・試験失敗・拒否操作の再試行ではない。

## WBS criteria判定・残る依存

主P016-25.03/関連P016-25.02、追加予算0。四JSの当source inventory・独立DOM/oracle・全実測三counterという局所証拠は充足した。しかしP016-25.01のexternal dependency P015-02は未受入、同項目の最後の既存測定sourceも当6b53ではない。従って.01→.02→.03の終了依存を今回のNode成功だけでは閉じない。各acceptanceはNOT_ACCEPTED、新受入0、費用減額/完成率への読み替え0。

481の親ownedArtifactsは四JS＋CSSを既に列挙する一方、契約文章は「3 Production JS」、resourceSelectors/CandidateTestFilesにはoperation-post-submit/OperationPostScriptTestが欠ける。今回の証拠は実ファイル四件を省略せず補完するが、旧WBSの記述・凍結見積り・過去受入は上書きしない。次の計画整合ではこの3対4の記載差、当sourceでのP015-02契約/trace受入、CSS/HTMLの.04を別々に扱う。画面設計変更や試験期待値変更はしていない。

現Java限定registry870/122suite・209Source281physical・四100130/195、自然074/80/noCode1/1/未達4Source5physicalは今回未変更。追加wrapper5はregistryへまだ未結合、Node30は別domain。正式1964PT/53scope・歴史17/190・工数null・QA051final・全F03/451/全HOLDを維持する。実VM/DB/鍵/intent/permit/配備0、外部状態UNOBSERVED_HOLD。共有枠は11:24頃used32/rem68、短期値null、専有費/N/Tは不明。
