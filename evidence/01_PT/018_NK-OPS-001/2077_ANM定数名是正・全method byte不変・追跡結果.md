# ANM定数名是正・全method byte不変・追跡結果

F03/群2412、着手前.25/1/3pp・cap10、BUG1837/YKT1588・工具baseline BUG1838/YKT1589。新source6612747b7a5492e5c49647d85cfc2dcbe6d75c9f、旧a82。AnimationControllerTestの値ANMを誤ってtimestampと命名した一identifierだけ、実変数typeに対応するFIXTURE_MENU_TYPE_CODEへ六参照変更。17桁JST stamp二literal/値・電文配置/期待・全assertion/他token/Mainは不変。

関連NK-WEB-002/PT-SCR054～065、UI235・SS323/313、原013_Animation一覧HTTP単体テスト仕様書。原Controllerは実DB等lifecycleのHOLD/未試験を保持し、今回試験実行成功へ置換しない。単なる内部名の是正なのでRD/UI/SSの仕様変更・QA/SSC不要。SS323のorigin/main正本はfresh fetch後も8b91944df、ANMREQ01/ANMRSP01とN17 timestampの区別を独立表で照合した。

## 意味・source・真正結果

10504 meaning-review.jsonは全54定数を分類。ANMは三byte Animation menu type prefix、17桁stampではない。他53はHTTP route/view名/DOM selector/model key・属性、成功code/ゲームcode、合成actor/CSRF/escape入力、series prefix、fault mode1/3の用途を閉じた独立literal表へ対応。値はhashで保存し、runtime secret値を扱わない。誤timestamp名/ANL/17桁をprefixとする誤り、旧identifier復帰/値変更の五metadata反例を拒否した。反例は製品PT数へ加算しない。

|公開run manifest|真正結果|SHA256|
|---|---|---|
|PG10504-anm-type-name-plan-v1|終了0、六identifier/全他token・54意味/五反例・SS正本一致|0d0d2f6fa38aaa86eb738162718ccd717179271ca3cfd1825589f5b4cb1443f1|
|PG10506原static工具|旧型source73/10462指定漏れを非対象input SHA guardが検出、終了1/SLOT・OUTなし/JVM0|manifestなし|
|PG10507-anm-type-name-static-v2-v1|直前a82/正常10480/plan.baseSourceを結合、raw exit1/PMD5・CS0/処理0|d3c018b12b4e6cc22099e6859386a6c5c54a53f587434317c185935b4bd60ba2|
|PG10508-anm-type-name-compile-v1|当source六module正常package終了0/製品PT0|bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5|
|PG10510-anm-type-name-post-v1|独立終了0、当classのUTF8 field名一entry以外の全byte完全一致|9b4846505a017402cdd65eefee11b35e2ca645228ebf55a7556fc8cbba79b809|
|PG10512-anm-name-trace-v1|983行中一SHA/他982全field保持、旧runtime/cost/UNKNOWN保持|b93037871e0227b4d3c699e290973d846e9cb7dd5808aa59d0415b219ae8bb93|
|PG10514-anm-name-trace-post-v1|独立終了0、九metadata反例・所定audit前後1同HOLD|2ad746aad6d14d79f929d51c99f591b540cd157dc21407c7c7b7db1c18d95889|

manifestは `evidence/provisional/<run>/manifest.json`。Linux7.0.0-38/JDK25.0.4/Maven3.9.12/PMD7.28/CS14.3、各tool/command/dependency/hash/時刻・actual exit/input/sourceはinvocation/stages、実行は共通PYTHONPATHで各pg10504/07/08/10/12/14対応工具を一度だけ。各新Python工具pyflakes0を実行前確認。原10506/誤baselineを歴史保持し、V2の全非対象input一致guardを弱めていない。

## binary/sourceの厳密範囲

GJF後もplanned SHAと完全一致し、再整形差0。二identifierは等長22byte。before Test classのCONSTANT_Utf8（tag1/u2 length/field名）一entryをOLD→NEWへ置換したraw全体がafter class rawと完全一致した。従って全methodの命令・属性・debug情報を含め、当field名entry以外は一byteも変更なし（単なるmethod名/Code長の比較ではない）。Main全1843/他Test1961 byte不変、Test総数1962不変。

当raw5は元26中の同じ二Thread/三volatile行と全属性一致。2076の個別可視性/設定write/並行read-onlyという静的契約もidentifier逆置換で不変、抑制0/当文脈適用0/全F03未受入。Java codeのcompileは実施したが、当Controllerや元DB/Root/VM/key/Graph9等の実PT/実環境操作0。CHRはMain機能変更なし・元HOLDにつき未実行でありPASSに加算しない。

traceの現sourceは661、原983行/候補975/1810-1808/UNKNOWN二/legacy749・原主責P01610/費用/受入を保持。旧a82の14template/counter partialと旧73の28view/15class100は各歴史sourceのまま、新global sourceへ成功転用/exec合成0。正式1964/53・個別17/190・工数null・QA051 final/安全HOLD維持。

本群に新scope受入/新Test ID0、意味名の自作手戻りとsource metadata/tool是正を元予定と分離。開始/残予測は変更しない。次は公開保存後、既G13の未登録二sourceについて過去follow-upをmetadataから確認し、既静的HOLD/担当/要求の根拠を限定整理する。対象の実行・新許可を付与しない。
