# ScenarioFile十一列COPY batch独立14仕様

NK-MIG-001/MIG003005006/MIG-DAT004005/DAT004/FUN004、UI223/242/254、SS331/V002/343§10 SSC349、WBS-P01903.02。

SS331/V002 script_files十一列（id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at）を明示順に保持するScenarioFileCopyBatch。既ScenarioFileMigrationMapと宣言済field Listを受け、件数/target一意/全対応と先頭三列完全一致、game内storage path一意、全row共通created_atを検証する。対応表のCurrent順に並べ、入力順/target ID順へ変更しない。空map+空rowは空値だけで移行完了を示さない。

ID/display_orderは正N12、game1/2、byte_sizeはcanonical十進0..999999999999、SHA lowerhex64。文字列は非正規surrogate/NFC違反/ISO controlを拒否し勝手にtrim/正規化しない。storage/display path1..512UTF8byte、file_name1..256byte、chapter nullable/0..256byte、section nullable/0..64 Unicode codepoint（varchar64はbyte数でない）。storageだけroot-relative POSIX/空segment/dot/dotdot/backslash禁止、display/file_nameをstorageへ流用しない。timestampはUTC canonical Instant/年0001..9999/µs単位で既Entry row契約と同じ、offset/補完や独自日時を作らない。

private immutable深いList snapshot、nullableなのはsection/chapterだけ、他null拒否。毎回byte所有のCOPY textを既encoderで生成しSQL/header/terminatorを足さない。例外/文字列表示は固定redactedでpath/本文/生値を漏らさない。FileMap/encoderの元byteを変更せず、実source採取/物理hash/asset照合/DB/COPY/FK/transaction/全ETL/Root/native/Actual4/aru/HOLD解除は別未完。

PT-MIG-FCOPY001..014: 001独立三row全COPY goldenとCurrent→target非単調順、002空/件数少多、003重複target、004未知target/先頭三列各不一致、005同game path重複拒否/別game同path許容、006storage危険segment、007全text NFC/surrogate/control、008UTF8byte境界とsection codepoint境界、009SHA grammar、010byte_size canonical0/MAX/invalid/overflow、011UTC年/µs/形式と共通stamp、012null map/list/row/field/encoderと固定診断、013深いsnapshot/List/byte所有、014 finite8worker64task/Future5/finallyshutdownNow-await10。expectedはDDLとASCII/UTF8独立literal/算術、productionを呼んでexpected生成しない。

必要scopeは新Batch1+FileMap4+Copy1の全6physical、whole14+12+12=38を同source一execで通常全静的/NullAway/lintWerror/個別適用性/CRC-init/XML/四100/実Code差で検証。旧成功の確認再演・合算/qualityskip0。追加不足1.2/3.6/7.2は詳細.1/.3/.6+製造14定義.7/2.1/4.2を群.8/2.4/4.8cap5、必要normal38は別群.4/1.2/2.4cap3。原費用/SV上限/群開始額を維持、専有実費/token null。
