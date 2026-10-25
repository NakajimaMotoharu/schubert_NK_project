# G13 明示case/spec行候補v2・独立結果と未確定範囲

2026-10-25 17:47 JST、2183/1946-1947/PG-D662、Production64446不変更。既存5622通常Test宣言と固定HEAD854cの1188仕様を照合。BUG1752/YKT1503に従い、任意のcomment内数字抽出をやめ、先頭の明示仕様番号chainだけをproducer anchored grammar/独立post手動parserで確認した。元v1/失敗67588/修正前sourceは268850069a86e0d36d1928e7bb1331b1d1242decへ保全・push済み。

|公開manifest（evidence/provisional以下）|元終了|SHA256|
|---|---:|---|
|PG9602-explicit-case-row-candidates-v2|0、旧corpus/仕様行保持|f4fa3e3fe68ef3343c20a7e8cbc8c128918f32cb10bad3b9634a90efe587d3ba|
|PG9604-explicit-case-row-post-v2|0、別parser/全候補再計算/13vector/8反例|24a6202625e1e76c6f070254d630330525438f34bb3a915ed4d9778563c08092|
|同correction-post.safe.json|0、追加8vector/全横展開差分|28a911908a04dc287fef9b390703e42e6df99de8e8498e0c634ebc887c1d6ca8|

|静的参照状態（method宣言単位）|件数|意味|
|---|---:|---|
|一意・source Javadocに仕様番号明記|44|case token＋先頭仕様番号が同じ既存行。意味的oracleレビューは未認定|
|一意・global case token|815|既存仕様行候補。source docrefに基づく結合ではなくレビュー待ち|
|複数仕様行|75|勝手に一つを選ばず保留|
|明示source docrefと行が不一致|13|global fallbackせず保留|
|厳密case tokenはあるが適合する明示仕様行なし|2397|range省略/別表現を推定展開していない。oracle不存在との断定ではない|
|method名に厳密case tokenなし|2278|Header等の文章型method名を含む。別の明示method参照方式が必要|
|合計|5622|試験実行数/PASS数ではない|

一意な候補859は初期traceの参照であり、859oracle/受入完了ではない。旧v1からsourceHeaderDocRefs3618行、実際に選択された仕様候補445行が変化した。修正可能fieldはdocref/status/specRowCandidates三つだけ、method/case token/元binding/false資格field/全5622行とcorpus/既存仕様行hashは不変と別実装で確認した。誤った初回候補を成果へ上書きせず、手戻り/工具修正として別計上する。

producerとpostの両numeric抽出を新v2へ置換し、元反例「1870/APISTOP001..018」→[1870]を変更せずpass。複数仕様番号/全角range/dash/date/本文数字/rangeだけ/改行asteriskを含む追加8vector、元13edge、8metadata反例が全て通過。入力corpus loaderと9554 literal表は数字docref解釈がないため非該当を確認。元不正数18が復活するか、未知参照をglobalへfallbackするか、oracle/実行/PASS捏造するかを拒否する。新v2初回Pyflakesは未使用Path importで実処理前に一回停止、削除後0。producer/post元実行は各一回で0、実PT/旧4222の確認再演0。BUG/YKTは工具scope検証済・commit/push具体化待ち、製品/全traceの完了に拡張しない。

source/TesID本文/期待値/元Markdown仕様を変更0、対象class/Compiler/JUnit実行0、実Root/VM/native/DB/私有raw/鍵/intent/permit/配備操作0。正式1964PT/53scope、個別17/190、工数率null、QA051final、全current audit1HOLD/BUG1746/G07残4493/全actualHOLD保持。source責任1781/1789/残8、全Test宣言5622/RepeatedTest別一は不変更。

開始08:35:08UTC used5/残95→08:47:19UTC used5/残95/reset1793513544/secondarynull、共有丸め差0≠専有費0。実N/T/配賦null、usage2e3fbe42/既cursor保持、.5/3/8pp/cap10と原/v3/v4/v5見積りは不変更。新規参照準備/追加発見BUG1752/初回失敗/全候補手戻り/tool修正を分離、見積減額や完成率へ換算0。次9606 END/9608 publicdelta/通常commit-push→既存明示source参照付き候補の意味的oracle対応、又は別の許可済みPG/PTへ進む。通常小群/commit/PMO待ちで停止せず、fresh現在窓残10以下等の保全条件まで継続する。
