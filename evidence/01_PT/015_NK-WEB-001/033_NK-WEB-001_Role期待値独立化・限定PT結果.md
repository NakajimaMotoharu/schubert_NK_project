# NK-WEB-001 Role期待値独立化・限定PT結果

2026-10-26、dev-foundation/source b98ab2b8a2e8868f07471a95530d1005b6121b10、BUG1825/YKT1576、仕様032。13Test sourceの18期待式だけをUSER/ADMIN明示switchへ是正。全元assertion・他tokenを保持、GJFによるString分割/Java Unicode dollar表記は両側のJSON互換Java Stringを同じ手順で正規化して比較した。片側だけ結合した初回非正式比較で出た不一致はraw保持の検査経緯であり、製品失敗ではない。

|記録|実結果|manifest SHA-256|
|---|---|---|
|PG10392-role-literal-plan-v1|18限定変換/13source、元SHA固定|af9752f79f1a4af7be0264e301841f31dc1be0f3976115198ec6a112f8ab147c|
|PG10394-role-literal-static-v1|own51395 actual1、PMD250/CS0/processing0。156duplicate、thread34、if literal17、volatile38、resource1、loader3、synchronized1。適用性未完でF03未受入|0b1be65fb8da3963f2565090880365c7091fecc39578ccc17b13dbbc25299f38|
|PG10396-role-literal-six-compile-v1|own77356 actual0、正常六module/NullAway/PT0|42e446d87c251b819592758cbadeee1d5ba4e785d91269edfb6ac873f71b8b5c|
|PG10398-role-view-preflight-v1|actual0、元全token/全assertion保持、誤role/欠落26metadata拒否。実行は032の四methodだけ/三suiteへ凍結|61d668553986bcee00eba79234f5db7c2458ec153973d26db6a82519add35aa4|
|PG10400-role-view-host-v1|own39321 actual0、当sourceの四PT/三suite、failed/skipped/aborted/container failure全0、新Test ID0|23352c80b40a5823c7f7c5625f984bbf946e6b8b316fb8ad7673fa802f0b09bd|
|PG10402-role-view-post-v1|own97276 actual0、元XML/選択4method/真正終了/同source session/CRCを独立照合。全Main1843同byte、他Test1909同byte、当13source由来47class差（新switch用synthetic13含む）、Test physical1943→1956。未選択依存/held probe/対象外product class load0|08802be2aec7b9a6794526549d9cf9a19bbde0a0c979d253ec9908cc6ad40d93|

## 当runの完全class四counter（covered/total）

|Main class|line|method|class|branch|
|---|---:|---:|---:|---:|
|AnimationMenuViewModel|19/19|8/8|1/1|4/4|
|GameListViewModel|10/12|4/5|1/1|1/2|
|GameListViewModel.Card|8/9|4/5|1/1|0/0|
|MusicCategoryViewModel|23/27|6/7|1/1|8/14|
|MusicCategoryViewModel.Card|8/9|4/5|1/1|0/0|
|MusicSectionViewModel|27/31|7/8|1/1|8/14|
|MusicSectionViewModel.Card|8/9|4/5|1/1|0/0|
|TopBarViewModel|7/9|4/6|1/1|0/0|

当四methodだけの実測であり、AnimationMenu一classの四100は技術測定。新WBS受入数への換算0、0/0を他classの未網羅補完へ使わない。全Java/全対象coverage100ではなく、別source/旧exec合成0。八classの全methodを分母に保持し、未実行getter/toString/境界を除外しない。

## エビデンス・境界

018_NK-OPS-001/evidence/provisional/上表run内のmanifestを参照。PG10402/xmlへ元XML/summaryをbyte保持で公開保存。source/入力hash/独立期待/工具・library/JDK25.0.4・Maven3.9.12・Linux7.0.0-38 amd64・branch/commit/command/終了値は各manifest/032に結合。Python commandは各tools/quality同番号、PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime。host JVMは固定四method catalog、coverage readerは既exec/class byte読取だけでJUnit再演なし。

残る9source/他Test method/元API DB・key等の試験は今回未実行。role是正のsource scopeと選択四PTだけを確認し、raw250/全F03/G03/451は未受入。正式1964PT/53scope、個別17/190、工数null、QA051 final/全安全HOLD不変更。元原本DB/Backup/鍵/native/stash/Scenario/Current baseline/held witness二fileに変更・アクセスなし。

次はBUG1826/YKT1577のcode15期待・負例fixtureを一経路として独立化。role13最終SHAはその変更とbatch追跡し、当四PTのsource b98と元担当P016-04/08/11・歴史runtimeを保持し、新source全体の成功へ流用しない。
