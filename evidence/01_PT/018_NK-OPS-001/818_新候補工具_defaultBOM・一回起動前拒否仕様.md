# 818 新候補工具default BOM・一回起動前拒否

工具PG2684 body/observer認証・PG2682/2700/2704/2706のdefault依存、WBS-P017-12/SS342343352/451/BUG1246/YKT1012。Production Main/資産・業務仕様・Currentbaseline不変更。工具fixtureをProduction PT/coverage/全leaf受入へ加算0。

## 修正前の実拒否・独立現在地

PG2684v1 actual1（06:47:49.244822Z～06:47:56.506613Z、payload0b2f939c）。observer()のmatches0で、watch=observer()がsave/一回予約/startに先行しておりguest予約dir/guard/issuedすべて不在。fresh systemctl四UnitはMorning/Caddy inactive-dead、API/Web failed-failed、全MainPID/ControlPID0/Job空。実Python watcher378658/t6337995/argvSHAd92a8735/Source42/BOM552c5e/PG2654/UID-GID全0/ExePython3.14を確認。sudo monitor378656はargv異なるため独立python identityへ算入0。watch/session25064は保全・再stage/restart0。v1失敗私有rawは保存、successへ合算0。

原因はbody(None)がprevious.body(None)へ委譲して旧PG2512BOM2f32を解決したこと。明示BOM fixtureだけでは省略経路の不一致を検出できなかった。新candidate_bomを委譲前に解決し、v1 host成果は保持してv2/new-only namespaceに切り替える。予約・start発行を独立確認するまで再実行0。今回は発行前拒否を実証しており、同業務startの再発行ではない。

## 独立default oracle・横展開

固定expected new SHA552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37、旧禁止2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395fをliteralとする。各producerでdefault==explicit(new)を比較し、previousのdefault読取をAssertionErrorで禁止、new literal存在/old literal不在をassert。dummy bindingは純構築dataのみ・guest/permit/Root成功の合成0。

対象：2682 source、2684 body、2700 terminal payload、2704 whole payload、2706 parent18 payloadの省略/明示。2684に修正、他四は委譲前にnew defaultを既に解決していて非該当、全五で再発防止fixtureを実行する。2708/2716 namespaceはcandidate_bomのglobalをnewへ置換してcloneするため非該当、terminal emitterも同BOMを伝播、既13関連fixtureで全namespaceを確認。2674 sourcesはnewcandidate_bomを入口で解決、2658/2666/2675/2676はbom必須引数で省略なし。2698/2702/2718/2720のactualreceipt参照はv2へ一貫更新、旧v1を受入根拠へしない。

実行：`python3 -B -m unittest pg2730_new_candidate_default_test pg2684_operation_current_test pg2704_operation_acceptance_test pg2712_operation_owned_test pg2722_operation_native_test pg2724_operation_backup_test`（既定PYTHONPATH tools/quality、vm/050_s1、pyflakes3.4runtime）。純fixture・静的解析0→source固定→既watcher認証→正規v2一回起動→同newgeneration照合→当親terminal/all24/wholeまで依存順。実再試験未完のためBUG/YKT対応中、正式1964/53/新native/全四100は未受入。
