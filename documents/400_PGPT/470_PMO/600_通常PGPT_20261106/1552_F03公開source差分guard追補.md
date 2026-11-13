# F03公開source差分guard追補

BUG2839の2339公開inventory差分guardを是正。旧src/*/src/main/javaは既知7aed→8bのMain105変化すら0になる反例を保全し、git diff -z name-only srcの厳密MainJava判定と未追跡Main拒否へ変更。独立glob集合105一致/8metadata反例・正常/全source逆変換/ASTを確認、現8b→tracked/untrackedMainは0。従って既PG29526対象source/hashは一致するが原v1guardの検出能力は未成立だったと追補し原証拠不変更、inventory再実行0。新ModuleMainも拒否しTest/resource/tool差分だけは非該当。製品Main/Test/PT/coverage/全F03/正式受入0、actual4.class/Root2本文/実Root/VM/DB/FD/鍵操作0、元190新0/正式1964-53/工数null。原計画行の追加完了0、追加ToolFix価格.05/.15/.3だけ完了、実専有費null。

原証拠: [PG29526](../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG29526-f03-public-six-module-preparation-v1/manifest.json)。是正反例・8controls・source整合: [PG29556](../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG29556-main-delta-guard-public-metadata-v1/manifest.json)。全6module静的品質/原F03/2は未受入。
