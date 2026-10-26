# 2089 固定安全診断の四expected是正結果

2026-10-26、2088仕様/PG-D680、BUG1846/YKT1597。source `095720ee2766cd9f0bd441ee4bc019833fde8184`、Main21d不変。四expectedのSUT constructor/getMessage生成を独立literalへ一行ずつ変更した。Log三/cleanup一の各file、例外型/cause-null/suppressed0・他assertion/fixture/処理は元byteのまま。上位/外部仕様変更0。

|公開manifest|SHA-256|真正結果|
|---|---|---|
|PG10594-fixed-error-oracle-plan-v2|5c535c7af7bd6b68eb70094ff6bfed55d83eb5ea6afdf85191b42689313b0b97|0、四元byteへ逆置換一致・十二metadata反例|
|PG10596-fixed-error-oracle-static-v1|e23b29ba95ba12a85c33230b406eb88e25e00216d4671b714374a5ae0c1062f6|1、PMD50/Checkstyle0/処理0、未分類を合格にしない|
|PG10598-fixed-error-oracle-compile-v1|9f88bf4302849e40fed8a699c391e7552d98af1e2038878d63b4fe4585b44077|0、六module正常compile/package・PT0|
|PG10600-fixed-error-oracle-post-v1|4f3af0c58f67c74208514c91b9701b553c736df2484ff2c3aa19f0daec1ce4c7|0、独立raw一行差/全Main1843・他Test1958不変、変更physical Test四/総1962|
|PG10602-fixed-error-oracle-trace-v1|df46372e702b3b0b28c9609250f002b3d7308cd825b8b0298fbe2a1867f99172|0、四最終SHAのみ、他979登録行全field保持|
|PG10604-fixed-error-oracle-trace-post-v1|3304879e8fb8d807e628c783f81e4ed9ffdb11958216f7651614b630345e90b3|0、原941/943・予算/受入・unknown二保持、八metadata反例|

各manifestは `evidence/provisional/<上記名>/manifest.json`（本docと同じ018_NK-OPS-001配下）。command/環境/version/source/入力SHA/actual exitは各manifestと正常compile begin/terminalへ保存。Python3/JDK25.0.4/Maven3.9.12/PMD7.28.0/Checkstyle14.3.0、既固定toolchain使用。原PMD50は四変更行を含まず、sourceの他byte保持で新expected以外を変えていないことを確認した。50の適用性全完了や全F03の成功ではない。

追跡はP01004/P01001/P01707の既canonicalOwner/Cost不変、現在983行/Java1810・登録1808/UNKNOWN二不変。所定WBS監査前後は同じactual1/HOLD、成功へ変換0。旧c919十TracePT/五Main資格、旧a82 template/旧73 view等は元sourceのままhistoryとして保持し、当sourceのPTへ移植しない。

手戻り：BUG1848はdata.shaへPathを渡しTypeError1/元v1空OUT保持、明示byteでv2成功。compile最初のcommandはPYTHONPATHのpyflakes欠落でimport前失敗（stage/job/OUT0）、既導入runtimeを環境へ追加して初回stageを実行、source変更なし。BUG1849は--post引数が無引数invocation契約に拒否、post本文/OUT前失敗。原primary工具hash/結果保持、別無引数10604でpostのみ実行した。emit patch初回出力上限は完全性guardで適用前停止、完全patchを内部受渡しし一度だけapply。拒否されたPT/セキュリティ境界の再演ではない。元失敗・不明を成功へ塗り替えない。

PGの四expected独立化とsource/型/byte/trace検証は完了。**元動的PTはNOT_EXECUTED_HOLD、coverage未測定/null、PT免除/全451/全F03/新WBS受入0**。正式1964PT/53scope・個別17/190・工数null・QA051final保留不変。共有used10→10の丸め差0は専有費0を意味せず、実費/実tokenはnull。usage cursor1606967c31a6f33f5fa91efee7728a4f3becdc8f67af57ea1aa5e5d75d0f6107。

次：公開保存後の限定障害close、原PMD50の公開後続成果/適用性/未是正duplicateを限定群で確認、独立PG/PTを継続。全体未読保証はBUG1847により不明、保留二fileの内容確認・実行・変更・stage/pushは行わない。
