# listener二Source六method独立oracle対応 結果

仕様3837、scope617。Production7aed不変更。PG24022の公開Source/既証跡読取checkはexit0、2Source/6method descriptor・原六caseへ明示対応、24assertion snippetを各Test body内で照合した。新PT・compile・JVM・backend実行0。原23436/独立23438の成功は再実行していない。

|Source|method|Test ID PT-JMS-PORT-|具体的な独立期待・観測|
|---|---|---|---|
|QuestionWorkListener|constructor|001/003/004/005/006|ASYNC_WORK/API_WORKの固定用途、提供processor/clock、null拒否。固定QWKREQ01 goldenが用途を検証|
|QuestionWorkListener|public onMessage|001/004/005|320/64 E/Iの明示値、delivery3/transport ID/固定時刻、mode→process→commit、null/非transacted拒否|
|QuestionWorkListener|observer onMessage|003/004/006|二配送を各一commit、null observer拒否、元例外identity/attempted→rollback→confirmed|
|WebLogListener|constructor|002/003/004/005/006|WEB_LOG/API_WEB_LOGの固定用途、提供processor/clock、null拒否。固定WLGEVT01 goldenが用途を検証|
|WebLogListener|public onMessage|002/004/005|2336/2080 E/I、REQUEST/INFO/GET /login/200/0という合成固定値、mode→process→commit、null/非transacted拒否|
|WebLogListener|observer onMessage|003/004/006|二配送を各一commit、null observer拒否、元例外identity/attempted→rollback→confirmed|

SS321のSESSION_TRANSACTED/成功commit・失敗rollbackとSSC319同期callback、SS322 header256/SCHBNK01、SS323 QWKREQ01・WLGEVT01の独立literalが根拠。承認design commit/pinと各methodのSource SHA/class SHA/Test ID/case/要求・UI/SS参照をmethod-oracle-relations.jsonへ保存した。Main methodは直呼出のみで、戻り値や例外を別物に変えない。期待値はProduction encoderやlayout計算を呼んで生成していない。

限界: 005の本文未読はsource順序根拠、独立read counterはない。003はcaller配送二回であってInbox/業務重複防止・broker並行の実証ではない。例外identityの実観測はsynthetic RuntimeExceptionであり、checked JMSException/直接Error/rollback・observer自体失敗・fatal DLQ各経路の全実証を含まない。constructorから委譲先へ渡すdetectedByの値はsource根拠で、当六caseのfatal経路では未観測。六methodの全期待/全例外oracle完了false、callee/全G13/451受入false。今回の明示link6をwholeSource追加、実行PT、coverage、PT免除又は正式受入へ変換しない。

追加unique517/候補114/pending12/whole暫定93、正式1964PT/53scope、新leaf0/工数null、G07未分類3313+22/actualSecretCountnullと全actualHOLDを維持。BUG追加なし。metadata checkの手順はpython3 -B input619（repoから完全pathで実行）、入力pin617/旧独立23438/現23972/承認SS。日時 2026-11-08T15:39:27.104556+09:00。manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG24022-listener-six-method-oracle-review-v1/manifest.json` SHA256 `15080d61f66be23a56982f3c69f9403641d347683815491a8ff4194d44b3a955`。source固定・通常pushはPG24024 publisher参照。
