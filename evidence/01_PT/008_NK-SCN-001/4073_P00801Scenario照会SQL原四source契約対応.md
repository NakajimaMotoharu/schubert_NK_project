# P00801 Scenario照会SQL原4source：契約・独立期待値対応

NK-SCN-001、FUN-003～005/FIL-001～009、UI223/224/234/237、origin/main SS332 §3/4/14。ScenarioQuerySnapshot/ScenarioRequest/ScenarioQueryException/ScenarioRepository全source読取、対象method/設計commit・hash・source hash・TestID/独立期待値は [PG26832 manifest](../018_NK-OPS-001/evidence/PG26832-scenario-query-contract-v1/manifest.json) checksへ対応。

PT-SCN001～004: games display_order/id/max10、speaker同名GROUP/minid/countentry降順/name昇順/max500、route game別固定map/2桁prefix/未分類/max50、file display_order/id/entrycount/max500。PT-SCN005～007: NFC/trim条件をvaluebind、本文lowerROOT LIKE/話者名完全一致/章ILIKE/game/type/voiceEXISTS、単一CTE/count/list/代表voice/entry順・100件page/empty1/clamp/99,999,900超9001。**Scenarioのpercent/underscore/backslashはCurrent LIKE pattern解釈を維持**し、他queryのescape規約を適用しない（SS332 §4.1明示例外）。

PT-SCN008-D01～004: global前後file/entry_index順1開始/voice全展開/音声なし0、expanded10000上限・10001sentinel、未存在Optionalempty→0104。titleはchapter/section/fileの最初のJavaisBlank-falseを加工せず、speakerはFKname。SQL NULL/整数桁/unknownenum/wire不整合9000、容量9001＋close複合障害は9000/fatal保持。借用readonlyTX/ownedstatement/result、接続commit/rollback/close/fileI/Oをしない。PT-SCN009-Q01～04: sixlayout/typedwireと明示LP/HMAC順/optional presence/actorowner/呼出側canonical消去、snapshotは権限や確定応答ではない。

候補ScenarioRequestTest3はactual FingerprintKeyRing依存、ScenarioRepositoryTest18はactualDB whole fixture。Repositoryはactual TemporaryInfrastructureException.preserveFatalへ直接依存するため、byte read/hash/parse/compile/init/runtimeの許可を推定しない。PreSQL9のnullmethod部分選択や旧Fixture抽出でHOLDを迂回しない。実DB Test body全体は未監査で、source method index/設計との期待値対応まで。原sample期待値・Test oracleは変更しない。

共有ScenarioDetailSnapshot原6（PG19818）のtargetMain/Test/sourceとnormal physical同一は確認。別所有componentの旧限定実績として保持し、変更済Protocol3の全依存資格を現在値へ移さない・新費用/再試験0。現在必要なpure snapshot正常PTは実主担当・全helper閉包の照合後に進める。

metadata command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1352_scenario_query_contract_audit.py` exit0、新規PT0。原/1 .087/.210/.420の準備のみ完了、原/2 .163/.390/.780、P00703/P00301終了依存、actualDB/held4/全451・元190は未受入。Main/Test/期待値変更0、正式1964PT/53scope/工数null。
