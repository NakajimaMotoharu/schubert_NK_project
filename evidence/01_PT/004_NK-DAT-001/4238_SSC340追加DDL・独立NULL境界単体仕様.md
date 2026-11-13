# NK-DAT-001 SSC340追加DDL・独立NULL境界単体仕様

対象V029、DatabaseMigrationTest/MigrationInventory。関連RD DAT001～011/AUT001～004/UI241242243、SS331/354 SSC340、BUG2846/YKT2405、WBS-P004-01.01～03。独立期待値はSS354 PT-DB-NULL340-001～015の固定表。production式からexpectedを生成しない。旧Testの19定義・goldenを維持し、新15定義とhelperだけを追加する。バージョン一覧29は承認済み設計から一つ追加し、実DB観測から生成しない。

1～4 media M/I/N/VIDEOのNULL/空/1/256/257byte、UTF-8境界と未知role。5～6失効済6reasonと未失効NULL。7～8 ERROR5code/message片NULLと非ERROR。9～10 snapshot片NULL/両NULL/29/1050000/28/1050001/不正key。11～12 ID型4種とUUID/NONE/PROCESSING/未知type、min1/max999999999999/範囲外。負例はSQLSTATE23514だけでなく対象constraint名を固定して確認する。各操作はsavepoint rollbackし、成功例も次例へrowを残さない。既FK/所有/state等は有効なfixtureを用いる。

13は版28の不正media pairを保持したupgradeの失敗と、五制約のpg_get_constraintdef/旧28履歴/row全JSONの不変・版29成功0を独立比較する。14は正常29適用/validate/再適用0、既catalog159CHECK/24table/role/index等は既19Testを保持して照合する。15はQA050未知expiry NULLをsynthetic pending rowで保持し、他対象外制約を緩めない。

実行対象はwhole DatabaseMigrationTest（19既存＋15追加）と共有版一覧利用の全影響Test。現時点DB/migration/権限/VMのHOLDでNOT_RUN。実行commandは条件成立後のMaven全関連test選択をsource固定して記録し、実終了/XML/DB後条件/coverageを採取する。今はSQL静的構造、旧28/roles hash不変、source/GJF/Checkstyle及び独立15定義の照合だけ。これを実行済みPT PASS・coverage・451正式・IT/ST合格へ加算しない。Null/例外/並行migration・grant負例は既Testと合わせ未完で追跡し、rollback実測を仮定しない。
