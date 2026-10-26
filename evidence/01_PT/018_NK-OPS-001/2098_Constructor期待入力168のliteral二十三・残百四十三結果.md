# 2098 Constructor期待入力168のliteral二十三・残百四十三結果

2026-10-27 00:21 JST、2097仕様、G03.01/群2443開始.5/2/5pp cap10、current source370fd74f6/Main21d変更0。元10582/10584の168全row/旧source SHA/型束縛fieldは保存し、新結果の追加分類へ結合した。

PG10646-constructor-literal-inputs-v1 manifest `a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55` actual0。原式の現source一致166、変更二（Log.deny/Cleanup.redacted）は既BUG1846のliteral化を確認し、元sourceを当sourceとして偽装せず「前群で是正済み・新修正0」へ分離した。

|入力起源/状態|原site数|当確認範囲|
|---|---:|---|
|literal-only・値保持constructor|23|Main十四＋Test内Progress六/Result三。固定String/数値/boolean/nullだけで、Production outputを引数へ呼ばない。Mainは元10588の検証のみ/暗黙record、Test内二recordは空body/暗黙canonical・custom equals/変換なし|
|method由来未確認|66|selectorや引数の起源を調べる必要あり。methodを呼ぶだけで欠陥とも独立とも認定しない|
|名前由来未確認|77|Test fixture定数/入力/enum literal/SUT出力等を未分類のまま保持。大文字名だけで固定値と認定しない|
|前群でconstructor expected撤去済み|2|2089/10600の独立message literal、当sourceのexpectedも確認。再是正/再実行0|
|合計|168|原全field保持、動的合格/新WBS受入への換算0|

独立PG10648-constructor-literal-inputs-post-v1 manifest `2b050795fa812907961133d344b2af7befe42d76f1290681c31130ccbf0dbcd7` actual0。主lexerの抽出結果を再利用せず、元AST行とraw sourceの候補span SHAから166全式を照合した。23のMain十四/Test九の実owner/源path/SHAとsource種別を確認し、未知入力・standalone L・未知Test owner・Test sourceのMain偽装の四反例を拒否。元Main constructor61/55sourceのhashはcurrent正常10632入力と全一致した。primaryのL/l suffix用の広い許容を将来の一般変数へ適用せず、独立postでは当23にsuffixも未知identifierもないことを厳密確認した。

BUG1856/YKT1607：primary初回はfield名mainSourceBindingの存在だけでMainと判定しTest内ProgressをMain辞書へ引いてKeyError1、次の是正もfield値nullを落としTypeError1、いずれもOUT前。元工具SHA e071527b4703e7b2060c1dcb3496c7a2344b5a15f1ea87f7b4d69d8b8d33769c / 1c04c42573ea2817e268b0d894c7c8316bd64c70027710c8c0e2aa385440f519を保持。非null dictはMain実path/owner、nullは当二Test owner/源rowへ明示分岐し、旧metadata自体を変更しなかった。元二失敗は旧10582/10584の誤分類でも製品PT失敗でもない。

各manifest/同directoryのinput-reviews.jsonへcommand/source/実時刻/環境/Python version・hash/actual exit/元row/追加判断を保存、前置pyflakes0を明示分岐してから本体を実行した。製品compile/fixture/classload/PT/新coverage/外部操作0、coverage null、全case fixture/業務期待値の妥当性を自動認定0。原正式1964-53/個別17-190/工数null/QA051final/全安全HOLD不変。

群共有used11→12/reset1793599188の+1pp、実専有費/実tokenはnull、usage63b8dcecdfc0925d6cc9813b560062eed6f5b104f62236b64a8223e423349e5d。次は公開保存後、残77名前由来の固定enum/Fixture入力とSUT出力を限定調査し、未確認66method由来と混同せず必要なPG不足だけを起票・是正する。通常小群/commitで停止しない。
