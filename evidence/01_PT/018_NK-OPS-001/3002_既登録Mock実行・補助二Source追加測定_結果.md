# 既登録Mock実行・補助二Source 追加測定結果

2026-10-31／3001／PG-D960／群3352・3353。Production source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、normal14216不変更。PG14540原12/3と14542独立成功を参照し、JUnit/Productを再実行せず二Source二Codeを受動測定。新PT・新JVM・新TestID・新機能受入は0。

| Whole Source | LINE covered/missed | METHOD covered/missed | CLASS covered/missed | BRANCH covered/missed | 結果 |
|---|---:|---:|---:|---:|---|
| ClosedWebAuthentication |14/0|2/0|1/0|11/7|分岐未達|
| SessionPrincipal |13/2|2/1|1/0|5/5|line/method/branch未達|
| 合計 |27/2|4/1|2/0|16/12|strict four gate 1|

全physical二、metadata/除外0。Closedのanonymous・正確なtoken型/状態・principal/credential/details/authority条件、Principalの不正UTF8・空・64byte超・末尾space・制御文字/getNameが未証明として残る。独立期待値はSS314の投影/username契約と元web138～141の明示assertionを参照し、実装methodからexpectedを作らない。将来の追加PTはこれらを個別条件・境界・nullごとに設計し、正規source/input固定と必要451検証を経る。新fixtureをsource資格回避や保留操作の代用として作らない。

元raw14540 SHA4a8e746973cf694404b494352ff8f6348cb4741cec67efa99e0ffc1377f42ea4、独立14542 SHA b3e3509aab38e895675a59f93f6b8fe8c01d8614b799b840d10065bf1513f36c。15758旧測定843d77fda87ded57728d392717a6e454ba09a8a2f4f904f9e2818a2dcd0c85a7は効果説明誤falseを保持し資格参照に使わない。BUG2146/YKT1893先行起票後、15759訂正版a11c2bc0601ce48308b82bd5573fa8c23183833923ec5308a7d551b4517f6d20は元counter/session/CRC/終端を変えず、公開request/event IDのUUID4生成とforeign token公開合成fixture使用を明示。元14542はfield欠落でありfalseだったとはしない。実秘密・実認証session権限・DB/JMS/HTTP/VM/Root/native操作は0。新工具はmetadata/受動解析だけ。

15760独立546e31b389488b4ed3534db911d97466978a58d02e54c3e353b24b2e9cab622d、35反例・元12case既登録/全counter/全元結果不変確認。15762 registry8c2d3069736a32b9154f030a14f6ca8274e2f4059a3f5507f67f778cbd277bb8、15764独立12ab69dbc272a9a767e456f41c5292cf0aa6cd96f672c4d50eb011060fa53b14・34反例、全actual0。公開manifestはevidence/provisionalの各対応PG directory/manifest.json。entry/command/環境/原run/session/input/class/exec hashesはそこに固定。別source/exec union0、旧API digest訂正等の全旧proofを保持。

現2023方法/266suite不変、測定447→449Source/591→593physical、Code569/metadata24、四247/360・自然173/188・NoCode6/6不変、未達21→23Source/37→39physicalは測定範囲拡大であり既成功退行ではない。全113JVM/2131方法実行=2023unique+108repeat不変。正式1964/53・17/190・工数null/QA051final保留・全451/HOLD不変。
