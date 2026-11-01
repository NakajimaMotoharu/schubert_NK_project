# エラー分類・表示値三Source 独立単体テスト仕様

Program NK-WEB-001/SCR090、PG-D1122、UI222§7・SS313§9/SSC047048/TST001..005。Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、開始HEAD647122176ad61704386a6ec2170d8aecd296cba2。群18150の事前0.5/2/5pp cap10、primaryWBS-F03/元owner参照追加費0。PG責務は省略せず既実装を点検し、仕様違反発見時は修正前起票。今回Main変更予定0。

## 全Source・具体的PT_DEFAULT境界

WebResultMapper25行/2e665570、ProblemViewFactory36行/d3ebd235、ErrorViewModel69行/6f0861b6の全bodyを確認。closureはMapper本体＋javac switch補助$1、Factory一、View本体＋Status一の三Source五physical、公式JaCoCo生成filterは不変更、手動除外なし。完全SHAはraw MAIN_UNITS。helper ResultCode/TopBar/SessionPrincipal/AuthenticationContext/UserRoleも全bodyと正常14216snapshotへ固定する。後続索引2074/2154/2933は旧source・constructor/他scopeの限定結果で当全Source資格へ転用しない。

全六新quality methodを一つの通常ローカルJUnit JVMで実行し、元ErrorMvc DB fixture/methodの抽出・改作なし。実HTTP/Servlet/認証/session発行/DB/JMS/file/Root/VM/native/鍵/時計/worker操作なし。公開UUID(0,73)とPUBLIC_DISPLAY/a64の合成snapshotだけ、NFC/UTF8検査は実行true、raw contextの保存0。JDK初期化内部効果は未知、単純命名で安全性を推測しない。ErrorControllerと保留ErrorMvc wholeは対象外のまま、独立結果をその代替合格にしない。

## Test ID・独立oracle・入力と操作

Test class tools/quality/architecture/ErrorValueContractTest.java、六methodの末尾番号とERROR-VALUE001..006を一意対応。

|ID|入力・操作・期待値の独立根拠|
|---|---|
|001|ResultCode十二を明示配列、SS313§9/UI232の200,400,401,401,403,404,409,429,409,200,503,503へ分類。httpStatusをexpected生成に呼ばない|
|002|null ResultCodeは契約NPE/code、catch正常化0|
|003|固定九HTTP入力は同status、属性欠落nullは404。公開UUIDの文字列は手計算hex73=49から固定、Optional.empty保持|
|004|0/200/500/Integer両端/string404/Long404/StringBuilder404/booleanは503。未知/foreignをparse/toStringして404に変換しない。SS313の既定503文言|
|005|九Status→明示九HTTP、UI222既定403/404/409/503全文一致。他五文言は上位全文未規定なので入力/ログイン/操作方法/範囲/しばらくの目的語・非空一行だけ（全文互換認定しない）。公開request ID/empty/redacted固定|
|006|status/requestId/topBar各nullはNPE、Factory経由nullも拒否。公開合成TopBar Optional instanceをdirect/factory双方保持。実ログインなし|

正常/境界/未知/null/Optional/固定redactionを上記で検証。並行/再送は可変状態・外部I/Oなしのため非該当、実業務の再送要件を免除しない。独立upper設計と手書きmap/UUID/purposeを使用しProduction値からexpected生成0。enum switchのjavac補助全byteも測定に含め、自然B0は四100と分ける。未達counterは除外せずそのまま記録。

## 実行・証跡・受入境界

正常14216/JDK25.0.4・静的14224の同source hashと六Mainjarを再利用、全回帰/署名の成功確認再実行0。raw18150→全closure単一exec post18152→独立oracle/metadata否定18154→registry18158/独立18160→WBS二面18162/18164→source結合18165。各entryをchecked_python_entryでlint後一度実行し、真正exit/XML/FESabort0/OS/JDK/branchHEAD/command/input/class/exec/hash/session/CRCをmanifestに保存。postは製品再演0、False PASS/foreign source/分母欠落/coverage union等を実否定。詳細は3465と各manifest、source/run一致まで暫定扱い。

正式1964PT/53scope・新受入0・工数null、QA051final/G07/G13/F03/451/全HOLD維持。新quality件数とordinary5786の消化を混ぜず、当初/現残/群開始見積と共有観測費・専有未知nullを分離する。
