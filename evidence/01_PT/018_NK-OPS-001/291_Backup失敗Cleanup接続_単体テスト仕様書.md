# Backup失敗Cleanup接続 単体テスト仕様書

Program NK-OPS-001/NK-BAT-001。RD BAK001/OPS009/DAT009、UI251、SS331/341§7.3/343§6.17、SSC117/124。対象はCleanupFailedBackupRequest/BackupFailureSnapshot・private reader/files・Root BACKUP readonly proof・Main/actual Cleanup/parent readback。独立期待値は下表と固定byte/SQL後条件で作成し、Production encodeからexpectedを作らない。

| Test ID | 目的・入力/操作 | 独立期待・根拠 |
|---|---|---|
| CFREQ001 | NKCLEANFAIL1手書きgolden・encode/decode、別NKCLEAN1 | SS343固定11key/順序/ASCII/LF完全一致、同owned byte消去、成功profileと排他 |
| CFREQ002 | null/空/欠落/未知/追加/重複/CR/NUL/非ASCII/1024超 | 拒否・byte消去、NPEを正常扱いしない |
| CFREQ003 | UUID nil/非canonical、数字0/先頭0/負/上限超、正常exit0/256、µs/日付/時刻/row ID/attempt境界 | SS343/domain境界、JST business_date明示固定、両ID異/started-ended同値・逆転拒否 |
| CFREQ004 | 固定18field Backup literalと新/旧Invocation、normal/signal/timeout/manager差異 | claims比較だけで権限無し、真正全kernel＋前後一致必須、FAILED normalだけ |
| CFREQ005 | private source新規/再読/退役・成功kind/失敗kind取り違え・owner残留 | Root metadata/同byte/part force/directory force、一意profileと同owner、上書き/修復禁止 |
| CFREQ006 | 根本Root種別/私有copy/親PID/boot/activation/Epoch/期限/原本異 | SQL/password/delete前に拒否、readonly BACKUP factoryからstart/stop不能 |
| CFDB001 | actual PostgreSQL固定FAILED pair全14列・latest row照合 | FAILED/COMMAND_FAILURE/固定summary/1,0,1,0・正確handle/JST date、rollback読取・secret診断無し |
| CFDB002 | SQL null/欠落/余剰/旧attempt/別run/cutoff/値変造/成功/abandoned | 実不一致を拒否、元行変更/FAILED捏造無し、各資源close/守衛前後 |
| CFDB003 | six SKIPの実begin/commit/再読 | 各SKIPPED/BACKUP_UNAVAILABLE/all0、未実行擬似値でなく今回実row |
| CFDB004 | commit前後/rollback/期限/guard fault/再送 | 未commit rollback、commit真実をFAILEDへ書換えず、UNKNOWN/親保全 |
| CFLOW001 | 実FAILED Backup→same owner Cleanup→six SKIP→Transfer | DELETE/Inspector0、Transfer実target/success/failure/bytes、7step全列親読戻し/正規退役 |
| CFLOW002 | actual FAILED branchと成功/通常SKIPの回帰 | 成功manifest・元SUCCESS/Archive不変、残Artemis/Expiry/issuerを未実行成功としない |
| CFLOW003 | fixed Root scope/DB handoff/共通30分/正常30とUNKNOWN | 全終端→親再取得→DB/namespace→intent、別budget/No-op gate/旧receipt利用無し |
| CFLOW004 | 同Source外部Production入口とCoverage | JAR/Source/全6/4実exec byte一致、actual normal/failure/skip明示、100%未達は未認定 |

fixture：非秘密DB/Test IDsのみ。既存PG392 original/元Backup9・10/25row/4fileを保全。真正新規runで正常--freshが可能か既存Admissionで確認し、可能なら新business dateの通常入口・退避済Unit/dropinとRootM/A/全停止/INVALID/fullBOM下の専用負pgpassを用いる。既存行や成功artifactの改変で失敗を作らない。必要なら別隔離fixtureを用い、元VMへDB restore/row削除をしない。Transfer byte010203/0405の独立期待2file5byteは新規fixtureで明示する。

実環境確認：PG392の旧activeと未完了beginが保持されており、SS343 §6.15により現在は別fresh runを許可できない。旧30をSUCCESS/WARNING doneへ読み替えず、同runのBroker/Expiry/issuer/API/Web・正規原本完了を接続した後か、独立した新隔離fixtureで実FAILED分岐を採取する。新規run用fixtureにはM/A/全停止/pin署名・全BOM/current INVALID/旧全activation完了/active不存在を必須とし、旧Source/drop-inをprivate保存して通常無引数Mainだけに変更する。前提未達と判明したため、新規fixture草案は未実行のまま取り下げ、既存VM・Unit・credentialに変更0。既存operatorの新run引数は信頼PT operatorが実測済みcanonical runを明示するだけで、原本照合やpin/BOM/INVALIDを省略しない。

実行command/JDK/branch/Source/coverage/結果/BUG/証跡hashは292とmanifestへ実測後記録。TDD初期未実装は障害に加算しない。既存実装の仕様違反は修正前915/必要916・SSCへ登録。coverage除外追加無し、failed/skipped/not-runを合格へ加算しない。
