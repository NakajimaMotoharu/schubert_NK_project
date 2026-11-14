# 設定file・directory・初期data・migration・切戻し設計

## SSC354 音声COPY行（2026-11-14）

SS34310.1.4・SS331/V002・UI242のaudio_files十二列の宣言COPY行をbootstrap.migration.AudioFileCopyRowに具体化する。RD MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI227/242/254、WBS-P01903.02。実Current抽出/素材採取/全件数/対応ID/link/game/FK・DB/COPY SDK/全migrationは別でHOLD解除しない。非秘密synthetic metadataだけを受ける純値であり、実素材やDB/鍵/Root/FS/permitを操作しない。

列順はid,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at。id/byte_sizeはcanonical正N12 1..999999999999、game1/2、duration nullable canonical0..999999999999。必須textはNFC/正UTF8/ISO control無しでstorage/display1..512byte、file_name1..256、basename1..255、audio_role1..8byte。audio_roleにDDL未指定のenumを追加しない。storageは相対POSIXで先頭/末尾slash/backslash/空segment/dot/dotdotを拒否する。containerはnullable、空保持、varchar16 Unicode codepoint以内（byte上限へ変更しない）、他text同様NFC/正UTF8/control無し。sha256はlowerhex64、時刻はUTC canonical Instant.toString・0001..9999/µs精度・全共通transaction時刻の合意は上位batch責務。値をtrim/正規化/再採番/欠落補完しない。

constructorはNullable List/nullable要素を受け、null入力/12列以外/必須null/不正値を固定IAEで拒否。private deep list snapshotと変更不能返却、columnNames固定immutable。copyBytesはnonnull既PostgresCopyTextEncoder.encodeRowへ委譲し毎回byte別所有、nullencoder固定IAE。診断/toStringにpath/本文/生値を入れない。既codec/Scenario各Main/Testの全byte・外部値を変えない。

PT-MIG-AUDIOROW001..016: 001手書き十二列全golden、002二nullable/空container/zero duration、003id/game正N12の境界とgrammar、004storageのUTF8byte境界/危険path、005各必須text byte上下、006container Unicode codepoint0/16/17とUTF8多byte、007duration0/MAX/grammar/overflow、008size1/MAX/zero/grammar、009sha lower64の異常、010canonical時刻年/µs/offset/不正形式、011全textのNFC/Unicode/control、012null入力/列長/必須要素/encoder・固定例外、013入力/返却Listとbyte所有、014SQL風literalもCOPY dataで独立escape、015finite8worker64task/Future5/finallyshutdownNow-await10、016redactionと拒否後独立正常。expectedはDDL/手書きASCII・UTF8 literalと算術、Production/Current generatorによるexpected生成0。

新Row1＋必要codec1の全2Main/2physical、新16＋支援codec12=whole28を同source/一exec・Root通常静的/NullAway/lintWerror・独立CRC-init/XML/四100/実Code一致で確認。旧成功12の確認再演でなく新接続に必要なscope。追加不足1.25/3.75/7.5未較正を、詳細+PG16 .85/2.55/5.1cap6、必要normal28 .4/1.2/2.4cap3に分離、元費用/SV上限保持・専有費/実token null。全Root/native/Actual4/aru/実DB/全ETL/CHR/global451/ITST/HOLDを閉じない。


## SSC353 Scenario二表転記（2026-11-14）

SS34310.1.4の二temporary stagingから初期target二表へ、既ScenarioStagingTablesにtransfer(Connection,int expectedFiles,int expectedEntries)を追加する。callerは既認証migration actor/排他単一Connection・同一transaction/実COPYが当宣言datasetと一致/他全table・参照・NFC型・asset等の前検査を保証する。expected件数は独立manifestの非負int、file0でentry正は拒否。部品は借用ConnectionのautoCommit=falseを必須とし、新しい接続/URL/driver/権限/commit/rollback/closeを行わない。既prepareの二SQL/診断/APIはbyte不変。PG SDK実行/実DB操作HOLDを解除しない。

一Statementを所有し30秒queryTimeout。固定順にtarget schubert.script_files count0、script_entries count0、staging pg_temp.nk_mig_script_files count=expectedFiles、nk_mig_script_entries count=expectedEntriesを確認。その後固定列のINSERT INTO schubert.script_files(11列) SELECT 同11列 FROM pg_temp.nk_mig_script_files ORDER BY game_id,display_order、続いてscript_entries(12列/generated body_search除外) SELECT 同12列 FROM pg_temp.nk_mig_script_entries ORDER BY display_orderを実行。各update countは宣言件数と一致必須。最後に両target countが宣言件数と一致することを確認する。schema/table/列は定数のみ、入力からSQLを生成しない。IF NOT EXISTS/DROP/DELETE/再実行/修復/業務Consumer登録を追加しない。既存target行、件数違い、途中失敗、close異常は成功にしない。callerがtransaction全rollback/discardを行う。

scalar取得はnonnull ResultSet、一行存在/getLong(1)/wasNull=false/宣言countと完全一致/次row無しを必須とする。ResultSet毎にtry-with-resourcesで終了し、単一Statementも全success/SQL/Runtime/Error経路で終了。null Connectionは既固定input IAE、負件数/不可能件数は固定input IAE、null Statement/ResultSet/不正結果は既固定SQL診断。元SQL障害/主障害とclose障害のJava抑制関係を保持する。SQLや生値をloggerへ渡さずtoString固定redacted。targetのFK/CK/UK・identitysequence最終化/他master/ANALYZE/全migration/実DBの正しさは別条件であり、当二表のcount成功から推定しない。

新PT-MIG-TRANSFER001..020: 全SQLと八操作順の独立literal/正常count、空宣言とintMAX値、null/負/entryのみ/autoCommit拒否、null Statement、六scalar各位置のmissing/null/mismatch/extra/nullResult/executeQuery SQL/getLong SQL/next SQL/close SQL、主SQL+close抑制、二insert各非一致と元SQL失敗、ownedStatement終了/借用Connection非変更、失敗後別正常入力、fixedredaction、finite8worker64task/Future5/finallyshutdownNow-await10。全てJDK JDBC Proxyのメモリだけでdriver/DB/file/socket/Root/native/aru操作0。旧STAGE001..018の全assertionは変えず、必要whole38/1Main/1physicalを同source通常Root静的/NullAway/lintWerror/一exec/独立CRC-init/XML/四100/実Codeと照合する。元成功18の確認目的再演ではなく、この同class横断変更の必要回帰である。

追加不足1.15/3.45/6.9未較正を、詳細+PG新20 .8/2.4/4.8cap5、必要normal38 .35/1.05/2.1cap3に分離する。元費用/SV上限保持、専有費・実token null。実DB/COPY SDK/全ETL/Rootnative/CHR/global451/ITST/全HOLDは未受入。


## SSC352 Scenario一時表準備（2026-11-14）

SS343 §10.1.4のCOPY前提となる二つのpg_temp staging表を、ScenarioStagingTablesが既に認証された借用Connection上に準備する。標準java.sqlだけを用い、PostgreSQL vendor SDKを必要としない。接続作成/URL/秘密/認証/権限変更や実DB試験の許可を意味しない。接続所有者は単一利用・期限/取消・正規migration actor・空target・原本保全・全transaction rollback/discardを保証する。本部品はautoCommit=falseを必須とし、setAutoCommit/commit/rollback/Connection.closeを呼ばない。

固定二SQLだけを順に実行する。CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM schubert.script_files WITH NO DATA。次にCREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM schubert.script_entries WITH NO DATA。PostgreSQLのtemporary relation解決でpg_tempに配置し、qualified sourceだけを参照、generated body_search/identity/default/index/constraint/行は複製しない。型はsource DDLに追随する。FK/CK/NFC/件数・全asset照合/空targetへのinsertは後続必須であり、この二DDLだけでは成功保証しない。

IF NOT EXISTS/既存表再利用/DROP/再試行/修復を行わず、表名衝突等は元SQLExceptionで停止する。単一Statementを自分で作成し30秒queryTimeoutを設定、各executeUpdateの結果が0以外なら固定SQLExceptionで停止する。null Connectionは固定IllegalArgumentException、autoCommit=true・null Statementは固定SQLException。Statementは成功/SQL/Runtime/Error全経路でtry-with-resources終了し、close失敗で成功にしない。主障害/close障害の抑制関係はJavaの規定どおり保持、exceptionやSQL引数をloggingしない。toStringは固定redacted。

PT-MIG-STAGE001..018: 001独立二SQL全literal/列順/二回0、002timeout先行/Statement終了一回/借用Connection非所有、003null入力、004autoCommit拒否、005autoCommit元SQL障害、006create元SQL障害、007null vendor Statement、008timeout失敗時close、009第一DDL失敗/第二未実行、010第二DDL失敗、011第一DDL非zero(-1/1)、012第二非zero(-1/1)、013close失敗非成功、014主SQLとclose SQL抑制、015RuntimeとErrorの元例外/close、016再呼出は新Statement/元SQL不変・conn非変更、017finite8worker64task/Future5/finallyshutdownNow-await10、018固定redaction/失敗後別独立入力の正常性。fixtureはJava Proxyのjava.sql.Connection/Statementだけ、ネットワーク/driver/DB/FS/Root/鍵/permit/native/aru操作0。

必要closureは独立1Main/1physical/whole18だけ。新18定義、Root通常静的/NullAway/lintWerror/同一source・単一exec・独立CRC/init/XML/四counter100/実Code一致を要求する。元成功113の確認再演0、SDK禁止条件を変更しない。追加不足.8/2.4/4.8未較正を、詳細+PG18 .55/1.65/3.3cap4と必要normal18 .25/.75/1.5cap2へ分離。元費用/SV上限保持、専有費・実token null。実DB/ETL/全451/Rootnative/Actual4/HOLD未受入。


## SSC351 COPY行streamとdataset内部接続（2026-11-14）

既PostgresCopyTextEncoder.encodeRowsは全行を単一StringBuilder/byte[]へ組み立てる。実ETLへのCOPY transportは全streamの追加bufferを避けるため、新PostgresCopyTextWriterで宣言済Iterableを一回だけ進め、各rowをsnapshot→同一非zero列数検査→既encodeRow→借用OutputStream.write(byte[])の順に送る。次rowを取得する前に現在rowを送信する。heap追加量は最大encoded一行に比例し、巨大raw_block一行自体の上限を追加せず実測は後続に残す。既byte-array API/既Main encoder全byte/escape/nullable/NFC責務を変更しない。

writerはnonnull既final encoderだけを保持、null encoder/Iterable/sink/row・空row/列数不一致は固定IllegalArgumentException。元codecのNUL/surrogate不正は元の固定例外を伝播する。IOException/iterator故障を成功へ変換せず元exceptionのまま伝播し、失敗後に次rowを取得しない。送信済prefixは残り得るので原子的保存/DB commitを意味しない。sinkはcaller所有、成功/失敗ともflush/closeを呼ばず保持しない。実DB/FD/file/Root/permit/サービスを開かない。toStringは固定REDACTED。

ScenarioCopyDatasetへwriteFiles(writer,sink)/writeEntries(writer,sink)を互換追加する。旧constructor/getter/byte-array methodsは不変。fileは既immutable rowsを渡し、entryは既Row.fieldsの参照List（O(行数)参照、本文複製なし）を渡す。null writerは既dataset固定診断、null sinkはwriter固定診断、元I/O故障を伝播する。二方法は共通FK/時刻検査済みのdatasetだけを使い、上流の1transaction/権限/全量/実source/asset受入を代用しない。

PT-MIG-STREAM001..012: 001手書き二row escape/NULL/UTF8全byte、002空Iterable・sink無操作、003一回iterator/次row取得前の送信、004null encoder、005null Iterable/sinkをiterator前に拒否、006null/空row、007mixed widthと送信済prefix、008元NUL/surrogate例外とprefix、009sink IOException同一instance/次row未取得・closeflush0、010iterator故障同一instance/既prefix、011input/sink所有・redactionと独立呼出、012finite8worker64task/Future5/finallyshutdownNow-await10の独立golden。新Dataset PT-MIG-DATASET013..015は二stream golden、null writer/sink、両経路の元sink障害/再呼出不変。

必要closureは新Writer1＋既Dataset接続変更と支援全8Main=9Main17physical、Writer12＋Dataset追加3＋元98=whole113。新定義15だけ、同source/一exec/Root通常静的・NullAway/lintWerror/CRC-init/XML/四100/実Code差を照合し、旧成功の確認再演・別source合算0。追加不足1.1/3.3/6.6（未較正）=詳細.1/.3/.6+製造15定義.55/1.65/3.3を群.65/1.95/3.9cap4、必要normal113別群.45/1.35/2.7cap3。元費用/群開始額/SV上限保持、実token/専有費null。小literal/メモリsinkだけ、実DB/全量/原本/Backup/Rootnative/Actual4/aru/拒否対象HOLDを解除しない。


## SSC350 Scenario二COPY dataset内部接続（2026-11-14）

既に別々に検証済みのScenarioFileCopyBatchとScenarioEntryCopyBatchを、同じ宣言済datasetとして接続する内部ScenarioCopyDataset。nonnull二batchを受け、全Entryの(game_id,script_file_id)が今回File batchの(id,game_id)へ一致することを検証する。他のFileMapを使ってEntryBatch単独だけが成立していても今回File batchに不在なら拒否する。全file/entryのcreated_atは同一canonical UTC値（両batchで検証済）を要求する。DBの一transactionで一回採取した値を共用する契約を具体化し、時刻/IDを生成・補完しない。

files/entries両方空、fileだけありentry空は値として許容するが、必要全量262/99661等の成功ではない。entryだけありfile空、game違い、未知file、二batch間時刻違いは固定IllegalArgumentExceptionで拒否する。既二batchは不変なのでその参照を保持し、公開getterもimmutable値だけ。fileCopyBytes/entryCopyBytesはnonnull既encoderで対応する各batchへ委譲し毎回別所有byte、SQL/header/terminator追加0、途中でDB/file/serviceを操作しない。nullは固定非秘密診断、toStringは固定REDACTED。本文/path/ID等をdiagnosticへ混ぜない。

PT-MIG-DATASET001..012: 001独立二COPY stream全byte、002両空、003fileのみ、004entryのみ/未知file、005同id別game、006全file/entry共通stamp違い、007null二batch、008null encoder二経路、009immutable二batch入力aliasからの独立、010毎回byte所有/呼出順独立、011redactionと拒否後正常値の独立、012finite8worker64task/Future5/finallyshutdownNow-await10。oracleは手書きliteral/DDLの複合FK/一transaction条件、Productionによるexpected生成0。

必要closureは新Dataset1+FileBatch1+EntryBatch1+FileMap4+EntryMap3+Placement4+EntryRow1+Copy1=全16physical/8Main。新12+既FileBatch14+既6suite各12=whole98、同source/一exec/通常Root静的/CRC-init/四100/実Code差を記録。旧成功の確認再演や別source合算をせず、この新しい二batch接続に必要なscopeとして実施する。実Current/全件数/物理asset/hash/speakerFK/DB/COPY/transaction実行/Root/native/Actual4/aru/CHR/global451/ITSTは未完でHOLD解除しない。

追加不足.9/2.7/5.4（未較正）=内部詳細.05/.15/.3+製造12定義.4/1.2/2.4を一群.45/1.35/2.7cap3、必要normal98別群.45/1.35/2.7cap3。前FileBatchの旧費用/開始額/元SV上限保持、再確認や新12の繰返し加算0、専有実費/token null。端末空き約5.6GiBで小source/固定小fixtureだけを作る。大容量実masterやVM/DB作業は行わず、既容量条件を満たす別工程へ送る。


## SSC349 ScenarioFile十一列COPY batch（2026-11-14、PG内部詳細）

SS331/V002 script_files十一列（id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at）を明示順に保持するScenarioFileCopyBatch。既ScenarioFileMigrationMapと宣言済field Listを受け、件数/target一意/全対応と先頭三列完全一致、game内storage path一意、全row共通created_atを検証する。対応表のCurrent順に並べ、入力順/target ID順へ変更しない。空map+空rowは空値だけで移行完了を示さない。

ID/display_orderは正N12、game1/2、byte_sizeはcanonical十進0..999999999999、SHA lowerhex64。文字列は非正規surrogate/NFC違反/ISO controlを拒否し勝手にtrim/正規化しない。storage/display path1..512UTF8byte、file_name1..256byte、chapter nullable/0..256byte、section nullable/0..64 Unicode codepoint（varchar64はbyte数でない）。storageだけroot-relative POSIX/空segment/dot/dotdot/backslash禁止、display/file_nameをstorageへ流用しない。timestampはUTC canonical Instant/年0001..9999/µs単位で既Entry row契約と同じ、offset/補完や独自日時を作らない。

private immutable深いList snapshot、nullableなのはsection/chapterだけ、他null拒否。毎回byte所有のCOPY textを既encoderで生成しSQL/header/terminatorを足さない。例外/文字列表示は固定redactedでpath/本文/生値を漏らさない。FileMap/encoderの元byteを変更せず、実source採取/物理hash/asset照合/DB/COPY/FK/transaction/全ETL/Root/native/Actual4/aru/HOLD解除は別未完。

PT-MIG-FCOPY001..014: 001独立三row全COPY goldenとCurrent→target非単調順、002空/件数少多、003重複target、004未知target/先頭三列各不一致、005同game path重複拒否/別game同path許容、006storage危険segment、007全text NFC/surrogate/control、008UTF8byte境界とsection codepoint境界、009SHA grammar、010byte_size canonical0/MAX/invalid/overflow、011UTC年/µs/形式と共通stamp、012null map/list/row/field/encoderと固定診断、013深いsnapshot/List/byte所有、014 finite8worker64task/Future5/finallyshutdownNow-await10。expectedはDDLとASCII/UTF8独立literal/算術、productionを呼んでexpected生成しない。

必要scopeは新Batch1+FileMap4+Copy1の全6physical、whole14+12+12=38を同source一execで通常全静的/NullAway/lintWerror/個別適用性/CRC-init/XML/四100/実Code差で検証。旧成功の確認再演・合算/qualityskip0。追加不足1.2/3.6/7.2は詳細.1/.3/.6+製造14定義.7/2.1/4.2を群.8/2.4/4.8cap5、必要normal38は別群.4/1.2/2.4cap3。原費用/SV上限/群開始額を維持、専有実費/token null。


## SSC348 Scenario Entry対応表とCOPY row batchの結合検証（2026-11-14、PG詳細補足）

SS34310.1.4、SS331/V002・UI223/242/254のID対応・表示順・型/参照条件を、内部ScenarioEntryCopyBatchで具体化する。既PlacementMapとScenarioEntryCopyRowを受け、List件数一致・target entry ID一意・対応表全targetに一rowを要求する。row先頭五列id/game/file/display_order/entry_indexを対応表と完全一致で検証し、未知/欠落/余剰を補完しない。複数rowのcreated_atはcallerが一回採取した同一canonical UTCを要求し、空は空batch値として許容するが全移行完了を示さない。

保存/送信順はtarget ID大小や入力順でなく対応表のglobal Current表示順。文字列/本文をtrim/正規化/再採番しない。private immutable Listを保持し、copyBytesは既COPY encoderへ全row fieldを同順で渡す。header/SQL/terminatorを追加せず毎回byte別所有、固定redaction/安全診断/null契約でbody等を出力しない。実Current抽出・全件数/データ適合性/speaker-FK/DB/pg_temp/COPY/transaction/権限・実業務表示は別条件として残す。

PT-MIG-BATCH001..012は固定三row全byte/global order、件数/空/重複/未知、game/file/order/index各不一致、共通時刻、入力/List/byte所有、null/固定診断、finite8worker64task/Future5/finallyshutdownNow-await10を独立literalで確認する。新Batch1と既Row1/Copy1/Placement4/Entry3/File4の全14physicalを同source必要whole72単一execで静的/CRC-init/四counter/実JVMCodeと独立postへ対応。新定義12のみ、旧成功の合算/coverage除外/品質規則抑制なし。実ETL/Root/native/CHR/全451/ITST受入は別で、haruka権限等の既HOLDを解除しない。


## SSC347 script_entries十二列COPY行の型・nullable・文字検証（2026-11-14、PG詳細補足）

SS343§10.1.4、SS331§2/V002、UI223/242§4.4/254の既条件をScenarioEntryCopyRowへ具体化する。入力Listは12列の送信文字列で、id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_atの順に固定し、generated body_searchを除く。新DDL/外部ID/本文変換を追加せず、実Current抽出・全件数/ID対応/FK/DB/pg_temp/transaction/driver/COPYの成功は別条件である。

outer/List列数12とmandatory9列のnonnullを先に検査し、optionalはline_number/speaker_id/speaker_labelだけ。target entry/file/order/speakerのnonnull値はcanonical positive N12 decimal、game1/2、entry_indexはcanonical0..IntegerMAX、nonnull line_numberは1..IntegerMAX。内部送信用canonicalなのでsign/leadingzero/空白/小数を拒否し、黙ってtrim/変換しない。typeはdialogue/narration閉集合、dialogueはspeaker必須、narrationはspeaker null。

bodyはNFC/strictUTF8・1..4096byte、nullable labelはNFC/strictUTF8・0..128byte、raw_blockはnonnull NFC/strictUTF8で既DDLにないbyte上限を加えない。ISO controlはinline labelでは不可、multiline body/rawでは既Current本文の改行を保持するTAB/LF/CRだけ許可し、NUL/その他control/孤立surrogateは拒否。NFCへの暗黙正規化はしない。実Currentdataに適合すると推定せず、実data不一致は所定feedback/障害管理で扱う。

created_atはcallerがtransaction共通Instantから作ったcanonical UTC文字列（Instant.toStringとの完全一致）、年0001..9999/µs精度とし、parse不能/offset表記/非canonicalfraction/nsを固定安全例外で拒否する。rows間の共通Instant採取や実PostgreSQL受理をこの値classで証明しない。

入力をprivate copy/変更不能wrapperとして保持し、fieldsとcolumnNamesは変更不可、copyBytesはnonnull既PostgresCopyTextEncoderへ渡すだけでbyte別所有。body/raw等を診断へ含めず、固定redaction/安全例外を用い、NPEをcatchして正常扱いしない。PT-MIG-ROW001..012は独立12列/COPY全byte、dialogue/narration/nullable、N12/game/int/role、body/labelのASCII・日本語byte境界/非制限raw、NFC/Unicode/control、必須null/列数、時刻境界、入力/返却所有、固定診断とfinite8worker64taskを検証する（Future各5秒/finallyshutdownNow-await10、非終端fail）。expectedはProduction methodではなく既DDL/手書きliteral/byte算術から作る。

新Row1と支援Copy1の全2physicalを同sourceのwhole24（新Row12＋既Copy12）単一execで初検証し、旧exec合算/coverage除外/規則抑制なし。旧Copy12を新定義へ二重加算せず、新Row-to-encoder変更群に必要な閉scopeの静的/CRC-init/四counterと実JVMCodeを独立postで照合する。実DB/Current/RootVM/native/CHR/全451/ITST未完、aru新規利用禁止とharuka構築/個別条件待ちを局所成功で解除しない。


## SSC346 移行COPY text送信fieldの純byte encoding（2026-11-14、PG詳細補足）

SS343§10.1.4のCOPYとSS331§2のUTF8型を、bootstrapのPostgresCopyTextEncoderへ具体化する。既存inventory/ID/file/entry対応部品とは別の送信用data変換で、DB/driver/SQL/FSの操作を持たない。[PostgreSQL18 COPY Text Format](https://www.postgresql.org/docs/18/sql-copy.html)のdefault text/TAB/NULL backslash-Nを固定する。Current generator copy_value/copy_rowは参照codeのみ、master/DBやそのgeneratorの実行をoracleにしない。RD/UI/DDL/電文/業務値を変更せず、新QA不要。

encodeRowはnullable String fieldを持つnonnull List、encodeRowsはそのnonnull rowのnonnull Listを受ける。null outer/rowは拒否、null fieldはNULL値として許容。rowは一列以上、複数rowの列数を一致させ、空outerはzero bytesとして返す（移行完了ではない）。各入力をprivate snapshotにし、保存可変state/入力の外部保持なし、返却byte[]は毎回別所有、診断は固定redaction。

UTF8 dataは列間TAB/行末LF、header/SQL/終端なし。nullはraw `\N`、空文字は空field、literal `\N`はbackslashを二重化して区別。backslash/TAB/LF/CR/BS/FF/VTはCOPYの標準escapeへ、literal backslash-periodも二重backslashとしてfield内に保つ。NUL/孤立surrogateを固定安全例外で拒否、正しいsurrogate pairをUTF8化する。trim/数値変換/NFC正規化やcolumn別control/byte/DDL型/FK検証はしない。既callerの業務検証/実ロード/全件数/権限/transaction成功を代用しない。

PT-MIG-COPY001..012は手書き二row、NULL/空/literal backslash-N、七escape、ASCII quote/ordinary文字、あ/é/音符の固定UTF8 hexと非NFC列保持、literal backslash-periodとSQL風文字列、null/欠落/empty/ragged row、NUL/孤立high/low/正pair、入力/返却byte不変、安全診断、数値風文字、有限8worker64task（各Future5秒・finallyshutdownNow/await10秒・非終端fail）を検証する。expectedは独立hex/ASCII literalで、Production encoder/Current generatorから作らない。全1physicalを通常static/固定Git whole12/独立CRC初期化/単一exec/全四counterで照合し、除外/抑制/旧exec合算0。実PostgreSQL解釈/driver/COPY/pg_temp/DB/全移行/Current/RootVMnative/CHR/全451/ITSTの未完を当局所結果で閉じない。


## SSC345 Scenario entry所属file・entry_indexと移行対応の接続（2026-11-14、PG詳細補足）

SS343§10、SS331/V002/V004・UI223§3.2/4/5・UI254の既存ID/表示順/FK条件を内部ScenarioEntryPlacementMapで接続する。SSC343のglobal entry順とSSC344のfile/game順を再実装せず二mapを再利用する。RD/UI/DDL/電文を変更せず、新QA不要。実Currentからのgame/entry_index抽出の正しさ、実DB件数/FK/ロード/権限は別条件である。

入力はScenarioFileMigrationMap、ScenarioEntryMigrationMap及びPlacement(gameId,currentFileId,currentEntryId,entryIndex)のList。gameは解決済NK1/2、source両IDはsigned値を保持、entryIndexは既DDL通り0..IntegerMAX。null両map/List/要素を拒否、List件数はEntry対応件数と完全一致、各source entryは一回だけ、既知file/game及びentryだけを許容する。targetFileIdとentryIndexの組も一意で、別fileの同indexは許容する。未知を新ID/0/先頭へ補完しない。空Entryと空Placementは値として許容するが、必要全量の移行成功ではない。

PlacedEntryはcurrentEntryId,targetEntryId,displayOrder,gameId,targetFileId,entryIndex。target entry/file/order各1..999999999999、game1/2、index>=0をconstructorで検査する。global entriesはEntry対応displayOrder昇順、lookupはcurrentEntryIdだけ、entriesForFile(game,sourceFile)は既知fileの行をentryIndex昇順で返す。既知の空fileは空List、未知fileは固定安全例外で拒否し空と混同しない。List/Mapを明示不変copy、byte[]は毎回別所有。公開record/aggregate診断は固定redaction、内部FilePositionは公開/診断/ログへ出さない。

canonical ASCII/LFはheader NKMIGENTRYPLACEMENT1 LFに続きcurrentEntryId TAB targetEntryId TAB displayOrder TAB gameId TAB targetFileId TAB entryIndex LF、global表示順、正準signed/非負decimal、BOM/escape/余剰列なし。realCurrent/DB・game/FK/全99661entry・body/speaker/audio/ロード/Goの証拠へ読み替えない。

PT-MIG-PLACE001..012は手書きentry2→900/order1/game1/file500/index7、10→100/order2/game1/file800/index3、30→50/order3/game2/file600/index0の全byte、同file index0/MAXによるglobal順との逆転、未知file/entry・game、source/targetfile-index重複、件数不足/余剰、空/既知空file、game/index/N12各境界/null、immutable入力/List/byte、signed両端/再順序、所有8worker64task（Future各5秒・finallyshutdownNow/await10秒、非終端fail）を独立literalで確認する。新4physicalと旧Entry3/File4の完全sourceを含め、新component/支援部品・未網羅counterを区別し旧exec/旧成功を合算しない。全451/実ETL/RootVM/native/CHR/ITST未完は局所成功で閉じない。


## SSC344 Scenario fileのゲーム内順と全体前後対応（2026-11-14、PG詳細補足）

UI223§3.2/4/5・UI254§4、SS331/V002/V004、SS343§10のfile ID対応・表示順を純metadata部品`ScenarioFileMigrationMap`へ具体化する。Entryのglobal順を扱うSSC343とは別範囲で、file内entry_index、Route prefix、speaker候補、audio link、動画/music、全DB/game/FK検証を代用しない。既存gamesのid/display_orderはV004通り1/1・2/2、file target IDとdisplay_orderは既N12を維持する。RD/UI/DDL/電文の変更や新DIFはない。

FilePairはgameId/currentFileId/targetFileId。gameIdはNK固定game1/2へ解決済みの値とし、実Current game対応の正しさはETL側の独立条件。source keyはgameIdとsigned currentFileIdの組、同game同sourceは拒否し別game同sourceは混合しない。targetは全gameを通じて1..999999999999で一意。game数値順→各game内currentFileIdの数値昇順を固定し、各gameで1始まりdense displayOrderを付与する。target再採番大小・入力List順を表示順へ使用しない。MappedFileもgameとtarget/order各N12をconstructorで検査する。List件数intに対するdense順位はN12内で、到達不能な余剰branchは追加しない。

保存List/位置Mapを明示copyして不変化し、null入力/要素・重複・不正範囲を拒否する。lookup(game,source)は当tupleだけ、unknownや不正gameを先頭/0へ補完しない。previous/nextは全保存順（games.display_order→files.display_order）で隣を返し、game1の最後とgame2の最初も接続する。最初/最後だけOptional.empty、未知sourceを端と混同しない。返値は宣言ID/順位であり、実DB存在・全file件数・game/FK・ロード成功・権限の証明ではない。

canonical ASCII/LFはheader `NKMIGFILEORDER1`の後にgameId TAB currentFileId TAB targetFileId TAB displayOrder LF。数値正準decimal、source signedを保持、game/source数値順でBOM/escape/余剰列なし。返却byte[]は毎回別所有、record/aggregate診断は固定redaction。空mapはheaderのみ、lookup/navigationは未知拒否で、移行完了を意味しない。

PT-MIG-FILEORDER001..012はgame1(2→900/order1,10→100/order2)・game2(1→50/order1)の手書き全byte、signed source両端/0・game別同source、source/target重複、game1/2・N12上下境界/null、不変入力/List/byte、既存/未知lookup、game内及び跨ぎ前後/両端、空/gap/入力再順序、所有8worker64taskを独立literalで検証する。Future各5秒・finallyshutdownNow/await10秒で未終端fail。Main/FilePair/MappedFile/privateSourceKey全4physicalの通常static/PT/CRC初期化/全四counterと独立postを確認し、actualMaster/DB/ETL/Root/native/CHR/全451/ITST未完は当局所結果で閉じない。


## SSC343 Scenario entry移行ID対応と現行ID順の不変値（2026-11-14、PG詳細補足）

SS343§10のID対応/表示順固定を、UI223§3.2・UI254§4・SS331/V002の既存条件のまま内部部品`ScenarioEntryMigrationMap`へ具体化する。対象はglobal `script_entries`だけで、file別entry_index、games/script_files/speaker/audio/link、動画/musicのcategory/pair/順序を代用しない。現行ID維持やbookmark互換を追加しない。Actual ETL/全件数/DB・game/FK・表示結果の受入は別に残す。

入力IdPairはcurrentId/targetIdのlong二値。currentIdは採取済みのsigned値を改変/再解釈せず保持し、targetIdはV002 identity/CHECKとEntryId/wireの1..999999999999だけを許容する。currentIdとtargetIdはそれぞれ重複拒否。sourceの数値昇順（減算比較や文字列順ではない）へ並べ、1始まりdenseのdisplayOrderを一度固定する。再採番したtargetの大小・入力List順は表示順へ影響させない。Java Listのint件数に対する1始まり順位はN12以内であり、不要な到達不能branchで検査を増やさない。公開MappedEntryもtarget/order各1..N12をconstructorで保護する。

入力List/要素のnullは拒否、保存List/MapはList.copyOf/Map.copyOf等で不変性を明示する。mappings返却Listは変更不能、返却canonical byte[]は毎回別所有。lookup(currentId)は当mapに登録したtupleだけを返し、未知を0/先頭/新IDへ補完せず固定安全例外で拒否する。返値はID/順位の宣言データであり、実DB存在/完全性/ロード成功/起動・配備権限ではない。

canonicalはASCII/LFのheader `NKMIGSCENARIOORDER1`一行に続き、currentId TAB targetId TAB displayOrder LFの三列、currentId数値昇順。longの正準decimal（sourceはsigned可）を使用しBOM/escape/余剰列なし。空mapはheaderのみでlookup拒否、必要移行件数を満たすとはみなさない。record/aggregate診断は固定redactionとし原本DB/本文/credentialをログへ含めない。

PT-MIG-ORDER001..012は(10→100,2→900)からの手書き2/900/1・10/100/2、signed source両端/0とN12 target/order上下境界、source/target個別重複/null、immutable入力/返値/byte、未知lookup、空、gapと再順序、有限64task/8workerを独立literalで検証する。Future各5秒・finally shutdownNow/await10秒で未終端fail。Production sort/encoderからexpectedを作らない。全Main/Testの通常static/PT/全physical四counterと独立postを行い、実Current/DB/ETL/Root/native/CHR/全451/ITSTや全scope同source資格を当局所結果で閉じない。RD/UI/外部電文/DDL/画面の仕様は変更せず、新QA不要。


## SSC342 移行素材inventoryの純metadata値・canonical差分（2026-11-14、PG内詳細補足）

P01903/SS343§10のcanonical manifestの内部単位を次で固定する。RD141/161・UI254の移行対象、全file件数/byte/SHA、表示順/ID対応、非移行log/account、現行原本保全、移行/切戻し判定は変更しない。これは未実装artifactの詳細化で、新しい業務仕様・操作権限・DIFを追加しない。

`AssetMigrationManifest`は既に採取した非秘密metadataの不変値だけを扱うbootstrap moduleの内部部品とし、file/DB/原本/鍵/Unit/権限・移行処理を操作しない。Entryはkind（SCENARIO/AUDIO/VIDEO/MUSIC）、currentPath、targetPath、byteLength、sha256。二pathはNFCのroot-relative POSIX表記、空/先頭slash/backslash/空segment/`.`/`..`/NUL・ISO制御・未対応surrogateを拒否する。ここでsymlink/実inode/許可root/実SHAを検証済みとはしない。それらの実読取と移行ID/category/pair/display_order/DB参照は後続ETLの独立条件として残す。CurrentPath/targetPathは一つの物理fileにつき各一意、byteLengthは非負long、SHAはlowerhex64。これは列挙済みfileの全体manifestであり、同一素材を参照する複数DB行やlinkをEntryへ重複挿入しない。

canonical UTF8/LFはheader `NKMIGASSET1`一行の後、currentPathのString自然順で、kind・currentPath・targetPath・byteLength正準decimal・sha256の五列をtabで区切り各行LFで終える。BOM/引用/escapeは出力しない。pathのtab/LF/CRは禁止済みで曖昧な列を作らない。入力Listと返却List/byte[]の所有を分離し、不変snapshotを保持する。空manifestは空inventory値として表現可だが、§10の本番件数基準を満たす証明ではない。総byteはchecked加算しlong overflowを拒否、原本の公表基準59,627file/19,240,707,190byteを実測又はこの部品の都合で変更しない。

Observationは既採取のtargetPath/byteLength/sha256という同じ構文の宣言値。`compareClaims`はtargetPathの重複を拒否し、欠落file数・余剰file数・byte不一致数・SHA不一致数と観測file/byteを返す。長さとSHAが共に異なる場合は各不一致へ一件ずつ計上する。値・null・要素の契約をconstructor/factoryで確定し、返値のmetadataMatchesは宣言値間の一致だけ。実filehash、symlink不存在、DB整合、移行完了、起動/配備許可、Go/rollback合格と読み替えない。不一致のrawpath/provider textを例外へ埋めない。

PT-MIG-ASSET001..012は固定synthetic二file（`abc`と空byteの既知SHA）による独立全byte golden、NFC/相対path/invalidscalar/null・重複、非負long/overflow、順序/alias/返却byte独立、完全一致/欠落/余剰/長さ・SHAの個別/同時不一致を検証する。sourceでexpectedを作らず、固定literalと算術を用いる。原master実体・DBdump/credentialをfixtureにしない。実採取/ETL/ID・表示順/transaction/COPY/途中失敗・再実行/実root・原本/DB/CHR/全451/ITSTは未完の別条件であり、当部品の通常PTだけで閉じない。


SSC327（2026-10-21）：WebNativeRuntimeの内部I/O portはRuntime組立時・最初の取得前にnonnullで確立する。default path bindingは既asset/transfer config二keyと固定/run/schubert-nk/webのみ、default port bindingは既HTTP/management二keyのみ、default directoryはLinuxDirectoryCalls.create、default検証は既StorageAttributeGuardと同一の保持root/StorageIdentityを使う。startはbroker→dependency→codecs→directories→transfer/verify→assets/verify→workers→HTTP/mappings→management/start/promoteの元順序と即時field captureを保つ。検証用Map.Entryの一時値はfieldへowner捕捉後にだけ作り、検証callback自体は取得前に準備済みとする。検証false/nullは固定IOExceptionで不成功、その他nullは境界拒否しNPEを正常化しない。Production既5引数からのみ固定native bindingを選び、実根拠不明Root/VM/current/cohort/permit/intentのHOLDを解除しない。volatile/ownerLock/逆順十phase・元deadline/UNKNOWN/borrowed DB/credentialsの寿命は変更しない。package内部fixtureによる別path/ephemeral port/自己所有検証は実Root許可/配備/署名/認証の証明ではなく、外部からのoverride機能ではない。

SSC326（2026-10-21、BUG1581/YKT1320）：MorningStartupLaunchOwnerの完了UNKNOWN後に呼ぶCompletionProgress.failureは、nonnull主障害の固定IO/FATAL/RUNTIME分類を維持し、emit内の時計/sink/文字列生成のRuntimeException/Errorを封じて元completion catchのretainへ戻す。診断不能は成功通知/正常解放ではない。通常phase通知・constructor/null境界は既どおり失敗を伝播し、固定literal/phase/elapsed計算/retirement順序/親30分/元Unit期限/DB/権限を変更しない。当局所診断保護で実親保持/真正DONE/nativeを証明せず、元依存と実環境HOLDを維持する。

## SSC318 keeper二次失敗の扱い

native policy getterの取得前呼出によりretainer/fixed observer/fallbackのclass初期化を完了させる。tick故障時はfixed monotonic1000ms fallbackを用い、外部flag・別Root・permit発行で切替えない。IRQ/早期parkとfallback故障もUNKNOWNのまま扱い、後者のVM/CPUリスクを正常性の保証に読み替えない。

SS342のUNKNOWN保持内で診断/tickが失敗しても外側資源/失敗frameを保持し、normal終了/再close/新Root/復旧権限を発行しない。fixed observerは取得前に準備し、外部設定で切替えない。raw例外・credentialは出力せず、JVM/OS終了時には既cold-boot隔離/再認証契約を維持する。自己所有childの有限観測を実native/Rootの解放・正常終了と扱わない。BUG1563/YKT1320/SS354。

## SSC316 native解放失敗時の借用資源保持（S3b）

SS321342SSC316の明示native retentionは、既credential/password supplier・DB・原本root/Backupを先に解放する理由にしない。未確認closeの同catch frameを保有し、新しいclose/復旧/permit/Root操作は発行しない。保持の指定はordinary native組立内の固定値だけ、外部設定/環境変数/role/権限/署名/期限を変更しない。固定診断のみで原例外message/stack/鍵/password/session/tokenを出力しない。既ownedReleaseのportは取得前に準備し、未取得の推定closeはしない。legacy componentのTWR/例外順位は維持する。実native後条件は別gateであり、host自己所有fixtureの143終了や静的確認を代用しない。BUG1547/1556/YKT1307、SS354。

SSC311（2026-10-20、BUG1537/YKT1297）：WebBrokerContextsのbroker factoryはSS321SSC311に従い、credential参照supplier・owner/lockを先に完成させ、ctor最後に取得/設定し同一factoryをfinal二fieldへ格納する。内部設定helperは全port先行→一回取得→直ちに保護した既12setting→live返却、失敗時一度close/既定primary保持・closeError対非Errorprimaryだけfatal優先・self-suppression禁止とする。これはJMS provider専用の境界であり、SSC304 exactJavaTWRやSS332SQL/unknown順位へ一括置換しない。三引数注入ctorのcaller所有、既live owner closeのretry/固定例外、open/password copy消去/外側credential寿命・Unit/current/原本/権限は不変更。

SSC310適用境界（2026-10-20、BUG1530/YKT1290）：SSC304のsuccessful直下usingJdbcは既Java25 TWR意味（同一secondary/self-suppressionを含む）を維持する。そのbodyから呼ぶExpiryAuditRepository.read内の二owned JDBC資源は、保持監査照合に対するSS331SSC200/SS332SSC063199の固定秘匿secondary・未知primary優先契約であり、SS332SSC310に従って局所是正する。二種類のscopeを一つのhelper/例外順位へ一括置換しない。stage/finish直下scope、原本/Backup/権限/DB/Unit/runtime世代・期限/所有/正常業務は不変更。実環境の安全条件やnative資格をproxy試験だけで認定しない。

## SSC309 世代存在とRoot/ordinary資格の分離

RootStartupContextの世代専用読取だけstat Zの同startTicksを保持し、missingGenerationはZを消失としない。終了は同boot/親の前後認証下で二回のNoSuchFileだけ、未知IO/別ticks/別cgroup/Unit driftは拒否する。Root/self/PID1捕捉はZを拒否し、ordinary readyはSS342の完全なidentity/command/socket/HTTP/infoを独立に満たす必要がある。非leader execの一時Zを通過してもreadyを短絡せず、恒久Zは元deadlineまで未readyとして非成功にする。設定、権限、permit、世代、元120秒/親30分、owned停止順序とUNKNOWN保持は不変更。BUG1470/YKT1233/SSC309、独立kernel反例PG5706及びSS354へ追跡。既failed cohortの回収は別承認済契約で行い、正常DONE前提の停止を失敗runへ流用しない。

## SSC308 Root IO所有の取得後callback構築gap是正

FFM返却先の継続補足（2026-10-19、BUG1414/YKT1178）：LinuxSystemdSessionのbus/message/malloc文字列は、C呼出後にMemorySegment wrapperやscope callbackを構築してから所有登録しない。Arena→完成Sessionは既handoffで保護し、初回native前にSession私有の三out slot（bus、request/property、reply）とprimitive状態を確保する。元の同期・同thread経路の同時最大三所有だけであり、追加RPC/権限/再送/新公開入口ではない。各呼出の全引数準備後、C呼出直前にslotをPENDING、正常復帰直後にprimitiveでRETURNEDへする。pointer decodeに失敗してもslotと状態はSessionに残す。scopeはout slotからC呼出/返却の検査・変換全体までを先行保護する。

nativeが正常復帰したslotは、旧と同じreply→request・property free・最後busの順で一度解放する。NULL/負statusの既分類を変えず、返却pointerが既知の場合は旧どおり対象解放する。呼出自体がIO/Runtime/Errorで不明なら当out pointerを「未取得」と推定してfreeせず、slot/arenaを保持しSessionをUNKNOWNにする。別の既知requestのcleanup試行は旧順で行い、不明な対象自身の再closeはしない。解放開始前にslotをUNCONFIRMEDへ進め、正常確認後だけ空きへ戻す。decode/close不明も元slotとarenaを保持し次照会0、Session.closeの既UNKNOWN拒否を維持する。物理native解放をprimitive消費だけで証明せず、正常ABI結果・資源後条件は同source実経路/nativeで別受入する。

完成owner移管の追加適用（2026-10-19）：MorningPermitPublicationのnativeStore/nativeIntent/create、BackupStartIntentFiles.create/createPublicationはSS333のhandoff契約でDirectory→Files/Store/Intents→Publicationの各完全組立まで保護する。返却するownerがnonnullで完成した最後だけ移管し、失敗時は同一資源を一度解放、旧IO/unknown優先/UNKNOWN・保持/親期限・current/epoch/原本/DB/Backup/intent開始・退役を変更しない。既取得順と役割・固定namespace/metadataを保ち、初期化/lock/policy/残callbackの取得後確保を保護域外へ残さない。BackupStartIntentFiles.createServiceの既manual tryは別既契約として失敗/close優先まで比較し、理由なしに共通補助へ置換しない。原237候補と追加直接open/TWR対象の母数・是正/非該当・残証拠を分離する。内部詳細のためRD/UI/業務仕様変更・新QA不要、製造/PT/native/全体未完。

StartupAdmissionFileのhost/private observation ownerはSS333追加詳細のN+3 primitive容量を取得前に確保し、native FDをboxing/List grow前に取り落とさず追跡する。各native open前のclosed/容量拒否、取得後の非負/既FD重複拒否とprimitive保持、逆順全close試行の後だけIO/unknown合成を行う。serviceOwner→hostOwnerの既exec前消費・A lockだけをtrusted callbackへ借用する順序、正規原本/同PID/current世代/Unit/期限/metadata照合は不変。close例外/論理消費済みをkernel正常解放又は未知tool成功と認定せず、同FD再試行/権限拡張をしない。関連BUG1414/YKT1178・SSC308は全体未完、RD/UI/外部仕様の変更不要・新QA不要。

継承二FDの詳細補足：LinuxStartupAdmissionは従来のnull/input/distinct/range検証前を引継ぎ前（close0）として維持し、二owner/全close portの構築完了後にadmission/proofを集合ownerとして同時にadoptする。proofの正常消費は業務callbackより前、admissionは最外終端又は既Leaseの早期消費で一度だけ、各AtomicBooleanの再close防止を保持する。proof内scope入場前のbody確保故障でも集合releaseでP→Aの逆順回収を試み、全portをadopt前に構築して元ResourceScopeのIO/unknown/複合close優先順位を適用する。既CLOEXEC/同PID/readonly/権限/署名/原本/親budget・外部操作の条件は変えず、集合ownerだけでready/成功を認定しない。

SS333 SSC308・BUG1414/YKT1178、SSC137/143/304/306307。RootServiceExecutableAdmissionのtop Root FD・usr/bin/etc/alternatives/opt/JDK/java-bin/channel、RootStartupPendingのlaunch/observe directoryは同一取得順/metadata/pin/SELinux外部設定/ACL/能力・世代/borrowed contextを保持し、取得前port構築→factory内取得→同一資源scopeへ接続する。topは既DirectoryCalls.openRootをpackage内専用RootDescriptorで保持する。wrapper本体をprimitive FD取得前に確保し、constructorはnonnull calls→openRoot→非負FD検証→primitive slot格納のみ、成功FD取得後の追加heap確保/boxingをしない。負FDは所有無しとして固定storage拒否、factory失敗は同一exception。保持型のcloseはscopeから一度だけ同FDを消費、既直接checkedのIO/Reasonを保つためOwnedDirectory.atDirectoryの追加正規化を挟まない。共通directoryのopenRootはSS333の保持directory用途に限定し、新しいRoot top検査の例外変換に使わない。追加open/close再試行/任意pathを導入しない。exec直前の既bin/usr明示close・その後のidempotent owner解放、全observer正常close先行、親30分/既Unit期限/同一世代・所有の条件は変えない。close・factory例外のidentity/redaction/優先順位はSS333どおりで、JDBC TWR契約へ混同しない。

既e8ecのPG5128は別固定sourceとして全体/独立資格を回収するが、当gap是正前には署名/配備しない。新共通helper/Directory/Root変更群の所定fresh whole/同source実経路/native・全四100/F03/451を別に閉鎖し、旧3791/10nativeや途中3814成功を新source成功へ合算しない。

SSC307限定実績：source558974ad9、5124元80431 actual47/7/新待機12、六format0/三compile static0/757予定差、待機21行/2method/8branch全miss0、同source ELF込み50行/5method/44branch、公開663063b3/1047・1048。追加Testのみe8ecで5126実50/8/新guard3、全Root Io0/公開bcc4ff2b/1049・1050。これらは正常・例外portの限定証明で、今回gapを否定する根拠にはしない。製造/限定PT完了、新全体/native/正式未受入。

## SSC307 Root launch待機の内部observation port・例外分類

SSC137/143/306、NK-OPS-001・WBS-P018-03.02、RD/UI/外部契約変更不要。RootStartupPendingの既native入口はroot.serviceRootDeadlineで得た同一絶対期限、同じLinuxMonotonicClock、25ms Thread.sleep、同じroot/self/issued/ownerと同じAPI/WEB選択へだけbindする。package内WaitIo（nowNanos/requireOwner/readLaunch/pause）と内部awaitLaunch(self,deadline,io)へ既順序を移す。CLI/ENV/公開constructorから差替えず、fake portはOS/DB/permit authorityを与えない。

各loopの順序は clock<deadline→owner完全一致→同current/start-intent/launch読取、launch有なら既verifySelf→owner再一致→clock<deadline→return、無ければ25ms待機し同じdeadlineで次loop。期限を延長/再起算せず、等号/超過で拒否、owner/自己generationの不一致時に後段を呼ばない。InterruptedExceptionは現在threadのinterruptを再設定し既固定IOException("root launch unavailable")/秘密cause無し、未知IO/Runtime/Errorは従来どおり伝播する。

launch欠落分類だけ内部LaunchRead/readLaunchへ抽出する。既requireStartIntent後、同ResourceScope action内でreadLaunchを呼ぶ位置と同一resource close/例外優先順位を保持し、StorageIoException.Reason.MISSINGだけOptional.empty、COLLISION/UNAVAILABLEその他IO/Runtime/Errorは同一失敗のまま。intent欠落やclose失敗を待機へ誤変換しない。null port/self/Optional/recordはI/O前又は返却境界でfail-fast、NPEの正常化は禁止。observeのnative identity/current/permit/guard/原本未完検査は本群では変更しない。

SSC306限定実績：Main/Testbb006492a（Main5e897d92c）、5120green-v3全28/4/新8・旧6・依存14、六format0/三compile module static0、digest29行/3method/36branchmiss0、当754Mainはouter変更1/SAM追加1/他752同byte。公開manifest1fbe4b6c/1045・1046、BUG1411/1412工具・期待値是正は失敗保全のうえ限定close。新whole/native/四100・正式は未完、配備a2ecc/PG4980への変更無し。

## SSC306 Root ELF固定SHA-256の内部port・同値read-count検査

SS343/SSC137/143/354・411のtestability内部具体化。対象RootServiceExecutableAdmission.digestのみ、RD/UI/353運用/外部CLI/ENV/権限・固定setpriv/Java link/hash・所有/期限・ELF条件・8MiB上限は変更しない。package内のnon-nullなDigestFactoryを追加し、既entryは固定`MessageDigest.getInstance("SHA-256")`のfresh instanceだけを渡す。caller入力からalgorithm/provider/pathを選択できず、global providerや共有mutable hookを変更しない。port/入力はresource読取り前にnonnull資格、factoryのnull返却も内部不変条件違反として拒否する。

provider生成時のNoSuchAlgorithmExceptionだけ既固定IOException("root executable unavailable")へcause/秘密値無しで変換し、未知RuntimeException/Errorは同一instanceで伝播する。factory失敗前はELF byteのread/hashを開始しない。digestは借用channelをcloseしない契約を維持、admitの既ResourceScopeが同一channelを逆順一度だけcloseし、成功/失敗時のmaterial配列zeroize・例外優先順位を変えない。新内部overload/port以外の公開入口/借用能力/DB/JMS/credential能力を追加しない。

readの既predicate`n>0 && n==bytes.position() && n<=material.length`は、同じ8192byte配列から作るByteBufferの`0<=position<=capacity=material.length`不変条件により、`n>0 && n==bytes.position()`と全入力で同値である。これを同値整理し、正当最大size/読取chunk/EOF-position/過大申告/負・零・size変化・IOExceptionの拒否を独立試験で保持する。無視する入力やcoverage除外を追加せず、非準拠channelのn=8193・position=8192も既一致検査で拒否する。元64byte公開ELF golden SHA256 caa6f4f58ad3ed35afa011abfdb3ef06a7799b5545082b32685f75cc9c454fe8と固定header各offset/上限は不変。到達不能宣言や無意味assertで100%を作らない。

独立literal/fixed hash・provider失敗/未知例外identity/null/借用寿命/zeroizeと既ROOTELF全case、当scopeのformat/NullAway/Werror/SpotBugs/選択PT・物理Main一outer変更/一内部SAM追加を資格する。これは部分製造/PTであり、変更群のfresh whole・同source runtime/native/全四100/F03/CHR/451/QA051finalは別未完。現a2ecc/PG4980/native10成功は保持するが、新sourceへ自動転用しない。QA不要のSS内部補足、設計only main反映を実装前に完了する。

## SSC305 当a2ecc既存ADMINの親終端比較・保持Ref pairの限定回収

当限定契約の実績（2026-10-18、製造/限定PT完了・全PGPT未完）：初回設計only9b9967b1f→main fb96f60f0/PR152を先行し、元verify143/旧closeUNKNOWNを保持したまま5098全原値proof→5096一回子親回収/同hostgate継承→5100別全post0、是正新5102/04/06/08で親end独立反例・当ABI五phase/新stage/verify/実20/独立全postを各0で閉鎖した。Unit実1.77017秒/元30秒以内、既単一ADMIN/全24・32・187/原本Backup・二credential私有退役/全資源0を検証。当具体PID/slotは終了・退役済で再実行を許可しない。5112全1650CRC/session/二pair独立単調・最新closing10stream12point/旧source輸入0、5114元六XMLを秘匿公開。BUG1405/YKT1169および付随1406～08/1170～72を全対象再試験付き限定close。実施/証跡はdev-foundation 9ce065ff7・1042/1043・公開PG5112 manifest SHA60dadc92cf4fa7ff66427348675d0b9ad2f9e1d9b3f34e29d19d95868f105773に保存、実装/設定/工具/証跡はこの設計only反映へ混入しない。batch残739line/147method/9class/434branch、F03/CHR/451/QA051final/正式1964PT・53scope/17・190/工数nullは未更新・別未完。

BUG1405/YKT1169、SS343/353/354・SSC274/276/277/279/300～304の内部具体化。RD/UI・業務仕様・CLI/ENV・原30分Root/30秒ADMIN期限・451/QA051 finalは変更しない。現a2ecc/PG4980/BOM78a6/187/schema028/boot79aの既存ADMIN20に対し、元親run15322936・activationb683・Invocationabe95の**start306951851178usとend308517705767usを別値で検証**する。end照合へstartを代入した工具5082は誤りであり原byte/失敗/未終端を保持する。独立の真正親receiptを使い、同じ誤値を持つfixture同士の一致で資格しない。Root/Browser/ownedstop/全3791/署名/host ABIの既成功を再演しない。

当verifyの保持Java927504/t31055084/argvSHA8bfbbbf082fadbc9569bbc0f2d21980d9eb02a03f1215594f983b5b79e6dc0bc/100FD、唯一Ref子927536/t31055311/argvSHAf8a143d4a170fe7cfe34b17bc0cafebd4150523c2dbcf1e0e0a3c521e11e4656/7FDを**観測基点のみ**とする。sudo927502は対象外。新しく原argv/exe/全authority/cgroup/全task親子、全FD set/target/inode/type/mode/権限・実M-A sole FLOCK/OFD、子唯一private systembus名と実PID/UIDを二読して束縛する。共有/run directoryの二時刻だけはSSC277の非減少・current上限でfresh資格し、同fresh像を以降固定する。他のFD不一致、第三子、foreign owner、元helper/hash/失敗phase不一致ならsignal0・保持とする。

failed-phase読取は、5084全frozen149工具hash/5080独立beforeaf59/全24・32設定・187artifact・原本Backup/native86・元真正親/同boot/currentと、Ref子がsnapshotの終了比較で拒否しprepare/credential/Unit開始前である実source/stack、失敗log1c6a71bb…を認証する。旧DBのidle期限後はfresh SQL peer/advisory全0と当actorのDB ESTABLISHED socket0を照合し、旧正常closeを推論しない。新十Refを保持する一つの回収接続で全原値/所有のfresh耐久proofを保存後、pidfd前後・一回予約・TERM直前を再照合して**当Ref子→当Javaの順に普通TERM各一回**、各15秒終端/30秒同ticks reapを要求する。新unit/DBserver/VM/他PIDへのsignal、SIGKILL、DB terminate、force unlock、再発行を禁止する。全bus/FD/peer/advisory/M-A消失・全24/原本native不変を確認し新Refを正常返却、旧wrapperが同hostgateを自然解放してから新後継が同inodeを取得する。失敗なら隔離とUNKNOWNを維持し、独立読取以外を先行しない。

回収成功も旧verifyの正常完了ではない。元実exitと旧close UNKNOWNを保持し、別接続の独立全post・正常新Refs/全資源0を満たして初めて別new-only baseline/工具で再試験する。旧slot/class/原本/credential不存在/署名/nativeを上書きしない。新20のcaptured terminal/credential私有退役/同source CRC/session/四counter/正式はそれぞれ別依存とする。設計only main公開を実回収より先行し、製造・PT・正式未完を維持する。

## SSC304 Expiry既成功読取の監査比較・nonnull JDBC所有scope

取得scope追補（PG4964の例外経路反例後）：内部`JdbcAcquire<T>`を加え、acquire/release/readの全port object構築・nonnull検査を**資源取得より前**に完了する。helper内で既固定JDBC取得→required非null確認→直ちにtry/read(resource)へ入り、body/closeの同一例外・suppressed順を下記どおり保持する。nested ResultSetのport構築は既Statement scope内、ResultSet取得はそのinner helper内とする。これにより取得後・scope入場前のcallback linkage/allocation失敗による未解放を防ぐ。acquire失敗時はbody/close未実行、acquire null戻りは既requiredの固定BatchRepositoryException、port nullは取得前契約拒否。resourceを受けないためWillClose annotationは付さず、解析抑制や例外edge除外をしない。release/readは同一取得資源だけを受取り、借用Connection/SQL/期限/権限を変えない。actual24独立PTと実DB/static0・Main宣言数増加を正確に照合する。

SS331/341・SSC117/125/200の`ExpiryAuditRepository.successful`は、引数/時刻/owner/元run検証、固定SQL・同日・元run照合、既`read`のstrong validation、末尾owner/元run再確認の順序を保持する。末尾のSUCCESS、ended非nullかつobserved以下、errorCode/errorSummaryなしの既5条件だけpackage内`verifySuccessfulAudit(Snapshot, Instant)`へ分離し、同じ短絡順と固定BatchRepositoryExceptionを保持する。helperのnull引数は契約拒否、NPEを正常化しない。直接Snapshot負試験は内部predicateの検証であり、不正DB行がDDL/readを通る証明ではない。

`required`済みのStatement/ResultSetは取得直後から同class内package境界の狭いlexical JDBC scopeで一度だけcloseする。既Java25 TWRと同じくbodyが正常ならclose成功後に値を返し、bodyが失敗ならcloseを実行してから同一primaryを再送出する。closeも失敗した場合は同一secondaryをprimaryへaddSuppressedし、同一Throwableのself-suppressionを含めJava TWRの挙動と一致させる。ResultSet→Statementの逆順を保ち、inner primaryとsuppressed順序・checked IOException/SQLException・未知Runtime/Errorのidentityを変更しない。SQLExceptionだけ既外側で固定BatchRepositoryExceptionへ変換し、cause/raw診断を公開しない。既ResourceScope/JdbcResourceFailuresの別契約へ置換しない。この範囲は既TWR契約の維持であり、他Repositoryの失敗優先順位や将来の設計変更へ拡大しない。

release/read portは内部の既取得資源だけを扱い、null portを実行前拒否、nullable資源を受理しない。借用Connectionのclose/commit/rollback、SQL・lock・期限・所有・DB変更・OS/permit/CLI/ENV権限は追加しない。独立literal監査反例と実Java TWR参照によるbody/close複合・逆順・self-suppression比較、実PostgreSQL既適合試験を併用する。compiler null-closeを人工null資源で通したり除外して100%を作らず、変更群のfresh全回帰・同source native/451を別に資格する。RD/UI/QA051 final/Current/DIF/ITST条件不変更、利用者QA不要。

## SSC302 retained Expiry監査比較の純data検証境界

SS331/341・SSC117/125/200のCleanupExpiryExecution.verifyPriorExpiryは、借用Connectionとrequestのnull契約→SKIPPEDかつselectedCount0→BatchRunRepository.verifyAlreadySuccessful→ExpiryAuditRepository.read(priorHandle)→元PriorExpiry取得という順序・所有・DAO内strong validationを保持する。最後の既監査比較だけpackage内`verifyPriorAudit(PriorExpiry, ExpiryAuditRepository.Snapshot)`へ分離し、同11条件を同じ短絡順で検査する。成功status、終了時刻、cutoff-7days、before/after非null、before>=after、before-after=success、success=target、failure0、errorCode/errorSummaryなしの全条件を残し、失敗は従来の固定IOExceptionとする。新helperのreference/snapshot nullは即契約拒否とし、NPE catch正常化0。外部呼出し順、SQL/transaction、ログ/電文/データ互換性、権限・期限を変更しない。

内部helperは取得データの比較だけでConnection/署名/UID/permit/Unit等を生成・確証しない。独立literal Snapshot負試験で各短絡条件を個別検査しても、その反例が実DDL/DAOを通ると主張しない。DAOとhelperの二重防御は削除せず、実PostgreSQL＋現DDLでのSKIP成功・全24原値不変の既単体試験も併用する。正常0/Long.MAX_VALUE等の演算、時刻/cutoff、status、null、誤差/カウンタ/診断・callback以前のskip/選択数拒否を独立期待値で検査する。対象除外/到達不能免除や旧source exec合算でcoverageを作らず、変更群fresh全回帰・同source native/451を別受入する。RD/UI/QA051 final/ITST条件は不変更。

## SSC301 API認可内の非秘密設定取得・失敗分類data port

ApiProcessMain.startNativeがServiceStartupAdmission.executeへ渡す既CONFIGURATION callbackの本体だけを、package内`admittedConfiguration(ConfigurationLoad, int[])`へ抽出する。ConfigurationLoadはApiStartupInputs.Valuesを返しIOException/NoSuchAlgorithmExceptionを伝える内部data-only portで、通常本番は既loader::loadを同じ認可内・同順序で一回だけ呼ぶ。外部FQCN/noargs/argv/ENV/固定file/UID/署名・DB/JMS/permit/親1800秒/Unit期限を変えず、任意loader/constructor/fixture/測定modeをCLIやENVへ公開しない。認可前に設定fileを読まない。

正常では取得した同一Valuesとその既canonicalSha256をConfigurationへ返し、callerの一slot failureCodeを変更しない。IllegalArgumentException又はNoSuchAlgorithmExceptionだけ既どおりfailureCode=70にし、秘密を含まない固定`IOException("non-secret configuration unavailable")`をcause/suppressedなしで送出する。IOExceptionは同一objectを伝搬し既50を保持、他RuntimeException/Errorも正規成功へ変換しない。port・slot・戻りValuesのnullは契約違反で即拒否、slot長は1だけ。null/不正slot検査はcallback実行前とし、NPEをcatchして正常扱いしない。各実行のslotはcallerに属し共有可変staticを導入しない。

独立PTは正常同一Values/固定canonical golden、実invalid loader及び型別失敗、固定診断/cause非出力、IO/未知同一object、null・slot0/2・並行独立slotとcallback回数を検査する。内部境界試験はOS認可/起動/readiness/DB接続成功ではない。変更Mainは旧source nativeで補完せず、必要変更群のfresh全回帰・same-source native/451を別に資格する。RD/UI/既正常・異常終了値と承認済DIF、QA051 final保留は不変更。SSC300のcurrent825e正常20/12point実測は原sourceの限定成果として保全する。

## SSC303 current04bbの既存ADMIN正常20・同source native資格

SSC300以下の全resource/credential/起動/正常20/独立post契約を変更せず、現Source04bbdb73b532537e3546191d72dee913b17629a0/release0.1.0-PG4860/BOM08300d492e9eb5ba6e31eb646c21e51fc3eb4d30680e205c2adcd35c92d298b2/schema028/boot79a3260a-e16d-42bf-942a-b914ed144c28へnew-only再束縛する。元825e限定の記録・成功・失敗・保全物は改変せず、本追補の資格や起動権限へ移植しない。

同source Rootrun4e220f3b-fbb4-411c-b5c4-7ca1371daa20/cutoff2026-10-17T01:03:09.221494Z/activation7bae6042-b79f-4fb2-9d9f-edf47b428cbe/INV7fe303d625de4a83b23d23fca4eca2bb/終端monotonic199849150395us、真正WARNING10/1611.390096秒と実Browser12、4920正規owned停止/4922独立全24二読・十kernel/actor/client/advisory/flock0・187署名を前提にする。4930fresh read実baseline28c6679e2bd13f84e33c21ea9dbcb2a5baa1e8efda7b2780471f80e74a6f6a63、884batch行/native78・既単一ADMIN/二credential不在・全24/32/187・全資源0は観測比較基点だけで権限ではない。操作前に現current/署名/Unit/NSS/原本Backup/全78/既scope終端を再認証する。

existing ordinary-bootstrap196 roleを再prepareせず、所定のfresh M/A→DB/advisory/十Ref/FD・全input closure、非運用二input一回発行・durable予約・専用Unit一回start、元30秒・captured正常20/DB作成更新監査0・全24不変・同Invocation terminal/closing二point、正常close後の同inode-byte/NOFOLLOW/RENAME_NOREPLACE私有退役・両dirsyncと全独立postをSSC300どおり要求する。旧run/secret/permit再利用、通常Root/別Login/未知owner操作/再start/部分補作成は認めない。Production/CLI/ENV/通常業務・451/RD/UI/QA051は不変更、新QA不要。

現04bb/4926の9stream10pointと当新Bootstrap pairだけを、全1647physicalMain SHA/CRC・個別session/point/INV/時間・closing優越で資格して同source host3761PT/551suiteへ結合する。旧825e/1646のnativeや合成coverageを輸入しない。設計main反映、当正常20/資源後条件/native、四counter100、正式PGPT/ITSTは別受入である。

## SSC300 current825eの既存ADMIN正常20・新一回native資格

SSC188/189/225/231/234/263の専用Bootstrap契約を変更せず、current Source825e463334c43a5bc96f50db964df22e11758d1b/release0.1.0-PG4702/BOMf1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80/schema028/boot79a3260a-e16d-42bf-942a-b914ed144c28の未実施正常20経路へ限定再束縛する。根拠は同source Root fff841d9-2554-4680-b17d-9548bfa79cbb/cutoff2026-10-16T22:12:38.570783Z/activation7ab6c953-b2fc-47ae-be96-26a3196ca76d、真正WARNING10/1652.392895秒、実Browser12/正規ownedstop/4778独立全24二読・十kernel/actor/client/advisory/flock0・署名187・native70安定。元after10field私有SHA b4f07e80538b7eab36e1ba87523097891252e5f14f9f1d86ad8106c753c740c3は観測比較基点だけで起動権限ではない。初回guest readで全原値/Source-BOM-current/同signature/全24・32設定とUnit宣言・NSS/credentials/原本Backup・runtime/startup/旧70native/既tool-scope終端を再認証し、ADMINが現存することをDB内だけで確認する。実体行や秘密を輸出しない。

ordinary-bootstrap196は既閉12role中の既owned roleとして検証し、roleを再prepare/mkdir/chmod/chown・旧execを復元しない。欠落/未知entry/owner又はagent/RW宣言不一致なら資格せず、当該範囲の新準備を別分類する。固定二bootstrap credential sourceが不存在である場合に限り、新M→A/現current・保持namespace/全必要FD・readonly batch DB/advisory71419602/十Refの各所定scopeと完全入力closureを保持して、ADMIN既存/全前値を再検査し、新CSPRNGの非運用試験username/passwordをO_EXCL/NOFOLLOW/root0400/link1/ACL0で一回発行する。旧秘密/旧permitを復元・Login利用せず、DB_API sourceを変更しない。DB/advisory正常帰還・全peer0を確認後、durable一回予約から署名専用Unitを一回だけstartし、当Invocation/PID/start/job・普通API identity/group/cap0/NNP/cgroup、元30秒と真正正常20、作成/更新/監査追加0・全24不変、同Invocation terminal→closing二pointを独立照合する。読取、準備、start、終了、scope closeを別判定する。

全体後条件後だけ新二sourceを同inode-byte/NOFOLLOW/RENAME_NOREPLACEで私有退役・両directorysyncし、元DB/全24/署名187/原本Backup/他九Unit/設定・依存/runtime・旧nativeの不変と新M/A・DB/client/advisory/Ref/FD/bus正常帰還を独立postで確認する。新Bootstrap20だけからRoot/API/Web/Backup又は全品質成功を推定しない。新slot/実handlerの全依存及びactual entry selector・保存schema・型/null/欠落/余剰/別Source/既予約・旧二source再利用拒否を先行PTにする。未知/部分発行/close不明では所有/証跡を保全し、同slot再start・別入力再試行・補作成・force回収・DB手更新をしない。運用秘密はGit/公開logへ保存しない。

本補足は既存ADMIN20の承認済み動作を当sourceへ適用する内部具体化で、通常disabled/argv0・exit0/20/50/70・署名/既認可/DB維持・元期限・451・RD/UI/QA051は不変更、新QA不要。Production Mainは変更しない。825e Root9 streamsと新Bootstrap closingだけを、各actualsource/同1646Main完全SHA/CRC/個別session-point/invocation時間で資格してから同source測定へ統合する。別Sourceの旧Bootstrap成功/nativeを輸入しない。設計main公開・当試験normal20/新scope後条件・native・四counter100/正式PGPT/ITSTは別受入である。


## SSC299 三外部entryの終了要求data/control-flow port

既SSC083/234のJava25標準instance-mainをMorningProcessMain/RootServiceLauncher/CleanupProcessMainへ限定適用する。公開noarg constructorは固定本番operation・既measurement source・既System::exitをbindするだけで、起動権限/代替path/fixtureを選択しない。package内constructorのcallbackは同じmainの引数判定・実行順序・終了要求の回数/値・未知例外を独立検証するdata/control-flow portであり、OS Unit/UID/原本/DB/permit/readinessのcapabilityではない。CLI/ENVから任意callback/測定profile/終了方法を選択する機能を追加しない。

FQCN/既argv/終了0・10・30・70/固定診断/親1800秒/各Unit期限/全保持owner・認可・失敗逆順回収は不変更。Morningは既runCompletedの真正typed completion/既例外分類をそのまま終了要求へ渡し、未知business failureは終了要求へ正規化しない。Rootは元の引数によるmeasurement選択→同Optionalを保持したnative admission→必要TERMINAL capture→終了要求の順序と、capture不明/失敗時に終了要求を発行しない挙動を保持する。Cleanupは元mainのuncaught handler設定、--expiryの固定選択、既runNative/runExpiryの終了値/未知例外を保持する。native default constructorで代替operationを取得・選択する公開APIは作らない。

独立port試験は正常/境界/異常/null/未知例外・同一callback identity・終了要求前後順序を手書きoracleで確認する。架空completion/測定fixtureを真正Root/Backup/OS成功やnative資格へ加算しない。実JDK25の同FQCN launcher/終了値・必要fresh全回帰/当source native/四counter・451を別に受け入れる。System.exit非帰還をcoverage除外/到達不能宣言、JVM終了抑止、private反射/bytecode改変で合格化しない。

## SSC298 正常postの未reap子を持つmetadata-only retainer

SSC297回収の旧Java/Python/本人DBとlock消失・元inspect143を維持する。独立post829193/t16712075はZ/FD0/cmdline空/PPid828676/rawWaitStatus0と保存manifest7ab5cdc6の全新post scope正常/全原値148a8d8aを認証し、親が未waitの事実と区別する。当metadata-only828676/t16705476/argv51c27aa6/4FD/root/caps/PPid828674/cgroup-session1042/同exe-root-cwdだけを対象とする。新十Refを先に重複保持し、全FD target/9metadata/fdinfo/全authority/children=[829193]・Z全stat identity、全19/32/24/189/原本Backup鍵/native58/37/全ordinary・DB/advisory/M-A0を各操作境界で全二読し比較前に完全保存する。

同artifact proof正常/独立反例/確定main公開後に当metadataへ通常pidfd TERMを一回だけ、15秒terminal/30秒本人・Z子の自然reapを確認する。Z子/旧Java/Python/DBserver/Unit/hostにsignal0、force操作0。元host684367/t16801848の同inode sole flockをqueued自然継承し、元4494実transport非0/旧UNKNOWNとguest終端/旧成功postを別々に保存する。元postを再実行せず、所有変更後の別fresh新namespaceで同current postの新M/A/RODB/十Ref正常・全原値を確認して外側Ref正常返却まで新回収未受入。

新post開始の固定payload/親/予約を先行保存、新PIDを記録して元Popen.wait/真正exit/XMLで終端を結合する。起動直後の変動FDを終了回収前の必須記録にしない。既保持ownerの全FD/権限/世代検査は省略しない。取得/close不明時はmetadata・証跡・元jobを保持し再送0、Root1800/451/品質/外部仕様/QA051は不変更。


## SSC297 配置前UNKNOWN管理pairの限定handoff

歴史差の唯一の限定例外：当JavaのFD31/90が保持する同一/run directoryのmtime/ctimeだけは、old<=current<=fresh観測UTC nsの範囲で単調増加を許す。target/inode/uid/gid/type/mode/nlink/sizeとfdinfo、他全FD/authorityは固定し、各操作境界内の全proc二読ではこの時刻も含め完全同値を必要とする。BUG1365保存像の四時刻差だけが根拠であり、未知FD/他directory/逆行/未来/境界不安定の一般許容ではない。

SSC296の配置前inspectが失敗して保持した管理pairに限定する。current7bb/PG3976/BOM0a409301/boot79a・候補964e/PG4432/BOM93807abdは変更しない。当Java827198/t16494387/argv72e6609e（101FD）→子Python827230/t16494598/argv8c039420（4FD）だけを対象とし、root/caps/cgroup/session1025/exe/root/cwd/agent変数名不在・全FD target/9metadata/fdinfo/children/全argv hashを固定私有像と完全比較する。DB827228/専用batch ROのsocket両端・advisory71419602とM/Aも本人へ結合し、各操作前の全像二読と全19Unit/32設定/24表/原本Backup鍵/署名189/native58/startup37の不変を必要とする。全像は比較前にnew-only root私有0600へfsyncし、拒否時も省略しない。

新十Refを旧十Refへ重複保持し、同artifact無操作proofの全新scope正常返却・独立反例・確定設計main公開後だけpidfd通常TERMをJava→Pythonへ各最大一回行う。各15秒terminal/30秒以内消失、Java後のPython PPid1だけを明示した世代遷移として認証する。自然終了済みなら再signalしない。元host677797/t16590755の同inode sole flockをqueued自然継承し、実transport終了値は実値のまま保存する。sudo/DBserver/Unit/Root/Backup/Admin/配備/reload/revoke/force/SIGKILL/DBterminate0。旧scope close UNKNOWNと旧Root143は不変更。

全旧pair/本人peer/lockの消失後、外側新十Refとhostgateを保持し別freshの同current独立postで新M/A/RODB/71419602/heartbeat/十Ref・全原値と全Unit/kernel空を検証し正常返却する。最後に外側Refも正常返却してのみ新回収0とする。未知時は新scope/証跡/予約を隔離保持し再実行しない。元frozen142/v4のhotpatchは禁止し、後続set型caller修正は別new-only v5と実sealed show独立vectorで行う。RD/UI/既1800/451/QA051条件は変えない。


## SSC296 回収済みfailed-DONEをdata-only基点とする新source配備

SSC291～294でRoot143の必要逆順回収・typed revoke・別fresh postが真正完了した現7bb/PG3976/BOM0a409301/boot79aを、新候補964e/PG4432/BOM93807abdへ接続する。旧7fff正常Root用のISSUED/正常GC/成功receiptを移植しない。現RootはINVbbcdb699/job167140/runb1ba37cb/activation8314450e、timeout143・done10/SHA654073a0は失敗親のdataであり、正常Root/停止権限ではない。旧scope UNKNOWNも保持する。

基点はfreshの全24表、全32設定・実Unitfile、原本/Backup/鍵・全189署名材料、全37startup（現INVALID）・native58・runtime・全10Unit/19field・全PID1 journal field/cursor/イベント順を完全11fieldへ保存したものとし、非native before10=66ee6f86/完全11=8e000cbaへ固定する。JSON object key順だけは非意味的だが、全値の型・list/イベント順・cursor/fieldを削除しない。raw双方を比較前に別root私有fileへdurable保存し、未採取の過去拒否を後日の同値で補完しない。実epochのINVALID・permitDigest無しと同run/cutoff/activation/done全byteを型付き前後二読する。現在failed/timeout143/全PID-job0・kernel空、active/pending/intent・全DB/client/advisory/flock0も再照合する。

新only閉鎖18roleは同artifactで`inspect`と`place`の二modeだけを受け、固定Java/同class/同modeの親子argv、各別SAVE、全file SHA/stdlib依存（UUID検証の標準uuidを明示）/bundleを認証する。M→A→実batch RO DB/advisory/heartbeat→十metadata Refを保持して各境界の全現在値を二読する。`inspect`は187artifact/全tar member/サイズ/hash/署名・固定source/BOM/schemaを検査し、private SAVEへmanifest証拠を保存して配置前にreturnする。candidate release/署名destination/current/approval/epoch/Unitは書かない。DB rollback/close・lease確認→十Refとbus/子の正常終了→A/M返却後にだけinspect completeを発行する。

同artifactの実inspect0・全新資源正常返却・設計main公開後、別freshの`place`一回で未使用releaseと新署名fileだけをnew-only作成する。旧原本/37/native58/全非対象byteを保全し、独立postが全現在値・新候補187署名・全資源0を確認してからcandidate ROへ進む。RO→別post→既承認の有限code-only公開→別postも個別new-only予約・source/hash・同所有へ結合し、UNKNOWNや途中fileを再発行せず保全する。公開許可差以外のUnit/原本/DB変更を追加しない。失敗親証明はdataだけで、旧親の期限や操作許可を発行しない。

新通常Rootは公開後の別fresh新run/cutoff/activation/epochによる一回であり、1800秒・各Unit期限・全境界鮮度/全graph・失敗逆順回収/資源後条件を維持する。旧source nativeの合算0、真正terminal/全24/seal/同owner Browser/ownedstop/新source native CRC-session/CHR/F03/四100/451は別受入。RD/UI/業務差分・QA051 final保留・正式1964/53を変更しない。


## SSC295 固定manager読取のbootstrap共通化

SSC239のin-process固定local manager readerをbootstrapへ所属変更し、Root NativeIoとChild NativeIoの固定Unit照会が同実装を使う。固定enumはAPI/Web/Morning/Cleanup/Expiry/InboxInspector/Artemis/Caddyの八Unitだけ、field組は既存7fieldとdeadline4fieldだけである。返却は非秘密観測dataで、Root/子の認可・起動/停止権限ではない。bootstrapからbatchへの依存、任意Unit/field/path、公開Factory注入、代替CLIへのfallbackを作らない。

各readは新busとarenaを所有し、固定system socket・非対話/非autostart・同PID1/euid0/unique ownerの前後認証、全指定fieldの型/長さ/ASCII、元5秒絶対残時間と全RPC/handshake期限、正常close又はUNKNOWN保持/次read拒否を維持する。共有してよいのは既Factoryのimmutable ABI bindingだけで、観測/認可/graph結果cacheを行わない。Childの前後Unit・boot/PID/ticks/cgroup/status/NSS/zero capability/NNP照合、Root全graph二読と各境界の検査回数・鮮度、元1800及び各Unit期限を減らさない。

移動した試験の独立literal/異常・null・owner/thread/close/期限の全観点、新classpath実ABBA、変更module静的・必要fresh同source全回帰/新正規経路を別々に受け入れる。既7bb署名/native/3717全体を新sourceの成功へ流用しない。限定速度改善だけでBUG1332/Root/PGPTを完了させない。

## SSC294 Java終端後の残Python・metadata holderだけのowned handoff

SSC293の元4368v3/66056はJava815726一TERM・pidfd終端/FD0 zombie/M-A0まで実施済みで、Python TERM直前の現在API93/DB両端入替を二読で正規拒否した。各全像とindexを保全し、Java又はCaddyへの再signal/stopをしない。残る元Python815643/t15408795/argvc8c952de/session970/7FDと、UNKNOWN metadata holder817783/t15666115/argva9deeaa1/session986/5FDだけを別new-only scopeの許可targetへ固定する。4376のowners627510df/current078c7f92は参照証拠で、直前全FD/authority/source/原値のfresh証明を代替しない。

新controllerは操作前から十metadata Refを保持し、元hostgate本人・両targetの全FD/argv/ticks/uid-gid/caps/NNP/cgroup/子、既JavaZ/FD0・M/A/advisory0、全189/32宣言/24原値/37・56/同三ordinaryとclient/server全FD二読を認証する。targetごとに通常pidfd TERMの一回耐久予約→再verify→TERM→真正terminal/消失を行う。元Python終了に伴うJavaZの自然reapを確認し、Javaへ追加signalしない。元58917の真正transport非0とguest両PID消失を別保存し、hostgateをforce/unlinkせず自然返却後だけ継承する。

次にmetadata holderだけを通常TERMし新旧管理資源消失を証明する。元4368 observerのactual1と、既にobserverが終了して回収不能な旧keeper SSHの実exit欠測/null、旧UNKNOWN closeを分離保存し、未知を0/正常へ読み替えない。新十Refが両旧holderの継承期間を覆い、各段階失敗時は現在のscope/予約/全拒否像を保全して再発行しない。

既固定4366v3 partial213f3a1eの実inspect/全新scope正常を先行、必要五停止（Caddy既真正終端は観測だけ）・typed revoke全37保持→既postd64b8c58の別fresh独立post→外側新十Ref正常まで回収受入れとしない。全新scopeの成功は旧Root143/元58917/元66056/旧keeper closeの正常化ではない。独立target拒否/全FD差/型・欠落・source違い/保存失敗/同artifact無操作実proofと設計only main公開を先行条件とし、新Root/Backup/Admin/配備/reload/VM/force0、RD/UI/1800/451/QA051は不変更。

## SSC293 ordinary pool履歴差・現在両端所有・境界内全FD二読

SSC292の同current UNKNOWN instance限定。元4336→4356の歴史差はAPI fd93のtarget/metadataだけで、旧TCP表は未採取のため旧pool所有・旧UNKNOWN正常closeを認定しない。全source/BOM/署名/Unit世代・actor identity/authority/NSS/children・非pool全FD（target/全9metadata/flags/mountId）は歴史継続を照合する。新現在基点4356のAPI93/96・Web110は実captured FDのinodeから固定role/app・当ordinary PID/ticks/INV・SS342 pool範囲・loopback ESTABLISHED→5432・PostgreSQL本人backendと逆向きTCPへ一対一結合済みであり、番号/socket型だけを許可条件にしない。旧fd93未分類はそのまま保全する。

操作境界の現在pool分類は、captured client fullFD像とclient TCP・同backendのPID/ticks/argv/OS postgres UID/GID・全FD capture・対応server FD/inode/逆向きTCPを証拠へ残す。未知/余剰peer・app/role/port/片端/owner差・重複inode/FD alias・pool上下限外・非pool変更を拒否する。歴史比較で許すのはこの本人両端証明済みpool動態だけで、固定authority/非pool FDは緩めない。各pidfd・予約後・TERM直前の現在全snapshotはkeeper/partial双方で明示的二読、全FD（server含む）と双方endpoint/state/inodeのauthority像完全一致必須。二読不一致を自動再採取で合格化しない。

TCPのqueue/timer/counter生値はprivate raw証拠へ保存し、authority比較はlocal/remote endpoint・ESTABLISHED state・inodeとfullFD/identityへ分ける。非authorityの時刻進行を不正FD変化とも権限とも扱わない。server側だけの差もkeeper/partial双方で拒否する。二回目bind又は取得途中の拒否でも既取得snapshot/TCP/server像を保全する。全before/after/referenceを単一fileへ詰めず、既一file64MiB上限を維持して各像を別root私有new-only fileへwrite/fsync/dirsyncし、全part SHAの小さなindexを最後に保存する。片方/証跡/dirsync失敗は未完・隔離のままで、rawの切捨て/部分indexの完了扱いをしない。

元58917/元4348/旧各失敗・未採取値を保存し、既Caddy再stop/元recover再発行は禁止。新同artifact全FD/pool・拒否証拠/保存失敗の独立反例と無操作実proof・設計only main公開後にだけ、SSC292の正規owned pair handoff→自然gate継承→同partial inspect/必要五停止/typed revoke全37保全→別freshpost/全新scope正常へ進む。1800秒/全fresh/451/業務RD/UI/QA051/旧正式認定を不変更とする。

## SSC292 新current UNKNOWN管理pairの限定handoffと残五停止

SSC291の元recover（Root167140/INVbbcdb699/run b1ba37cb/activation8314450e、source7bb/PG3976、boot79a）のCaddy一回停止後UNKNOWNを対象に、旧SSC288/289の別instanceとして扱う。元driver/予約/failed pair未取得の事実を保全し、Caddyの再stop又は元recoverの再実行をしない。原本DB/Backup/鍵・署名187とmanifest/materials・全32宣言・起動37entry・既native56を保持する。主因未確定のsnapshot不一致をfield除外/再試行で成功化しない。不一致の前後全snapshotはroot私有new-only fileへwrite/fsync/dirsyncし、rawを公開しない。

新only scopeのmetadata十Refを保持したまま、元host634760/t15505417/argv・SSH634870/t15505594、管理Java815726/t15409721/argv5312514a・Python815643/t15408795/argvc8c952de、session970のauthority/cgroup/98・7全FD/子関係・同open-description・M/A flockを直前二読認証する。記録された専用backend815747/advisoryの期限後不存在は旧正常closeではない。実batch DB結果と全ordinary clientの固定role/SS342 pool範囲/両端TCPも照合し、不明ownerへsignalしない。Java→Pythonの各一回pidfd TERMと真正終端/全旧PID・lock消失を記録し、元observer/SSHの実transport終了値と分離する。SSH終了を一律143と仮定せず、真正非0をそのまま失敗保存する。旧scope正常close/Root正常を主張しない。hostgateをunlink/forceせず元ownerの自然返却後だけ継承する。

同artifact新partial controllerのinspect・全新scope正常を先行し、Caddyは保存した停止前世代と現在のnormal terminal/kernel空/旧PID不存在を再認証する観測だけである。必要Web→API→Expiry→Artemis→Cleanupの五停止だけを各一回予約/verify/真正terminal/資源後条件へ結ぶ。全fresh二読・全FD/署名/原値/ordinary pool・native固定出力条件を落とさず、六終端後の現ISSUED typed revoke/全37保持→全新M/A/RODB/十Ref正常→別fresh独立postまで回収受入れしない。UNKNOWN/未取得pairの過去値を後日の同値で補完せず、再失敗時も隔離・元job保全。新Root/Backup/Admin/配備/reload/VM/force操作0、1800秒/業務RD/UI/451/QA051は不変更。

## SSC291 同source新failed-DONE instanceの正規逆順回収

SSC287～289の権限/終了条件を変更せず、Production7bb/PG3976/BOM0a409301/boot79aの別instanceだけを新only工具へ固定する。Root167140/INVbbcdb699/start149622262076μs/exit151422334917μsは1800.072841秒timeout143、runb1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1/cutoff2026-10-16T11:32:53.943173Z/act8314450e-0dd5-4986-875c-81f73e1b50b2。原本done10/SHA654073a05ac1101060b235c8dc1e058efb94f0884e4eb87613b7f182b199644aはdata-onlyで、正常Receipt・旧親の期限・停止権限ではない。PID1同boot/INV/job starting→failedの6record、現在Unit failed/143/全PID-job0・cgroup空と当原本byteを独立照合する。

同API807944/t15096765/INVa2854d41、Web808319/t15098199/2a74a4ca、Caddy808868/t15101177/25aa7706、Artemis801335/t14991135/251daea1の四ordinaryは、新freshのUnit/実kernel/全NSS/caps/FD/argv/INFO/socket/原値から認証する。4306私有63269de9…は当初の基点で、次操作のlivenessへ流用しない。全187署名＋pin/signatureの189保持file・全32宣言/実Unitfile・DB全24/原本Backup/鍵・native56の各既byteを保持する。startupは現37entry（permit9/owner9/launch18/epoch1）で、permit-start/service-start intent無し。旧33等へ正規化せず、全37と履歴を保持する。

旧4112のJava literal/class byteを新cohortへ再認定せず、独立kernel/原本基点から新Java/hash/helperを固定・JDK25で再compileする。固定artifactのread-only inspectは、新M→A→実batch RO DB/advisory71419602/heartbeat＋十metadata Ref・同source/全原値/typed ISSUED/owner/launch/完了原本を確認し、全新scope正常返却まで完了してから回収へ進む。親expiredのparentsGuardを呼ばず、失敗データの型付きreadをliveRoot資格へ変換しない。

回収は別fresh同契約でCaddy→Web→API→Expiry→Artemis→Cleanupの必要6Unitを一回ずつ予約/直前再照合/通常stop/真正同世代terminalへ進める。既SS288の設定宣言tripleと実行補助値の分離、SS342/API2..8/Web1..2＋本人DBの両端socket/role、全189/全24/原値の各phase不変を維持する。普通API/Webは独立PID1/native終端、Artemisはvendor witness、残Unitは設定通りの正常terminal/kernel空を検証し、普通poolも0へ縮退する。6正常後だけ現在ISSUEDをProductionの型付きrevokeでINVALIDへ移し、全37のうちcanonical epoch一fileと親directoryの許可metadata差以外を変更しない。全DB/holder/M-A/Ref/busが正常closeし、さらに別fresh独立postが全24/原本Backup/鍵/全189/32/native旧56＋同INV API/Webの正当な二終端stream/全37と全資源0を実証するまで未完とする。

旧8208/旧4152/metadata retainer・既Caddy停止履歴はこのinstanceの回収対象ではない。Root/start/Backup/Admin/配備/reload/VM操作、raw復元・原本削除・失敗正常化・強制解放・再stopは禁止。UNKNOWN/部分完了は元source/予約/所有を保全し二重発行しない。正常用Root/Browser/ownedstopの未実行を補完せず、性能対策・新通常経路/native/451は後続の別受入とする。

## SSC-285：署名拒否・DB/Ref取得前の保持39FD profile

QA047内の内部限定回収を具体化する。対象はBUG1305/YKT1071のcurrent4856/PG3420/BOMdc535a48、boot79a、SIGNED_CURRENTで旧signature stemを拒否した当Java410196/t8469964/ppid410194/argvSHA7da390fcだけ。3502読取proof16145fbc…は全39FD/全task子0・管理DB/advisory0・M/A各一・全24/187/四ordinary/原本Backup/runtime/startup/native不変を二読した。これを旧99/101FD/Ref/DB保持profileの許可へ代入せず、別の取得前profileとして扱う。source署名拒否や旧UNKNOWNを正常closeへ読み替えない。

FD閉集合は0～36、43、128の39件。0/1/2は当SSHの対応stdin/stdout/stderr pipe、3は固定JDK25.0.4/lib/modules、4は署名済PG3420 operations/batch.jar、5～27は当実classpathの固定23 Jar。各regular target/Root所有・group/mode/nlink/全9metadata・file hashと署名187内の対応を固定し、JDK moduleは既toolchain pinへ結ぶ。flagsは3～27/35/36=0100000、0=00、1/2=01。28/31はlinked /run/schubert-nk、29/32はそのlinked /run、Root0755/同dev-inode/type/ACL・flags02700000を検査する。30/33はmaintenance.lockのO_PATH属性descriptor（flags012400000、別OFD）、34は同Root0600/nlink1/size0の唯一FLOCK holder（02100000）。43/128はstartup-admission.lockの同Root0600/nlink1/size0・同一OFDdup/唯一FLOCK（02100000）。35/36はRoot所有の/dev/random・/dev/urandomの固定character deviceであり内容を読まない。socket/Ref/bus/DB/新child・余剰FD/未知targetを許可しない。

過去3502像からfreshへ許す差は29/32の共有/run mtime/ctimeの非減少だけ、旧時刻≦fresh≦その測定上限を保持し、fresh二descriptorの全9値はlinked pathと一致必須。他37FDはtarget/全metadata/flags/同OFD関係/権限・root/exe/argv/cgroup・全task子0を完全一致にする。全fieldを一度でも省略/0化して成立させない。現在の普通API/Web peerはSSC280同様に各role/app・当service/source/cgroup/FDと両端TCPをfresh再認証し、管理peer/advisoryは0を固定する。

host347505/t8560863/ppid4249/argvSHA6db8bae1・同inodegate66306-9337730/fd4のsoleFLOCK、凍結SIGNED_CURRENT failure/log hash・未終端を先に認証する。SSC276のfailed-phase単一read-only接続と取得後の一般critical診断禁止を維持、force unlockしない。同inodequeued後継を用意した一つの回収接続内で、新十Refを保持して当全39/OFD/DB0・全24/設定32/Unit状態18/187/原本Backup/native等をfresh二読・耐久proof保存→そのfresh像からpidfd前後/一回予約/TERM直前再照合→当Javaだけ普通TERM一回（15秒終端・30秒同ticksreap）→子/全FD/管理DB/advisory/M-A/bus消失・四ordinary/全原値保存・新Ref正常返却→旧wrapper終了後同hostgate取得→別wholepostを閉じる。sudo410194/業務Unit/別PIDをsignal対象にしない。変動/unknownではsignal0・隔離・再送0、SIGKILL/DBterminate/VM/Root/Backup/ADMIN/current/epoch/原本変更0。旧stop結果は143/UNKNOWNのまま保全する。

回収後だけ、別new-only工具で同sourceの未実施owned stopへ進む。composer関数の検査だけでなく、最終emitの全Java/Python/実fixtureとsignature stem/boot/source/BOM/全Rootbindingを独立固定値へjoinし、旧boot/stem・誤署名・null/欠落・余剰を取得前に拒否する。旧稼働classやfrozenをhotpatchせず、newABI→正常新scope→別post/nativeで再試験する。この設計公開だけでは実回収・PGPT受入を宣言しない。

## SSC-284（PG/PT、2026-10-14、reload済み保持11FD・shared/runと宣言viewの具体化）

実最終283をlocal及びorigin/mainで確認。BUG1232～1235/YKT998～1001/QA047既承認内、RD/UI・業務結果・Root1800秒/Unit期限不変更、新QA不要。current Main3b7f/PG2126/BOM62213f・bootb2d6の当管理Java101019/t1808679/101FD、唯一Ref101050/t1808864/11FD、sole管理DB101048/PG998-native-stage/idle-TX/71419602、親M-A/同peer双方向TCPを新fullproofへ束縛する。sudo101017/他actor/業務Unitはsignal対象外。独立2342 proof a8eb610cff840dc9be93eb83f59d369097ec145d743c92e62d1e5344a41147ff、全24row/187/原本Backup/native/状態18/署名decl tripleを保持、partial runtime inode4223/4224・644bytes/SHA888ee856を全9metadataとACL/linked path/readonly flagsで照合。旧2332のUNKNOWN/143を成功に補記しない。

子FD0/1は親の対応pipe、2は固定refs log、3は当private systembus、4=/、5=/run、6=/run/systemd、7=/run/systemd/system、8=固定Morning Unit.d、9=同一zz-pg2316-once-resume.conf、10=当private SAVE。全11閉集合・Root権限/cap/cgroup/全task子0/唯一bus名とargv hashを二読する。4～10のO_RDONLY/O_NOFOLLOW/O_CLOEXEC及びdirectory flags、fd9 regular Root0644/nlink1/既byte・hashを検査、別FD/新file/未知差を拒否する。親31/90と子5は同じlinked /runの元dev/inode/type/Root owner/mode/nlink/size/ACLを持つ。過去proofからfreshへの差はこの三FDのmtime/ctimeだけ、旧時刻≦現在時刻≦当fresh測定上限として別保存し、子5のfresh全9値は親31/90と一致必須。他親99FD/子10FDは全9値・target・authority/bus/socket一致、時刻を0化・無視しない。

新only同一接続/十Refの中で全元像・全pair/DB/socket/OFDを二読→独立fresh proofを耐久保存→各pidfd前後・耐久一回予約・TERM直前にそのfresh像を完全再照合する。Refだけ普通TERM一回/15秒終端・30秒同ticksreap→bus消失/親全task子0/失ってよいFDは当子stdin/out pipeだけ→親だけ普通TERM一回/同有限reap→旧actor/全FD/DB/advisory/M-A/bus0・全元像二読・新scope正常→別全post。SIGKILL/DBterminate/他PID/旧toolhotpatch/VMboot/原本補修/permit-epoch変更0。未知は隔離、同signal/reloadを再送しない。

systemdの状態18と設定32を混同しない。partial file後のGC/LoadUnitでMorningのExecStart/DropInPathsが固定元UUID二引数/固定一fileを反映する場合、その既知deltaと全残30値を独立に検査する。正規daemon-reloadでは他UnitのExecStart宣言tripleは同値を維持し、末尾五実行metadataだけがexact CLOSED(n/a,n/a,0,(null),0/0)へ戻り得る。実状態18/Job/PID/invocation/bootと全他config・fileは不変更、余剰argv/unknown/状態変更を拒否する。このviewだけから正常reload・旧scopeclose・起動資格を推測しない。

旧同inodefragmentを再write/削除/再配置しない。署名済み20工具・reservation/logのbyte、固定helperのcontrol-flow（reload return/empty stdout-stderr/verifyの後でpost guardが拒否）、独立PID1/readbackの宣言/状態を相互照合して既一回reloadの実施を分類する。old closeはUNKNOWNのまま、正規owned回収/別全post後に、新M-A/実専用DB/十Refのverification-only scopeで元原本/全24/宣言32/187/partial inode/currentを正常照合し全scopeを正常返却する。さらに別独立postで全資源0・fixed effective --resumeを閉じてからだけ、別observer/一回durable予約/明示resumeを開始できる。verification-onlyでreloadや業務startを追加しない。旧entryをactual0へ書換えない。

PT工具のmkdir時刻にはLinux filesystemのcoarse clockが使われる場合がある。有限操作の下限は操作前に独立採取したkernel realtime-coarseと高精度realtimeの関係/分解能を検査し、既mtime/ctimeからの非減少・現在上限/全identity/content/唯一namespace deltaを維持する。壁時計を変更せずRoot cutoff・epoch・budget精度を緩めない。既partial原本に未採取の時刻を後付けしない。独立過去/未来/範囲逆転/型/null/unknown差の反例、全11FDとCLOSED宣言の再発防止PT、実正規回収/verification/newresume/各postが未完。設計公開はこれらやcoverage/PGPT完了の認定ではない。

SSC283（2026-10-13）：SSC278の署名Morning Unit10配備はrelease/current交換だけで通常Unitへ反映済みとしない。十Unit/kernel/全actor/管理DB-advisory-FLOCK0・当Root真正WARNING/旧managerfailed10・全元像を再認証し、管理gate/連続M-A/専用DB/十Ref下で当source全回帰・独立MUNIT4・全Mainbyte/署名187/SQL28history29を資格したsiblingを正規hostRO・canonicalINVALID/approval/current交換へ進める。新signed current全187資格後だけ、唯一Morning通常Unitをnew-onlypart/root:root0644/nlink1/fsync→元SHA・oldFDを保持した同directory RENAME_EXCHANGE→旧inode私有保持/両directory fsyncで更新、一回期限付き正規daemon-reload。状態18は当旧failed10世代を保持、別設定2はTypeoneshot/SuccessExitStatus10二読を資格。他Unit/drop-in/secret/DB/原本Backup/native変更0、reset-failed/Root再演/旧UNKNOWN成功化0。全新scope正常返却と別全post/新署名byte/旧inode・byte保持後、次合法current/一回freshresumeの実WARNING正常終了を別受入する。拒否はphase/所有を保全しQA047限定現所有回復、旧slot再送0。


SSC282（2026-10-13、BUG1177/QA047）：親の状態FIELDS18とType/SuccessExitStatus設定2を別strict読取にする。状態18に設定を仮想追加せず、設定二keysのduplicate/unknown/欠落/null/不正representationを拒否・Type一致・前後状態/設定不変を確認する。旧1816のinitial-before保存後UNKNOWNは當host288085/t9335833、Java481511/t9066715/101FD、Ref481540/t9066872/4FD、管理481538/PG998/sole71419602/同hostgateへ限定してSSC281のfreshproof/一回子→親TERM・有限reap/queued排他継承/全元値保持/別postを適用する。1822proof9b2f5c8f…は元全像b8ceと保存before全値を別照合、failureRootの既二fileは固定hash・原本として保持。sudoは対象外、旧slot再送/hotpatch/強制unlock/Root再演/正常close推論0。元普通pool上限/全TCP・全品質不変更。


SSC281（2026-10-13、BUG1172～1174/QA047）：当新WARNING保持pairはhost282491/同gate66306-9337730、Java479190/t8906867/101FD、Ref479219/t8907026/4FD、管理479217/PG998/sole71419602を全現在値・qualified helper hashで束縛する。Root13 Run4148e3e8-f107-431a-ab27-d6e6d1f1772e/Activation9adbf05a/failed10は不変。工具番号置換はpg/Pg/PG prefixのnamespaceだけ、UUIDを数字部分で書換えない。§5.2の既pool API2～8/Web1～2（max/min不変更）をrole/app/DB/loopback/元service全freshTCP両端へ検証し、観測2/1や普通backendIDを恒久権限へしない。管理1/activity/socket/advisoryは固定、未知/範囲外/重複/foreignは拒否。SSC276/279/280の単一故障phase回収接続・fresh耐久proof・子→親一回普通TERM/有限reap/同hostgatequeued継承・全原値/普通daemon保持/管理資源0・別wholepostを維持する。旧1802/1809/1810の拒否・UNKNOWNを成功化せず、原本/期待値/品質の緩和0。

SSC280（2026-10-13、SSC279/276）：当retained101FDの共有/run29/32は同target・同directory・前7metadata不変、mtime/ctime非減少を旧proof→fresh像の限定変化として扱う。他99FD/子4FD/全OFD/原本・管理476114activity/socket/advisoryは厳密不変。通常API app2/Webweb1のpoolbackendは元ordinary service PID/ticks/sourceの全freshTCP両端へ毎guard再結合し、古いbackend IDを不変管理権限へしない。別role/不足/余剰/foreign/mgmt変更・shared時刻逆行/他属性変更は信号前拒否、fresh二読/耐久proof/同一回予約/pidfd・元全後条件を省略しない。旧失敗の成功化/DBterminate/SIGKILL/業務再演0。

SSC279（2026-10-13、BUG1165/1166、QA047）：当停止前WARNING guard拒否の旧1774/UNKNOWN pairは、旧凍結14と実Java476087/t8492401/101FD・子476116/t8492565/4FD・元全24/32/187をfresh全値で認証する。Root13 DONE10/managerfailed10は不変の別事実。通常API/Webの正規DBpeerをcold前提0へ消さず、API451130のapp2・Web452144のweb_session1・retained476087のbatch1/同server476114を全TCP inode/loopback/固定DBへ結び、管理71419602唯一を別検証する。未知/不足/余剰/foreign/changeを拒否。旧工具hotpatch/再送・新permit・業務再演なし。SSC265の子Ref→Java普通TERM/有限reapと全FD/OFD・原本・通常daemon・管理peer/lock・新十Ref正常返却を当profileへ具体化し、独立proof/一回予約/別wholepost前に回収完了を宣言しない。

SSC278（2026-10-13、BUG1162/YKT930）：署名対象Morning親Unitは唯一SuccessExitStatus=10を宣言する（正常0はOS既定）。実Java完成出口/同原本0・10と一致させ、30/50/70/143やsignal/timeout/UNKNOWNの非成功を維持する。独立Unit golden/余剰code拒否、署名BOM/実Unit readback、fresh同Root PID1 job done/原本/元期限・全後条件を同sourceで確認する。Unit変更は停止・保全・正規code-only配備契約内で行い、live Unitのhotpatch/reset-failedや旧failed10の正常化は禁止。未受入実装・工具・証跡を設計main反映へ混ぜない。
SSC277（BUG1157/YKT925）：SSC276の当Bootstrap全99FDの共有/runは実認証31/90（旧unused29/32ではない）。全FD数一致からlayout一致を推論せず、全argv/authority/cgroup/99FDset/全target/他97全metadata、31/90の同linked/run dev/inode/Root/type/mode/nlink/size/ACLを固定する。共有二時刻のみ過去像から非減少/current測定上限でfresh観測し、同fresh全像をpidfd/予約/TERM直前へ完全固定する。旧1724はfresh保存/予約/TERM前拒否、再送0。hostgate待機はTERM未発行の失敗なら旧owner保持を明記、正常一回TERM/reap後だけ同inode新gate取得完了を要求する。その他SSC276の全原値/DB0/一回正常TERM・有限reap/別post/UNKNOWN維持条件は不変更。

SSC276（BUG1156/YKT924/QA047内部復旧）：BootstrapのDB監視Expected constructorが取得後に拒否してlease未代入・Ref前retainとなった場合、旧UNKNOWN/byte/slotを保持する。現在全99FD/argv/exe/Root権限/cgroup/全task子0、soleM-A/OFD・凍結111・署名current2741/PG1638・元24DB/32設定/187/原本Backup/native18を独立証明する。serverpeer/advisoryが期限で消失した場合もSQL0/当ESTABLISHED socket0をfresh二読し、正常closeへ換算しない。全proof3b84d06a…は当383695/7281859のみ、sudo383693/別PIDを対象にしない。失敗phase静止・Ref/Unit/credential前を実source/stackで資格した読取接続だけを許可し、fresh signal guard中のguestobserver禁止を維持する。

旧hostwrapperの現在PID/ticks/argv/FD/同inode soleFLOCKを再認証し、force unlockせず単一回収operatorへ引継ぐ。当TERMで旧wrapperが終了するまで既存gateを保持し、その終了後は同inodegateを新operatorが有限待機取得する。他管理接続/observerの発行0、競合/owner差/期限超過は隔離する。同一guest接続のfresh全99二読・全元値/DB0をsignal前に私有耐久保存し、旧proofとの差は共有/run29/32二時刻の非減少/current上限だけ、同fresh像をpidfd前後・新一回予約・TERM直前で完全再照合する。当Javaだけ普通TERM一回/15秒終端30秒同ticksreap、別wholepostで全旧資源0/元値不変/新Ref正常。SIGKILL/DBterminate/他PID/業務/current/原本/VM変更0、旧closeUNKNOWN/失敗保全。

新DB監視工具の取得前検査はfile/hash/import閉包だけでなくactual Expected constructorまで含める。管理labelはPG後3又は4桁＋限定suffix、role/database/readOnly/advisory契約を独立境界testで確認し、ロック/DB取得前に現label/role/schemaのconstructorを検査する。dummy backendは入力ABIの資格だけに使用し、実DBのbackendStart/socket/identity/advisoryを取得後に同peerで再認証する。失敗工具/凍結classを上書きせず新versionで正常scope/別postを閉じる。


SSC275：BUG1152/YKT920、SSC274子291242/5962938は一回普通TERM・全task子0/同ticksreap/bus消失まで閉鎖、親291213/5962776はreserve後guard例外でsend前拒否（実payload ffbf5516032bc0540d4b212ececee9ac54c8d7be1bba2afd9c1f676e68e636eaのreserve→send順とprivate traceback照合）。旧親予約/失敗/143UNKNOWNを成功補記・再利用しない。新PG1672独立proof537aaccf3ff3f98e17e71dbda28fa7bfe671e44699f9b7d59c6fde9241dd93aaは当親99FD・子0・唯一DB291240（同role/app/backendStart/双方向socket/71419602advisory）・M-A sole/OFD・全原値不変を現在認証、旧101FDから消失は当子pipe100/101のみ、99の他差は/run29/32二時刻だけ。new-only同一管理接続/新十Refで全99fresh二読/旧guard完全一致・共有二時刻だけ非減少/current上限を耐久保存し、同fresh像/唯一DB/M-A/child0をpidfd前後・新一回予約・TERM直前に照合して当Javaだけ普通TERM一回/15秒終端30秒reap、別全post元24/32/187/原本Backup/runtime/nativeと99FD/DB/advisory/MA/bus資源0を閉じる。新host排他gateを同接続開始前から終了まで保持し、critical区間はhostjob付着/hostlogだけ、別guestSSH診断/observerを開始しない（必要通常observer契約を一律廃止しない）。guard変動ならsignal0隔離/再送0、SIGKILL/DBterminate/他PID/Unit/業務/current/epoch/VM操作0。正常全post後にだけ別new-only依存閉包是正工具へ進む。

SSC274：BUG1150/YKT918のPG1661unused配置はarchive suffix不一致で配置前拒否、現在Java291213/ticks5962776（sudo291211非対象）と唯一Ref子291242/ticks5962938、DB backend291240を保持する。PG1664独立読取proof c0036f9a79672f32ad9c51453b7ca16e067d4ec34cc183d6321ab63b42fe0e8aの全101/4FD・argv/exe/root権限/cap/cgroup/親子全task、M属性30/33別OFD・保持34、A43/128同OFDdup・全global soleFLOCK、schubert_batch/PG998-native-stage/同DB・idle transaction/同71419602advisory/実双方向TCP inode、子の唯一private systembus名・tenRef、current4d6/1544/boot3d69/全24DB32config187署名・原本Backup/runtime/native14不変・candidate1638未配置を再認証する。旧noDB97FD回収許可を流用しない。新only同一管理接続で新十Ref保持、旧proofとfresh全current二読を分離して耐久保存、共有/run FD29/32二時刻のみSSC273と同じ非減少/current上限・全他field不変でfresh測定、同fresh像をpidfd前後/耐久一回予約/TERM直前へ完全固定する。まず当Refへ普通TERM一回・15秒終端/30秒同ticksreap・bus名消失、親は全task子0、失ってよいFDは当子stdin/stdout pipeの対応FDだけ（余剰/別FD/再利用/新子拒否）、他FD/全guard/soleDBpeer-MA保持を再照合して親だけ普通TERM一回・15秒終端/30秒reap。各段階unknownは隔離し再送0。全二actor/全FD/bus/DBpeer/advisory/MA消失・全原値二読・新Ref正常閉鎖を別独立postで閉じる。SIGKILL/DBterminate/他PID/Unitstop-start/reload/Root/Backup/VMboot/current/epoch/許可変更0、旧143/closeUNKNOWNを成功化しない。候補入力は次new-only工具で実archive basename/hash・bundle/signature・helper/classes/transitive importの閉じた集合をM/A/DB/Ref取得前に検証し、failed slot hotpatch/再placeはしない。

SSC273：SSC272当289328/5627480/97FDの共有 `/run` 祖先FD29/32の過去mtime/ctimeだけで回収を拒否した場合、旧proof6297…/時刻を改変せずcurrent fresh測定と分離する。dev/inode/type/Root owner/mode/link/size/ACL・linked path/namespace、全argv/cap/cgroup/FDset97・他95FD全metadata・M-A唯一FLOCK/kcmp・全原値24DB/32config/187/原本Backup/runtime/native14・十kernel/DB0は旧proof完全一致必須。FD29/32の二時刻だけを非減少/current測定上限内のfresh観測へ記録し、他差/未知を拒否する。新SSHが共有/runを更新し得るため、新only同じ読取接続・十Ref保持の中で全current像二読→signal前に独立実proof・私有耐久保存→同fresh全97像をpidfd前後/一回予約/TERM直前に完全再照合する。時刻の無視・0化/Production ancestor変更/oldclose補完0、保存/Refで変動した場合signal0・旧slot再送0。SSC272の一回普通TERM/15秒終端30秒reap/当Javaだけ/全post/業務変更0・old143UNKNOWN保持を維持し、全正常回収後のみ別fresh四tuple是正のunused候補保守へ進む。

SSC272：current4d6/PG1544/boot3d69のPG1648placeがSIGNED_CURRENTのLABEL旧値に拒否された場合、DB/Ref/配置前・全task子0の固定Java289328/ticks5627480/argvSHA2f9c6368…だけを当PG1651proof6297a9d8…へ束縛する。frozen1645全135hash/全argv/exeRootUID/cap/cgroup/97FD、全原本24DB・32設定・187署名・Backup/runtime/native current8歴史6/十kernel0/DBclient-advisory0を二読する。M inode1997の属性FD30/33は互い及びFLOCK34と別OFD、A inode1998の43/128はkcmp同OFDdup・fdinfo両FLOCK、global各sole289328を確認し、属性FD/lockFD/dupをinodeだけで同一視しない。当完全proof・同ticks再照合・耐久一回予約/pidfd普通TERM一回/15秒終端・30秒有限reap/別全postだけを許す。sudo289326/他PID/子/強制kill/DBterminate/業務操作/Current-epoch-approval-permit/原本Backup/reload/VMboot変更0。未知は隔離・再送0、旧143/closeUNKNOWNは正常化せず保存。全97FD/M-A/旧owner消失・元全値二読・新Ref正常を閉じてから、別fresh正常scopeでLABEL/STEM/SOURCE/RELEASE四tupleの完全一致を独立検査したnew-only unused候補保守へ進む。新source2741/PG1638の配備/真正Root/native/正式は別受入、RD/UI・期限・品質不変更。

SSC271：SSC270のPG1562でcanonicalzz作成/reload後のREADONLY_PREPARED/KeyErrorが残る場合は設定を再発行しない。当current4d6/1544/boot3d69/元pending15700-9e706、frozen72e34dbd8、Java105206/ticks3041121/Ref105232/ticks3041209の実父子/argv/helper/現署名187・M-A/同batchRWReadCommitted peer/advisory/十Ref/privatebus・全原値/旧Root143/DONE無しを二読する。現在公開runtimeはtmpfs Root0755→fixedUnit.d0755→canonicalzzRoot0644・singlelink/ACL0、独立署名base/native＋元run二引数と有効ExecStart/DropInPathsだけの正規差へ固定し、旧scopeのbefore-image又は正常closeを補作成しない。新proofの全現在値を耐久保持後に当Ref→Javaのpidfd普通TERM各一回・同ticks有限reap、旧中断143/closeUNKNOWN保持、別独立全post/資源0を閉じる。次の別fresh正常M-A/RWbatch/advisory/十Ref/原本Sessionは既公開設定のverify-onlyであり再prepare/reload/unlink0。全正常と別post後のみ新observer/耐久一回startへ進む。未知owner/差分/partialは隔離継続、一般復旧/旧成功化/手DB・epoch・permit/newstart0、品質/1800秒/RD/UI不変更。

## SSC270 当current pendingのcold一回用runtime接続

PG1556/1558で正常code-only/別全postを閉じたsource4d6bcbddb417b76d27e52d5d9640752c300edccf/PG1544/BOMe36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c/boot3d69f5af-6bac-46b1-a540-7591c4a79a0dを、SSC198/259/260の一回用runtime契約へ接続する。元run15700a87-9117-4f63-a0ff-768dd604d0f1/cutoff2026-10-11T21:18:59.040097Z/activation9e706936-a3c9-4a09-bb66-e2b1e8bbef66とbegin、旧Root1456failed143/DONE無し、旧INVALID/permit・全原本/24表/Backup/nativeは保持する。旧D5 source/run/profileを現在値へ流用しない。

別fresh M→A→実RW batch ReadCommitted/advisory71419602/heartbeat→private十Ref・全署名187保持FD下で、現在tmpfs Root:Root0755/ACL0の`/run/systemd/system`を祖先保持・直下空/Unit.d不在へ二読する。SSC259のmkdirat0700/同inode0755/dirsyncと全EXCL/NOFOLLOW/write/force/close契約を維持し、canonical `schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf`だけをRoot0644/new-only作成する。固定署名Morning base＋既pg477 native literalから `--resume 15700a87-9117-4f63-a0ff-768dd604d0f1`二引数だけ追加し、一回reload後Morningの有効ExecStart/DropInPathsのみ正規差、agent1/旧native/他全設定と十Unit履歴/kernel/全原値不変を照合する。設定成功は起動authority又は親成功ではない。

全DB/FD/十Ref/bus/A/M正常帰還と別全post後だけ、別fresh observer/耐久一回予約/外部Root通常resumeへ進む。Productionだけが新Root/epoch/permit世代を発行し、元1800秒/既Unit期限・元成功handle再用・API保持Web/Caddy/真正DONE/owned逆順停止/native/同source451を維持する。unknown/partialはownerと全原値を保全し、同slot再prepare/reload/start、old/run復元、手DB/epoch書込、旧143の成功化0。独立literal/全IO fault/null/foreign/effective順序/競合/原byte保持と当source実postへ追跡する。

## SSC269 保持inode filesystem fresh等価分類（2026-10-12）

全原本graph二読/全外部boundary再検査を維持したまま、保持/proc/self/fd capabilityのfilesystem判定をLinux/glibc LP64公開statfs ABIへ置換できる。許可済ext2/ext3/ext4はmagic0xEF53の共通familyとして内部Snapshotへ記録、xfs0x58465342/btrfs0x9123683E/tmpfs0x01021994は別分類。LOCAL許可意味、runtime tmpfs必須/durable非tmpfsかつRW、readonly/ACL/metadata/owner/全原本/期限は不変更。未知magic/ABI/失敗/無効capability拒否、filesystem/graph/認可cache又はscan省略禁止。familyは内部判定だけでUI/電文/DB業務値不変更。実header/版・独立magic/ABI120byte-offset0/retainedFD/tamper/例外/当source影響PT/必要全回帰・当Root再発防止実証が揃うまでtimeout解決/正式にしない。

## SSC268 publication-only正常復旧後のUnit GC readback（2026-10-12）

SSC266/QA047の正常同fresh所有によるExpiry→Artemis→Cleanup停止・真正PID1/vendor全証拠・全原値不変・canonical型付きpublication intentのみ退役・全管理scope正常返却を、当source/boot/BOMのimmutable warm receiptとして保持する。Ref返却後のsystemd Unit collectionによりcurrentを再Loadした際、同三Unitの補助INV/start/end/code/statusが空/0、ExecStart補助が閉じた未実行値へ戻る場合を別current lifecycleとして扱い、0表示をwarm停止や旧Root成功の証拠にしない。

currentがwarm18/full32と一致する場合はそのまま照合する。GCの場合は固定同三Unitのfull18でinactive/dead/success・MainPID/ControlPID0・Job空、InvocationID空・ExecMainStart/ExitTimestampMonotonic/Code/Status各0だけを認め、Id/LoadState/Type/Restart/RemainAfterExit/KillMode/SendSIGKILLほか全残fieldを当warm宣言と一致させる。full32のhardening/Requires/After/Role/実Unitfile/source/署名/argv/固定pathを不変とし、ExecStartの宣言path/argv/ignore_errors tripleのみ同一、補助はexact n/a/n/a/0/(null)/0/0である。片側・未知・nonzero・別宣言は隔離し、GCへ正規化しない。

真正warm PID1/vendor/当stop予約・同scope fullpostを先に検証し、当boot/BOM/current、全24DB/原本/Backup/credential/旧proof/epoch/permit/nativeと全task/FD/lock/peer/advisory/bus消失を独立二読、current metadata十Refを新しく通常返却する。warm/currentの相違は補助履歴だけに限定し、stop/reload/起動/epoch再失効/intent再退役/DBwriteは行わない。旧Root143/旧UNKNOWNは維持、限定GC readbackはRoot/DONE/全native/正式品質へ加点せず、正常post後のみ別fresh same-run一回resume候補へ進む。

## SSC266 failed publication-only current Rootの限定復旧（2026-10-12）

QA047承認内、RD/UI/外部仕様不変更。Main769/PG1292/schema028/現boot3d69のRoot1456（INV1ee3b3…/Job13033/start5711141318us）が元1800秒timeout143、当run15700a87…/cut2026-10-11T21:18:59.040097Z/activation9e706936…のactive保持・DONE無しの場合を限定する。startupは同INVALID epoch・同公開permit・permit-start.intentの三entryのみで、owner/API-Web launch/service intentは無い。SS174/179/209/211のPair/API-child profileを仮構成して適用しない。

現在1477の原観測bcfd08285abe448ebe28c2adffc39acca0346e25b1769c44d72f43290da38cd5をdata baselineとし、別fresh管理所有でM→A、同生成lock inode/本人FD・kernel、実batch readonly DB/同peer専用advisory/heartbeat、十metadata Ref・全full18/full32と実設定、固定署名187/実Unitfile/current/credential、全24DB/原本/Backup/旧proof/nativeを継続認証する。読取観測だけから操作権限を授与しない。期限143・元close UNKNOWNは保持し、当管理scopeが正常でも旧親の正常終了へ変換しない。

Artemisは固定simple/現PID41805/ticks636663/INV47be234…/start6366634712us、真正PID1 done（Job13935）一記録をmanager start/kernel identity・argv/authority/cgroup/全FD/lock・元Root期間へ結合する。simpleに無いStarting記録を生成しない。Cleanup/Expiryは現active-exited0/同INV・start/done二記録（Job13492/14379）と元Root期間を要求する。未知peer/別cohort/設定差/原値差は隔離し操作0。

同fresh所有の全proofが成立した後だけ、実起動順の逆順Expiry→Artemis→Cleanupを一回予約付きで通常owned停止し、Artemis真正vendor正常終端/PID1・全task/FD/lock消失、oneshotの真正停止後条件、固定十Unit/kernelと元全原値不変を検証する。元INVALIDを再revoke/invalidateせず、同permitの型付きbyte相関だけを検証する。readRevokedのformer-issued値は構文相関に限定し、実ISSUED履歴/許可/失効操作の証拠へ使わない。

正常全terminal/current証明・元原値をgateとした同namespaceのBackupStartIntentFilesのtyped observeQuarantine→retire→dirsyncだけでpublication intentを退役する。任意unlink/owner生成/Pair生成/不存在intent生成は0。epoch/permit/active/DB/Backup/原nativeは保持する。不確実な退役は同現M-Aでstrict publication quarantineを保全し、正常scope返却・本人資源0・独立全postまで後続を止める。新epoch/permit/START/DONE/DB手修正・旧/run復元・既成功Root/ADMIN/Backup/配備/停止の再実行0。

同所有下の原本whole graph/署名/metadata syscallのreadonly費用測定を許し、計測は権限や業務成功の加点にしない。原因是正は別固定source/独立tamper・race・null/全品質・実同条件再発防止へ結合し、security検査・元1800秒・coverageを緩和しない。有限復旧と全新scope正常返却/独立post後のみ、既SSの別fresh同run一回用resume又は必要code-only配備へ進む。実実装/PTは未完。

## SSC265 固定current cold子起動前失敗の父限定handoff（2026-10-12）

SSC264のPG1447子がAST namespaceのKeyErrorでRef/保持inventory/finite write前に終了し、父だけがDATABASE_ADMISSIONでM/A・readonlybatch/advisoryを保全する当世代に限定する。current769/PG1292/boot3d69・source0fe8/frozen1444/stage1446・Java3323/ticks388541/全argvSHA6f8b48e1…・現exe/loaded tool hashes/authority/cgroup/全task-child集合・全FD/socket・現M/A inode/OFD-FLOCKを二読する。sudo wrapper3321を父Javaと混同せず、旧PIDを将来actorへ再利用しない。Source/partial/debug原値を私有保存し、子exit/父UNKNOWNを正常に補完しない。

全10 cold18/full32/kernel、全24DB/原本・Backup・credential/署名187/18Unit実file・current/approval/pin、root maintenance.lock/startup-admission.lock/maintenanceの閉3entry・namespace/epoch/active不在を同Source1440封印へ照合し、当父の実専用batch backend/application/loopback socket/peer/advisoryと全他client0を証明する。本人pidfd→全二読→NOFOLLOW/new-only一回TERM予約/force+dirsync→予約後全再読→当本人普通TERM一回→deadline内の本人/全子/task/DBpeer/advisory/FLOCK消失→全元値二読/正常metadata閉鎖の順。SIGKILL/別actor/DBterminate/再signal/prepare/ROOT起動/原本又はnamespace修復0。未知/変異/非終端なら新観測scopeで隔離し次操作へ進まない。

この限定handoffは元Javaの正常close証拠ではなく、元143/UNKNOWNを保持する。全後条件後にだけ別freshM-A/current修正sourceからnew-onlycold準備を行う。旧tools/root/署名公開/Backup/ADMINの成功は再発行しない。実再発防止はnamespace exec先行oracleと同currentSource全guard/正常資源返却/独立postへ結び、handoff又は設計公開を正式PGPT/ITSTへ加算しない。

## SSC264 current全native不存在のcompleted-cold有限準備（2026-10-12）

QA052の専用LAN移送後もSSC165174/243246のcold隔離条件を維持する。current769/PG1292/BOMecae・新boot3d69、保持真正Root d2e3a86f-27a4-4c2a-be21-b512eebf1216/cutoff2026-10-10T23:30:23.481632Z/ACT841b507c-2713-4ffe-8882-68f5fb3f87f5/DONE2026-10-10T23:54:39.918039Z/原byteSHA59f3、全24DB/Backup/credential/完全原本・署名187/28SQL29history/十cold18-full32を新同sourceで二読してから処理する。旧startup/native tmpfsの消失を旧intent退役成功・旧close正常へ変換せず、hostに残した旧native/failed原byteを現/runへ復元しない。物理guest byteの移送比較だけでadmissionを授与しない。

全profile物理親も不存在の場合に限り、別fresh新M→A/現lock同inode/専用readonlybatch/advisory71419602/実heartbeat/十Ref/完全原本Sessionと全必要FDを連続所有し、既承認current releaseの必要self-bindRO→full pin/Ed25519/187 verifier→固定startup/backup-request/cleanup-request/expiry-request/pt-coverageをnew-only有限作成する。既maintenance Root0700/空は元inode/全属性で保持、root Root0755/ACL0の許可deltaは追加五dirのentry/link/sizeとoperation内mtime/ctimeだけ。currentlink/approval/pin/署名/原本/DB/旧Backup/設定・runtime/Unit及び旧成功を変更しない。新epoch/INVALID/permit発行、start-stop/reload/DDL/business writeは本準備に含めない。

coverage親は新Root:Root0755/ACL0、閉12childroleはbackup/cleanup/expiry/inspector/ordinary-api193/ordinary-bootstrap196/ordinary-inspector196/ordinary-web193/parent/root-api/root-api193/root-web193。全childはempty0700/ACL0/tmpfs-RW/nlink2。同current固定NSSでbackup=schubert-backup（992:977）、inspector・ordinary-inspector196=schubert-inbox-inspector（991:976）、ordinary-api193・ordinary-bootstrap196=schubert-api（999:981）、ordinary-web193=schubert-web（997:980）、他六Root0:0を独立固定profileと完全joinする。各actual effectiveagent/RW/User/Group/固定role名を設定・NSS・held inodeで認証し、任意role包括作成・既inodeへのchmod/chown・未知entry/ACLの修復・旧execの再作成をしない。完全に存在しない当fresh coverageに対する初期権限設定だけが対象で、SSC263既親への一role追加と混同しない。

前認証→held mkdirat/O_EXCL/NOFOLLOW→新heldFDでowner/mode→empty/ACL/FS/同dev-inode二読→子/親dirsync→原24/32/187/原本/Backup/既lock-maintenance/runtimeの全不変・新閉集合→DB rollback/close/server0→全Ref/FD/bus/A/M正常返却→別独立post/新before、の順。primary/secondary close不明又は部分準備は私有保全し同slot再prepareしない。全対象source/run/独立oracle/故障・null・競合・正規元値後条件を残す。準備完了は起動権限・新Root/Inspector/native/CHR/四counter100/正式451又はIT/ST完了ではない。

## SSC263 cold固定native role matrixのordinary Bootstrap補足（2026-10-11）

SSC193/195/196/234の固定PT native profileは、通常RootとAPI/Webだけでなくordinary Inspector/Bootstrap oneshotを含む。SSC254/255のcold有限五role整備を全profile整備済みとしない。固定profileのrole名、全十Unitのloaded/type/effective agent/RW宣言、現在NSS UID:primaryGID、実directory/inodeを完全joinする。ordinary-bootstrap196はschubert-nk-bootstrap-admin.serviceの専用oneshot/固定API identityに対応し、API起動やpermit発行の代用ではない。当current769/PG1292ではagentとRW宣言/NSSは適合し当roleだけ物理的に欠落、current全11role/18execは保全対象。native_treeのrole必須拒否を緩めず、正規準備後の新beforeを用いる。

既真正Root1322の原本DONE/元1800秒、普通四所有停止1336・独立全post1340、署名187/28SQL29history、startup ISSUED/原run-cutoff-activation、全24DB/Backup/credential/全32設定/全元nativeを先行再認証する。失敗工具1362の親子/Ref/M-Aの限定回収1368・全資源0を先に閉じ、旧actual143/UNKNOWN/normalclosefalseを維持する。別fresh M→A/専用readonlybatch/advisory71419602/実heartbeat/十Ref/保持common directory FDでだけ、欠落ordinary-bootstrap196一件をNOFOLLOW/mkdirat0700/new-onlyで作成し、保持子FDへ固定API UID:primaryGID（当NSS999:981）を設定、empty/0700/ACL0/tmpfs-RW/dev-inode保持を二読して子と親をdirsyncする。既roleへのchmod/chown、任意role包括作成、coverage親0755の再変更、元exec削除/書換えをしない。

親coverage inodeはRoot:Root0755/ACL0/元11role閉集合（backup/cleanup/expiry/inspector/parent/root-api/root-api193/root-web193/ordinary-api193/ordinary-web193/ordinary-inspector196）を保持し、追加一件だけを許す。全元子entryの9metadata/ACL/contentは完全一致、親のdev/inode/uid/gid/mode/ACLは同値、nlinkだけ+1、tmpfs directory sizeは当一entryの限定増分、mtime/ctimeは実mkdir/dirsync区間に限定する。未知inode/外entry/元子変化/FD又はDB所有喪失/close不明では隔離し、同slot再prepare・Root/Unit再起動・旧成功補作成をしない。全24/32/187/原本/Backup/startup・全新scope正常と資源0を独立postで再照合後に、新beforeと専用既存ADMIN正常20/元30秒・当同Invocation terminal/closing二native（SSC234）を受入する。設計反映・role準備・正常20/native・四counter100/正式451を別判定とし、PG/PTからIT/ST完了を宣言しない。

## SSC262 ordinary真正ISSUED-DONE後の署名code-only有限公開（2026-10-11）

§11/SSC190の通常全停止code-onlyは、ordinary親の真正PID1 start/done・原本SUCCESS/10step・正常owned停止・全kernel資源0と、現boot/原run/cutoff/activationを先行認証する。startupに正規ISSUED epoch及び旧permit/owner/launchが保持される場合、SSC249のcold空startupを現在値として偽装しない。対象currentD5/PG1068/BOM0b61→unusedRO new769/PG1292/BOMecae/187/schema028は、既真正Root1240/9f651096/27accac0/cutoff2026-10-10T20:03:22.718197Z/DONE2026-10-10T20:22:34.439375Zと、正常stop1256/全post1303を実初期条件とする。これは固定PG/PT profileの詳細で、RD/UI/業務/DIF/権限/元30分及び品質を変えない。

別fresh M→A・readonly batch/advisory71419602/実heartbeat・十Ref・真正原本Session・old/new全signed inventoryと保持directory/entry FDを連続所有する。新UUIDv4を選び同boot/元run/cutoff/activationのcanonicalINVALIDを既Production invalidateでforce/dirsync/再読→独立literal候補version/BOMのRoot0400 approval atomic置換/dirsync/再読→固定new-only sibling symlink/dirsync→同filesystem RENAME_EXCHANGE→newcurrentと旧同inode linked sibling全属性/target/ACL二読→旧linkを固定private SAVEへ一回atomic移動/両dirsync→全新gateと全未変更値を再読→DB rollback/close/server0→Ref/FD/bus/A/M正常帰還→new-only完了と独立post、の順。管理INVALIDをRoot起動許可にせず、新permit/owner/launch/Unit start-stop/reload/DB business write/DDL/Backup操作を追加しない。

有限oracleはbefore/epoch/approval/link-staged/exchanged/old-linked-private/releaseを閉集合とする。startupではepoch.currentのみcanonical新byte/inodeへ替え、他全entry・byte/hash/target/ACL/9metadataを保持する。旧epoch/approval regular FDは原byteとdev/inode/uid/gid/mode/size/mtime/ACLを保持し、正規unlinkのnlink0と当operation内ctimeだけを別検査する。旧current symlinkは全区間nlink1・同inode・oldtarget・ACLを保持し、交換/移動の有限ctimeだけを許す。unlink-O_PATH xattr取得を推定したり属性検査を省略しない。各親dirの同inode/owner/mode/link・正規entry集合/size・mtime/ctimeの有限効果をphaseごとに限定し、他全field/集合/Root binding/全原24表・DONE/Backup/credential/oldrelease/native/Unit/config/runtimeは不変。atimeのみreadlinkによる読取時刻として9field外、mtime/ctimeは除外しない。

独立oracleは候補の実current値から承認内容を導出しない。固定version/BOM/canonical schemaと事前保持値・当operation timeboundsから期待を作り、unknown/NULL/重複/不正順/別boot-run-act-source・外entry・全field変異・短IO/force/close/競合を負例で閉じる。新公開途中又はclose不明はそのowner/Ref/FD/DBを隔離保持し、同slot再公開・旧成功補完・旧permit/approval fallback・一般rollback/手修復0。真正oldlink移動済みなら再exchangeせず保存済みphaseから限定再認証する。設計公開/工具host PT/code-only成功と、newsource真正Root/defaultexport/native/CHR/全四counter100/451正式を別に受入する。

## SSC261 内部保持channel資源port（2026-10-11、SSC193 native採取の補足）

固定native採取の観測IoはUID/cgroup/FS/inode/属性等のdata-only契約を維持する。別package-private資源portで承認済み保持entryのchannel READ/WRITE・size/read/write/force/closeだけを分離し、native adapterは既FileChannelの通常操作をそのまま使う。任意path/name/profile/configによる開放や権限付与を追加しない。固定profile/name/祖先・owner/gid/mode/link/ACL/FS/readonly、保持inode前後一致、新規file/partial保全、全byte SHA、全resource通常closeという成功条件は不変更。null port/channel、0進捗、不正長・short/long read、前後size不一致、force/close失敗は非成功、NPEをcatchして正常化しない。

agent pinのsize307843/readonly scalar検査を独立純検査へ分離しても、物理Root祖先/保持file/fullSHA検査を代替するauthorityにはしない。PTのresource fault fixtureは進捗/size/closeと原byte/全FD後条件を独立literalで照合し、native adapterの実filesystem正常系とモデルscalar/故障を区別する。モデル試験を本番Root/Unit/署名/pin成功に加点しない。coverage条件削除/到達不能除外/人工終了で100%を作らず、source変更後は必要fresh品質と当source nativeを別に閉じる。RD/UI/通常起動・画面・電文・DB・credential・承認DIF変更0。

SSC260はSSC259の一回用basenameを`zz-pg1160-once-resume.conf`へ訂正する。既`pg477-native-coverage.conf`より後のmerged basename順を独立に確認し、当署名base/nativeから同run --resume二引数だけ追加した有効ExecStartとagent1を必須とする。file内の文字列が正しくても有効宣言へ現れなければ不合格・start0。旧誤順`pg1160-once-resume.conf`はRoot0644/singlelink/647byte/SHA d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0として私有原byte・全metadataを保全、固定失敗owner回収後の別fresh M-A/RWbatch/advisory/十Refsでのみheld typedentry退役/dirsync・訂正reload一回を実施し、新正常scope/全post後だけ空同inode Unit.dに正規fileをnew-only準備する。Unit.d/既nativeの修復・削除、旧prepare/reload再発行、旧close正常化はしない。

reloadによるExecStart表示は全field parserで設定path/argv/ignoreと後半start/exit/pid/code/statusを分離する。前三fieldは各署名declと完全一致（Morning正規resumeのみ差）、他全設定不変、後半は元全tuple又は当sameboot正規reloadのempty(n/a,n/a,0,(null),0/0)だけ許可し、元rawを私有保持・全18実Unit history/kernelの独立不変照合を維持する。任意field除外・部分reset・未知type・旧history削除は禁止。独立basename-order反例/全field悪性変更・null/二重agent/foreignargv/部分historyと当source実有効宣言/全新scope/Root/nativeの証跡をSS353へ追跡する。

SSC259（cold PT限定）：SSC258全十物理terminal・正規失効/intent退役・全資源0、SSC255五native-role/親0755と全原値postを先行し、別fresh M/A・実batch ReadCommitted/RW transaction/backend・exclusive advisory・十Refの連続正常管理scopeで当samepending一回用runtimeを準備する。現在Root:Root0755/ACL0/tmpfsの`/run/systemd/system`をNOFOLLOW FDで保持し全祖先・直下を二読、未知Unit/drop-in/子/ACL/owner/RO/modeを拒否する。今回cold直下空かつ`schubert-nk-morning-controller.service.d`不存在の場合のみmkdirat0700→NOFOLLOW held child→same inode/Root:Root/ACL0確認→0755→child/parent dirsyncとする。既Root:Root0755/ACL0の空Unit.d再用はSSC198を維持し、既存directoryの修復・削除はしない。既startup・原本・DB・Backup・PT native全値を保持する。

当sourceD5/PG1068の署名Morning baseと固定native literalから`--resume 343a5a1b-d064-47d5-88c2-31c36d7ba7a4`二引数だけを追加する。`pg1160-once-resume.conf`を保持Unit.d FDからEXCL/NOFOLLOW/new-only Root:Root0644で全byte write/force/dirsyncし、daemon-reload一回後、MorningのExecStart declaration/DropInPathsのみ正規差、他全設定・十Unit history/kernel・原値を再照合する。全new DB/Refs/FD/A/M正常帰還・独立post後のみdurable予約/新observer/一回外部startへ進む。不明・部分作成・未知closeは全保全して隔離し、再prepare/start・手unlink/reset-failed/旧permit再用0。真正親終端後、別owned scopeで一回用設定だけ正規退役する。

activeありsame-run resumeは§6.15に従い既run/cutoff/activation/beginをそのまま返す。当run343a5a1b-d064-47d5-88c2-31c36d7ba7a4/cutoff2026-10-10T12:40:27.396847Z/activationada3f7ff-8287-48d7-9ba9-5cce71f61bd3を維持する。新しいのはRoot PID/ticks/Invocation/元30分budgetとepoch/owner/permitの所有世代であり、旧activeを消して別activationを作らない。元二Backup SUCCESS/manifest/handleを再用し業務副作用を重複発行しない。Production template・業務RuntimeDirectory・原本・時計・品質条件変更0。独立literal/短write/全IO故障/foreign/null/競合/二重操作拒否と実samepending Root/nativeをSS353/SSC259へ追跡する。

SSC258：当全十Unit実matrixは元七inactive/failed＋Expiry/Cleanup oneshot active-exited＋Brokerrunningである。Broker正規一回stop後ExpiryはRequires依存でinactive-dead、Cleanupは元active-exited/全18保持。固定旧UNKNOWN ownerのread-only保存/handoffではCleanupを停止せず、旧owner/資源消失後の別fresh正常管理scopeで元同CleanupINVへ一回正規stopして全十物理terminalを閉じる。既Broker/Expiry/他七stop0、元history/native/設定/原値保持、canonical元ISSUEDrevoke/単一heldAPIintent退役条件は全十terminal後のみ。PID0をinactiveと同一視せず、独立literalmatrix/依存/PID1/全18/負例と実postをSS353/SSC258へ追跡、設定byte/Production/業務仕様変更0。

SSC257：SSC256の九terminal記述を優先訂正し、Expiryのoneshot active-exited/PID0/RemainAfterExityesと物理inactive-deadを区別する。既Requiresにartemis.serviceを含む実宣言（BindsTo/PartOf空）・同boot/PID1依存非稼働化・同INV/全18の二state fieldだけの差/元ExecMainCode1-status0/全kernel空を結合し、既Broker一回停止/Expiry非稼働化を再発行しない。PG1139当固定UNKNOWN Java/RefはSS353の実M-A/soleDB又はidle後0/Bus/全toolhash・全原値二読/pidfd耐久TERMだけでhandoff、旧正常closeへ変換しない。その後の別fresh連続管理scopeで直接全終端証拠→canonical元ISSUEDrevoke/元permit-owner原byte保持→単一heldAPIintent退役/fullpost/全正常closeを閉じる。新epoch/oldpermit/start/DONE/DBupdate禁止とSSC255五role/755後続条件は維持、RD/UI/Production/設定byteの変更なし。

SSC256：当d5/PG1068・bootcbcaの親timeout143/APInamespace226後、元ISSUED四startup（epoch.current/元permit/data-only owner/API.start.intent）を固定before/private証拠へ束縛しSS353有限profileで復旧する。新M/A/RWbatch/advisory/独立RO全列/十Refs/全署名と原値の管理scopeで、既terminal九Unitはstopせず当同世代Artemisだけ一回正規stop、全終端・原値と資源を閉じた後のみ既Production canonical revokeと単一heldinode API marker退役/dirsyncを使う。expired親guard・元permitの再使用・owner削除・手epoch/DONE/DB書込は禁止。rawjournalのkey表示順は原値の差でなく、全field/cursor/event順の独立canonical比較と各raw私有保全を両立する。元Backup正常七世代retentionは変更せず最古退役原本は別非変更diskから私有保全、当pending同run/新activation resumeでは元二SUCCESS/manifest/handleを再用。全新scope正常後のみSSC255の五native-role＋親0755を別fresh管理scopeで整備する。内部profileの詳細・負例/再試験/unknown保持はSS353/SSC256、RD/UI/Production通常起動・30分・品質条件変更0。

SSC255（2026-10-10、BUG1030/YKT799）：SSC254の全role補足を実TenUnit ID/loaded/NSSで再同定する。正規Expiry=schubert-nk-expiry-cleanup.serviceは既agentあり/RWexpiry、Inspector=schubert-nk-inbox-inspector.serviceはbaseagent無しでもRWordinary-inspector196が必要、固定NSSはschubert-inbox-inspector。未loaded別名の空値を正常契約にしない。cold有限整備対象は既SSC193の四roleにordinary-inspector196（当Inspector UID:primaryGID0700）を追加した五role、共通親Root0755と元六role/exec全保全はSSC254どおり。Expiry既agentを再設定せず、Inspector未採取を成功/native100にしない。全正規ID/type/loaded/RW/NSSのliteral matrixと旧not-found反例、元failed親cohort全保全/限定回収/post後の別fresh管理scope実試験を要求する。SSC254の「Expiry agent無し/四roleで全網羅」は本補足により訂正、過去観測と限定13host結果は保全し正式へ流用0。

SSC254（2026-10-10、BUG1029/YKT798、cold PT-native復旧と既SSC193/195の整合）：SSC243/246の「coverage711/六childrole」だけをordinary API/Webの開始条件にしない。保持PT設定のeffective ExecStart/Environment native引数とReadWritePaths、署名drop-in全byte、現NSS固定roleを独立joinする。共通coverage親は既SSC195のRoot:Root0755/ACL0、root-api193/root-web193はRoot:Root0700、ordinary-api193/ordinary-web193は各固定role UID:primaryGID0700。既六role/exec全原byte-metadataを保全し、欠落四roleのみNOFOLLOW/new-only作成、保持同inode親711は管理scopeで一回755、各directory sync/厳密二読後だけ受入する。旧root-api名だけではSSC193宣言の代用にならない。

currentd5/PG1068/bootcbcaのPG1115/API exit226（ordinary-api193不存在）は当実結果として保存する。live親/他ownerには整備操作をせず、元1800秒の終端又は限定owned回収・当全原値/DB/原本Backup/source/Unit/資源後条件を先行する。別fresh M/A/専用DB/十Ref/元原本Sessionを正常保持した管理scopeでだけPT環境の有限deltaを行い、新scope正常closeと独立全postを要求する。Production template、業務RuntimeDirectory、原本、時計、旧permit/epochを試験都合で変更しない。Inspector/Expiryの未agent・未起動をnative成功へ補完0。全role契約matrix/独立missing-link-owner-mode-byte反例及びreal cold再試験を残す。

SSC253（2026-10-10、BUG1027/YKT796、SSC252の全private領域列挙是正）：現ordinary before1106後の共有S1祖先はnlink661→664、size同値。許す既知newdirはpg1107-observer-v1/pg1108-ordinary-cold-once-v1/pg1112-observer-v1の計3であり、SSC252の「一件/+1」は誤り。固定7inventoryの(3,3)/(4,3)だけ+3/実区間mtime-ctimeとし、各3dir Root0700/nlink2/ACL0と観測工具400の完全閉集合・byte/hash/それぞれの実stage0/sourceを証明してから比較する。失敗once領域は空/guard無し、他new回収・onceは既1106配下nestedでS1増分0。全identity-security-size-ACL/content/他全行・専用runtime/原本/DB/Unitと新scope全9fieldは不変更。実値に合わせた無根拠nlink許可やunknown entry追加0、新observer第三stageを作らずlive1112の同source RootStart+1860を維持する。

固定旧1111工具(sourcee8d815a0a6934d734f7b4e9c997fd085f5204b76/script55f4b085422d339b5a96784096938865df7e0fe30331e36ca1bc64b4e0d1620e/error51249e300665dcc00ccfd92ec2d0dc7849e1ec66f0773f9f0edf0a1221dcabb6)のreadonlyPython134103/start3382984/argv5a5cff3b…/exePython3.14/PPID134100/child0/FD452/privateBus十Ref、nestedguard無し・cold/全原値/DBclient-advisory-MA0だけを独立十Ref/署名/全値二読で認証する。同世代pidfd/耐久各一回予約→TERM一回→actor-Bus消失/全原値資源0/新正常、旧actual/旧closeは不合格別記。SIGKILL/oldtoolhotpatch/二重Rootstart/旧原本修復0、不明隔離。次only別nestedslotで全3dir証明・correctcrossscope/当scopeholdを再認証し、既live1112観測で一回noargs開始へ進む。Root1800/Unit期限/業務/品質/QA051保留は不変更。

SSC252（2026-10-10、BUG1026/YKT795、cold ordinary before→onceのscope分離）：同署名素材を同期間FD/link保持する9metadata-ACL-content検査は不変更。別observer/onceで捕捉した全ancestorのmtime/ctimeが全期間同じだと仮定しない。今回固定7inventory/pin順の(3,3)/(4,3)=Root0700のpgpt-s1-preservationだけ、既失敗once1108のRoot0700/空/private newslot一件が認証済みならnlink+1・size同値・有限mtime/ctimeを許す。(6,1)=Root0755の共有/runだけ、別OS観測期間のmtime/ctime（before開始～再認証の実区間）を跨scope値として分離する。dev/ino/uid/gid/mode/size・/runのnlink・ACL/contentsは完全一致、位置/名/型/数/余分行を緩めない。他の全artifact/親・専用/run/schubert-nk subtree/current/epoch/原本/DB/Unit/config/nativeは全項目同値。無断snapshot rebaseや全held行除外0、元beforeはimmutable保全。新scope内では共有祖先も含む全9metadata/FD-linked同一性を二読・一回予約後まで厳密維持する。

既1108/read-only失敗工具(source296ad46bc9b0adbcca07688b729b6ddc26e50322、scriptSHA5f4c9fc66b9ab0ce8960846208c9ea80f561cc332d79b5884ba4ef5606a0c19f、errorSHA09e5fedd9400be084fb71a7d316243c1a4cfc63afe9f4cf6e01318ac142f438f)だけを回収する。固定Python20312/start3250518/argv5a5cff3b…/exePython3.14/child0/FD452/Root権限/privateBus十Ref、start guard無し・Unit/原本/DB/current/INVALID不変・他業務client/advisory/M-A0を新独立十Ref/全署名/原値二読で認証する。同pidfd・耐久new-only一回予約→再全値→TERM一回→当actor/Bus消失/全原値資源0/newscope正常、旧actual/closeは別不合格採取。SIGKILL/oldhotpatch/二重start/予約捏造0、不明は隔離。

次onceは既1106private before配下の別freshnestedslotだけを使い、共通S1祖先を再変更しない。before原byte/同current1068/元30分/noargs/native宣言・新Root観測を再認証、一回予約→再全before→外部start一回。client0は真正RootDONEではない。観測のcold待機期限とRoot元1800を混同せず、Rootを捕捉したら観測期限は当実StartMonotonic+1860へ束縛しRoot自体を延長しない。旧watchをRoot受入へ流用せず、新source/slotの現在観測を先行する。業務/RD/UI/DIF/coverage/元原本/同日SUCCESSは不変更。

SSC251（2026-10-10、BUG1025/YKT794の固定部分交換からの所有回収）：PG1096/工具1094/sourceb73a8bd2cのcurrent1068・approval1068・正規INVALID/当completed原本を維持し、旧currentリンクが固定pg1088-current.partにlinked1で残るEXCHANGE不明を成功へ読み替えない。旧Java16222/start3020295/argv8df52e97210dd41650da536a037da7b2647f6851c764973e8f0810b160d7f788、唯一子16248/start3020358/argv4f134149ae07696304143818530e6ec17b9948a3c1b2f9b4d943a5bd28bbc04c、子十Ref/privateBus/旧FD・親M/A/専用RODB/advisory/heartbeat/socketを現在二読で認証する。新独立observerは全old/new署名inventory/固定工具/既before-epoch-approval私有証拠/全24原本Backup/Unitfull32/runtime/有限公開効果・linked旧inode/target/ACLを保持し、DB終了とUnit GCを観測する全区間に独立十Refを保持する。

旧actorをhotpatch/同activate再発行/再交換/oldfallback/DB直接terminate/原本修復しない。両pidfd固定・耐久new-only各一回予約・全二読後だけ親TERM一回、親/DB/advisory/M-A消失と同原値を二読、生存同子のPPID1/authority/全FD/privateBus同一性後だけ子TERM一回、全資源0/旧Bus消失/全原値を二読して新scope逆順正常close。未知・部分回収では所有を保持し隔離、SIGKILL0。旧transport actual/rollback/Unrefは別採取し新observer正常から補完0。

後続の旧linked保存は別newscopeのM/A/専用RODB/実heartbeat/十Ref/原本と同部分公開全値を再認証して、固定partから固定新privateへ同filesystem一回移動・両dirsync/全postだけを許す。public current1068/approval/INVALIDを再公開せず、旧link全9metadata（dev/ino/uid/gid/mode/nlink/size/mtime/ctime）、target/ACLを保持し移動に伴う有限ctimeだけ独立oracleで許す。atimeはreadlink自身による読取時刻でありこの9field契約外だが、mtime/ctime/ACLを除外しない。全正常/独立post後だけcode-onlyを新sourceで受入、旧失敗は不合格維持。普通Root/Inspector/native/正式451は別fresh受入。
SSC250（2026-10-10、SSC249の旧current symlink完全属性保全）：unlink後のO_PATH symlink FDでxattr取得可能と推定しない。今回Linux7.0 guestのlistxattrat AT_EMPTY_PATH/NOFOLLOW read-only診断はempty/NULLともEBADF9、readlinkatはoldtarget一致。属性検査を省略せず、currentだけnew-only固定sibling symlink/sync→同filesystem renameat2(RENAME_EXCHANGE) atomic交換→newcurrentと同oldinodeのlinked旧linkの全属性/targetを二読→旧linkをnew private SAVE/current-link.privateへatomic移動/両dirsync→oldO_PATH FDとprivate linkedpathのdev/inode/全metadata/target/ACLを照合する。public currentの欠落window0、oldlinkのnlinkは全区間1を保持し、有限ctime/親dir交換・移動効果だけをphase oracleで許す。oldapproval regular FDの正規nlink0/byte/xattr保全は従来どおり。

未知/半交換/private保存移動又はclose不明は隔離保持、再交換/任意unlink/旧fallback0。before-afterの全原値/DB/Unit/oldrelease/candidate、INVALID→approval→current順、newscope正常/独立postと後続freshRoot/native/451を省略しない。独立exchange/属性・反例・失敗/競合/再送禁止fixtureでhost/guest ABIを確認してから実公開する。RD/UI/業務/DDL/許可発行/期限変更0。

SSC249（2026-10-10、SSC190243247のcompleted-cold空epoch code-only）：current40ef/PG932・bootcbca/当完全DONE原本eeae/091663・全24表594/原本Backup/credential/旧proof・準備runtime/資源0・unused署名d5/PG1068全187/独立post1082を再認証する。new M/A/専用readonly batch-advisory/実heartbeat/tenRef/原本Session/保持directoryFDでoldcurrent fullverifier・candidate署名/全payload/固定schema028-SQL28-history29を検査する。prepare-roは必要当候補hostRO/既固定aliasだけ、未知mount/別namespace/不明の一般修復0。各modeは別fresh固定slot、旧冷準備/配置/工具退役/旧permit再発行0。

activateはstartup空を確認し、既StartupPermitFiles.invalidateのempty対応で現boot/新UUIDv4/当completedactivationの正規INVALIDを生成する。旧/run原本復元・oldboot借用・ISSUED/owner/launch発行0。INVALID force/dirsync/再読→Root0400 approval同filesystem atomic置換/dirsync/再読→current symlink atomic置換/dirsync→newfullmanifest/全後条件の順。oldapproval/current原byteをprivate durable保存、全DB/原本Backup/oldrelease/credential/Unit/configを保全する。許可deltaは当候補RO・新canonical epoch.current一件・approval/current及び明記した各親dir有限効果だけ。旧file/link FDのoldinode/bytes/ACLは保持し、正規置換のunlink/nlink0・親dirのentry/時刻変化をphase別有限oracleで独立検査する。旧metadataを無断rebaseしたりmtime/ctimeを無条件除外しない。同dev/inode/owner/mode/ACL・集合・全未変更値を各phase二読する。

unknown/半切替/close不明はM/A/DB/Ref/原本を隔離保持し旧承認/permitfallback0、新DBwrite/DDL/Unit start-stop/reload0。DBrollback-close/server0→Ref-FD/A-M正常帰還/独立postで当modeだけ受入する。切替後は別freshnoargs通常Rootが新run/cutoff/activation/INVALID/ISSUEDを生成し、管理者INVALIDを起動権限へ使わない。元30分/各Unit期限/owned逆順停止/Inspector合法日/同source native/451を維持、APIreadyだけで親成功0。

SSC248（2026-10-10、BUG1024/YKT793）：当cold unused tool9e9b/1075のpre-Ref BYTE_AUTH失敗だけをSSC245の固定親子回収へ接続する。RootJava11678/2433710/argv3ea4939c…・唯一Python11704/2433776/argve80bc4b8…・bootcbca/current40ef-PG932、親M/A/専用RODB PG243 heartbeat/advisory/socket、子Ref0/stdio3を現在二読認証する。sudo11676は対象外。75byteerrorSHAb41b40a2…/SAVErefsだけ・candidate/signature不存在・全24/原本Backup/approval/空epoch/準備namespaceを保持、新observer独立tenRef/全current189/全tool/hash/全cold宣言/heldFDを取得する。

子D-Bus/旧正常Ref解放を捏造せず、全authority/cgroup/task/exe/argv/generation/FD・実kernelM-A・同RODB heartbeat/socket・全原値を二読。二pidfd固定/耐久new-only各一回予約/予約後再読→親普通TERM→親/peer/advisory/M-A0と全原値再二読→同世代残子のPPID1/stdioFD/Ref無しを認証してのみ子普通TERM→全資源/全原値二読/new正常close。旧actual/rollback-close不明を分離、候補配置/epoch/current/DB/Unit変更0。SIGKILL/別actor/直接DBterminate/旧hotpatch/再送/旧成功補完0。不明は新Ref/FD内で隔離保持し、全後条件後だけ別newsource/slotで是正候補配置へ進む。

SSC247（2026-10-10、SSC190243のcompleted-cold未使用候補配置）：冷準備が全scope正常完了しstartup/requests/native空の場合、旧pending又はwarm baselineを現在値へ代用しない。今回current40ef/PG932・bootcbca・完全DONE原本eeae/091663・全24表594/Backup/credential/旧proof・十cold全宣言/資源を再認証し、新M/A・専用readonly batch/advisory71419602/実heartbeat・tenRef・原本Session内で正規署名d5/PG1068/BOM0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d/全187を未使用固定releaseへnew-only配置する。old currentのhostROとimmutable full verifier、全原値二読を維持する。

許容deltaは当未使用release tree/私有detached signature/工具receipt、各親dirの有限追加効果だけ。閉archiveの全member/type/ancestor/alias、全payload size/hash/canonical sums、固定pin/Ed25519とowner/mode・file/directory syncを検査する。current/approval/epoch/DB/原本/Backup/Unit/config/start-stop/DDL/permit変更0。current祖先FDは兄弟候補追加後に新取得し、追加前認証と追加後保持を別scopeとして記録する（旧祖先metadataの無断rebase/除外0）。追加前current full verifier、両側のcurrent/全原値/資源二読、追加後から正常closeまでの保持全inventoryを省略しない。DB rollback/close/server0→tenRef/FD/bus→A/M正常帰還後のみnew-only完了receiptを作る。unknown/partial/close不明では所有を保持し、同slot再配置/旧成功補完/次起動0。候補配置だけをimmutable候補受入・current切替・真正親/Inspector/native/正式品質へ加算しない。


SSC246（2026-10-10、BUG1020/YKT789）：cold finite layoutは既§6.9の`/run/schubert-nk/maintenance`を省略しない。before root:root0755のclosed entriesはmaintenance.lock/startup-admission.lock/maintenance、nlink3。maintenanceはroot:root0700・nlink2・ACL0・空を保持する。SSC243のstartup/backup-request/cleanup-request/expiry-request/pt-coverageだけ5dir追加後、rootnlink8、coverage711/六childrole等は既契約のまま。before/after双方でmaintenanceを厳密二読し、identity/全metadata/空が同じことをFDで証明する。unknown entry/非空/不明を修復や除外で通さず拒否する。

当1055-v3/source da73f7001・新metadataobserver7427/start1860448/argvSHA5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0、Root/usr/bin/python3.14、child0、UNKNOWN/Ref-FD349だけのnew-only限定退役を認める。全task/authority/cgroup/完全argv/generationと当guestscript/失敗log/source、observer独自D-Bus unique名/UID0/PID7427とtenRef、全捕捉FD metadata/ACL/linked inode・保持189signed/tool107/pin/signature/approvalを二読する。observerはDB socket/advisory/M-Aを持たず、旧5463/5489はSSC245の同source/世代/FD/kernelM-A/readonlyDB heartbeat/socket/原値で現在認証する。全原値/十coldfull32/連続dispatch禁止/timerpath・corrected finite beforeをnewobserverのRef-FD内で二読する。

本人pidfd→全二読→O_EXCL/NOFOLLOW file+dir fsync一回TERM予約→予約後全再読→普通TERM一回→旧7427実PID/当D-Bus接続/FD消失を確認する。SIGKILL/別actor/再送/直接DBterminate/oldhelper hotpatchは禁止。旧5463/5489/M-A/同DB transactionと全原値・namespace/config/署名を独立再二読し、新Ref-bus-FD正常close後だけ限定退役受入にする。途中不明/変異はnewobserverのRef/FD内で隔離、旧正常Unref/FDclose/actualexitを補完しない。旧host44275はactualexitを別採取、退役成功やcold準備成功へ流用しない。全条件後だけ別fresh corrected preflight→SSC245 fixedtreeへ進み、別新scopeへの一般権限に拡張しない。

SSC245（2026-10-10、BUG1017/YKT786、今回fixed1037のみ）：SSC244 noDB/child0を今回RODB+唯一子へ無条件流用しない。元source776/f08/frozen1038・Java5463/1373880/argvfcb09442…と唯一Refs子5489を、同bootcbca/current40ef-PG932/実exe・全task子集合・PPID・全authority/cgroup・全FD/inode・child payload hashで二読固定する。旧SQL42601/UNKNOWNの元receipt・完成原本を保持、future SQL空白修正で旧工具を再成功化しない。

新observerは既連続admin dispatch禁止/抑止timer-pathを全区間維持し、十Ref・全189signedfile/祖先/pin/signature/approval・oldtool凍結payload・原値FDを保持する。全DB clientを列挙し、観測自身以外は同source親の唯一backend/role/application/database/backend_start/xact_start・same advisory/実heartbeat queryだけを許容する。SSC238の同Connection実readOnly/onを確認する認証済pulseと、その喪失を示さない保持log・現在server peerを合わせ、60s idle期限を解除せず、別backend/role/query/失効・DB変更を拒否する。元childが既UNKNOWNでも権限を拡張せず、scope内の既signed/metadata/全24-594/原本59/Backup47/credential19/旧proof28/十coldfull32/kernel0を独立二読する。

親子両方のgenerationへ先にpidfdを束縛し、各actorのO_EXCL/NOFOLLOW一回予約をfile+directory fsyncで耐久化する。親送信前に全tree/peer/原値を再読しordinary TERM一回→親pidfd終端と実PID/旧DB backend/advisory/M-A消失・全原値不変を確認する。次に元の同世代子だけを、同argv/UID-GID/caps/cgroup/全FD・保持Ref/原値・旧親不在/PPID1へ限定して再認証し、子の予約後も再読してordinary TERM一回を送る。SIGKILL/名前検索kill/別actor/再送/server pg_terminate_backend/旧helper hotpatchを禁止する。予約・送信・wait・pidfd-close/Ref-FD不明又は片側終了なら新observerのRef/FD内で隔離を保持し、続きを自動再発行しない。

両実PID/全旧client-advisory/両M-Aflock/旧Ref接続・保持FDの消失と全原値/十Unit宣言・kernel/抑止の独立二読、newobserver全Ref-bus-FD正常close後の資源0を別証拠で閉じる。旧parentのactualexitはhostexec30116から別採取し、子exitは取得不能ならunknownと記録する。旧JDBC rollback/closeや旧Ref Unrefを正常と認定せず、旧失敗143/UNKNOWNを保持する。限定tree退役はcold準備/Root/PGPT完了ではない。原本/DBrow/epoch/config/mount/runtimeを変更せず、全後条件後だけ別fresh new-only準備scopeへ進む。業務親1800秒・既Unit期限・RD/UI/DIF・coverage条件は不変更。

SSC244（2026-10-10、BUG1009/YKT778）：coldのhostRO前は固定pinで署名原byte・source/BOM/approval/187artifactのmetadata/hash・旧原値を二読して真正性を認証する。これはimmutable payload/起動admissionではない。ReleasePayloadVerificationのreadOnlyFilesystemを満たすfull verifierは、正規M/A/専用RODB・実pulse/tenRef/heldFD内の必要hostRO設定後だけ実行する。warm用verifyCandidateをRO前に呼び、UNKNOWNを正常化することを禁止する。readonly前段はbyte認証と所有readbackのみで、epoch/namespace/mount/DBrow/業務Unitを変更しない。

今回固定PG1023失敗工具（source5a8aacfc8、frozen0dd14dce…、current40ef/PG932/BOMb75e/bootcbca、SIGNED_CURRENTのIO・RODB/tenRef/原本Session前、M/A-only、complete無し）だけのnew-only fixedhandoffを設ける。別のRoot/旧tool/actorへ拡張しない。新read-only observerのtenRef内で、当Java argv/UID-GID/boot/startticks/実exe・全凍結payloadを二読し、唯一のactor・child0・DBclient/advisory0・両M/Aflock同actorと型/metadata・全十cold/full32/kernel空・全24-594/原本59/Backup47/credential19/旧proof28/署名187不変更を確認する。同世代pidfdへ束縛してordinary TERMを一回だけ送り、SIGKILL/再送/forceはしない。timeout/変異/閉鎖不明は隔離維持。

実actorと両flockの消失、全元値/Unit/資源の独立再二読、観測Ref-bus-FD正常closeが揃った限定退役だけを認定する。失敗工具actual143/旧callback close UNKNOWN/complete無しを保存し、正常close・旧試験成功・準備/Root成功へ補完しない。旧/run/permit/DONE復元、原本/DB/credential/Backup/config/mount/namespace変更0。全後条件後だけ別fresh readback/準備scopeを新onlyで実行する。RD/UI/DIF/親1800/Unit期限/要求coverage/正式source条件は不変更。

SSC244の実施補足：SSC191の管理者起動/namespace禁止と既timer/path抑止をhandoff全区間で再認証し、M/A解放の間にも別dispatchを許さない。TERM前にnew-only O_EXCL/NOFOLLOW・file/dirsyncの一回予約を永続化し、pidfd束縛後と予約後にもactor/全原値を再読する。全taskのchildren・全UID/GID/groups/caps/NNP/cgroup・実exe/完全argv/generationと全凍結payload、両捕捉lock inodeと実actorFD/FLOCK（blocked/余分holder拒否）を照合する。全署名artifact/祖先・manifest/pin/signature/approvalのmetadata/ACL/identity/hashを保持NOFOLLOWで保存し、二読間の属性変化も拒否する。全application-DB client backend（migration/未知roleも含む、観測自身だけ除く）とadvisoryを確認する。観測body失敗はRef/FD内で隔離保持し、finallyで先に解放してnormalと推定しない。pidfd readinessと旧exit143は別に実証し、旧transport48449の実終端code/UNKNOWNを新handoff結果と分けて保存する。

SSC243（2026-10-10、SSC165174のcompleted・active無しcold接続）：保存原本が完全DONEでactive/pending無しなら、旧pending専用cold工具のactivationを捏造しない。今回固定source40ef/PG932/BOMb75e/187/schema028、instancepgpt-r2、新bootcbca、24表594行/原本59/Backup47/credential19/旧proof28・旧991-v4原値、1004-v3全二読/署名と1005全10冷32宣言/metadata正常閉鎖を接続基点とする。元diskを不変更read-only backingにする私有new COW layerのlogical equalityと全backing chainを認証し、作業disk/現在QEMU/boot/jobを記録する。元disk直接起動・snapshot apply/reset、独立backup認定、旧/run/permit/owner/launch/intent/native復元0。

新M→A→専用readonly schubert_batch/advisory71419602/実server pulse→tenRef/held directoryFD→署名187/approval/全現原値二読→固定署名payloadと必要aliasのhostROを認証し未済だけ設定→欠落4namespace（startup/backup-request/cleanup-request/expiry-request）と所定PT-native directoryのみnew-only・Root/固定role/mode・directory sync→全後条件→DBrollback-close/peer0→Ref-bus-FD/A-M正常→私有new-only complete。既lock inodeは現boot値のまま、既空dirは既契約の型/owner/mode/ACL/同device/heldFDで保持、未知entry/partial/close不明は隔離維持。startupは完全空を期待し、operatorが新INVALID/ISSUEDを発行せず、旧active/原本/DB/credential/Backup/configを変更しない。

その後だけ通常Morningのfresh/noargs一回経路を許す。新原本/UUID/cutoffとINVALIDはProductionの新live owner/M/A/DB/全停止再認証内で生成する（existingCurrent空はStartupPermitFiles.invalidate既仕様）。元完成親の期限/許可を借用0、API readyだけの親成功0、元1800/逆順owned停止/全資源・同source native/451は維持。Inspector固有の新日経路は同JST日既成功を消さず合法なfresh cutoffで検証し、時計/既履歴/原本改変・expired ownerでの単独Unit起動0。合法入口待ち以外の独立Log/host残部を継続する。設計公開は実準備/普通親/Inspector/native/PGPT受入ではない。

SSC242（2026-10-10、SSC230/238/241のcompleted-INVALID code-only）：正規復旧とruntime退役の独立861（全24/564・full32・47entry・tenkernel/DB/advisory/M-A0・runtime空）を新開始基点とする。old2a/832/8bcb/schema028/187/28SQL29history・bootcc9、original9de2/021111/cutoff05:42:22.532331Zの完全DONE0 ended15:32:16.513983Z・SHA37356f…、old8b153538INVALIDとparent9c08timeout/1/143を厳密認証する。RootDONEはdata-onlyの配備前提であって親成功receiptではない。旧genuine/ISSUED/pending専用工具への偽装を禁止する。新M→A→専用RObatch/advisory＋ROschema実server生存→tenRefs/保持namespace FD→全原値二読→unused e016/862/BOM20b99d・全187/同SQL28/29history・hostROとfixed個別mountRO（既済なら再bind0）→verify全正常又はactivate有限公開→全後条件/DBrollback-close/Ref-bus-FD/A-M正常帰還→new-only complete。許容deltaは新UUIDv4INVALIDのepoch.current（同boot/run/cutoff/activation）・Root0400approvalとcurrent symlinkだけ、各親dirの正規効果も記録する。oldINVALID/permit/owner/launch/DONE/全履歴/原本/24表/Backup/Transfer/native/credential/Unitを保全し、新permit/DBwrite/DDL/start/stop/reload/原本修復0。unknown/半公開/close不明は新scopeを隔離保持、有限rollbackを一般修復や旧成功補完へ拡張しない。全正常後だけ別fresh noargs通常run/元30分真正DONE・ownedstop/同source nativeへ進む。業務/RD/UI/DIF/coverage条件不変更。

SSC240（2026-10-10、BUG968/YKT737、SSC200/203のDONE後data-only参照補足）：同Root/Session/threadのconfirmed completionがあるOriginalProofは、pending参照能力へ戻さずtyped completed参照へ分岐する。active/pending空・current run anchor/activation begin/完全DONE全tuple一致と全Graph二読を必須とし、正規SUCCESS(0)とWARNING(10)を維持する。historical SKIP observedはcurrent DONE終了より前でも正常で、参照する別prior runの終了<=observed、同JST日、observed>=current cutoff・microsecond・上限、未知run/別active/Graph・namespace変化/owner-thread-lifetime-budget失効の拒否は維持する。これは読取データの根拠であり新DB/起動/原本変更権限ではない。complete不明をpendingへ戻す・active再作成・DONE書換・観測clockで過去SKIPを書換0。DONE_AFTERのDB成功参照もこの同じtyped経路を使う。DB側のprior成功条件は別に維持し、current全体をSUCCESSだけへ狭めない。

SSC241（2026-10-10、SSC179/211/235の当DONE後timeout限定）：当Production2a/PG832/BOM8bcb/schema028/bootcc9の親9c08/3417355が元1800sでtimeout/1/143、親kernel空・PID不存在であり、原本9de2/021111完全DONE・active/pending無し・全start intent無し、ISSUED epoch8b153538である場合の別new-only復旧入口を定義する。新連続M→A→専用batchDB/advisory＋readonly schemaの実生存→十Refと保持dirFD→署名full187/28SQL29history・全24/原本DONE/Backup/Transfer/native/config/Unitbyteと現在四actor generation/PID/ticks/argv/権限/cgroup二読を先行する。同世代Caddy→Web→API→残保守→Artemisの正規owned停止・native/vendor witness・十kernel空後だけ同epoch canonical INVALIDを正規revokeで公開、permit/owner/launch/全履歴原値は不変更。intent無しは復元/Pair生成/退役加算しない。新scope全正常帰還と独立全原値/資源0確認後にruntime841を正規退役する。旧親143/UNKNOWNを成功化せず、元DONEを書換/消去/同run再resumeして真正成功を作らない。後続は品質確定した当source署名code-onlyと別fresh通常run・元30分真正DONE/ownedstop/nativeである。unknown・半停止・close不明は新所有を隔離保持し次操作を拒否、RD/UI/DIF/期限変更0。

## SSC239 fresh system-manager読取transport（2026-10-09、QA047内部補足）

RootStartupContextの固定Unit照会は、同owner-threadのJava25 FFM/libsystemd公開sd-bus ABIによる固定ローカルreadだけへ置換する。GNU/Linux LP64のamd64/x86_64/aarch64を明示し、固定`/usr/lib/<対応arch>/libsystemd.so.0`のrealpath及び全祖先uid0/non-group-other-writeを検証する。immutable ABI MethodHandle以外の返信/owner/許可はcacheしない。環境bus/library指定、user/remote bus、process運用fallback、新権限付与は不可。

各queryにfresh私有接続を所有し、固定`unix:path=/run/dbus/system_bus_socket`へ接続する。元query全体5秒のBudgetで認証/Helloのprocess/waitをboundedに行い、RUNNING確認前の同期RPCは禁止する。固定DBus driverへauto-start0のGetNameOwnerを発行し、返ったunique nameのGetConnectionUnixProcessID/GetConnectionUnixUserを別の明示一RPCで読取、PID1/bus EUID0/unique形式を照合する。propertyはそのunique宛先だけであり暗黙service activationを行わない。全property後に再びwell-knownのowner/PID/EUIDをfresh取得して前後同一を確認する。

固定Service enumだけを対象とする。full projection=Id/LoadState/ActiveState/SubState/MainPID/InvocationID/ControlGroup、deadline projection=Id/InvocationID/MainPID/ExecMainStartTimestampMonotonic。Id/Load/Active/Sub/InvocationはUnit interface、ControlGroup/MainPID/ExecMainStartTimestampMonotonicはService interface。string/uint32/uint64/ayを実ABIで厳密読取し、Invocationは長0又は16byte、unsigned値を十進・IDをhexで表す。ASCII printable・各値/全返信4096byte以内、NUL文字列はNULまで逐次読取し未終端/超過/NULLを拒否する。systemctl旧読取は独立比較・故障注入試験だけに残す。

全引数準備後のRPC直前に、同元Budget残量を再取得してtimeout設定・ready/期限を検査する。owner三RPCも同元残量、接続waitを含めrenew/5秒延長0、親1800秒/各Unit期限も不変更。既Root kernel PID1/exe/boot/UID/proc/二読/全field、同peer/generation/identity/socket/info/ready・全row/seal/receipt・typed退役前後の証明を省略しない。bus/message/credential相当の所有返信・malloc文字列・arenaは当threadのscopeで解放する。IO/Runtime/Error/型/close不明は拒否・不明capability保持/次照会0、強制kill/不明closeの正常化をしない。

導入OSpackage版/入手元/ABI/header/hashと再現command、独立literal/stateful・境界/null/時刻/所有/解放故障PT、同sourceの実停止VM full値/FD/時刻比較を記録する。固定security library pathの静的検査は既kernel固定pathと同じEXACT局所理由付けのみ、global除外/coverage緩和0。停止中速度は旧timeout原因・負荷中性能・親受入の代用にしない。BUG949原因/新source全体回帰/署名code-only/別fresh一回resume/元30分真正DONE・owned停止/native/global四100/正式は別に実証する。RD/UI/DIF/業務仕様変更なし、承認QA047内の内部補足。


SSC238（2026-10-09、QA047/BUG936、保持工具の実DB生存）：隔離PG/PTの新pending code-only/resume工具がDBを所有して待機/未知保持する間、同owner-thread・同Connection・固定backend/role/application/database/readOnly/advisory71419602の現在生存を読取SELECTで確認する。JDBC object保有から実server所持を推定しない。確認間隔は既role60s idle timeout未満とし、既60s/親1800sの設定値・権限を変更しない。SELECTはbusiness更新/commit/新Connection取得を行わず、Unit/runtime/許可の再発行権限でもない。SQL/closed/異thread/値不一致/Runtime/Errorで所有確認を失ったらDB_NOT_CONFIRMEDに固定し、以降heartbeat/別Connectionでの再取得を止め、M/A/十Ref/原本等を隔離のまま正規fixedhandoffへ渡す。旧779の失活/143/close未知を補完しない。通常解放は当scopeの真正rollback/DB close/十Ref Unref・bus/FD/入場lock後条件を別確認し、未確認を成功としない。

SSC237（2026-10-09、SSC187203の全証拠配線補足）：真正DONEの完了証拠をCaddy/Web/API各intent退役前後へ同じ保持DB/原本能力で渡す。Web退役直後・API退役前後も、全Backup/Cleanup/Expiry行・参照/seal・明示停止済Backup cycle/元receipt・Cleanup/Expiry保持receiptと同ordinary peer/current/launch/identity/socket/info/readyを実再確認する。typed marker自体は既Attemptだけが所有し、純gateは追加marker/receiptを生成せず、DBを新規再取得しない。半退役/未知close/証拠変化は次退役/DONE0・同scope隔離。失敗のfixed phase/class/monotonic経過以外に例外原文・DB値・credential・tokenを出さない。旧FAILED_TIMEOUT143と新source真正成功を分離、旧原本active/Backup/Current baselineを保全し、新source所定quality→code-only→別fresh一回resumeで実証する。追加QA/RD/UI/DIF変更は不要。

SSC236（2026-10-09、QA047/SSC211235内の保持工具限定移譲）：779の当署名8d/PG750/bootcc9・旧親e409timeout143・run9de2/activation021111b4を維持する。逆順owned停止は全十kernel0・API/Web native TERM143・Broker vendor143まで既実施、同epoch e9f11f1c-f087-458a-aad0-8c1e4e140571は既INVALID、current/元permit/owner/launch・原本active・全24-544/Backup/Transfer/assets/credential/config保全、全startup42/実API-WEB-publication三intentで未退役。retirement callbackの固定O_EXCL診断再作成で保持した旧779を正常完了へ置換しない。private781/SHA823d5be73223e2c6232fa2758cba4badae3eba10ebb751b0c0c859465deb703bが現在原値基点。

現在Java3105271/startTicks14283385・同class/argv/source/binary/旧Root単位、Refs3105303/startTicks14283477・parent相関/同script・十UnitRef/十dirFD、sudo3105269はcontrolでJava本人ではない。M/Aの同inode/FLOCKはJava本人が保持、実DBclient/advisoryは0。捕捉backend3105299のrole60s idle-in-transaction timeoutは実log確認済み、Java object保持からserver所有/正常closeを推定しない。timeout設定解除/Root元30分延長0。隔離を継続し、固定管理者handoffだけで元三intent/全24/原本/Backup/Transfer/全旧private/署名BOM/current/approval・全Unit/kernelを二読し、旧二本人のPID/ticks/exe/argvと実FD/相関を発行直前にも認証する。

同旧保持区間中、pidfdでJava本人へ通常TERMを一回、所定期限内に子・FD/OFD/FLOCK/UnitRef・DBsession/advisoryの消失を独立確認する。Refsが親EOFで終端した場合は再TERMせず、非終端の場合だけ保存済み同本人/同ticks/entryのpidfdへ通常TERM一回を許す。SIGKILL/pattern kill/OS停止/Unit再stop/同recovery・revoke再発行/未知owner停止0。kernel解放を旧Java正常close/Unref成功/DB通常closeとしない。失敗/未知は再隔離、残serverを新所有として横取りしない。旧tool hostexit143等とprimary/secondary/oldCloseUnknownを維持する。

全旧所有消失・原値不変後のみ別new-only M→A→fresh専用DB/advisory71419602＋十UnitRef/helddirを取得し、既INVALID/実三intentのtyped Pairを再観測してWEB→API→publication退役/syncする。旧owner/launch/permitを補作成/復元せず新permit/別epoch/原本DONE/業務再発行0、42→39・他原byte/metadata/全24/Backup等不変・新全scope通常返却/独立後条件成立でこの限定退役だけを認定する。callbackは反復可能な純観測とし、固定一回receiptの作成を境界gateへ混入しない。最終一回receipt/予約はO_EXCLのまま。設定とargvの宣言部分/順序を保持し、ExecStartの実補助start-stop/code/status変化は同世代主要18/PID1/native証拠へ束縛して照合、履歴初期化や任意decl変更を許さない。

保持処理は実serverの同backend/advisoryとJava object、M/A/dir/Refを区別する。新設の所有監視/keepaliveが必要なら同actor/同sessionのreadonly照会だけで検証し、lossは非成功・DB_NOT_CONFIRMEDとしてM/A/Refs隔離を維持する。DBを無断再取得/再発行・期限renew・暗黙close成功へ変換しない。各取得/停止/移譲/反復callback/close/idle失活の独立故障試験と実限定後条件までBUG935/936は未解決、通常起動/native/正式品質は後続条件。

SSC235（2026-10-09、SSC179の現PG758限定束縛）：Production8d4b68b4f1449932ebe506aaf08e584bbfea8dd2/PG750/BOMa96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289/schema028/187artifact/28SQL29history、bootcc9ed874-7f4f-450e-a188-8de1e42c8441。元親2797579/INV e4093109ab234700b61dd45711126e4e/Job142602/start137240785885→end139040817174µs/timeout143、原本9de2d03c-28c7-4647-97d9-c66ace06048c/cutoff2026-10-09T05:42:22.532331Z/activation021111b4-6de5-4733-917d-5ac176240ffcを保全する。ISSUED epoch e9f11f1c-f087-458a-aad0-8c1e4e140571にはcurrent/permit/owner/API.launch/WEB.launch/API.start.intent/WEB.start.intentの七file、publication intent無し、全startup現物41entry。履歴epochの原byteを変えない。RootDONE無し・active有/pending物理無しは未完了graphで、pendingfile作成/原本完了化0。

稼働後readonly777の新private全24二読（batch544、snapshot80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4）と捕捉4live/API3063762・Web3066272・Caddy3072633・Artemis2841798を固定し、現在値を再認証する。Backup途中760の全24を終了値へ流用しない。元760全rowを保持し、その後のapp_logs56/web_http_sessions55/web_log_outbox56の有限追加を分類した新現在値から、復旧区間は全24完全同一を要求する。systemd Requires/Afterだけ重複拒否の集合比較、他設定raw/順序・全fieldを維持する。CLIが空ExecStopを表示しない場合は実PID1 Serviceの型付き空arrayだけを補完、未知値は推測しない。全十RefでcoldGCを防ぎ、観測LoadUnitを起動や旧正常終了へ読み替えない。

連続新M/A・実専用DB/advisory・実保持十Refの下で旧全原値/署名/approval/currentと同boot/actor/security/launchを認証→逆順owned stop→全十kernel/全旧PID消失と真正停止witness→同epoch StartupPermitFiles.revoke→既存quarantinePairでpublication最初のnew-only隔離→typed PairのWEB/API/publication退役/syncを実施する。41→39の有限namespace差とcurrentのINVALID以外、元permit/owner/launch/履歴file・原本・全24/Backup/Transferを不変更とする。別epoch発行/旧run復元/DB修復/業務再発行0。主/secondary・保持scopeとclose不明を非秘密で分離し、未知は隔離・非成功。新全scope正常返却と独立後条件が揃って限定復旧のみ受入、旧親143/BUG927解決/global100は別条件。

当runtime現物を先に認証する。空なら「既退役又は不在」と記録し架空の退役操作0、現存した当固定one-use entryだけ既SSC220/230契約で退役する。必要code-only/署名候補配備は別のnew-only通常scope/原値照合、fresh一回用resumeも別scopeで同run/cutoff/activationを維持する。元30分・既Unit期限/owner/security/真正DONE/逆順停止/nativeを維持し、再送Backupは既SUCCESS原本保持・所定SKIPPED/件数byte0・保持期限削除0を検証する。失敗復旧の成功を通常起動や正式受入へ加点しない。

## SSC233 現completed原値21・所有変更群のcode-only再束縛（2026-10-09）

SSC227のcompleted code-only有限deltaを、別new-only固定profileで現物へ適用する。current36fe7a0b938489d61d17d49c1c30a6fbbef699d5/release0.1.0-PG631/BOM57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe/schema028/bootcc9ed874-7f4f-450e-a188-8de1e42c8441。現run601297d0-a8ba-47da-852b-0ffeae409965/cutoff2026-10-08T21:33:23.332578Z/activationad15ac4a-8d8e-4970-bcb3-2e000050ce77の真正PID1 INV095f6d1d7f8442b7b2b44ae59a4314f5/job111752/start107901545407/end109694780700/DONE1793.235293s・原本ended2026-10-08T22:03:10.738020Z、PG655正常ownedSTOPを保持する。PG664 existingADMIN20/当actor2142585-ticks11164505/INV65bfe1da3b9e454997f1d899fea9510e/job119175/元30秒内1.593351s・新二input同inode-byte私有退役とPG665全20正常を別履歴として保持する。旧成功を新候補の受入へ流用しない。

PG684v2はRootreadonly/十Refの現全21二読を別newonlyに保存、seal c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d。旧20項へcurrent664 immutable tools/verify/execute私有原byteを加え、全24表514batch行・十主要/設定/依存・署名18source/runtime空/四namespace・startup/原本/Backup/credentials/native/currentapproval・旧停止/旧Bootstrapproof-tool・親PID1を保全する。GCは既sealednormal20と五idle項/宣言ExecStart補助履歴だけのSSC217で照合し、GCから20成功や正常closeを逆算しない。private input/DB/master/execをGitへ保存しない。readonlysealは操作権限でなく、新連続scopeで原値を再照合する。

新candidateはsource9bd50536f692610036a0ed8b83e0a8b35fe2a66f/PG680-681 fresh3489PT516suite/static6zero/main1612、release0.1.0-PG682/BOM076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480/署名187artifact/schema028/SQL28/history29。API既3class＋MaintenanceOwnerFrame/既Guard/Parent3byte・内部abstract7が閉差分で、既Guard/Parent executableは独立javap一致。全非JAR/DDL/設定/Unit/依存GAV/外部仕様は同byte、JARは当freshsource全byte資格を要する。

別newonly verify/activate毎に、新M→A→old同pin署名/current/observeStartup完全DONE→専用readonly schubert_batch DB/71419602Exclusive/固定tag→本人owner/samepeer→十Refと保持namespace-dirFD/全21二読→unusedcandidate hostRO/同pin型付BOM187/schema028→有限deltaと全原値二読→DBrollback-close/peer-advisory0/Ref-bus-dirFD/A/M正常→completeを維持する。verifyは全原値不変更。activateは同boot/run/cutoff/activationの新UUIDv4INVALID epoch・Root0400approvalVersionPG682/BOM076f・current symlinkだけを原子的公開し、旧ISSUED原byte/metadata/permit/owner/launch/DONE・全DB/Backup/privateproof/nativeを保持する。startup親directoryの正規size/mtime/ctimeとepochの新inode以外は変化を許さない。newpermit/start/stop/reload/DDL/migration/DBwrite/原本修復0。新DB/Ref/bus/FD/A/M帰還又は全後条件が未知なら隔離/所有保持、旧UNKNOWN正常化0・同slot再実行0。正常後だけ別fresh通常親/同RootordinaryAPI-Web-Caddy/元30分/owned逆順停止/同source nativeへ進む。新global100/CHR/正式/ITSTは別gate。

## SSC232 当PG662 verifyのimport前失敗・固定Java限定回収（2026-10-09）

SSC202/221/224/226の工具起動前error-only限定回収を当保存profileへ固定する。current36fe/PG631/BOM57a/schema028/bootcc9、601-ad15真正DONE・PG655正常ownedSTOP・PG661全20/24表514不変更。PG662source152c262f1 immutable11payloadの参照子はpg556_parent_receipt推移import欠落でmain前exit1、SAVEはrefs-prepare.private.logだけ/SHA c1935ed537f31f678be275164c100acc7db979986bf47cd0688d0ec363b0d761、before/Ref/credential/start未発行、旧scopeUNKNOWN。固定RootJava2141065/ticks11112630/argvSHA4406b878234be0e15d15334e7238c029f27ebd0e8a85a63624546608d67c6367、exe/opt/jdk-25.0.4/bin/java・parent sudo2141063（TERM対象外）・全task子0/実M-A inodeFD-FLOCK/他owner0・全peer/advisory0を現在再認証する。

新metadata十Refで全20の同source/全24-514/十Unit主要18/全署名source18/typed依存/四namespace/credentials/原本Backup/native/current/approval/旧proof/toolを二読しPG661seal8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8へjoinする。新onlyprivate profileと一回pidfdTERM予約を耐久保存し直前同peer/owner/原値を再照合した場合だけ当Javaへ通常TERM一回。本人15秒内消失・全M-A holder/DBpeer/advisory0/全十kernel・全原値二読不変/新Refbus正常返却を必要とし旧actual143/closeUNKNOWNを保持する。sudo/SSH/他owner/businessへ拡張0・SIGKILL/OS停止0・再start/retire/reload/配備/DBwrite/原本修復0。別freshv2のhost推移import非操作正常/依存欠落拒否→新verify→正常後新executeと独立post/native資格へ進む。証拠不足/新失敗は隔離・二重TERM0、正式/global/ITST合格へ読み替えない。

## SSC231 当PG631完了後のBootstrap既存ADMIN一回試験（2026-10-09）

SSC225の業務/所有/credential/実専用Unit/元30秒・既存20/作成0/全24不変契約を維持し、Production36fe7a0b938489d61d17d49c1c30a6fbbef699d5・release0.1.0-PG631/BOM57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe/schema028/bootcc9へ専用新only工具を再束縛する。601297d0-a8ba-47da-852b-0ffeae409965/cutoff2026-10-08T21:33:23.332578Z/ad15ac4a-8d8e-4970-bcb3-2e000050ce77真正DONE1793.235293s・PG655正常ownedSTOP/PG656全資源0/PG658同source資格16を前提に、別fresh readonlyで現在全24-514/十主要18/設定18source/typed依存/四閉namespace/credentials/原本Backup/native/current/approval・既proof/toolの全20を二読する。readonlyは実操作権限ではなく新M-A/前post専用DB・十Ref・保持namespaceFDの各scopeで原値を再確認する。

ADMIN一件を認証してから現在空の固定二sourceへ新CSPRNG試験入力をO_EXCL/NOFOLLOW/root0400/link1/ACL0発行する。旧PG535537570のinput/permit/valueを復元・再利用せず、通常Loginにも使わない。前DB/advisory正常返却・全peer0→durable一回予約→署名専用Bootstrap Unit一回→元30秒normal20/PID1当job/ordinaryUIDgroups/cap0/NNP/cgroup・当INV native一file→別post DB/advisory/全24完全不変/他九Unit・設定/依存/原本Backup保持→新二source同inode-byteの私有RENAME_NOREPLACE退役/両dirsync→postDB/Ref/bus/保持FD/A/M正常返却→独立全資源0の順を維持する。元runtimeは空/18source、DDL・配備・reload・Morning/APIWeb/Caddy再start/permit発行/手DBwrite0。未知は隔離・二重start/別passwordで回復扱い0。旧969/PG548/472row結果は履歴固定、当36fe nativeへ輸入0。設計確定は実受入やglobal/formal/ITST完了ではない。

## SSC230 当completed原本のruntime635正規退役（2026-10-09）

current36fe/PG631/BOM57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe/schema028/bootcc9、同e492/cutoff2026-10-08T18:32:42.140966Z/activation7d381b67-b37b-48c6-99ac-e04a336f887dの真正PID1 job104329 DONE1697.279879s・原本ended2026-10-08T20:40:56.335977Z・new正常ownedSTOP/全新scope正常を保持する。PG646readonly full19二読/全24-504/全十kernel-peer-advisory-FLOCK0・19effective source・runtime1のseal e9c9b270aea859cc13f69f24bee4406c401a61786b3081b698f20e9ac82be40cを固定するが、read-only捕捉だけで操作権限を作らない。

別new-only工具/保存先・新連続M→A→実専用RODB/advisory71419602→samepeer/owner→十Ref/namespaceとruntime実dirFDを保持し、全19と同genuine DONE/正常停止seal/現completed graph/ISSUED epochを直前・直後に同scopeで再認証する。Root0755/ACL access-default0の既実directory・Root0644/link1/ACL0/runtime635一件を認証し、署名base/既nativeから独立算出した同e492 --resume literalとmetadata9/SHAが全値一致する当一件だけを保持directoryからunlinkする。原directoryをremove/rename/再作成せず、force/dirsync→一回daemon-reload→全後条件→DB/Ref/bus/FD/A/M正常返却・独立全原値/資源後条件の順を閉じる。fileの不在を既退役済み正常と推定しない。

許容deltaはruntimefile一件の不在、Unit source19→18（他全path/byte/security exact）、Morning補助ExecStart plain native argvとnative-only DropInPaths、342の有限補助履歴reset/Caddy pairedだけ。runtime directoryのunlinkに伴うsize/mtime/ctimeだけは効果として記録し、dev/inode/uid/gid/mode/nlink/ACLと実保持FD identityはexact。その他全19（原本/元DONE/旧failure/epoch/全24/Backup/credentials/native/currentapproval/current/旧Proof/BootstrapProof・tool/全依存/主要十18）は不変更。旧完了3a53/失敗e492の途中原保存を新成功で書換・正常化しない。unknown/部分unlink/reload/closeは隔離・所有保持、一般修復/旧scope再開へ拡張しない。全正常後のみ別fresh新通常runへ進む。RD/UI/DIF/親30分/要求coverage不変更。

## SSC229 当PG631・failed30原本の新一回用resume準備（2026-10-09）

SSC228実正常切替/独立全19後条件after4d77bd92b7a7c3c85481b342659375e9be5fb7a50c0cd19f72363efb0f719879、current36fe/PG631/BOM57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe/schema028/bootcc9、同e492/元cutoff18:32:42.140966Z/7d381activation/既INVALID・全24-494を固定する。既runtime Root0755/単一実directory/ACL access-default無し/空を前後確認し、別new-only `/run/systemd/system/schubert-nk-morning-controller.service.d/pg635-once-resume.conf` を実保持dirFD相対O_EXCL/NOFOLLOW、Root0644/link1/ACL0、force/dirsyncで作成する。旧runtime復元/再使用/namespace repair0、署名base/既nativeの独立literalに `--resume e49243d5-de84-4714-8612-6912ddc17e9e` 二引数だけ追加し、RW/hardening/credential/他argvは不変。

新M→A→実専用RODB/advisory71419602→samepeer/owner→十Ref/namespaceFDを連続保持し、一回reload前後の全19原値を独立照合する。主要全十18属性/旧INV/start/end/code/status・全kernel/Job空はexact保持。SSC192/220補助履歴分類の当profileは、Morning固定新argv＋n/a,n/a,0,(null),0/0、七Unit（Artemis/Caddy/API/Backup/Cleanup/Expiry/Web）のsaved exact又は同path/argv/ignore_errors＋exact未実行へのresetだけ。現Inbox/Bootstrapは全config exact、未知/別宣言/部分reset不可。CaddyPre/Runはpaired同old又は両exact未実行だけ。旧143/30・close未知は主要18/原保存で保持し、n/aから旧成功・旧正常close・新readyを作らない。旧source/private証跡を当sourceへ流用せず、一回設定準備をstart許可そのものにしない。

全epoch/startup/原本/Backup/全24DB/current/approval/credential/native、旧18Unitfileの全byte metadataは不変、新runtime一fileと有効Morning宣言/DropInPaths及び承認済補助表示だけ有限delta。全新DB rollback-close/peer-advisory0/Ref-bus-FD/A/M正常・独立post後のみ別fresh observer/durable一回startへ進む。不明時保全/隔離・reload/同slot再発行0。新親1800秒/既Unit期限、同Root普通API-Web-Caddy/真正DONE/ownedstop/native・REUSED_SUCCESS削除0・別NEW_SUCCESS保持期限実試験を維持、RD/UI/外部仕様変更0、実装/PT未完。

## SSC228 固定failed30・二Backup SUCCESS後のpending code-only補足（2026-10-09）

数値訂正（BUG898/YKT667、2026-10-09）：以下の33.986083秒は転記算術誤り。真正manager start97060184910/end97094171993の独立差は **33.987083秒**。二値・INV/job/status30・原証跡は不変更、開始/終了の厳密照合と元1800秒条件を維持し、旧誤記を履歴として保存する。

SSC198の一般pending原本保全を維持し、旧二RUNNING/request/part profileとは別に次の固定状態を許す。boot cc9ed874-7f4f-450e-a188-8de1e42c8441、current72fb7440697ee1048a5c0145055dc1cc3c577914/PG621/BOM4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e/schema028。原本run e49243d5-de84-4714-8612-6912ddc17e9e/cutoff2026-10-08T18:32:42.140966Z/activation7d381b67-b37b-48c6-99ac-e04a336f887dはactive109byte・同begin・anchor整合、completion EMPTY。pendingは未完了graphの導出値であり物理fileを作らず、activeの削除/改名/再公開も行わない。

真正PID1同boot/INV3a2de24f931544c0a2fd83556a659cd0/job98394/exit30、start97060184910/end97094171993/33.986083秒を完全履歴で認証し、旧PID不存在・十Unit全kernel/job空を確認する。旧失敗/外側close未知を正常へ書き換えない。全24表/494batch行は二読、元492行全値不変、新e492 BACKUP_DB/CONFIG各SUCCESS attempt2だけ、非Backup新行0。全Backup/旧原本/保持startup/INVALID epoch・requests三空・intents/runtime無し、Unit全停止18属性/設定/署名source-files、client/advisory/FLOCK0を固定private sealと照合する。Backup dump/master/raw credentialはGit/通常証跡へ保存しない。

新候補はsource36fe7a0b938489d61d17d49c1c30a6fbbef699d5、唯一MorningBackupRetention.class変更・class追加削除0/1605、187artifact/SQL28/history29。451に基づく同source六fresh成功・全payload/同pin署名・owner/type/modeを実測確認してから使用する。未来BOM/sealは実測前に値を補完しない。別new-only verify/activateそれぞれ新M→A→専用readonly schubert_batch DB/advisory71419602→same-peer/owner→private十Ref/namespaceFDの連続保持、完全19観測二読・候補hostRO/typed署名を要求する。verifyは全原値不変、activateの唯一deltaはRoot0400 approval/version/BOMとcurrent symlinkだけ。既INVALID epochを含むstartup/全原本のbyteとmetadataは不変；invalidate/newEpoch/newpermit/start/stop/reload/DDL/DBwrite/Backupdelete0。新DB rollback-close/peer-advisory0/Ref-bus-FD/A/M正常・独立全postを満たさなければ隔離保持する。

正常切替後のみ別fresh一回用通常 `--resume e49243d5-de84-4714-8612-6912ddc17e9e` を固定同owner/新budgetで準備する。Productionが同原本run/cutoff/activationを再同期し、新親30分・既Unit期限・同Root普通API/Web/Caddy・真正DONE/owned逆順停止/nativeへ進む。operatorがactive/DB/原本を修復して成功条件を作らない。e492既二SUCCESSの同run BackupReuseを実四file/manifest/元rowで検査し、fresh Backup worker/CONFIG閉鎖を必須とする。新attemptはSKIPPED/ALREADY_SUCCESSFUL/zero件数byte、旧SUCCESS不変。REUSED_SUCCESSはretention削除0で八世代を減らさず、NEW_SUCCESS実保持期限再試験とは別受入。七CleanupとExpiryの旧3a53成功参照・progress/audit・現selector0、正常時十新attempt494→504を独立検査する。旧完成3a53/DONEと失敗e492の履歴を混同しない。RD/UI/外部仕様変更0、新QA不要、設計公開は工具/VM/工程合格ではない。

SSC227（2026-10-08、PG603/604、SSC190/221の新source候補・completed code-only固定profile補足）：fresh PG602/source d03e14bd79b32aa5c5270931b50389c9fa533932はboot cc9ed874-7f4f-450e-a188-8de1e42c8441/current PG548/source969d8ded10c0bf5841d9e3a5c531e922caf4a24a/BOMa224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515bを再認証した。PG573 run b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e/cutoff2026-10-08T07:36:21.802335Z/activation57f0e73d-d334-4882-9284-04246011da54の真正PID1/原本DONE0（ended2026-10-08T08:02:11.015742Z・1554.342064s/元1800秒）、PG579四owned停止と全八terminal/全newscope正常を維持する。PG602では全24表/482batch行・startup/全原本/Backup・全十Unit/設定/全kernel/全client-advisory-FLOCK0を二読、元after cb5951e30fda2ef63f2691a24f302e46b8cffcff6c8345e69644672b9135eaf6と一致、現epoch ISSUEDのSHA060a42b6735362ba26d22c48de3d5367791c2cbadc399e952838157240cb1838、doneSHA bf0695584592b7f7f3d00d48dd20b81e79695102a472e4c07cfa9b04e3cb6548を保持する。これらの旧成功/旧nativeを新candidateの正式受入には流用しない。

新候補はPG599 fresh source23b14a44b10504172e030bbd6625926bf049fb5c/3457PT/511suite/静的六0/1603class（bootstrap三class変更・三abstract interface追加、他五byte不変）、PG600署名187artifact/schema028/SQL28/history29/BOMa6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f、release0.1.0-PG600とする。PG601 unused実配置とPG602の全187byte/同pin署名/owner-mode/type再読だけが済み、current切替・native/global100/正式未受入。DB/migration/Unit/config/その他payloadは旧と同byteで、old ISSUED/permit/owner/launch/完了原本は起動権限へ再使用しない。

正規工具は別new-only verifyとactivateで、M→A→old署名/current/observeStartup完全DONE→専用readonly schubert_batch接続/71419602Exclusive・固定tag→本人owner・同peer・十Ref/保持namespaceFD/全原値二読→unused candidate hostROを一回固定（既ROなら再bind0）→同pin/全typedBOM187/schema028→verify全正常又はactivateの有限delta→全原値再読/DB rollback-close/peer-advisory0/Ref-bus-FD/A/M正常→私有complete、を維持する。有限deltaは同boot/run/cutoff/activationの新UUIDv4 INVALID epoch（旧ISSUED原byte/metadata・permit/owner/launch保全）、Root0400 approvalのVersionPG600/BOMa634とcurrent symlinkPG600への原子的公開だけ。startup同namespaceのepoch新inode・親directoryの正規mtime/ctime変化以外は全旧原本/482row/Backup/credential/transfer/native/Unit設定・停止履歴を変更しない。保存型・namespace/FD・DB/owner/thread/budget・有限delta拒否を独立fixtureで試験し、未知/半切替/close不明は所有保持・隔離、旧UNKNOWNを正常へ書き換えない。candidateRO又はverifyだけで配備完了を宣言しない。

新permit/start/stop/reload/DDL/手DBwrite/旧run復元0。正常activate後の通常Morningだけが新run・新owner/許可を生成し、旧DONEをpendingへ戻さない。親30分/既Unit期限、実Root→ordinary/同世代peer/socket/info/真正DONE/owned停止/新native・CHR/DIF・451全qualityの後続確認を保持する。RD/UI/承認業務仕様・外部画面/電文/DB契約変更0、SS内の固定profile具体化としてQA追加不要。設計onlymain公開と工具・実VM・正式受入を区別し、実装/PT未完。

SSC226（2026-10-08、BUG859/YKT628、PG566 verify pre-SAVE固定pair回収、QA047承認内）：現Production969/PG548/BOMa224/schema028/bootcc9・PG554真正DONE・PG559v2fresh全terminal正常・PG564追加114独立・PG565Production byte不変を保持する。PG566工具source64454b82eのreadonly verifyはM-A/署名187/専用RODB/advisory/十Refまで保持後、completedのrows:listへjournal bytesを渡して拒否。新二credential発行/専用Bootstrap start/SQLwrite0、SAVE pg566-bootstrap-verify-v1はerror-only（0c5b6d55d1141cc792c202559a877b1aa0ddbf2e24434f1e5b67787726c7b8c8）・before無し、旧scopeUNKNOWN。固定RootJava905353/ticks5420973/argvSHA7bb32363c5bc0336419f5233788a4a397b649595232f6dc33b433daa411d9223、唯一Ref905382/ticks5421098/argvSHA23277b6e8103a39e03590adaa7a499a9e9c1675a7a7c1433fccf204ee72bbd5f（sudo905351対象外）とimmutable九payloadを再認証する。PG567 readonly全二読profileSHA7ee165d041a05cf00451565f90955f8d9fbf1fa454d40a7751124de3182df677、PG558 beforeSHA51c4c14e2828fca4bf0703cbc8db2cab2feddb3e1b02af4da8b202b2f8e23cb1/PG559after23263d…へ全24-472・原本Backup/Startup/native/Unit現在値が一致している。

SSC214223224のcorrect oneshot18/型付き依存集合/PID1三stop64603-64601-64600/vendor143/四ownedSTOPの保存契約を同じ現cohortへ適用し、本人M-A FD/inode1997-1998/FLOCK/全task唯一Ref子/Ref子0を固定する。専用peerは当PG566-bootstrap-guard schubert_batch/71419602Exclusiveだけ、又はroleidle後全peer/advisory0を認証し、旧正常closeには変換しない。新metadata十Ref保持で全十18/実宣言履歴/config/全kernel/全24当原値/原本DONE/全Startup/Backup/native/元18proof/現error/九payloadを二読・私有一回予約後だけ当Ref→当JavaへpidfdTERM143を一回実施する。旧実143/UNKNOWNとbefore不存在を維持、新Ref/bus正常・全oldowner-peer/advisory/FLOCK0・全値不変が必要。業務Unit stop/start/credential発行退役/配備/reload/旧run復元0、一般UNKNOWN/別actorへ拡大0。回収後だけcompletedへJSON行を一回parseして渡す厳密typed fixtureと負例を追加し、別new-only工具/verify-v2で全新scope正常→同hash前提のexecute-v2一回へ進む。設計onlyの公開は実回収・Bootstrap・正式受入ではない。RD/UI業務変更0、新QA不要、実装/PT未完。

SSC225（2026-10-08、PG566、現source専用Bootstrap不足nativeの別新世代、RD/UI変更なし）：Production969d8ded10c0bf5841d9e3a5c531e922caf4a24a/PG548/schema028/BOMa224、bootcc9を固定する。PG554通常親の真正DONE/PG559v2fresh全terminal正常/全24表472batch行・追加114Log/outbox/session/原本Backup/currentと旧失敗証跡を保全する。旧PG535/537の二credential sourceは退役済み原byte/inodeのまま私有保存し、旧source/値/permit/旧runを復元・再利用しない。現在署名専用Unit（30s/Restart=no/disabled）だけのexisting-only一回PTに限り、現在before全24でapp_users一件ADMINを二読認証後、新CSPRNG passwordと試験専用usernameをO_EXCL/NOFOLLOW/root0400/nlink1で現在空の固定source名二つへ新規発行する。これは旧credentialの復元ではなく、新入力世代であり通常Login/認証には使わない。空UserDBや未知cohortへ拡張せず、作成0/既存20/全24不変を必須にする。失敗時に別password/再startで回復した扱いをしない。

一つのfreshM/A保持→現署名187/hostRO/完全DONE→専用RODB71419602/tagと十Ref/本人FD/全現在値二読→新二source発行・fsync→前DBrollback/close・全peer/advisory0→私有start一回予約→専用ordinary Unit一回→真PID1当job/done・ordinary UID/GID/groups/cap0/NNP/cgroup・同boot/PID/ticks/Invocation・normal20/元30s内・新当Invocation terminal.exec一つ→別post専用DB/advisory→全24完全不変/他九Unit18と全十設定/依存不変・当Bootstrap新20を旧履歴と分離→新二sourceだけ同inode/byteをRENAME_NOREPLACEで私有退役・両dirsync→postDBrollback/close・全peer/advisory0→Ref/bus/namespaceFD/A/M正常返却→completeの順を固定する。GCで履歴が空なら成功へ再構成せず当十Ref内の捕捉記録を使う。旧Backup/native/原本/Startup完全保持、nativeはordinary-bootstrap196の当INV一file以外増減0。通常Morning/API/Web/Caddy再start/permit発行/DDL/配備/reload/手DBwrite0。未知/半完了ではM/A/Refを保持・scopeUNKNOWN/限定復旧を台帳先行とし、重複startや任意owner停止を禁止。全new scope正常と実kernel/peer/advisory/FLOCK0まで独立照合する。管理工具/source-payload pin/typed18/config実履歴/依存集合/語境界SQL/閉namespaceはSSC214223224の既是正を再利用し、旧テンプレートの例外を再導入しない。正式/global100/ITSTの受入とは別の限定native採取であり、工具・実PTは未完。

SSC224（2026-10-08、BUG853/YKT622、QA047既承認内・PG559 pre-SAVE固定pair回収）: current Production969/PG548/schema028/BOMa224、bootcc9、真正PG554親DONE/PG557四STOP/PG558正常限定回収を保持する。新PG559は署名187・M-A・専用RODB/advisory・十Ref後、peer照合SQLの数値keyword境界欠落で拒否。SAVE pg559-terminal-readback-v1はerror-only/SHA=fc04799fbb37a39a6a699cff306e3e558559b897ed24ee5eeeb44deb14d16dd0、before/操作未発行、旧scopeUNKNOWN。固定RootJava902135/ticks4877955/argvSHA54ccadfedd692ad9d2f5226378205f897e4dae80722fad4b4ebd60ea8e51551d、唯一Ref902164/ticks4878076/argvSHA5f09e9e92ea2097e042bbf3e7d88e4c09df4ff337d1b993c3961851261241798（sudo902133対象外）とimmutable五payloadを認証する。PG560 readonly profileSHAc15addc8fb088dff6f8d3f0732d2aab2f10558fe9dc089ed1eb1ae494ad1873d、PG558全terminal beforeSHA51c4c14e2828fca4bf0703cbc8db2cab2feddb3e1b02af4da8b202b2f8e23cb1/complete0f673d9b…を二読joinする。

SSC214/215/223の正規Expiry終端/PID1当Job64603/64601/64600/vendor143/型付き全十Unit依存契約を維持し、実本人M-A inode1997/1998・FD/FLOCK・全task唯一Ref子/Ref子0、元DB tagPG559-terminal-readback/advisory所有観測と既idle60s後の全peer/advisory0を分離する。新metadata十Ref保持で当全18/設定/全kernel/全24当原値/Startup/原本DONE/Backup/native/oldproof及び現errorを二読、私有一回予約後のみ当Ref→Java pidfdTERM143、全oldowner-peer-advisory-FLOCK0/原値不変/新Refbus正常を必要とする。旧PG559 beforeを捏造せずUNKNOWN保持、旧PG557143/UNKNOWNも保持。SQL pure builderのpositive-int・数値後の字句空白/独立literal負例/実PostgreSQLreadonly parseを修正後、別new-only fivepayload/fresh M-A/RODB/十Ref/FDで全terminal正常後条件を再試験する。業務STOP/start/replay/reload/配備/退役/DBwrite/原本復元0、任意UNKNOWNへ拡大0。RD/UI/Production外部仕様変更0、新QA不要。実工具/再試験/横展開/正式は未完。

SSC223（2026-10-08、BUG851/YKT620、QA047既承認、SSC214/215の現固定profile適用）: Production969d8ded10c0bf5841d9e3a5c531e922caf4a24a/PG548/schema028/BOMa224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b、bootcc9ed874-7f4f-450e-a188-8de1e42c8441。PG554親581443/Invocation075ad6644b284056a6cccf7af252519b/job59402・genuineDONE1503.187759s/元1800秒、PG557 Caddy/Web/API/Cleanup四予約receiptを保持。旧Refの依存Expiry照合は既BUG824と同原因で拒否、旧後四receipt未保存・closeUNKNOWNを保持する。RootJava900001/ticks4742627/argvSHA6d561374450d704467420dad3ed7549a9c51abe4e828049e7bc4162b3592f40a、唯一Ref900030/ticks4742750/argvSHA048e80a297f67770721ce04e56d4a3597f37d2f32889ee62efda3067a8a1716b（sudo899999対象外）・七immutable payload・全task子/実本人M-A FD-inode1997,1998/FLOCKを現在認証する。PG558 profileSHA82543cb438dfd18a1c9442cb4ae057ad856822840651a87591dcb303a6c21824、PG557 beforeSHAc6098b236a5bbc03f7729417d11b6b23dc9365e2aea5246bc843e7415aad1cce/errorSHAfe94cbbd53a08a497b1abfc9b9cb5491aa66744075e46506d941c07c2075551c、PG556独立before8a524559…へjoinする。

新metadata十Ref保持の下、全10主要18/型付き依存集合・全kernel、全24表の当before全列全行/原本DONE/Startup/Backup/native/currentと旧proofを二読する。Expiryの当oneshot/RemainAfterExit active/exited/code1/status0→inactive/deadは残16field/INV/履歴不変、Requires Expiry→Artemis→Cleanup/両PartOf-BindsTo空、当PID1 stop/done Expiry64603/mono47437153773、Artemis64601/47437298657、Cleanup64600/47437301481とvendor全journal正常143を認証する。表示順だけをtyped集合で正規化、欠落/duplicate/未知値を拒否する。元専用DB/tagPG557-native-stop/Exclusive advisory所有観測と既role idle60s後の全peer/advisory0を区別し、旧正常closeとは扱わない。私有一回予約後のみ当Ref→Java固定pidfdTERM、旧actual143/UNKNOWN保持、全old owner-peer-advisory-FLOCK0/原値二読不変/新Ref-bus-FD正常closeを必要とする。その後別fresh M-A/専用RODB/advisory/十Refの全terminal正常readback/native同sourceへ進む。再STOP/start/replay/reload/配備/退役/DBwrite/原本復元0、任意UNKNOWNへ拡大0。RD/UI/Production外部仕様不変更・新QA不要、工具/実再試験/正式は未受入。

SSC222（2026-10-08、BUG843/YKT612、QA047承認内のPG549新Ref pre-SAVE限定pair回収）: source868c2d4e6/verify-v4はold/sourcea2署名187/current/真正PG522DONE、M-A/専用DB/advisory取得後、Refのowner AST namespace欠落でNameError拒否した。Root保存先pg549-completed-verify-v4はerrorSHA8d8b373a0d1ebc4b92c17aae1f2132ee5f25db62907c87162c499bc5f7448da8のみ、before/候補hostRO/epoch/approval/current公開未実行。RootJava576780/ticks4161990/argvSHA3be3de301dcbd99e087eae25622d42718f1d167ae96db6cbb353c592342aedcc、Ref576809/ticks4162106/argvSHA48093440b74bdf9b4ed0808a61d6526904a468331bb422b5e2844aa79d660e73（sudo576778対象外）、immutable7payload/実M-A inodeFD-FLOCK/全task唯一Ref子・Ref子0を認証する。初回backend576807/PG549-completed-codeonly/tag/advisory所有と、承認済role idle60s経過後のfixedbackend/tag/全peer/advisory完全0を区別し、旧closeUNKNOWNは不変更。新metadata十Refで全十F18/設定/依存/全kernel終端・currentf699/sourcea2/schema028/未使用candidatea224署名187、全24-462/原本Backup/Startup全原file/native9/元proofを二読して私有一回予約した場合だけRef→Javaの順で当二actorへpidfdTERM143を一回発行する。全oldowner/peer/advisory/FLOCK0・全元値二読不変/新RefbusFD正常close後だけ別fresh v5 scopeへ進み、旧actual143/UNKNOWNを保持する。既retire/reload/新run/配備/start/DBwrite0、Root前提を任意UNKNOWNへ拡張0。

新v5は抽出owner関数globalsにpathlib/os/sys/strict/command/requireを明示し、独立AST globals契約と固定owner fixtureで検査してから実same-peer/FLOCK/十Ref全beforeへ接続する。M-A→RODB/advisory→十Ref/保持FD→unused候補hostRO一度→署名typedBOM→verify全正常→別freshcompleted freshINVALID/codeonly公開というSSC190/221順序は維持、Production仕様/coverage/readOnlyFilesystemを緩めない。

SSC221（2026-10-08、BUG841/YKT610、QA047承認内・PG549 pre-SAVE候補readonly拒否の限定回収）: completed専用code-only工具source9ddde2d4cのverify-v1はold/sourcea2署名187/currentと真正PG522 DONEを認証、新PG548署名成功後、host readonly固定前のtypedBOMで拒否した。DB/Ref/SAVE未取得・公開/epoch/Unit/DB更新0。固定RootJava575778/ticks4093969/argvSHA4dfeee7365ffb8538dc3b9896ffb8ce7b9a1fd918a2083991d0038337b11a994、sudo575776除外、全task子0・RootUID0/同bootcc9/実M-A FD-inode-FLOCK/他owner0、immutable7payloadと元errorSHAf39757e7cb16567e999637b404c317989d12f82684463c11a711663b3ca372fb・SAVE不存在を認証する。新metadata十Refで全十主要18/署名宣言/全kernel終端・currentf699/sourcea2/schema028/ISSUED全原file・全24表462行/全原本Backup/旧native9と全proofを二読、全peer/advisory0を認証・私有一回予約した場合だけ当RootへpidfdTERM143を一回発行する。全oldowner/peer/advisory/FLOCK0と全値不変二読、新Refbus/FD正常close後のみ別fresh正常scopeへ進む。旧closeはUNKNOWN・旧actual143保持、Ref未取得を旧正常closeへ変換0。候補PG548は未使用配置のまま/再配置0、既runtime不存在/退役再発行0、旧親/newrun/start/reload/原本手修復0、一般UNKNOWNへの拡張0。

新completed工具の順序はM→A→old署名/current/observeStartup完全DONE→専用RODB/tag/advisory→十Ref・保持namespace FDと原値二読→unused candidate host readonly固定（一度、既readonlyなら再bind/reload0）→同pin元byte署名とtyped wholeBOM187/schema028/SQL28/history29→別verify正常又はcode-only fresh INVALID/approval-current公開→全原値許容delta二読→DB/Ref/bus/FD/A-M正常返却→completeとする。readOnlyFilesystem契約は緩めず、候補readonlyだけを現current配備成功としない。SSC190の公開後通常noargs新runと旧DONE/原本Backup保持は不変更。

SSC220（2026-10-08、BUG840/YKT609、QA047）：PG543 source d44293eed/retire-v3/同a2-PG495-schema028-bootcc9のdurable before c34c0582…/643B runtime3992…コピー/boundaries/一回予約を保持、保持inode unlink-dirSyncとone reload已実施・現runtime不存在を正とする。全十主要F18/旧INV/start/end/code/status/全kernel・署名宣言/他hardening/全24-462/原本Backup/ISSUED7/native9/currentを保持する。正規reload補助ExecStartはsaved exact又はexact(n/a,n/a,0,(null),0/0)だけ、宣言path/argv/ignore_errors不変（Morningのみ署名base/nativeの独立no-resume golden・native dropinだけ）、Caddy validate/runはpaired・片側不可。今回後条件は全十補助とCaddyPre exact n/aを要求、主要18から旧143/成功/終端を補完変更0、n/aを新readyや旧normalcloseへ読み替え0。
SSC220限定回収：固定Root573159/ticks3787228/argvSHA3884a575b13e0c6f347247c7fcb102e99128a4e5acf2572b69c46b6ab52b0ce2、Ref573188/ticks3787344/argvSHAb3360a48a242b36cc73cf3df039824f40da49707478f9bda477b7001e335fe1e（sudo573157対象外）・immutable六payloadとpg543-runtime-retirement-v2の五原file/error、全task唯一子/M-A本人FD-FLOCK・専用peer/tag/advisory又は既idle60s後完全0を二読。新metadata十Ref/私有一回予約→Ref→Java onlypidfdTERM/旧actual143-closeUNKNOWN保持→全旧owner-peer-advisory-FLOCK0/全原値二読/新Refbus正常後、別fresh M-A/署名187/専用RODB/advisory/十Ref/保持FDで已実行後条件だけを新before/after/completeへ封印し全DB/Ref/bus/FD/A-M正常を実証する。既runtimeのrestore/再unlink/reload/配備/Unitstart/DBwrite/元run復元は禁止、一般UNKNOWNへ拡張0。設計only公開は実受入/native/正式を意味しない。

SSC219追補（2026-10-08、BUG839/YKT608）：上記同固定PG543 Root571379/Ref571408だけ。初回backend571406/role batch/ROTX/tag PG543-runtime-retirement/Exclusive advisory1の観測を保持し、既role idle_in_transaction_session_timeout=60sにより現在そのbackend・全他peer・当advisoryが全0である状態も別の閉じた状態として認証する。peer判定は当backend全数・正しいtag/role/状態合同数・他peer・全advisoryを分け、owned1/tag1/other0/exclusive1又はbackend0/tag0/other0/advisory0＋既role60sだけ。誤tag/別backend/残lock/他peer/再接続/旧normal判定は許可しない。固定actor/immutablepayload/M-A/十Ref/全元値/限定pidfdTERM順と旧closeUNKNOWNは不変更、actor全消失後はpeer/lock全0必須。fresh新正規退役のRODB必須・正常close条件を期限後0で置換しない。

SSC219（2026-10-08、BUG836/YKT605、QA047既承認）：PG543 sourcee6eb8306a/verify-v2のpre-SAVE SQL schema拒否だけを対象とする。schema028全24はschubert業務20＋schubert_web_session四表（pending_context_revocations/web_http_sessions/web_log_outbox/web_receipt_references）であり、SQL再読の独立閉集合を一namespaceに狭めない。元全列/行/順序oracleと外部仕様は不変更。固定Root571379/ticks3670527/argvSHAf46ba13d3123ce2dc770a48183351a81d262a143c9d667802ad1fd680cb4a7bdと唯一Ref571408/ticks3670640/argvSHA9fff6140014fb039d6b3d21efb5e4964bdc3d65ee9a40ba0e35193534474cffc（sudo対象外）・immutable六payload/型付きclasspath依存/old errorとSAVE readonly-v1のerrorのみ、M-A dev0:28/inode1997・1998/Root本人FD-FLOCK・専用backend571406/tagPG543-runtime-retirement/Exclusive advisory・peer0を現在認証する。新metadata十Ref下で全24-462/原本Backup/ISSUED7/native9/runtime3992…/全十F18/kernel/設定・依存/真正親・停止原値を二読し、私有一回予約→固定子Ref→JavaだけpidfdTERM・全旧owner/peer/advisory/FLOCK0・新Ref/bus正常closeまで閉じる。旧143/closeUNKNOWN保持、一般未知ownerへの拡大・Unit start/配備/reload/runtime退役/手DBwrite/旧run復元0。その後だけ別fresh new-only工具でM-A/署名187/RODB/十Ref正常と現runtime一回退役/元全原値・全資源正常の再試験へ進む。実受入/native/formalは未完、design-only公開を工程完了にしない。

SSC217（2026-10-08、BUG829/YKT598・SSC216のfresh退役前GC観測補足、RD/UI変更なし）：PG536 fixed工具回収はsourcec2b7f5be4/actual0、十Ref保持内のbefore=after全原値SHAaa8f9216…とcomplete03ebd13e…を封印し、真正ordinary BootstrapのINV08face…/PID567513/ticks2872520/正規20/元30s以内1.666104s/真正PID1Job41051/native一件を保持したまま旧143UNKNOWNと新Ref/bus正常・全旧peer-advisory-FLOCK0を別認定した。新参照を解放した後、当Bootstrapだけsystemd GCでInvocationID空・ExecMainCode/Status/Start/ExitMonotonicがexact0に戻ったことを現在値で確認。これは新正常0・旧close成功・再起動許可ではない。
fresh PG537退役の観測profileは当固定ケースに限りGC_AFTER_KNOWN_20と明示する。PG536 sealed whole18正常20/PID1/ordinary actor/全native/原byte/署名BOMを歴史正本に保ち、現在Bootstrapはその五fieldだけexact空/0かつ他十三field完全不変・全kernel空を認証する。宣言path/argv/ignore_errorsは同じ、sealed履歴(start,end,捕捉PID,exited,20)と現在history(n/a,n/a,0,(null),0/0)を別々に固定parseし、他configuration全値・他九Unit18/同世代履歴・全24-462/StartupISSUED7/原本Backup/runtime/旧八＋新一native/二new synthetic sourceの全値を不変照合する。sealed正常20証跡がないゼロ、foreign/missing/null/余剰/別PID-INV/decl/partialGC/業務actor生存/原値差は拒否。現在GC値を正常20へ再構成・書換・coverage成功加算しない。
新fresh M-A/RODB/advisory/十Ref/FDで当二sourceだけ所定同inode/byte no-replace退役・両directorysync、全新scope正常と独立peer/advisory/FLOCK0を閉じる。PG535を再start0、sealedを更新0、一般GC/別cohortの回復許可へ拡張0。GC正常20の二profileを独立literalで区別し五field各変異/十三field全不変/宣言履歴/schema/型/欠落/foreign/保存hashの負試験を追加、後続Inspectorは当設計の固有観測契約を別認証する。設計onlymain公開・工具/PT/正式未受入を区別、QA047承認内の内部実観測補足につきQA追加不要。

SSC216（2026-10-08、BUG829/YKT598、QA047既承認内のPG535 Bootstrap正常20後の限定工具回収・二synthetic source退役）：Productiona2/PG495/f699/schema028/bootcc9、PG522真正DONE/PG526ownedSTOP/PG530正常fresh読取は保存する。PG535専用Bootstrapの一回startはINV08face250787426aab68796452a0289f/PID567513/開始28725207186→終了28726873290usのordinary同actor資格・正常20・PID1 start-done/native完了を捕捉したが、ExecStart実行履歴を設定差としたRef拒否で工具全closeはUNKNOWN。全24-462/原本Backup/startupISSUED7/runtime/旧八native不変と新ordinary-bootstrap196一file、二new-only初期sourceだけを認証する。専用Unit/親/配備/reload/復旧操作の二重発行0。
固定RootJava567192/ticks2871934/argvSHA4cc659cb2ca0264e69829c81b0cd9a40d46db1b4d05cb302e491eb9e72423ee4、Ref567221/ticks2872058/argvSHAbf970c5edc115d47659136f86e4f008cd77a3eca541fc8a74455efe84ed2a48b（sudo567190非対象）だけを限定回収可能とする。immutable六payload、旧SAVE八fileとbefore4f4bd05f…/errorf33b9630…/actor0dd31425…/states485e1619…/真正PID1d34729d3…/journal dedf46cb…/一回予約8ce3f384…を原byte/metadataで固定する。全task exactchild一件/子0、同inodeFD/FLOCK M-A（dev00:1c/ino1997・1998）・他holder無し、DBpeer/advisory0、全10Unit18/kernel空・bootstrap正常20/元30s・old9完全不変、全configurationは当Bootstrap ExecStart履歴だけ別合同検査、全元原値を二読する。新十Refでmanager履歴を保持し私有一回予約後、当Ref→当JavaだけpidfdTERMし旧143/closeUNKNOWNを維持する。全raw/二初期source/九nativeを不変二読、全oldowner/peer/advisory/M-A消失と新Ref/bus正常closeを認証する。欠落/別owner/別cohort/不明は隔離保持、一般UNKNOWNの成功推定へ拡張0。
別fresh M→A→専用readonly batch DB/advisory→十Ref/FDの全原値再認証後、当二synthetic初期sourceだけを同dev/inode/uid/gid/mode/nlink/size/hash確認しRoot私有保全先へRENAME_NOREPLACEで退役・双方dirsync・同inode/contentと元source不存在を認証する。DBwrite/既credential変更/原本更新/Unitstart0。全新DB/Ref/bus/FD/A/M正常と独立peer/advisory/FLOCK0を閉じる。新工具成功は旧工具の正常終了へ代用しない。
ExecStartはpath/argv/ignore_errorsの厳密三宣言を比較し、不達初期history exact(n/a,n/a,0,(null),0/0)から今回history(start,end,capturedPID,exited,20)への唯一差だけを実Unit開始終了文字列・actor INV/ticks・full18/code1/status20・PID1/nativeへjoinする。GCゼロ/宣言差/unknown/missing/null/異PID/異INV/別時刻/30s超過/別code-statusは拒否、他Unit設定と元四receiptは完全不変。独立literal全変異・実currentsource再検証、Inspector将来初回履歴も宣言/history分離を明示し任意phase許容へ一般化0。RD/UI/外部仕様/Currentbaseline/451条件変更0、追加QA不要、設計only公開と工具/native/正式未受入を区別する。

SSC215（2026-10-08、BUG825/YKT594、QA047既承認内のPG528停止前・全terminal限定owner回収と内部依存集合join）：当sourcea2/PG495/f699/schema028/bootcc9、PG522真正親DONEとPG526四owned停止receipt・API/Web正常TERM/native、依存Expiry33502/Broker33499/Cleanup33498のPID1 stop-done、PG527新読取Ref正常解放・全原値二読（beforec8c6b915…/complete0f673d9b…）を保持する。PG528は新M-A/RODB/advisory/十Refの現在全terminal/kernel/親DONE/宣言を通過し、Ref snapshot line64でBootstrap/Inspector/Morning依存属性の表示順差をraw字列で比較して拒否した。依存token集合は全件同じ、SAVE pg528-terminal-readback-v1はrefs error411dd81a…の一fileだけ、before/業務stop-start-reload-revoke-DBwrite0。元source/UNKNOWN/未保存beforeは改変0。
固定RootJava563427/ticks2139689/argvSHAe6b8aa63dff76d94978974f89c646e666ccc6c2eeb60b37da9a64948b033d9bb、Ref563456/ticks2139804/argvSHAa8c126c4e0d99db54d98a0e0707fc7210f31e827ff60f458c270c7202913ce7c（sudo563425対象外）、immutable3payload（Root3420c237…/References3fcd6d96…/refs aaeb276f…）と旧PG526署名済み六helper/library原byte、全task子exactRef一件/Ref子0/実M-A inodeFD/FLOCK/他owner0を認証する。専用PG528-terminal-readback peer/advisory現在保持又は既idle期限後0を識別し、全10Unit18/全kernel終端・四receipt/所定API-Web143/failed/Expiry正常0/Broker vendor143/当三PID1job/署名宣言とprimary終了履歴を直接再読する。全24-462/原本Backup/startupISSUED7/native8/runtime3992…/Root原error・PG527sealed原値を二読、新読取十Ref保持・私有一回予約後だけ当Ref→Java限定pidfdTERM143で回収する。旧scope UNKNOWN/旧原raw保持・正常化0、四STOP/配備/起動/退役/reload/手DB書込0、新Ref/bus正常closeと全旧owner-peer-advisory-M-A消失/全現原値不変二読後だけ別fresh正常scopeへ進む。一般UNKNOWN/別cohortへ拡張しない。
systemd Requires/Before/After/PartOf/BindsToは依存Unitの集合であり、exact10Unit/属性五種・ASCII正規Unit token/typed string/empty集合・重複無し・固定上限を検査し、その五種だけをtoken集合へ結合する。元property字列/metadata/入力raw/hashは別私有保存で不変更、canonical内部graphの全値と原集合の一致を独立に検査する。表示順だけの差は内部集合同値、missing/duplicate/foreignUnit/prop/null/型/不正token/制限外/異sourceは拒否。argv、宣言順、画面/電文/外部SQL表示順やCurrentbaselineを無断集合化しない。journal JSON field出力順とDB PK joinも型/全値を明示した各内部契約として相互に分離する。
別fresh M→A→RODB/advisory→十Ref/FD→原本・全terminal/whole10Unit/依存graph・全24-462/startup/原本Backup/native/元receipt-vendor-PID1を同source/runで再認証し、全新DB/Ref/bus/FD/A/M正常返却と独立peer/advisory/FLOCK0を閉じる。独立literal10Unit graphのreorder/全属性/全null/duplicate/欠落/foreign/token/上限/各保存close故障と実graph同集合/raw別SHAをPTへ追加、旧before無い又はInspector/Bootstrap未起動を成功/native100へ置換しない。Production gate/coverage/外部仕様/元1800s不変更、設計onlymainと工具/native/正式未完を区別する。

SSC214（2026-10-08、BUG824/YKT593、QA047既承認内のPG526部分停止後限定回収・全terminal再認証）：Productiona2/PG495/f699/schema028/bootcc9、当親INV8f4514e…/Job26968真正DONEと原本SUCCESS/ISSUED7/全startintent退役を保持する。PG526は当462行のuniquePK全column照合を通過し、Caddy/Web/API/Cleanup四段の一回stop予約・同世代stopped receipt、API-Webの全journal/正常cleanup/native capture witnessを保存した。Cleanup停止transactionによりExpiry Requires Artemis/Artemis Requires Cleanupの固定依存がExpiry→Artemis→Cleanupの順で終端し、旧RefはExpiry旧active/exitedとの完全一致で拒否した。元Refを修正・再開せず、未保存後四receiptは未保存、旧正常closeはUNKNOWNのまま保存する。API-Web Unit exit143/failedは所定ownedTERMデータであり、工具close成功又は業務再起動許可へ置換しない。
固定RootJava561260/ticks2040839/argvSHAe538b174fdb55b348b364b49ecca438f03c4cd1aba9f65b28ef9f9c85c8119ba、Ref561289/ticks2040952/argvSHAce648ae9ecb7c8fed4e0dcd1677b35dff79ff1c98c3a3d4fadfab8fcb27bb814（sudo561258対象外）、原immutable6payload/前before15fa5248…/error0587a241…/四receipt全原byteとmetadata、全task子exactRef一件/Ref子0/M-A inodeFD-FLOCK/他owner無し・専用PG526-native-stop peer/advisory現在保持又は既idle期限後0を認証する。全10Unit exact集合/full18/同INV-start-end/code-status/全kernel空を二読し、API-Web/Caddy/Cleanupは保存receipt完全一致、Expiryは同INV oneshot active-exited→inactive-dead・Code1/status0・元exit履歴保持、Artemisは同INV inactive-dead/Code1/status143/Resultsuccessとvendor全journalを認証する。依存三UnitのPID1 stop-done（Expiry Job33502/mono20418217592、Artemis33499/20418357422、Cleanup33498/20418359226）は当boot/UID0/PID1/INVに束縛し、ORDERのreceipt確認順を実終了時刻順へ強制しない。Inspector/Backupは今回元beforeどおり既terminalでstop0、Morning真正DONE/Bootstrap元beforeと全kernelを保つ。
全24-462の原全column/原本Backup/startupISSUED7/native/runtime3992…/署名current/release readonly/宣言hardening不変とprimary終了履歴を分離して二読・私有予約し、新読取十Refで全18履歴を保持した場合だけ当Ref→Java一回pidfdTERM143で限定回収する。旧SAVEに未保存receiptを追記0、業務STOP/start/reload/revoke/配備/手DB書込0、旧UNKNOWNを正常化0。全旧owner/peer-advisory/M-A消失・全現原値不変二読と新読取Ref/bus正常close後、別fresh連続M→A→RODB/advisory→十Ref/FDで現在全terminal/同cohort/全原本・依存/vender-PID1を直接再認証し、当工具の全新DB/Ref/bus/FD/A/M正常返却と独立peer/advisory/FLOCK0を閉じてnativeへ接続する。Inspector/Backup未起動はnot-run、native全role/coverage100への代用不可。
独立全10Unit matrix・oneshot/RemainAfterExit literal、欠落/foreignINV-boot/異status/kernel/依存無し/前段receipt無し/stopjob欠落重複failed/vendor欠落/原値差/各保存close故障・既terminal再STOP0のPTを追加する。限定reviewは具体反例の読取だけ、品質・Production/Currentbaseline/外部順序・元1800sを変更しない。設計onlymain公開と工具/実fresh全scope/native/正式品質の未完は別管理、一般UNKNOWNや別cohortへ拡張しない。

SSC213（2026-10-08、BUG823/YKT592、QA047既承認内のPG524停止前限定owner回収・内部SS補足）：当sourcea2/PG495/f699/schema028/bootcc9の真正親INV8f4514e…/Job26968DONE1341.508568s、原本SUCCESS/CurrentISSUED7/全startintent退役と当API504968/844d…/ticks1616183・Web507277/7127…/1617567・Caddy512938/bcb3…/1620623・Broker353417/3808…/1525015のlive同cohortを保持する。PG524は新M-A/RODB/advisory/十Ref/全24table/原本Backup/startup/configの二読後、PG523 order by idのbatch-only listとPG524 jsonb_agg order by j::textの同全462行を直接比較して拒否した。独立primary-key全列mapは一致、停止予約/STOP0、SAVEにはrefs errorとbeforeだけ（SHA15fa5248…）、current/業務原値へ変異0。期待値・画面表示順・DBの実データを実装都合で変更しない。
固定RootJava560210/ticks1926229/argvSHA9b1b8949c16b214dc83fb808e40d0ed3d67769de8eca0099da4fe1dc8360e1e1、固定Ref560239/ticks1926340/argvSHAaae5a794feb3a901d89fb7ab7bc9127d19f7afc3da03bf2bf29355ad15a8b9c3（sudo560208は対象外）だけを扱う。immutable6payload/class2-Python4/原before・refs error add3b29f…、全task子exactRef一件/Ref子0/実M-A inodeFD/FLOCK/他owner無し、当operator専用PG524-native-stop DB peer/advisory現在保持又は既idle期限後0、live4cohort全18/実PID-ticks/cgroup/全configuration・全24table/原本/Backup/startup7/native15と実原値を二読・予約した場合だけchild→Java一回pidfdTERMで限定回収する。ordinaryAPPの既許可peerは当固定APP/Unitへ束縛し、当operator peer以外のbatch/backup/advisoryがあれば拒否する。APP/BrokerへのSTOP・revoke/start/reload/配備/DB書込0、旧scope closeはUNKNOWN/元actual143を保持、ツール消失/Ref-GC/DB idleを旧正常closeへ読み替え0。
全旧工具owner/専用peer/advisory/M-A消失とlivecohort/全原値不変二読後だけ別fresh所有へ進む。是正版はartifactのtable/key/schema/rowcount/id唯一性と全columnを結合し、SQL返却順が契約でない内部joinだけprimary-key mapで照合する。raw保存artifactのhash/順序/型は不変更、外部表示順/電文byte/Currentbaselineは別承認oracleのまま。正常reorder/欠落/重複/null/型/違うsource/column差・consume close/競合・全新scope正常と実同cohort逆順TERM/nativeを独立再試験する。一般UNKNOWNや旧全terminal/INVALID profileへ拡張しない。RD/UI/業務・Production仕様変更0、利用者新判断不要、設計のみmain公開と運用工具/正式受入の未完を区別する。

SSC212（2026-10-08、BUG821/YKT590、QA047既承認内のPG519 pre-SAVE限定owner回収・内部SS補足）：PG519/sourcea2/PG495/schema028/bootcc9の新M-A/専用DB/advisory/十Ref・署名187と現全24-452/INVALID3/native15/wholeterminal snapshot二読後、Ref module baseline未定義NameErrorでruntime-before保存・unlink・reload前に拒否した。SAVE pg519-runtime-retirement-v1にはrefs-prepare.private.logだけ、固定pg492-once-resume.conf原byte/inodeと全設定/元permit-owner/current/原本/Backup/native全値を不変保持する。一般UNKNOWNへ拡張せず、既PG519 native/配備/stop/削除/reloadを再発行しない。
固定Root Java317317/ticks1323648/argvSHAb7596427a9f33333fa4d4f12c02a0223434dac7f7df748e1a982d40ee8bb9269、固定Ref317346/ticks1323764/argvSHAe653326b14f0e0a7349f497d06465a0a2c57930cb8400d056735f0e9deaf3d3f（sudo317315は対象外）、全task子exactRef一件/Ref子0・実M-A inode/FLOCK/他owner無し・immutable5payload（Java cd3f77…/References cef226…/refs b678ce…/test4bc426…/parserb198ce…）・全10Unit18/config/kernel終端と現全raw/私有原値を二読・予約した場合だけ当child→Javaへ一回pidfd TERMで限定回収する。DBは同PG519 solepeer/advisory現在保持か既idle期限後0を識別し、process aliveだけで十Ref/DB全保持又は旧close正常を主張しない。旧実scope不明はUNKNOWN、元actual143は異常中断、限定新handoff actual0と区別する。両旧owner/peer/advisory/FLOCK0・全原値不変二読後だけ別fresh所有へ進む。
新fresh runtime工具はmodule-level原treeを新before snapshotへ結合し、PG518正常after/現全24-452/INVALID3/native15とPG516 wholeterminal frame・現在署名/current/元原本を固定profileとして認証する。Pythonundefined-scope静的検査は認証した動的AST注入名だけを明示しbaselineを除外せず、実artifact/schema/path/旧boot-row拒否・故障/資源後条件を独立試験する。正規runtime退役はSSC198の同NAME/原byte/保持inode→unlink/dirsync/一回reload/全effective宣言・hardening/full18/元原値不変→全新DB/十Ref/bus/FD/A/M正常後だけ認定し、その後別fresh一回resume/親1800s/API保持WebCaddy/真正DONE/native/正式へ接続する。新epoch/元run-cutoff/旧run復元・手DB書込・旧close正常化・Production gate/coverage/承認済み外部仕様の緩和0。

SSC211（2026-10-08、BUG820/YKT589、QA047既承認内の限定profile補足・RD/UI変更なし）：PG515/sourcea2/PG495/schema028/bootcc9の新所有回収は、実ISSUED4/元親bbb6dc timeout143を認証後Expiry→Cleanupを各一回stopし、依存Artemis060871も同世代終端へ到達したが、Artemis ExecStart primary終了履歴を設定不変扱いしてrevoke/intent退役前にUNKNOWNへ入った。DB全24/452・全原本/永続102・startup4原byte及び他全設定は不変、declared path/argv/ignore_errors/開始/捕捉PIDは保持し、Artemisの終了時刻/code/statusだけを現ExecMainExitTimestamp・全18property・同INV/manager終端/vendor全journal/PID1 stop-done/全kernel空へ束縛する。SSC205のprimary bindingをこの一Unitへ限定し、一般設定差のignore/aux n-aへの書換えを禁ずる。Expiry stoppedのみ保存、Cleanup stop-reservedは存在するがCleanup/Artemis stopped receipt未保存は未保存のまま保持する。現終端の直接証拠を保存し、receipt捏造や同stop再発行はしない。
固定Root Java310706/ticks1180403/argvSHA36f0d26dc4cbdf629ae3b837c2e15dc5b66c2341ac1cf019c5b0723ff2ffd456、固定Ref310735/ticks1180516/argvSHA8476771a5992c433aff204c9a4720bdeb612485ea72bf0dc9cee228185a923ac（sudo310704は対象外）、全task子exactRef一件/Ref子0・Root/同boot/実M-A inodeFLOCK/immutable7payload・全10kernel終端/全full原値/private before二読を現在認証・私有予約した場合だけ当child→Javaへ一回pidfd TERMで限定回収する。DBは同PG515専用peer/advisory現在保持か既idle期限後0を識別し、どちらも旧正常closeを推定しない。原値不一致/未知owner/第三子/foreign世代なら隔離保持。両旧owner/全peer/advisory/lock0・全raw不変を二読し、PG515 actual143・innercloseUNKNOWNと元親143を維持する。
その後は別fresh M→A→専用RWbatchDAO/advisory・独立RO全24/十Refで、正常handoff後の全terminal snapshot/configと元ISSUED4/readIssued/同元permit/owner及び署名/current/元原本を認証する。既Expiry/Cleanup/Brokerへstopは0、全終端vendor/PID1/wholekernelを再照合し、SSC210既canonical sameepoch revoke一回→SSC209単一API marker退役/dirsyncへ進む。失効前後の明示2profile、元permit/owner/native/DB/原本不変、新全DB/Ref/bus/root/A/M正常を独立に閉じる。運用工具限定再試験と同10Unit宣言/履歴・全故障/null/欠落/foreign/依存no-restopの再発防止を記録し、正常新scope後だけnative6role/runtime正規退役/別一回resumeを許す。親1800s/Root120s/Production gate/coverage/Currentbaseline/外部仕様は不変更。未知旧scope又は全親DONE/native100/正式/ITSTを当限定回収で合格にしない。

SSC210（2026-10-08、BUG817/YKT586、SSC209の現物profile訂正、内部SS補足・QA不要）：PG505 current現物はINVALIDでなくISSUEDであり、boot/run/activation一致・current原byte SHA87a7556e280c58a61d1390d69f5ecde78c430fd807f8a025c401af8bd17dd21e、startup exact4=current/元permit/元owner/単一API.start.intentである。元親bbb6dc timeout143・RootJava/launch不成立、API namespace拒否5回、Expiry/Cleanup正常0/Artemis060871生存というSSC209の他実証は維持する。Morning start-client失敗retainは正規issuer後、Root子の失効処理前なのでISSUED保持は正規隔離である。旧INVALID推定とその限定復旧入口を当profileへ流用せず、旧断定記録を訂正履歴として残す。Currentbaseline/Productiona2/PG495/schema028/署名BOM/業務仕様・期待値変更0。
PG513工具native-v1は新M-A/専用DB/advisory/十Ref/全24-452/永続102/全volatile・設定のbefore二読後、停止前state guardで拒否した。固定Root Java309605/ticks995739/argvSHAcee2b64efddd54fbbd7c72c48306d6a505c0a7f7d76bfd2e99ae39fbb11782c3・固定Ref309634/ticks995850/argvSHAebc1706cca5d81f5d45c802e3ca368ce28ac549d1549cd431d0c2c57d42d5357（sudo wrapper309603は対象外）、新bootcc9・immutable class4/Python2の原byte、全task子exactRef一件/Ref子0/実M-A inodeFLOCK/他owner0、専用DBの現在同peer-advisory保持又は既idle期限後0、全10Unit18/config20/cohort/kernel・全24/452/永続102/startup原4byte/native原byteを私有二読・予約した場合だけ当child→Javaへ一回pidfd TERMを発行して限定回収する。業務cohort/原値へ作用0、全旧owner/peer/advisory/lock消失・全原値/cohort不変を確認、元actual143/closeUNKNOWNを維持。DB idle/Ref busGC/工具消失は旧close正常の証明にしない。
次の別fresh M→A→専用RWbatchDAO/advisory＋独立RO全列/十Refで、現署名全187/完全pending原本・同activation/currentISSUED/readIssued実permit・data-only owner frame/全原値/当親失敗/full33journal/全kernel・現在cohortを再認証する。ISSUEDの元permit/ownerを保存して全同世代owned停止・vendor全journal/PID1/全10kernel終端を独立に閉じてからだけ、既StartupPermitFiles.revokeへ同epoch/boot/activationのINVALID値と実元permitを渡す。fresh invalidate/別epoch/current手書き/存在しないlaunch/Pair/publication再構成は禁止。canonical current一件のinode/byteとstartup directoryのsize/timeだけを許容deltaとし、同epochINVALID/元permit・owner全byte属性/元API marker不変を独立再読する。
その後SSC209の単一API marker限定借用gate（保持startup-root FD＋fresh held-entryの同inode snapshotであり、Intent objectの永続FD保持ではない）へ接続してmarkerのみ退役/sync、after exact3=currentINVALID/元permit/元ownerを確認する。初期ISSUEDと失効後INVALIDの二profileを明示し、単に両方を許す緩いguardへ変更しない。revoke/retire/innerclose不明は元stateと現在canonicalの相関を区別してM/A確認の下で同APIだけfailclosed再隔離、消費済scopeには操作せず旧UNKNOWNを保持する。新全DB/Ref/バス/root/A/M正常と独立peer/lock0後だけ限定新復旧を認定、その後別native6role/runtime退役/一回resume/真正親DONE/native/正式へ進む。独立ISSUED/INVALID/current全field/permit hash/各列・各stop/canonical失効の故障/競合/部分closeと実同source再試験を416以降に対応する。

SSC209（2026-10-08、BUG813814/YKT582583、QA047の内部限定復旧補足・RD/UI変更なし）：PG505/source a2/PG495/schema028/newboot cc9の真正親bbb6dcが元1800s timeout143・親kernel空となり、当boot API journal全33行にordinary-api193欠落のnamespace ENOENT5回（Java Root開始前）、Web/Caddy/Inspector/Bootstrap未起動、Expiry/Cleanup同世代正常0、当Artemis060871/PID38602/ticks396578だけ生存を独立保全した固定事例に限る。startup現物はsame currentINVALID＋元permit/owner＋API.start.intentのexact4fileでAPI/WEB launch・WEB/publication intentは不存在、requests全空。SSC179二launch/PairやSSC204 intent不存在へ偽装しない。Root私有failure全24/452batch（元442＋10段exactSKIP）/永続102/全native/全10Unit18property・20設定/全journal/原byte・metadataを二読し、fresh連続M→A→専用RWbatch DAO/advisory＋独立RO全列/十Ref・元署名full187/BOM/approval/current/完全pending原本を保持して、当前親失敗・残cohortの実identityと全kernelを再認証する。Expiry→Cleanup→Artemisを同世代正規stopとするが、依存による先行Artemis終端は同INV/full18/kernel/vendor全journal/PID1 stop-doneで照合して二重stopしない。APIのnamespace失敗子群は全journalと全kernel空で認証し、存在しないRoot child三値/launchを作らない。未知世代/第三子/owner/原値差/不明closeは隔離保持。
全10物理終端/全旧原値不変後だけ、既readRevoked(currentINVALID)の元permit/formerIssued・data-only owner frameの親/boot/run/activation/cutoff/deadlineを失敗親証拠へ結合し、当空Root0600/link1/ACLなし/tmpfs・同heldinode API markerのみ既BackupStartIntentFiles.observeQuarantine/retire/dirsyncを固定operator借用gate下で退役する。元currentINVALID/permit/ownerのbyte・metadata、全DB/原本/Backup/Transfer/旧nativeを保持し、ownerやpermitを消さず、newEpoch/current手書き/publication/WEB intent/Pair/launch/start/DONE/DB書込は発行0。途中unlink/sync/新scopeclose不明は旧成功とせず、同API固定markerだけの既quarantineServiceでfailclosed再隔離を試み、未知二次故障は非秘密で分離しM/Aを保持する。全新DB/十Ref/バス/A/Mが正常帰還し新operatorのpeer/lock0を別認証した場合だけ当限定復旧を認定し、旧親143/旧closeUNKNOWNは保持する。
その後の別fresh所有でSS193196 native6roleをnew-only所定NSS/mode/ACL/tmpfsへ準備、legacy9/全旧exec保持・4Unit effective role集合照合を実証してから、一回runtimeの正規退役と別fresh resumeへ進む。Production通常reader/issuer/Root120s/親1800s/資格情報/coverage条件は緩和しない。独立exact集合/null/foreign/元phase・各stop/同INV依存停止・intent前後/dirsync/close fault/競合・原値差拒否と同source実VM後条件を415以降へ対応、当復旧だけで真正親DONE/native100/CHR/正式/ITSTを認定0。
復旧gate補足：固定3file current/permit/ownerの全byteと相関を不変保持し、mutation中は当API空markerだけoptional（3/4集合）とする。開始はexact4、退役同期後はexact3で、retire内unlink後requireClearによるgate再照合を正常削除の誤拒否にしない。成功proofは全終端/全原値を含み、異常再隔離correlation gateは確認済M/Aと利用可能held-root/現在同相関の下でのみ動作する。成功proof失敗をfailclosed保全の禁止理由にしない。root.closeはFDを消費し、A/M又はUnref closeは例外でも所有を消費し得る。body/DB/Ref close故障を外側unwind前に捕捉して確認scopeを区別し同API再隔離を試みる。A close失敗はA未知/M確認、M close失敗はM未知/確認所有無しと記録し、全M/A保持や再操作を主張しない。工具process aliveだけで十Ref/DB/lock全保持とは扱わない。

SSC208（2026-10-08、BUG811/YKT580、SSC206/198の現cold分岐内部補足）：PG503新工具が固定runtime directoryをumask077下のmkdir0755で作成し実0700となったため、NAME作成/reload前に拒否した。旧UNKNOWNは正常化しない。現bootcc9/sourcea2/PG495・Root3262/ticks310103/argvSHA1416c7acc909846118faa7947e3cf1c5e1368bd945b2eba5d233a1c539a40287と固定子3291/ticks310212/argvSHA85c10c135c139c7757c0bb46840da1336d082297ac54678fe11f25a6d87248b5、実M-A inode/FLOCK/全task子・immutable class/Python・全10cold/full18/全24table442batch/永続102と現startup/coverage全metadata/hash・全config・空runtime Root0700の固定inode/原metadataを二読し私有予約する場合だけ、child→Javaのpidfd TERM一回で限定回収する。専用DBは当peer/advisoryの現在保持又は既idle期限後0を識別し、どちらも旧close成功にしない。後条件は両owner/全peer/advisory/lock0・全原値不変・runtime空同inode/0700。次の別fresh M/A/専用DB/advisory/十Ref/同署名/全原値認証下に、保存された当空Root0700単一directoryの同inodeだけ0755へ明示fchmodしdirsync、その0755/ACL無しを認証後だけ固定NAMEをnew-onlyで作る。既空Root0755は維持、欠落時mkdir後同heldinodeへfchmod0755、foreign/file/ACL/非空/原metadata不一致は拒否。umaskを下げて一般fileを公開せず、他directory/owner/業務UnitのTERM、old/run復元・業務start/DB更新/旧退役成功化0。全新scope正常後に別durable一回startへ進む。RD/UI/外部仕様不変更・QA不要、独立umask実fixture/拒否/競合/原値と実後条件へ追跡。

SSC207（2026-10-08、SS331332既契約を満たす工具是正の限定回収）：SSC206のPG501 cold工具が、typed署名/host readonly確認後・new namespace作成前に親接続readOnly混同で拒否されUNKNOWNを保持した場合だけ、固定現boot/Root親子/PID-ticks/argv/immutable byte/全task-child・M/A inode実保持と他owner無し、元全24/442/永続102/全10coldとstartup/coverage不存在を二読する。DBのidle期限後peer/advisory消失はclose成功としない。私有原本/前後captureとpidfd予約・直前同peerを確認して子→Javaのowned TERM一回、143/旧close未知を記録し、両PID/kernel/peer/advisory/M-A holder消失と全原値不変更後だけ別fresh修正cold工具へ進む。業務Unit/未知owner/再start/newISSUED/旧raw復元/DB手修正/一般UNKNOWN補修へ拡張しない。親接続は既RunReferenceRepositoryのRW/readCommitted/autoCommitfalse契約、独立全DB後条件readerはROとして役割を分離し、データ更新0を維持する。

SSC206（2026-10-08、SS内の保存profile更新、QA不要）：SSC165/174のcold契約を、再開時に実認証したPG495/source a2/schema028の固定隔離VMへ接続する。新boot cc9ed874-7f4f-450e-a188-8de1e42c8441、固定instance同一、canonical9＋既承認bootstrap-adminの全10Unit/full18/kernel冷停止、PG498after原値SHA1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3の全24table/442batch・永続5tree/102要素を独立二読する。旧boot/run内のruntime/startup/request/coverageとreadonly bind消失は正規退役・旧close成功ではない。旧runtime/epoch/permit/intent/rawを復元せず、PG499旧退役を未受入のまま保持する。新M→Aの実inode/Root owner→専用batch DB/advisory＋readonly全24→十Refの実継続所有下で、旧保全原値・cold/他peer0・現署名approval/current/BOM187・28SQL/29historyを前後で再認証する。固定現PG495だけ既承認freezeCandidateでhost readonlyを再確立し、既valid空rootは保持、欠落startup/3request/coverageだけ所定owner/mode/NOFOLLOW/new-onlyで準備、当bootと完全pending同activationへcanonical新INVALIDだけ発行する。pt-coverage共通rootは既承認0755、worker/root-privateはSS342所定owner0700等を維持する。全原値/manager/kernel/設定・全scope正常帰還後にだけ別fresh一回用通常resume/正規issuerへ戻る。旧成果の成功補完、業務DB/DDL/migration/worker/start/newISSUEDは当管理段0。競合/元値不一致/署名不明/閉鎖不明は隔離/非成功として保持する。型付きpin再試験、現boot拒否/競合/故障/上限/資源返却の独立PTと実後条件を必要とし、cold成功だけでPG499退役/親DONE/native100/正式/BUG544解決を主張しない。

SSC205（2026-10-07、QA047/BUG805/YKT574）：SSC204回収中のCleanup停止に伴うArtemis依存停止は、同INV/full18/start/end/全kernelとvendor full-journal/PID1 stop-doneを認証し明示stopを重複発行しない。7receipt後・canonical revoke前の固定PG496管理工具UNKNOWNでは、全24DB/原本/Backup/Transfer/設定/73startup byte・metadataが元beforeと一致することを二読する。固定boot/Root/PID/ticks/argv/class payload/全task子0/実M-A lock inode/他owner無し・専用DBか既idle期限消失を認証しraw/native/失敗証跡を私有保全する場合だけ、一回pidfd TERMを当工具へ発行し全旧owner/peer/advisory消失と全原値不変更を確認する。工具actual143は異常中断であり旧close正常でない。別fresh M/A/専用batch DAO/RO全24/advisory・全10終端/同署名/source/boot/current/pending/元permitで再受入し、sameepoch canonical current一件だけINVALID→全新scope正常帰還へ進む。旧73file/元原本/全DBBackup保持・intent退役0・newEpoch/permit/start/DONE/DDL/手DB書込0。一般UNKNOWNへの拡張/不存在Pair復元/旧成功化は禁止、各段未知は隔離保持する。

SSC204（2026-10-07、BUG799/YKT570、当PG493 timeout143・intent不存在だけの限定operator復旧）：元親INV52accf6d/PID3905484/boot e07aa706のtimeout143・全kernel空を正常化せず、真正live API4105598/INV730085ab、Web4108080/INV1dedba9e、Caddy4113865/INVb656fdfe、Artemis3939714/INV12360e61をfresh M/A/専用DB/advisory・同署名PG489/source388/schema028・全10Unitで現在値認証する。startupは同ISSUED epoch4d35762d-54b4-4187-ab03-cc9b7e9e3baf/元run91a748b4-1abe-484c-9682-44f46429b324/activation179758d2-5b77-443a-a743-bf0065e732ea、73file=当current/permit/owner/API-WEB launch＋旧17epoch各4file、三intent0を私有保存と二読で照合する。原本完全pending・24table全列/442batch・Backup/Transfer/nativeを保全し、SSC179の同cohort逆順owned停止/全kernel終端/原値再認証後のみ既canonical revokeで同epochINVALIDをcurrent一件へ公開する。Pair再構成・intent復元/新規作成/このoperatorによる退役済認定は禁止（退役数0）。旧68file及び当permit/owner/launch原byte/属性・原本/全DB/Backup/Transferを維持、newEpoch/permit/start/DONE/手DB変更0。半停止/失効/close不明はM/Aを保持し隔離を継続、全新資源正常帰還後だけ別pending配備/固定runtime正規退役/通常resumeへ進む。旧UNKNOWN/timeoutを正常化せず、独立拒否・各段fault/順序及び実現在世代の前後条件を記録する。

SSC203（2026-10-07、BUG799/YKT570）：完了compound読取り内の継続原本検査は同保持Sessionの六namespaceを再openして保持inode/device/securityと照合し、alive/owner-thread/未確定完了禁止/Root/元budgetを確認する。namespace検査だけからgraph/業務成功/DONEを発行せず、SS342のcompound前後と各intent退役前後で全graph/全row/seal/peer/receiptを独立再読する。原本内容や旧/run復元・SQL変更・capability再構成・cache・期限緩和0。

## SSC202 pending原本を保持した027→028限定移行（2026-10-06）

対象は隔離VMのPG487 pending `91a748b4-1abe-484c-9682-44f46429b324`・元cutoff/activation・INVALIDだけとする。新M→A→専用DB/advisory71419602→固定10Refとsame boot/loaded Unit/全kernel終端を保持し、署名PG486/schema027/current/approval・空request・完全原本graph・全24業務table・432batch十四列・Backup32/Transfer2・config/native/Unitの私有before-imageを取得する。停止済みRemainAfterExitのactive/exitedはlive PIDと混同せず、既terminal契約で判定する。旧失敗親30を正常closeへ変換しない。

移行前にRoot0700/0600私有pg_dumpの真正正常終端・header/list検証・syncを完了する。既V001～027の全byte/checksumと旧28履歴を独立に照合し、署名候補のV028一件だけをmigration専用roleでappend-only適用する。許可deltaはV028一履歴行、SSC201関数/owner/search_path/親専用EXECUTE、backup-profileのschema027→028一値だけ。全業務row・元原本/Backup/Transfer/epoch・Unit・既configは不変更、旧profileを保全しnew-only part/atomic/readbackでprofileを公開する。各段未知なら私有証拠と保持所有を残し、Flyway repair/clean/再発行/手DB更新/自動rollbackをしない。

移行正常帰還後のpending code-onlyは別の新所有でcurrent/approvalだけを署名候補へ公開し、epoch/原本/Unit不変更を証明する。続く別所有の一回用Root resume drop-inは固定元UUID二引数のみ、独立argv/metadata/effective再照合・予約/observer/一回start・真正終端後の正規退役というSSC112114198契約を適用する。元027Backupは元manifestのまま通常再用し、028への偽装/再dumpをしない。途中証跡を全親/CHR/native coverage/正式へ算入しない。

SSC201（2026-10-06、SSC200/BUG788/YKT562）：新V028の同source署名schema履歴/関数inventoryを候補、Root admission、Backup条件へ横断し、旧V001～027のchecksum・所有/権限・全実DBを保全する。基表cursorのrawを通常log/PT/Gitへ保存せず、全row seal/独立非秘密fixture/hashだけを公開する。PG/PT VMへのmigration/配備はfresh全回帰と専用pending復旧/実DB保全認証後の正規所有経路のみ、設計公開や限定試験をmigration/起動の許可として扱わない。

SSC200（2026-10-06、BUG788/YKT562、実装前補足）：保持中の原本Sessionへ、現activationを前後照合し全graph/inodeを二読するUUID限定readonly completed-run lookupを追加する。指定UUIDの実anchorと完了した元activation/完了時刻を確認して元BatchRunを返すdata能力だけで、active/pendingの書換え、resume/退役/permit、一覧を所有証明へ変換する操作ではない。欠落/退役途中/非完了/同日不一致/時刻逆転/graph競合は拒否し、元原本をDB値から再生成しない。

新生産sourceのprestart canonicalはNKPRESTART2とし、ALREADY_SUCCESSFUL referenceを固定順 prior_run_id,prior_cutoff_utc,row_id,attempt,started_utc,ended_utc,status,target,success,failure,bytes,reason,artifact_sha256 の13値へ明示拡張する。UUID/UTC6µs・ASCII/LF/既上限・固定slot・SUCCESS/NONE/元終了≦今回開始・同business_dateを検査、今回header/producer/fresh receiptと元完全成功を別保持する。Backup元参照は引き続きsame-run、非SKIPはliteral -、削除/Expiry artifactだけliteral -。既NKPERMIT1のdigest field/鍵/所有gate、外部64電文は不変更。旧NKPRESTART1保存byte/digestを新文法へ書き換えず旧source証拠として保全、混在を拒否する。

別run対応のExpiry requestはNKEXPIRYSKIP2、既10fieldの後にprior_run_id,prior_cutoff_utc,prior_step_id,prior_attempt,prior_started,prior_endedを固定順追加（ASCII/LF/canonical、最大1024byte維持）。元handleは元run/cutoffで構築し、今回runへ偽装しない。従来NKEXPIRY1の通常経路は不変更、旧NKEXPIRYSKIP1の保存物は保全し新sourceのcross-run証拠へ流用しない。同日/step・元完全SUCCESS/元原本・元audit cutoff−7日・現在fresh selector0を親/子/最終issuerで独立再読し、不明/非0では再purgeせず保全拒否する。新request/intentは通常親の現在所有だけが発行・正規退役する。

## SSC198 固定Backup途中世代の限定operator隔離退役・pending配備（2026-10-06）

SSC198限定補足（同日17:02、固定same-run一回用Unit引数）：pending code-onlyのUnit不変更条件とは別の新M→A→実専用DB/advisory71419602→private10Ref所有区間で、一回用 `/run/systemd/system/schubert-nk-morning-controller.service.d/pg481-once-resume.conf` だけをRoot管理new-onlyで作成できる。Root0755単一実directory/Root0644単一link・ACL無しregular file、旧署名base・既PG477 native drop-inは全byte/metadata保持する。唯一deltaは固定Morningの既署名base＋既native parent optionの独立literal argvへ `--resume 49437eda-1681-43a9-883a-424eb55a6166` 二引数を加えるExecStart再宣言（他Unit/RW/hardening/credential変更0）。未知drop-in/二重agent/余剰argv/別UUIDを拒否し、全Unit/kernel停止の同世代でdurable before-image保存→一回daemon-reload→effective ExecStart宣言/DropInPaths/RW/全hardening/旧停止18propertyを再照合する。独立expectedを実測argvから自己生成しない。新scopeが全部正常帰還してから別の一回予約/observer/startへ進む。reload/readback/close不明は隔離保全・再発行0。

今回親及び全対象kernelの真正終端後、別M/A/DB/10Ref管理区間でこの一回用runtime fileだけを原byte保持→同inode確認→正規退役→dirsync→daemon-reload/readbackし、既noargs＋PG477 nativeへ戻す。稼働中設定変更/旧/run復元/署名baseの編集/一般resume fallback化は禁止。host拒否/fault/引数優先順位・実VM新Invocation/元cutoff/全旧値保全/正常所有帰還を別証跡とする。これは隔離PG/PTの既SSC112/114通常resumeのsystemd束縛で、RD/UI・日次業務・QA047承認範囲を拡大しない。

本経路は利用者の今回明示復旧・内部SSC自走指示下の隔離PG/PT VM/Root管理者だけ。QA047の旧Pair退役を一般化せず、Runtime起動主体・Root権限・通常admissionを増やさない。元30分後の真正Morning timeout/normalCode1/status143・同boot/INV/start/end/旧PID-startTicks消失、fresh Backup正常0と明示stop0を元Invocation/full journalへ束縛する。全10Unitの18property/全kernel/Job/PIDを二読、未知/coldだけの結果復元や旧close正常化は不可。

新しい連続M→A→専用DB/advisory→固定10Ref保持下でold/new署名BOM/current承認/全namespaceとsame run/cutoff/activationの完全未完了原本・current INVALID/digest無しを再認証する。全24DB/旧411全列全行・旧全原本/Backup/Transfer及び当回新dump-only.part、Root0600/link1/ACL無し/tmpfsの旧request全byte・固定空backup-start.intent全metadataを私有保全/前後照合する。残留allowlistはこのexact request＋markerだけ、他intent/途中part/未知名を許可しない（既Backup保存tree内の旧.part保全は別）。旧子成功はarchive成功pair/親成功の代用ではない。

専用型付き退役入口だけが既observeQuarantine→同owner token retire→directory sync→不存在/readbackを行う。任意Unit/name/単純unlink/API-Web Pairへの拡張0。unlink後のsync/readback/資源close不明は固定Backup markerをtyped再隔離しM/Aを保持、再隔離不明も成功を返さない。旧request/二RUNNING/partを変更せず、全DB/root/ref/A/M正常帰還後だけ新退役完了を私有保存する。旧143/UNKNOWN/close不明は別証跡のまま。

その後の専用pending code-onlyは同exact原本/request/二RUNNING/partと全保全を認証した新M/A/DB/Refの連続区間で行う。一般requireNoUndeliveredWork/normalDoneを緩めず、旧署名/currentとnew fresh全6/署名/全payloadを保持してapproval/currentだけを一回切替し、同既INVALID原byte・実config/Unit/hardening/DDL/旧nativeを保全する。newEpoch/permit/start/DB更新0、未完了配備/closeは隔離維持。全scope正常帰還後だけ既SSC114/SS341 SSC198の通常同run resumeを別発行できる。各段独立fault/未知/foreign/owner競合/close/半退役再隔離と実全後条件を915/916/PTへ記録し、native未受入の公開設計を工程成功としない。

## SSC197 固定Backup入力のmode横断（2026-10-06、BUG771/YKT551）

SS341 SSC121の静的復旧config8名は、api.env/web.envだけRoot:既API/Web primary GID0600、common.yml/api.yml/web.yml/batch.yml/backup-profile.json/inbox-inspector.envはRoot:schubert0640。Inspector静的envは§6.9の0640のままであり、`.env` suffixを理由に0600へ変更しない。credential固定17名はRoot:Root0600、runtime Inspector envはarchive対象外。全allowlist・regular/link1/ACLなし・保持前後metadata・署名payload・実archive hash等の既存検査を維持する。既成功bundle、設定原byte/権限、秘密配布、業務外部仕様は変更しない。固定名ごとの独立mode表と未知/null/他catalog取り違えを試験し、実親Backup完成は別native受入を必要とする。

## SSC234 CLOSINGのnew-only原本とBootstrap entry（2026-10-09）

SS342の二terminal roleだけ、同owner/同profile/同checkpointでTERMINAL全帰還後に`<INV>.closing.exec`を新単link0600/保持FD/write-force-close-dirsync/hash/再読・前後identityで一回追加する。旧terminal/before-exec/原本Backupを保持し、repair/再試行/別path/別session/RootやAPI-Web aliasを許さない。attemptはagent/I/O前に消費し、TERMINAL失敗後/先行CLOSING/foreign-thread/重複は拒否する。追加点の末尾は同body独立試験で閉じ、採取点連鎖をしない。agent option/pin/outputnone/dumponexitfalse/private namespace/UID等は既契約を維持する。

SSC083のJava25 instance-main termination portをBootstrapAdminMainにも限定適用する。公開noargは固定環境・本番operation・測定callback・System.err・System::exitをbind、package ctorは同mainの順序/終了値を独立確認するdata/control-flow portのみ。FQCN/zeroargv/既0・20・50・70/初期ADMIN動作/未知business failureの既固定診断は不変更。CLOSING/終了portをadmission/初期作成authorityへ流用しない。

## SSC196 二つの固定terminal role namespace（2026-10-06）

SSC193/195の親Root:Root0755/ACLなし/tmpfs下へ、正常owned停止・M/A/DB/全原本・旧Backup/current/旧native全byte保全を認証したRoot operatorだけがnew-only `ordinary-inspector196`（既resolveInspectorのUID:primary GID0700）と`ordinary-bootstrap196`（既schubert-api UID:primary GID0700）を作成する。runtime mkdir/chmod/chown/repair/置換0。出力は`<INV>.terminal.exec`一回だけ、新単link0600・同保持FDのwrite/force/close/dirsync・再読hash・前後identityを維持する。Root/before-execやAPI/WEB専用roleへのalias0、旧exec/heaps/原本/Backup/退役済秘密は全保全し現/runへ復元しない。Unit/identity/phase/session/default及び採取失敗はSS342 SSC196を正とする。rawexec/credential/session/DB値は私有だけ、safe evidenceはhash/counter/actualsource-run/kernelと未確定事項だけ。公開設計は実装/native/正式品質受入ではない。


SSC194横断補足（2026-10-06）：SSC193普通terminalの新private inode/dir通常返却は、SS342のPT-only outer stop holdがJVM終了を待つ区間内に完了させる。元application finished後のmainだけからdump完了を推定しない。終了期限/Root管理namespace/旧exec・原本Backup・tmpfs cold保全・profile default不変更、部分dump及び非成功は保全し未受入とする。設計反映はfresh全6/同source実TERM・dump・正常owned返却・正式品質の完了ではない。

## SSC193 隔離PG/PT native採取namespace（2026-10-06、§11.1配備補足）

既存Production namespace/初期data/migration/原本Backupを変更しない。隔離PG/PTの現bootで `/run` と `/run/schubert-nk` はRoot:Root0755、既存 `/run/schubert-nk/pt-coverage` はRoot:Root0755・ACLなし（SSC195：旧0711はordinary O_RDONLY FD取得に不足）とし、旧coverage領域とexecを全保全する。新role名は `root-api193` / `root-web193`（Root:Root0700）、`ordinary-api193` / `ordinary-web193`（当固定NSS accountのUID:primary GID0700）だけ。管理者が正常停止/M/A/DB/現boot・元原本/Backup・current/lock/署名/旧5exec byte metadataの保全を確認して、既存親のRoot:Root0711/同inodeを一回だけ0755へ変更し新規専用directoryを作成し、runtimeは作成/chmod/chown/置換・旧/runの復元を行わない。agent固定pin/Root0755 parent/0644単link/ACLなし/ROはSS342 SSC193で規定する。出力roleはtmpfs・RWを保持capabilityから検査する。

既存OwnedTransferDirectoryのNOFOLLOW absolute segment/child保持と0600新private entryを使用する。nameは真正32hex INVと`.before-exec.exec`または`.terminal.exec`だけ、同role/phaseが決定しcallerの任意pathを受けない。`createPrivateEntry`はsingle segment/null/operation/closedをmutation前に検査し、O_EXCL|O_NOFOLLOW|O_CLOEXEC/0600で新inodeを保持する。writerは `/proc/self/fd/N` の実inodeへ有限byteをwrite/forceし、通常channel close→元file inode/owner/group/mode/nlink1/size/fullhash→保持native FD通常close→directory sync→同nameの保持再open/inode/fullhash→directory identity及びrole再open/通常closeを確認する。名前/dir置換を追従せず、既存regular/symlink/partialの内容一致を再利用・再forceの根拠としない。ACL/owner/mode/device/inode/size/namespace差異・write/force/close不明は非成功、partialを削除せず私有保全する。

runtime出力はRoot/ordinary世代別、同INVでも各role領域が分離される。Root before-exec/known終端・ordinary所有帰還後終端の意味はSS342 SSC193を正とする。原始exec/session/私有診断はGitへ格納せず、source/run/sessionの実限定照合・counter/hash/正常終了及び不明範囲だけをsafe manifestへ保存する。Cold bootで消失した旧tmpfs出力を旧archiveから現/runへ復元しない。設計公開は新profile配備・fresh全6/native100/正式品質完了ではない。

SSC192配備補足（2026-10-05、BUG730/YKT517）：正規署名code-only配備のdaemon-reloadは、停止済みCaddyの正常F18/旧Invocationを保持しつつ補助Exec履歴を両exact未実行へ戻すことがある。これをSS342 SSC192の旧世代拒否dataとして分類し、設定変更前後・全kernel停止・原本DB/Backup保全と新所有を維持する。補助n/aを旧処理成功へ補完せず、片側混合/未知/失敗履歴を拒否し、新Caddyは新普通actor・真正validate・新Invocation/socket/TLSで再認証する。旧/run/permit/原本を復元して再起動したことにせず、設計公開はnative受入と区別する。

SSC191（QA047内、BUG720/YKT511、SSC190の正常DONE配備停止中断）：旧工具の保持UNKNOWNにresume/exit APIがない場合、旧操作をそのまま成功再開するのではなく、次の限定管理者handoffを別入口とする。業務/原本/Current baselineの修復、新permit、DDL、startは本handoffでは実行しない。

1. 固定隔離環境の管理者start・namespace変更禁止、timer/path等の自動起動抑止を全移譲区間継続する。現在boot/旧工具PID/startTicks/loaded class・固定entry/実M/A inodeとOFD flock/専用DB session・advisory及び実保持scope、署名old/currentと候補、私有保存の完全原本DONE/activepending不存在・全DB14列/業務原値/history/Backup全属性hash/Transfer/33startup名前・全byte metadataを再同定する。履歴PIDや一般UNKNOWN表示だけから所有scopeを推定しない。
2. 旧holderがM/Aを実保持中、同定した管理者の固定stop-only操作で残るAPI→保守→Artemisを捕捉同世代の発行直前再照合後に一回ずつ正規停止する。Caddy/Webの既停止は再stop/再startせず実full18/全kernelを再認証する。普通API/Web143はSS342 SSC191の全witnessで認証し、旧工具の成功へ補完しない。原本/epoch/permit/DBを更新0。Morningを含む全9Unit/kernel終端を二読し、旧holder・全保全・同oldapproval/currentを前後再照合する。別世代/競合/UNKNOWNは隔離継続。
3. 全停止/保全成立後だけ、固定旧工具本人のboot/PID/ticks/entry/classを再認証しpidfdへ一回の通常TERMを要求する。SIGKILL/OS停止/任意pattern killは禁止。所定期限内の本人と子孫・全FD/OFD lock・旧DB二session/advisory消失を独立確認する。旧操作はinterrupted/143/oldCloseUnknown/activated=falseと記録し、kernel解放をJava正常closeの証拠にしない。非終端/不明なら次の取得・変異へ進まない。
4. 新M→A→専用DB/advisory＋readonly schemaを実取得し、同existing inode/現在boot・取得前後全9kernel・旧session消失・完全DONEと旧全保全原値/metadataを再認証する。既存SAVEがある旧工具やpending/3intent専用入口を再実行しない。別のcompleted-recovery入口内で正規code-only INVALID/current/署名新bootstrap Unit配置を完結し、全後条件と最外scope通常返却後だけ新成功receiptを保存する。旧143/close未知/BUG544の成功化0。
5. 工具はphase・primary/secondary・実保持scope・再隔離結果を非秘密で分離する。各段故障・null/未知/false・世代差・保全差・部分stop/close例外を独立試験し、原本raw/DB/credential/秘密をGitや通常ログへ出さない。私有captureはnew-only0600/parent0700・実終了/上限/全record/hashを照合し、属性不適合の旧captureと別に記録する。移譲に失敗しても独立承認済みhost作業は継続する。

SSC179（2026-10-04、QA047内の当該timeout世代限定復旧）：親の真正同boot/Invocation・18fieldがResult=timeout/ExecMainCode=1/ExecMainStatus=143となり、親kernel空・旧PID不存在を確認した事実は正常30/0/10でも旧UNKNOWN-close成功でもない。現在ordinary API/Webの真正manager/PID/ticks・固定UID/GID/groups/NNP1/全5cap0・argv/cgroupと親保持launch/owner/permit hashをprivate保存してから、連続M→A→専用DB/advisoryの下でCaddy→Web→API→残保守→Artemisの正規停止・全9kernel終端を確認する。停止後も生存時capture、現在の真正失敗receipt、署名full BOM/current/approval、完全pending原本・同activation、全261行14列/DB原値、Backup全20entry/全file hash/属性、非空Transferを再照合する。欠落した外部Web Root観測は未捕捉のままとし、親の真正launch相関と区別する。別世代、unknown/third child、未知namespace、保存差異、PID再利用、停止/close不明なら変異なしで隔離する。

当回startup現物はISSUED/current＋permit/owner/API.launch/WEB.launch＋API/WEB.start.intentのexact7fileでpublication intentはない。正規StartupPermitFiles.revokeに同epochのINVALID値と検証済み元permitを渡し、元permit/owner/launchを不変更でISSUEDだけを失効させる。fresh invalidateによる別epoch発行・手書きcurrent・旧/run復元は禁止。続いて既存Pair quarantineでpublicationを最初にnew-only隔離し、API/WEB両intentを再認証する。全保存/物理終端/所有proofを連続確認したtyped PairだけをWEB→API→publicationの順に退役/syncする。これはSSC168正常30/Web50の条件変更ではなく、真正timeout143/所有stop143という別の限定operator proofである。許可の再発行・業務処理・原本DONE・旧失敗解決を同操作で行わない。失効/半退役/再隔離/資源close不明は主原因・secondaryを非秘密で分離してM/Aを保持し次起動を拒否する。独立literal拒否/順序/各段faultと同source実VMのcurrent INVALID・全intent無し・残4原byte/属性及び原本/DB/Backup/Transfer不変が揃った場合だけ、この限定復旧を認定する。

SSC175（2026-10-04、QA048/SS331§9.4）：受付参照table/PK/id index/限定grant/固定孤児function/atomic cleanup kindは実際の最新migration末尾を照合してappend-only追加する。旧V001～末尾のbyte/checksumを書換えず、通常startupの承認schema-history/BOM/profileは新Sourceの全SQL hashと整合するまで配備・migration実行しない。technical Backupは既定`schubert`/`schubert_web_session`/`schubert_meta`の同一custom dumpへ新table/3列/indexを含め、restore inventory・Web/backup roleの権限を独立確認する。旧成功bundle/保存原本のcatalog/hash/DBへ新名を後付けしない。旧成功原本の通常resumeは旧bundleをそのまま認証し、新schema更新が必要なら既存M/A・新INVALID・全停止/DB排他・正規署名candidate・保全・新run契約へ従う。Web locatorを正として業務DBへ修復しない。schema追加だけでBackup/restore/native/IT-ST成功を認定しない。

SSC174（QA047/BUG544/YKT388、2026-10-04、SSC165保存VM再bootの内部接続補足）：明示OS停止で旧bootのtmpfs intentが消失した場合、私有archiveの旧permit/owner/launch/intentを現namespaceへ復元しない。現実に存在しない旧3intentをSSC168 typed退役の入力へ代入せず、oldIntentRetired=0・旧UNKNOWN/primary/secondary close不明を保持する。新bootの固定instance・現在のcanonical9Unit全18property（loaded/inactive/dead、Invocation/Job空、Result success、Main/Control/code/status/start/end全0）を二読し、全cgroup subtree空を確認する。新bootで生成されたM→Aの実inode/全kernel・専用DB/advisoryを取得前後で認証し、旧inodeを流用/再作成しない。既存完全pending原本/同activation、全DB14列/全行、Backup全treeの名前/type/metadata/全file hash、Asset/config/非空Transferを停止保全と照合する。今回保全対象は251行/Backup20entry、現承認はPG430（PG432は未有効candidate）であり、古いPG428の232行/PG425期待値を流用しない。

startup/backup-request/cleanup-request/expiry-requestは欠落時だけroot0700のnew-only作成を許す。既存の正常空dirはheld NOFOLLOW/owner/mode/ACL/tmpfs/同device・前後identityを認証して保持し、存在だけで拒否/修復しない。未知entry、current/旧intent、所有競合、保全差異、close不明は隔離・非成功、worker/start/新ISSUED/migration0。全保全と現承認の署名/full BOM/approval raw byte/selector一致後のみSSC165の当該新boot INVALID準備へ進む。これは旧失敗退役成功や通常起動権限の発行ではない。工具は固定stage/primary failure/各owned closeのknown・unknownを非秘密codeで分離し、raw message/cause/suppressed/秘密を出さない。非空Transferの正常date/part/readyを消して旧fixture空条件に合わせず、既存held directory/entry能力とSS333属性/size・全tree前後集合/hashで保全する。旧診断fixtureの意味/旧成功証跡は不変更。cold/競合/変異/未知closeの独立PTと同source native隔離後条件・原因/未解明範囲の記録が揃うまでBUG544/YKT388は未完了。

SSC168（BUG539/YKT383、SSC164の2子既知失敗再開）：旧SSC144単一子のxor入口を維持し、固定API+WEBだけの別Pair観測/退役入口を追加する。共通INVALID/current/permit全byteとdigest/boot/activation/ownerが一致し、2childのpid/Invocationが異なること、親/各childの真正捕捉世代と同source・署名BOMを要求する。捕捉Root→ordinaryとAPI本人/親readyの後にWeb普通50/親30/API通常TERM143・cleanupとなった場合も全親成功へ読み替えず、M下で実18field/全namespace/原本/全DB列/Backupをprivate保全→全8停止→A/専用DB/advisory/全kernel/全原本/BOM不変を独立再確認してからtyped退役する。3intentを先に捕捉、WEB→API→publicationの順で退役/sync/再検証し、current/原本を完成化・別Epoch発行しない。例外時はpublicationを先に再隔離しAPI/WEB両方の再隔離を個別に試み、不明はM/A保持して次起動を拒否する。intent有無の初期Pair確認と、半退役後も共通sourceを再読するgateを分離し、自分自身の正規unlinkを未知にしない。unknown boot/role/親/第三child/foreign markerやGCだけの終了code復元は不許可。

SSC167（BUG536/YKT380）：SSC165のboot-only namespace設定を署名payloadへ含める固定pathは `config/tmpfiles/schubert-nk-maintenance.conf` だけ。既存payload型の厳密集合へこの1件を追加し、全inventory・原署名・実file size/hash・Root/config group/0750dir・0640file・RO保持・再openは同じ検証を適用する。他tmpfiles名/拡張suffix/未登録file/secretを一般許可しない。配置先 `/usr/lib/tmpfiles.d/schubert-nk-maintenance.conf` はRoot管理の初期boot設定であり、signed template存在を導入済み・boot済みへ読み替えない。既存lock/holder稼働中のtmpfiles再実行・lock再作成/置換は禁止のまま、導入及び次bootの実確認は別後条件。

SSC166（BUG532/YKT377、同S3初回cold経路）：SSC131の旧正常143及び非空BOOT_JOURNAL契約は不変更。初期18field/kernel前後同値・全cold（Result success、code/status/start/end 0、Invocation空）を保持し、同boot/固定Artemis Unitの全journalをInvocation/time/cursor/grep/linesフィルタなし・最大4MiB/既存5s/親元期限内で2回取得する。成功した両readが厳密0byteの場合だけ別型NoPriorを作る。IO/timeout/overflow/null/unknown/空白/非空を無履歴へ読み替えず、最初の非空は既存厳格Closed収集へ戻す。STOP_SETの末尾は既存CLEANを捏造せず `NO_PRIOR|BOOT_JOURNAL_EMPTY|2|0|0\n`（実read回数/実byte数）を出す。これは現boot旧console証拠の不在であり、旧boot正常停止・GC成功・削除済journalの復元ではない。fresh typed Liveの実previous baseline一致及び前後Live/親/原本再検査の中で、同boot全journalを再取得し既存consume/contentSha256で全rowのfresh Invocation/実start以後、required startup3event、error/重複/foreign/surrogate拒否を検査する。Broker cycleの既存2readiness callback内（intent退役前）とMain末段・issuer再検査の両箇所に接続する。後から現れた旧rowを無視・成功fallbackしない。独立旧4goldenは不変更、新present/absent goldenと遅延旧row/失敗時intent保持をPTへ追跡する。

SSC165（BUG527/YKT376、隔離PG/PT保存VMの新boot初期準備）：旧bootのtmpfs intent/currentが消失した場合、古い失敗世代の成功退役を主張せず旧private証跡を保全する。新boot/固定instance・current不在・全8Unit＋Morningのmanager/kernel冷停止、既存lock同inodeのM→A、専用DB/advisory、pending完全原本同activation/全232行14列、Backup/Asset/config、既検証旧署名BOMを前後で確認する。startupと3requestは欠落時だけRoot0700/new-only、既存lockの再作成/置換禁止。保持原本に現boot/newEpoch INVALIDだけを初期発行し、通常resume/正規issuerへ戻す。全処理成功や旧143/30の正常化、旧current復元、DDL再実行はしない。PT-only coverage領域とrelease hostRO bindは現bootの別準備として再確認する。Production tmpfilesの固定namespace整合は新Sourceで検証し、operator限定成功から本番boot品質完了へ加算しない。

SSC161/PG-D336：API普通native startupは固定literal `API startup entered `の後にADMISSION/CONFIGURATION/PROCESS_RESOURCES/BROKER/DEPENDENCY_READINESS/APPLICATION_PREPARATION/CODECS_AND_ROOTS/MANIFEST/TRANSFER/READY_INFORMATION/OUTBOX_START/MANAGEMENT/CONSUMERS/ADMISSION_RELEASEだけを境界直前に記録する。enteredは成功証明にせず、既存固定終了診断と非成功codeは不変更。例外本文/credential/path/電文/DB値は記録しない。MAIN003は固定入力でADMISSIONと既存3診断の独立stderr全literalを照合する。隔離PG423唯一995失敗世代の現在物理復旧は914 SSC161に限定し、原本202全列/Backup/Asset/config/同署名/M/A/全kernel/pin観測を保持してtyped2intentだけ退役する。未知phase/過去cleanupを成功化せず、通常復旧/起動gateに例外を足さない。

SSC160（BUG512/YKT370、隔離PG/PT限定）：初期空Asset rootは準備完了ではない。SSC150の最小fixtureはmandatory `manifests/master.sha256`、実体、独立既定件数1と固定SHAを必要とし、data:read directory750/file640/単一linkでnew-only配置する。本番既定59627/移行baseline不変更。唯一Source995d3c5386・manifest2348f978・epoch058eaf2bの正常親30/API50世代の現在物理復旧は914 SSC160の捕捉三値/full18/private pin/原本192全列/Backup/全kernel/同署名/M→全停止→A→専用DB/advisoryを全て満たしたtyped2intentだけに限定する。50から到達phase・過去close・成功を推定しない。全private byte保存後だけ当該fixture配置/count1原子置換を行い、同Source通常Production入口で再試験する。通常Root/runtime/unknown復旧の例外を増やさない。

SSC150/S3普通API（2026-10-01、実装前）：`nk.api.storage.asset-manifest-entries`は非秘密内部設定、既定59627、canonical decimal1～59627。Production移行baseline全件/総byte/SHA検証は別の既存必須gate、隔離PG/PT fixtureの検証済み最小件数は明示overrideする。値はApiNonSecretConfig canonical hashへ含める。held Asset root→既存manifest読取（期待件数を自己manifestから算出しない）→HeldMediaFileInspector→既存Media8を、Transfer probe/全usageとLogin/Logout/Scenario6/Log/User query2/mutation5のgraphに接続し、Question7/async/outbox/Web未接続のままconsumer/A release/readyを許可しない。全codec/root/DB所有は業務listener終了まで保持、外部仕様/認証/Inbox/監査/SQL期待値不変更。

SSC159/S3候補更新operator追補：既存PG410の唯一PG408/source32c6a7b1e普通API正常50/親30世代は、独立full18/watch事前hash・同署名全BOM・真正Root→同PID普通API・元run/activation/INVALID/owner/launch/permitを閉鎖照合し、private durable原本全byte/182row全14列/Backupを保全する。50だけから故障phase/unassembled到達/過去closeを推定しない。連続M→全8Unit停止→A→再全kernel確認/同boot/旧PID再使用拒否/manager二読→専用DB/advisory/完全原本再確認を全期間保持し、現在の物理解消だけを再認証後、既存typed RootFailedStartRecoveryの2intent退役を使用する。一般50/未知世代/証拠不足/partialGC/signal/timeoutの自動退役は禁止、歴史close/DONE/readyを主張しない。続く新signed25SQL候補は旧V001～023全byte/履歴24不変/private restore pointを先に確認し、専用migration role/SET ROLE nk_ownerで承認済V024/025だけ適用、26履歴六列/DDL後条件/旧原本全列不変を独立照合する。effective BackupProfileのschema025だけを同新署名BOMから旧private byte退避→原子的置換/同期/readbackする。その他credential/ACL不変更。approval/current更新は既存署名/全BOM/M/A/所有readbackを再使用し、partial/unknownはINVALID/quarantine、通常issuer/Root/readyの例外にしない。工具試験はProduction PT分母外。

SSC149/S3 assembly追補：既存普通ServiceStartupAdmissionがA保持/self/proof/config/同PIDを検証したcallback内だけで、固定current Context/Snapshot/HMAC三credentialと各versionをpurpose別codecへ組立て、temporary copyを全分岐消去しpartial成功ownerも逆順closeする。借用DBと固定Transfer（schubert-api/schubert-web）の既存probe→全usage→quota/publisher/inspectorを同A区間で保持し、既存Login/Logout/Scenario/Logサービスを実生成する。同期31request完全登録gateは起動前に固定集合/nullを確認し、未登録はreceive/HTTP/A解放を行わず非成功とする。鍵/FD/可変quotaは外部公開しない。callback帰還前にconsumer等を停止してからcodec/root/DBをcloseする。同S3の残Media/User/Question/async/outbox/Webはこのgateの必要依存であり、仮handlerや部分readyによる完了代用を禁止する。

SSC148/PT配置追補：SSC103の`LoadCredential=artemis-users`・read-only bindを最正とし、固定app user名整合はroot管理source `/etc/schubert-nk/credentials/artemis-users`の旧hashを保持して行う。host instance etc/usersだけの変更・readbackを実効認証修正としない。旧source/instance/role全byteはprivate保全、metadata/各mq credential/Ops/Maintenance/role ACL不変更、全停止/M/A/同署名/完全原本/全172row・Backup不変とknown-auth失敗の物理解消証明下だけ新配置する。実Unit namespaceのsource同一・真正app認証/negativeまで確認する。秘密値はGitへ出さない。ROOTREC工具通常判定/runtime gateは緩和しない。

SSC147（BUG411/YKT328、SSC144～146の隔離既知失敗一件のみ）：Source32c6a7b1eの真正Root→同PID/API/全5cap0と実Brokerのnk_api認証拒否を独立観測した、当回API正常exit1/親30は、署名同Source・完全原本・INVALID・同owner/launch/permit・full18/独立kernel/Broker拒否のprivate durable保全、M/A/専用DB/advisory・旧162全列/Backup不変・旧PID消滅/全kernel終端/manager二読の全条件下で現在の全所有解消を再認証できる。過去のclose/DONE/成功receiptを主張しない。既存typed2intentだけを退役し、固定app login fixtureは旧private byte保存・全停止・限定置換/同期/読戻し後に通常同Source/same-run resumeで検証する。一般exit1/未知phase/証拠不足/partialGC/signal/timeoutの解放は禁止。unknownはINVALIDと固定publication quarantine、復旧不明はM/Aを保持する。Productionの通常Root reader/issuer/2FD/資格情報/ACL/ready条件に例外を追加しない。299300/SSC147へ記録する。

SSC143（PG406実拒否後、BUG403/YKT323）：Java selectorはUbuntuの実固定二段 `/usr/bin/java`→`/etc/alternatives/java`→`/opt/jdk-25.0.4/bin/java`。両selector root:root777/link1、`/etc`/`alternatives`もroot:root0755/NOFOLLOW/ACL0で保持し、両linkのO_PATH保持typed metadata、保持parent配下のNOFOLLOW named属性・literalと同名再保持を前後比較する。独立OS lstat/fstat/proc魔法statは同symlink dev/ino/modeを示し、既存保持link検査は緩めない。下記SSC137の唯一linkという初期仮定はこの二段固定profileへ訂正、任意link/relative/別target/chain増加は拒否。最終JDK Java ELFのtrusted whole SHA/cap不存在とsetpriv保持exec/全観測close/第三継承FD禁止は不変更。既存VM selectorの修復/書換を実装の前提にしない。PT297298・421の実CLI/独立golden/nativeを根拠とする。

SSC141/隔離trusted配備内部補足：S3候補へ進めるときも同M→固定全8Unit/全kernel停止→A/再停止確認→pin元byte署名/全BOM→元run完全未完了graph→現在原本全byte保全→new epoch INVALIDの順を維持する。旧ISSUEDは厳密readIssued/raw SHA/旧承認release一致と全binding確認後だけ新INVALIDへ失効し、旧permit/owner/launchは消さない。残service intent/part/未知名は保留・拒否し自動修復しない。Root Unit候補の許容deltaは固定API/WEB ExecStartと5cap候補、SSC139のAPI保守子Requires削除だけ、旧署名byteとの閉鎖変換を検証してnew-only退避する。実ordinary exec/ready/五cap0の認定を配備toolから捏造しない。固定tool/private証拠・元backup実体はGit格納しない。

SSC137/S3接続追補（実装前）：当回startupの閉集合に`<epoch>.API.start.intent`/`<epoch>.WEB.start.intent`を追加。固定API/WEB selectorからのみ導出しnew-only root600/size0/link1/ACL0・dirsync後にsystemctlを一度呼ぶ。Rootは当回role intentが厳密存在することと、正常client帰還後の実Root三値launch一致を双方要求する。他epochのintentは正常artifactとして許容せず、次MorningはM取得後・原本/DB/stop前に全startup名を検査し残留intent/part/未知名を拒否。UNKNOWNやRoot未完成30/ordinary50ではintentを自動退役せず隔離する。正常readyの同世代証明と実全終了がない限りretireしない。親は実捕捉前の想像Invocationをticketへ記載しない。Root待機は実Unit ExecMainStartTimestampMonotonic+120秒と元Morning deadlineの小さい方、期限更新不可。

SSC137/保持ELF追補（実装前）：隔離Ubuntu amd64のtrusted util-linux `2.41.3-3ubuntu2.2` deb SHA256 `11fd410b1d3797b1e9127b68302160213c15e1553745fb6982e270b1e32d1f2a`から独立展開したsetpriv ELF SHA256 `86965a019d37dc11d176ce8cbe9f5f5f8f37027c95e03cb4a8cad4c73d940993`、既存toolchain Ubuntu OpenJDK `25.0.4+7-1~26.04` JRE debの独立展開Java ELF SHA256 `c324471f8b7933a3cb401eafbc35a7055443779b438a3ab928bda3867a1b8ab1`を閉鎖platform期待値とする。全固定root祖先0755/uid0/gid0/NOFOLLOW/ACL0、ELF regular0755/link1・x86_64/class64/LE/全byte SHA、security.capability不存在（ENODATAのみ不存在、ENOTSUP等は不明拒否）・mtime/ctime/dev/ino/size安定を要求する。Java唯一root-ownedlink777/link1→既定JDK targetを前後再読。setpriv held FDはCLOEXEC、exec入力以外の全観測ownerは先に正常close。Java FDは第三継承にしない。別OS/CPU/tool updateはこの固定profileを無断拡張せずITでtrust metadataを更新し再試験する。

SSC137/§6.17内部追補（2026-10-01、実装前）：固定startup root0700/tmpfs内の当回実ISSUED epochだけから`<epoch>.owner`/`<epoch>.API.launch`/`<epoch>.WEB.launch`を導出する。任意name/path/別UUID選択factoryは禁止。既存MaintenanceOwnerFrame全byte（cleanup empty）をownerへ保持し、当回boot/run/activation/cutoff/epoch/実Morning三値/元deadlineを束縛。launch byteはASCII/LF、`NKLAUNCH1\n`から固定順service/boot/epoch/permit_sha256/owner_sha256/invocation/pid/start_ticksを`key=value\n`で記載、serviceはAPI/WEB、hashは実raw全byte SHA256、三値は真正Root manager/kernel/manager二読の当回値。root600/link1/ACL0、新規part→force→NOOVERWRITE公開→dirsync→全byte/metadata readback、既存canonical artifactは保全し再使用/修復不可。namespaceは正式固定名epoch.current（SSC140）・canonical epoch permit/owner/API.launch/WEB.launchと当回API/WEB start.intentの限定集合、permit-start.intent/part/未知名は拒否。古いartifactは今回権限へ流用しない。Rootの普通5credentialへowner/mq-opsを追加せず、Root host専用固定db-api又はdb-web/mq-opsを厳密NOFOLLOW/localRW/owner/ACL/EOF/消去で読む。原本pending/completedとsame-current最後再読、全観測closeをexec直前まで維持。独立golden/hash・null/malformed/別世代/close/unknown/実VMをPT297へ対応する。

SSC133 BACKUP_RETENTION具体byte（2026-10-01、実装前）：`NKBRET1\n`に§6.17共通boot_id/epoch_id/run_id/cutoff_utc/activation_id/morning_invocation_id/broker_invocation_idを同順で付ける。続けて`MODE|NEW_SUCCESS又はREUSED_SUCCESS又はFAILED\n`、`CURRENT|actual directory名strict UTF8hex又は-|actual MANIFEST raw SHA又は-\n`、`ROOT|actual mode|uid|gid|dev|ino\n`（非rootbackup UID/GID・0700・dev非負/ino正）、`COUNTS|before_all|after_all|successful_after又は-|deleted|protected\n`を固定順。successful_afterは新規SUCCESS時のみ全検証後保持数、READONLY二modeでは全世代未検証なので`-`（0と捏造しない）。actual nameをASCII順で`BEFORE|name_hex\n`、`AFTER|name_hex\n`、実完了削除を`DELETE|name_hex|manifest_sha\n`、実検証保持を`RETAIN|name_hex|manifest_sha|dump_size|dump_sha|config_size|config_sha|credential_size|credential_sha\n`、保護を`PROTECT|name_hex|reason\n`のgroup固定順に置く。reasonはUNKNOWN_NAME/PART/NOT_DIRECTORY/UNEXPECTED_FILE_SET/MALFORMED_MANIFEST/CONTENT_MISMATCH/NON_SUCCESS_PAIR/READ_ONLYの閉集合。CONTENT_MISMATCHは全正常IO/close/同inode/owner検証後に確認した型・size・digest差だけ。IOException/SQL/close/未知Throwableを当該reasonへ変換しない。SHAは実閉じた全byteの値、全数字canonical decimal。最大16MiB、names最大4096・1name strict UTF8 1～255byte・NFC変換なし。現在成功bundleは同Epoch原本run/cutoffへ束縛、NEWは現在bundleを保持7内に要求。counts/list/set削除/全hash/rootと保存結果を末段再読、継続borrowed rootを閉じる前にも再確認。pure byte encoderは発行権限でない。独立PT input/golden/実FD/SQL/nativeを揃えてからgate受入とする。

SSC126接続前補足（2026-10-01）：Expiryの親読戻しは`ExpiryObservation`として今回の完全handle、今回ended/result、当回真正TerminalReceipt、実audit、別のoptional元Priorを保持する。通常SUCCESS/WARNING/FAILEDではauditは今回handle、ALREADY_SUCCESSFULでは今回SKIP全0/ended=startedをDB再読した上でauditは元handleの実値と明示する。元auditを今回terminalへ読み替えず、SKIPのreceiptも当回EXPIRYだけ。Morning callback内で返値を保持し、発行時は同Accessで再読する。data record自体は発行権限を持たない。既存のAPI/Web/NKPERMIT1外部契約は不変更。

Cleanupも当回7terminal、当回CLEANUP receipt、固定7slotの元SUCCESS参照を別に保持する。ALREADY_SUCCESSFULのみ参照を要求し、同run/business_date/step、異なるrow、より小さいattempt、元ended≤今回started、元SUCCESS/NONE/完全count・byte・diagnostic再読を必須とする。その他SUCCESS/WARNING/BACKUP_UNAVAILABLEには元参照を付けない。当回snapshotと参照の取得・発行前再読は同Morning Access/advisoryのREAD_COMMITTED transaction内、最新7row全値の一致を先行する。これだけではLog END/Inbox summaryの別完全gate検査を代用しない。

STOP_SET前段の値保存は、既存`MaintenanceUnitTermination`のbus/kernel/bus一致とGetUnitProcesses空配列検査をそのまま使う。A取得後、current INVALID生成前の固定8Unit順（CADDY/WEB/API/CLEANUP/INSPECTOR/EXPIRY/BACKUP/ARTEMIS）についてmanager12fieldと固定host cgroup root・sys・fs・cgroup・system.slice・optional leafの5属性（mode/uid/gid/dev/ino、既存ACL/FS検査済）を同Morning root snapshotとともに保持しControl→Stage→Mainへ渡す。前段stop中の値で代用せず、発行時に保守後8Unit全部へ再びquiescentを要求しない。末段は当回Backup停止、Inspector終端、Cleanup/Expiry保持receipt、同Broker生generation、API/Web/Caddy停止を別に照合する。初期観測保存だけでは旧Artemis clean-stop journalの未接続を埋めず、STOP_SET gate成功へ昇格しない。

Root effective configは同Morning actorの`RootReleaseAdmission.inspectConfigurations`から既存ServiceConfigFiles.productionの固定common/API/Webを保持inodeで読み、common二読の全内容一致、両shared parser、API/Webのasset/transfer実効path一致と6root lexical非重複を検査して保持する。release署名/BOMのraw template hashと、この実配置のeffective canonical hashを別fieldとして扱う（effective YAML未収載の署名BOMへ存在しないpathを捏造しない）。公開前の再読は全raw内容と実効hash/root一致を必須とし、commentだけの変更も途中漂移として拒否する。unknown keyやparse不正は既知の失敗閉鎖、NPE/未知provider Runtimeは正常化しない。configだけで全root/全gateを通ったことにはしない。

6rootの未具体化NSSは固定`schubert-data`（ASSET owner、primary schubert-data、読取groupはschubert-read）、固定`schubert-migration`（STAGING owner/primary）とする。LOGはroot:schubert0750、STAGINGは`/srv/schubert-nk/staging`基底rootをschubert-migration:schubert-migration0700、その直下run childも0700。ASSET schubert-data:schubert-read0750、既存TRANSFER schubert-api:schubert-web0750、BACKUP schubert-backup primary0700、ARTEMIS schubert-artemis primary0700は保持する。追加NSS/rootは署名fullBOM、同M/A、全8停止のtrusted initial provisioningで不存在時のみ作成し、既存配置への所有/権限修復は行わない。空Asset rootを初期化できるがasset実体の移行・互換検証完了を代用しない。今回issuerのactual root観測は未完了。

SSC126（2026-10-01、正規issuer実装前）：API/Web effective hashは署名BOMだけのraw YAML hashで代用せず、保持実common/role YAMLと同じshared strict parser/default/precedenceから取得する。2既存parser・独立vectorをbootstrapへ移すがcanonical契約は不変更。Root Morningの6root/10step/5gateを同M/A/原本/INVALID/元30分/真正Broker内で収集・再確認し、今回SKIPと元成功参照、実producer receiptを別々に保持する。共有config parse成功やdata frame単独はissuer authorityではない。具体gate codecとactual readbackは接続前に本§6.17/PT295へ追記し、未定義digestの仮発行はしない。Source変更群を閉じて全6 security回帰/実同owner発行→Root/APIWebへ継続する。

SSC125具体化（2026-10-01、BUG369/370・YKT290/291）：後掲SSC111の「Expiry LoadCredentialは4名だけ」は、同Morning所有を結線する本補足で5名（既存4名＋maintenance-owner）へ置き換える。Root Morningには既存db-batchに加え、固定mq-opsのprivate copyだけを渡す。アプリrole/子secret catalogは拡大しない。Broker startは閉鎖BROKER/artemis.service、intentは既存root0700 startup配下のbroker-start.intent。M取得後・DB/原本/停止前に残留markerを拒否し、daemonをoneshot receipt engineへ渡さない。実Rootが固定schubert-artemisのNSS primaryのみを照合し、manager7値とprocfs boot/PID/startTicks/UID/GID/Groups/zero capabilities/NNP/cgroupを前後で照合、既存Root/Inspector/APIWeb契約は不変更。

Broker回復の追加根拠は、真正fresh Invocation/boot/unitに限定した全console journal JSON（最大4MiB、並列drain、元期限以内・query5秒上限）。systemd必須metadata/重複cursor/UTF8/厳密JSONを照合し、vendor2.56.0の実logger定数AMQ221013 NIO・221007 active・221001起動を確認、優先度error/AMQ224/ERROR/FATALは拒否する。これは全Ops/role/topology/settings/acceptor/圧力・実Expiry結果と合わせる証拠であり、journalだけでpermitを作らない。MQの全既存固定管理exchangeは同期callbackだけの同親期限へ束縛し、2秒上限と残時間の小さい方・前後guardを使う。callbackの入替/別thread転送/期限の更新は禁止。SQLは親期限内の接続・socket/query/local statement timeoutとpre/postcommit、未知は保存真実を保持する。

SSC125/BUG369（実装前）：ARTEMISの固定read-only18propertyはsrc/deployment/systemd/artemis.serviceのsimple/on-failure/Remain=noと一致させる。active/running/Job空/MainPID非0/Control0・fresh Invocation/start>0/end0のデータ判定をworker oneshotと区別し、元Source Unitをoneshotへ変えない。Morningだけが同原本/M/A/INVALID/共通deadlineでBrokerを開始し、実Ops/recovery・fresh生存の独立証明なしにpermitやExpiry成功へ進まない。EXPIRY start対象追加はRoot Morningだけ・既存固定expiry-request namespace/expiry-start.intentに限定する。Expiry専用LoadCredential maintenance-ownerは同親frameのprivate readonly copyで、親生存/元deadlineとbindし任意起動能力を与えない。初期namespace/Unit変更はM/A/全停止/pin署名fullBOM/既存private退避を先行し、既存旧active/原本/DB/Backupを保全する。293/294、SSC117/119下位。

SSC114固定request補正：SSC113のsame request再使用は同一実試行の場合だけ。新実開始時刻resumeは旧file保持/全byte・metadata/namespace前後照合とDB両ABANDONED完全根拠を得てから既存retire/force→新part/CREATE_NEW/force/readbackで置き換える。Root old/new run/cutoff一致・新INVALID・M/A・全8終端・intent無しが必須。旧fileの存在だけを復旧許可にせず、ctime/size/型/ACL/FS異常/未知DBは保持拒否。公開前crashは次回strict隔離/明示再実行で扱い、旧DB成功や旧epochへfallbackしない。

SSC113固定Backup request補足：新規runは従来CREATE_NEW/part/force/atomic公開を維持。明示resumeだけ、同M/A/原本/DB/current INVALID・intent隔離・全8終端が外側で証明済みのscope内で既存requestの同run/同cutoff・root0600/link1/ACL0/tmpfs/RW・全byte/保持前後namespaceを照合し再使用する。MISSINGだけ新規公開、COLLISION/UNAVAILABLE・foreign/corrupt・途中partの修復や削除はしない。再使用はarchive/step成功の証明ではなく、後続実worker/fresh Invocation/両結果/全終端/退役が別必須。

SSC110/BUG340横断補足：immutable release layoutは `config/effective/backup-profile.json` と `config/effective/backup-age-recipient` のexact2pathだけを追加許容し、両payloadは他dataと同じroot:schubert0640・single-link/ACLなし/全size・hash・namespace照合を受ける。任意effective file・秘密key・alias・追加dirを許容しない。実 `/etc` profile/recipientのmodeは前述0640/0600のまま別gate。署名後layout拒否を迂回して原本発行しない。

SSC111固定Expiry request：source `/run/schubert-nk/expiry-request/expiry-request`（directory root0700、file root0600、tmpfs/ACLなし/new-only/force/readback）。private copyは当該Expiry UnitのCREDENTIALS_DIRECTORYだけ。NKEXPIRY1 ASCII/LFの固定順はrun/activation/cutoff/boot/epoch/broker/step_id/attempt/started/skipped、末尾LF・canonical UUID/UTC Instant/整数/true-or-false、最大1024byte。brokerは当該Artemisのnonzero32lowerhex Invocation、stepは当該runのCLEAN_EXPIRY完全handle。cleanup-request/NKCLEAN1との相互受理禁止。LoadCredentialはexpiry-request/db-batch/mq-maintenance/mq-opsだけ。MQ login名はschubert_maintenance/schubert_opsで、role名をusernameへ読み替えない。秘密byteは既存credential readerの保持inode/全close/消去で扱う。

SSC110 canonical profile確定：ASCII compact JSON、最後にLF一つ。固定順 `profile,host,app,schema,os,jdk,postgresql,artemis,age,pgDumpWrapperSha256,pgRestoreWrapperSha256,pgDumpSha256,pgRestoreSha256,tarSha256,ageSha256,artemisArtifactSha256`。全値string、profileはNKBACKUPPROFILE1、version tokenは既存BackupVersions契約、hashはlowercase64hex。余白/escape/CR/未知・重複key/順序差/末尾extraは拒否。pg_dump/pg_restore wrapperの正規実体は`/usr/share/postgresql-common/pg_wrapper`、ELFは`/usr/lib/postgresql/18/bin/pg_dump`・`pg_restore`、tar/ageは`/usr/bin/tar`・`age`、Artemis配備artifactは`/opt/apache-artemis-2.56.0/lib/artemis-cli-2.56.0.jar`。ここでpath/versionを環境入力へ開放しない。工具変更時は配備profile・署名BOMを一貫して再検証し、caller supplied tool hashだけでは認証しない。

SSC110実装前補足（実親Backup入力）：非秘密`/etc/schubert-nk/backup-profile.json`はroot:schubert0640・regular/link1・ACLなし、最大4096byte。固定`NKBACKUPPROFILE1`は実host/app/schema/os/jdk/postgresql/artemis/ageの8versionと固定pg_dump/pg_restore/tar/age/Artemis配備artifactのSHA256を持つ。配備toolが実vendor package version/工具binary hashと対応を検証し、環境別render後の同profile原byteを署名されたrelease inventoryの`config/effective/backup-profile.json`へ収録する。親は真正root/current承認BOMのpayload hashとprofile原byte、実platform/schemaとprofileのapp/schema/OS/JDK、現在の保持工具hashを照合してからarchiveを生成する。caller supplied profile/hash/booleanをnative権限へ読み替えない。詳細JSON canonical codec/goldenと工具の具体配置は実装前に後続PTへ固定し、未定義のまま親受入としない。

同補足の固定archive入力集合：config root `/etc/schubert-nk`からcommon.yml/api.yml/web.yml/batch.yml/api.env/web.env/backup-profile.jsonだけ、credential root `/etc/schubert-nk/credentials`からdb-api/db-web/db-batch/db-migration/backup-pgpass/mq-api/mq-web/mq-maintenance/mq-ops/api-context-aes-current/api-inbox-response-aes-current/operation-hmac-current/web-session-aes-current/web-revoke-aes-current/web-log-aes-current/artemis-usersだけを使用する。dir探索からallowlistを増やさず、各正規name/type/owner/mode/ACL/保持前後snapshotを確認する。公開recipient source名は既存§6の`backup-age-recipient`を使い、旧VM test-only `backup-recipient`は破棄せず未認定材料として保全する。復号private keyをserver/Gitへ追加しない。暗号化credential archive/DBdumpはPGPT実物もGit外private保存。最終manifestは既存NKBACKUP1/完全両handle/独立実hashと同owner DB commit/readbackへ束縛する。

SSC107/PG363：固定親MorningのUnitはSS341/342の`Type=oneshot`・`TimeoutStartSec=30min`、親から子への`Before`なし・target親のみ必須起動とする。`RootStartupContext.MORNING`はその実ExecStart中の固定MainPID/Invocation/ControlGroupを観測する。`backup-start.intent`はUnit timeout/SIGTERM/親死亡では自動retireせず、次回M取得直後の厳密不存在gateが残留を拒否する。`SendSIGKILL=no`下の終了不明を成功へ変えず、現current INVALID・worker Unit/marker/OS lockの実観測とoperator隔離を要する。30分経過時の親単調budget・実systemd終了とM/A後条件は別PT/実VM受入まで未認定。

SSC106/PG355：固定Backup start intentは既存`/run/schubert-nk/backup-request` root0700/tmpfs内の`backup-start.intent`という空root0600 regular/link1/ACLなしの別fileとする。`backup-request`のcanonical byte・子のLoadCredentialは変更しない。親M/A内で同root保持FD相対CREATE_NEW→file force→directory force→同inode読戻しを行い、失敗/残留を消去修復しない。次回親はM内の最初の永続変更より前にmarker不存在を確認する。同一親のretireだけがfresh worker receipt/全Unit終端/明示stop/原本照合後に同inodeをunlink/dir forceし得る。markerの中身を資格情報や任意commandへ流用しない。

SSC103/PG321補足：Artemis JAAS hashed user propertiesのtrusted root配布元は `/etc/schubert-nk/credentials/artemis-users` regular root:root0600、起動前にroot所有で検証する。`artemis.service`の固定`LoadCredential`が作るprivate `/run/credentials/artemis.service/artemis-users`を、Unit mount namespace内だけで既存instance `etc/artemis-users.properties`の期待pathへread-only bindする。host側の秘密property実体を配備手順が勝手に上書き/消去しない。Source欠落、bind/ACL/権限/実Unit不一致は起動失敗とし、broker既存file fallbackを認可しない。実配布・JAAS認証・journal cleanは隔離VMで別実測まで未認定。

SSC100/PG317: 親全8対象・12field・真正host cgroup2全終端・停止方針/worker receiptとの分離はSS341冒頭を正とする。leaf存在時にmanager ControlGroup空の観測から全process不存在を推定しない。固定ControlGroupへのbindingと全nested queryを確認し、全保持能力のclose後だけ限定終端観測を返す。未配置実Unit/unknown client/全親未達ならapproval/permit/業務開始を成功へ補完しない。

SSC093/PG310: root朝controller固定Unitはschubert-nk-morning-controller.service、RootStartupContext.MORNINGで自己由来を認証する。backupのcold/post-stop全終端はSS341 §5の固定Slice/Delegate/ControlGroup＋真正PID1 host view＋NOFOLLOW cgroup2 leaf不存在/存在時全processの厳密条件を適用する。親だけがM/A/原本/current INVALID/DB両step begin commitを所有し、nonsecret backup-requestのprepare/retireは全Unit終端の内側だけ。API/Web child catalogの追加・秘密増配・権限緩和・bus error→emptyは行わない。実接続とPTは018141以降、fullbackup/morning/許可発行未達を省略して受入しない。

SSC093/native026配備検証: root専用前段が固定PID1 exe/rootの由来を検証するには、そのkernelアクセスが実際に許可されるroot Unit設定を必要とする。隔離VMでcapability全空はPID1 exe read拒否を実測、fixed self cgroup/proc/Invocationは一致した。root-only試験Unitのbounding CAP_SYS_PTRACEを最小候補として検証する（一般ptrace操作/任意PID/pathを実装しない）。これはAPI/Web/backup普通主体のzeroCapsを緩める変更ではなく、root前段から最終serviceへは従来どおり全capabilityをdropする。親backup生成に要る別root権限は実用途ごとに検証し、全capability許可を安全条件の代用としない。

SSC092/PG309実装前補足: 固定backup-request sourceは `/run/schubert-nk/backup-request/backup-request` root:root0600、親directory root:root0700/tmpfs、M/Aとbackup Unit全終端の排他下でnew-only公開/原本一致retire。systemd専用backup Unitは固定LoadCredentialで非秘密requestとbackup-pgpassを受け、API/Web5材料catalogやmaintenance原本公開権限は変更しない。requestはcanonical version/run UUID/内容生成開始時刻のみ、任意path/command/UID/role/DBattempt禁止。固定NSS backup専用入口はbackup primaryとrelease/config読取に必要なschubert groupのみを明示し、API専用groupsをコピーしない。Inspectorの固定18field観測をBACKUPに内部共用し、backup receipt0だけ/fresh Invocation/empty-process/前後安定、RemainAfterExit保持と次回stopを必須とする。parent/M/A/budget全接続未達は単体成功へ代用しない。

SSC089/PG302 code前の現在許可canonical record: ASCII LF、最大8192byte、未知/重複/順序違い/末尾欠落/CRLF/非ASCII拒否。epoch.currentは`NKEPOCH1`＋state/boot_id/epoch_id/run_id/cutoff_utc/activation_id/permit_sha256の固定key順、state INVALIDはdigest `-`、ISSUEDは小文字64hex。permitは`NKPERMIT1`＋boot_id/epoch_id/run_id/cutoff_utc/activation_id/broker_invocation_id/release_sha256/api_config_sha256/web_config_sha256/roots_sha256/prestart_steps_sha256の固定順。boot/epochは非zero canonical UUID、既存run/activationのUUIDとcutoff UTC固定6桁microsecondをそのまま束縛し新cutoffを生成しない。Broker Invocationは非zero小文字32hex、全hashは小文字64hex。親A内でroot-owned原本・permit実byte SHAと現在boot/epoch/run/activation/digest完全一致後だけISSUEDを受理する。record parser/value単独・公開test vector・DB成功行だけで許可を発行しない。FAILED/欠落工程を成功digestへ置換しない。root fullgate/実prestart evidenceの意味と所有・原本atomic公開/読取が別必須で未実装。

SSC089（code前、root/child release selector具体化）: /optはroot:root0755、/opt/schubert-nkとreleasesはroot:schubert0750、version directory/root-owned非秘密manifestもroot:schubert0750/0640・ACLなし。唯一の既定current symlinkはroot:root所有/nlink1で絶対/opt/schubert-nk/releases/<version>へ限定し、versionはASCII英数字で開始する単一1～64文字の英数字・dot・underscore・hyphen（`.`/`..`/slash・相対target不可）。保持link inodeのtyped metadata前後とparentからの再保持を照合、target側は全segment NOFOLLOWで保持する。manifestはregular/nlink1/1～1048576byte、前後identity/size/mtime/ctime/ACL・namespace再照合、bounded全read/EOF・全所有close後だけ実byte SHA256を返す。子はこの独立bytehashをroot packet release_sha256へ照合。rootは別にimmutable BOM全artifact/hash/role/configを検査し、manifestのhash一致だけでrelease全体を合格にしない。private mount RO/RWはread-only adapterで観測可、host配置/許可/FS policyはroot全gateの別必須。current変更はM/A・許可失効/新発行に従い、reader自身は作成/修復しない。

SSC089現在原本の固定namespace: /run/schubert-nk/startup root:root0700・ACLなし・hostRW tmpfs、epoch.current root600/link1、<epoch UUID>.permit root600/link1/CREATE_NEW。既存永続maintenance namespaceと分離しbackup/切戻しから除外する。毎回新epoch INVALIDをatomic公開/force/close/sync/readback確定後だけmutation可。同run resumeもepoch再利用0、原本欠落/破損からISSUEDを再構築しない。実morning API前の必要工程・全root/Ops/schema/boot/Broker/release/config/step証跡を照合後だけpermit公開→ISSUED(epoch,digest)確定/readback→A解放。permitだけの旧復元、publish後crash/INVALID、不確定readbackは拒否、失敗partは保全。rootが原本も同時巻戻しする運用をファイルだけで防ぐとは主張せず、復元・再設定もM/Aで新世代発行を必須にする。原本/permit実装・fullgateは未完了。

SSC088: 固定NSSはAPIならschubert-api、WEBならschubert-webのpasswd/同名primary groupを固定getentで独立取得する。UID/GIDは正unsigned32（sentinel4294967295除外）、passwd/group shadow marker x、単一canonical LF rowを要求。必要補助groupはschubert・schubert-read（APIだけschubert-web）を固定名で解決しprimaryと重複なし昇順IDにする。OS accountの暗黙全groups、init-groups、任意名前/command/env bus overrideを採用しない。root前段と子が同じ固定解決値/実UID-GID-groupsを照合する。子の非秘密内部FD環境keyはSCHUBERT_NK_STARTUP_ADMISSION_FD・SCHUBERT_NK_STARTUP_PROOF_FDだけ、alias/未知startup key/非canonical値を拒否。既存非秘密env file1行は変えず、root固定exec環境にだけ2FDとmanager Invocationを追加する。秘密値をenv/argvへ追加しない。

SSC086/087・PG296/297具体化: root contextはUID0、proc FS、kernel PID1 exe固定/usr/lib/systemd/systemd、boot UUID、自己PID/startticks、init startticks、固定API/Web cgroupを観測し、環境Invocationとfixed system bus showのId/loaded/起動中state/MainPID/Invocation/ControlGroupを一致させる。2観測一致を取得し、A後/exec直前に再照合。子の2FDは別128～65535で初期CLOEXEC0、両CLOEXEC1設定後にroot regular0600・proof link0/size1～8192/seal15、A link1/empty/devino非0/F_GETFL read-onlyを確認する。proof ownerはcallback前にcloseし公開bufferは退出時消去、A close-only ownerはbusiness failure cleanup後またはready境界でone-closeする。root contextとnative属性だけでは現在permit/全root/schema/Ops/canonical fresh child bindingを証明しない。

SSC086/087・PG295内部packet文法: NKSTART1＋固定順17 key=value行＋最終LF、ASCII/最大8192byte。順序はservice、boot_id、invocation_id、pid、start_ticks、admission_fd、admission_device、admission_inode、service_uid、service_gid、service_groups、permit_epoch、permit_sha256、release_sha256、config_sha256、roots_sha256、broker_invocation_id。未知/欠落/重複/順序違いを拒否。PID2～intMAX/start1～longMAX/予約A128～65535/devino正U64/非root UIDGID1～4294967294、groupsは正IDの昇順重複なし最大16、UUID/Invocationはlowercase非zero、digest64hex。proof FD自身はseal後に予約するのでpacketへ含めず番号を推定しない。文法検査はroot ownership/seal/A/fresh process admissionの代用ではない。子はroot-only factsを admitted emitterから受理し、自己identity/readable config/release/実app能力だけ再観測する。

SSC086/087・PG294補足: root A adapterはhost/privateのrun・app・AをNOFOLLOW保持し、root755/empty regular root600/link1/ACLなし/tmpfs/host native RW・devino一致を確認する。A取得直後に両viewを再確認し、別private OFDが実競合することを確認後、観測用root/parent/entry FDを逆順early-close/one-closeし、その成功後だけA借用callbackへ入る（BUG265/YKT199）。CLOEXECだけで観測closeの失敗を飛ばしてnative execへ進めない。A original/reservedは別所有scope、Mは非委譲。normal callback後のnamespace再確認は新しい短期scopeとし、後続確認失敗を成功へしない。PID1/proc/Unit/boot由来・現在epoch/permit・全root/Ops/schema・secret close・最終service能力はRootServiceLauncher/子admissionの別必須で未結線。

SSC086/087・PG293（限定native具体化）: A低位処理は既存LinuxFileLockのopen/flock/errno/closeを再利用し、独立`tryExclusiveForStartup`だけでreadonly open→F_DUPFD_CLOEXEC(min128)→予約同OFDをflockする。FD128～65535をtrusted callback内で借用、平常/失敗はreserve→original逆順close、native execではoriginal CLOEXECを維持し予約Aだけを明示継承する。予約失敗/同一FD誤戻り/範囲外/close失敗は非成功、競合はcallback0。通常tryExclusive/M adapterはdup0/FD公開0の従来契約を維持する。Aのhost/private保持inode admission・同一性・現在許可/実readyは上位root adapterが別必須であり低位だけの成功では不足。

SSC-087（SSC086のnamespace補足、code前）: Aのhost配布はRW local tmpfsのまま、private service namespaceからのA観測はRO/RWの両方を許す（readonly flockのみ）。M/credential/runtimeの従来FS契約は緩和しない。root前段はPID1が現在のsystem manager/root/同bootのkernel procであることを先に確認し、固定kernel magic link `/proc/1/root`を一度保持するread-only DirectoryCallsを用いる。これはuser選択symlinkではない固定root管理専用例外で、以後の各root/config/permit/Aへの全segmentはNOFOLLOW。create/publish/unlink/sync等の変更能力を同adapterから提供せず、host root FDはexec前にclose/CLOEXEC、appへ移さない。現在hostのFS RO/RWは保持inodeへのnative statvfsで測り、Java FileStoreのpathname canonicalizationによるprivate mount観測を代用しない。host Aとservice Aのdevino・UID/GID/mode/ACL/type/link/size一致、実host lock中のservice拒否を必須とする。固定Unitに古いpermit file/namespaceをbindせず、host許可の失効/再公開がservice viewへ届くこともPT確認する。過去parent観測だけを今回restartのhost現在状態としない。API Transfer実RW/probe/scanとWeb実RO能力は最終UID/private viewで別途必要。

SSC-086（SS341/342内部起動契約）: startup-admission.lockはMと別の固定root:root0600・空regular/link1・ACLなし、/runのRW tmpfs・同deviceに配布する。NOFOLLOW保持能力で前後同一性を検証し、稼働中の作成/修復/unlinkは禁止。起動用Aだけはreadonly同OFDをroot前段から同PID exec後段へ短期委譲する。readonlyはflock解除権限のkernel attenuationではないため、trusted固定後段のclose-only所有契約として扱い、maintenance Mは委譲しない。sealed memfd proofはbounded canonical非秘密値のみ、全sealを確認しfresh boot/Invocation/MainPID/release/config/root/Broker/現在保守許可へ束縛する。static OK、時刻のみ、過去activation/Inspector receiptの再利用、argv/env秘密、app private Ops credential追加は禁止。後段は継承直後にCLOEXECを再設定し、受理前に業務資源を開始しない。readyまで所有し、失敗は業務資源を全closeしてからAをcloseする。現在許可の保存/失効/読取adapterとroot検査実装が欠ければ起動拒否。

SSC063継続/PG174・BUG195/YKT154: ConfigurationGroupResolverの3stdio・reader executor・join前TERM・最外TERMを明示scopeにする。IO/Interrupted primaryと未知Runtime/Error cleanupの競合は未知cleanup優先、Interrupted flag保持、未知primaryとcleanupは元identity＋固定IOException secondaryとする。IOだけの失敗は既存固定IOException、非同期readResultのRuntime固定診断・Error identity・NSS65537byte境界・5秒/全getter後null検査/TERM-before-join/全buffer消去を維持。StopGate専用scopeでIOExceptionを別の公開例外へ変換せず、このclass内のchecked IO用scopeを使う。executorは所有reader終端までjoinし、TERM無効・OS/NSS無応答を成功と扱わない。JDBC契約の横展開は別途残す。

SSC063継続/PG173・BUG195/YKT154: SystemctlStateSourceのstdout/stdin/stderr・照会process TERMを、InspectorUnitProbeと同じ既知Stop/IO/Interrupted対未知Runtime/Errorのclose優先順位へ統一する。同じ例外のself-suppressionを禁止し未知bodyを同一identity＋固定Stop secondary、既知body＋未知cleanupは未知cleanupと割込flagを保持する。Probeの既存狭いscopeをpackage内ProcessResourceScopeへ移し両照会から利用する。Systemctlの全getter取得後null検査・逆順stdio close・最後に生存childだけTERM・5秒/固定8引数/1025byte上限・固定環境を変更しない。戻す予定の読取byteは全cleanup成功前に返さず失敗時消去する。サービス変更/SIGKILL/外部診断やcredentialの出力は禁止。ConfigurationGroupResolver/Future/JDBCの残候補は別段。

SSC063継続/PG172・BUG195/YKT154: MaintenanceFileLockのrun/app取得・再照合、InspectorEnvironmentFilesの5 root取得・再照合、MaintenanceRunFilesの6 root取得・再照合とnames列挙を共通ResourceScopeへ横展開する。取得順・取得直後のadmission順・逆順一度close・Session無効化の時点・static参照byte消去・失敗時run環境保持・borrowed能力を変更しない。DirectoryIteratorExceptionは列挙body内で既知IOへ固定化してからcloseし、未知cleanupを隠さない。未知bodyと同じThrowableをcloseが投げても元identity＋固定secondary1、既知IO bodyと未知cleanupは同じ未知cleanupを伝播する。Runtime/NPE/Errorを正常化せず、入力null契約と公開仕様を維持する。process/JDBC候補は別段で未完了を維持する。

SSC063継続/PG171・BUG195/YKT154: 同じIO close優先順位をDurableRecordFiles.readFile/write/force、InspectorEnvironmentReader.readFile、InspectorEnvironmentPublisher.writeNew/forceExisting、ExistingFileAccess.walkのchannel/childへ適用する。nullable IO resourceは従来の固定IO拒否（ExistingFileAccessのnonnull channelは境界NPE拒否）を所有受領前に実施し、callbackの値/IO順/サイズ/metadata/partial保全/借用root・非公開能力を変更しない。8所有scopeを既知IO＋未知cleanup/同一未知body＋cleanupの各Runtime/NPE/Error3型で独立再試験する。Directory/Process/JDBC等の残候補は別段で未完了を維持する。IO型と回復責務を変える一般frameworkや追加coverage除外は採用しない。

SSC062/PG169: 341§6.7のreaderはcallerがadmitした保持backup rootから正規単一子/MANIFEST.jsonだけを読む。専用backup UID/GIDの0700 root/子とroot:root0600/link1のfile、同device/ACLなし/RW、typed前後属性と1～4096byte/canonical/原本両handleを確認する。rootのCREATE_NEW生成・FS durability/NAS保証・実archive生成/再hash/7世代は別責務であり、readerの成功を代用しない。既存directory/config/credential配布先や権限を変更しない。

SSC060/PG167（先行81e0e64b）: 341 §7.4の固定Inspector unit18property・GetUnitProcesses空配列と前後snapshotを、親のfresh終了観測へ使用する。実InvocationID/commandline/process一覧は設定/証跡へ保存せず、独立合成vectorだけで単体検証する。現行unitのRemainAfterExit=no/固定起動wrapperは本変更で変えない。古い状態の流用、query process終了を実検査unit全終端へ代用、start結果不明のままOS lock解除は不可。018021～024/UNIT001～016を追跡し、実親start/stop/quarantine/原本・DB結線は引き続き未完了。

## 1. 目的・追跡

SSC-049/PG-D-148: read-only照会は`/usr/bin/systemctl --system --no-pager --no-ask-password show --property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID <固定APIまたはWeb unit>`だけ。子環境はclear後にPATH=/usr/bin:/bin、LANG/LC_ALL=C、SYSTEMD_COLORS=0、TERM=dumbのみ設定し、親credential/envやbus address overrideを引き継がない。stderrはdiscard、stdoutは終了後最大1025byte読取で過長を拒否、固定projectionを出す信頼OS binaryが前提。5秒wait timeout時は照会子processへTERMを要求し失敗、SIGKILLやservice stopへ置換しない。全stdio close完了前の成功返却は禁止。敵対rootがbinary/systemdを差替える場合や、TERMを無視するOS障害の強制解消は保証しない。実対象unit不在でもcommandがexit0/inactiveを返すため、必ずLoadState=loadedを検証する。PTでは実read-only診断と制御Process portを区別して記録する。

SSC-049/PG-D-147: root管理のboot時tmpfiles設定は/run/schubert-nk0755、maintenance0700、maintenance.lock0600を固定root:rootで配布する。既存service子directoryの到達性を保つため共有親を0700へ変えない。lockfileは空regular/単一link、local /runのRW tmpfsだけ許可し、稼働中の再作成・削除・権限修復を禁止する。MaintenanceFileLock公開factoryは固定pathとnative portだけを生成し、実行時UID0を先に検査する。保持inodeのmetadata/ACL/FS・再open identityを検証して既存LinuxFileLockへ接続、path/FD/例外causeを結果へ公開しない。PTのroot metadata合成は非特権fixtureの実Linux IO/flockとの接続検証であり実root配置の合格ではない。起動時tmpfiles実行・権限配布・privileged親unit・停止/backup/DB引渡しは後続gate。

SSC-049/PG-D-146: maintenance.lockは親root管理のlocal runtime namespaceへ配布し、保守中にpathを置換/削除しない。低位LinuxFileLockは保持済み/proc/self/fd能力を借りてflockするだけで、root/file owner・ACL・regular type・link・配置を検証するfile adapterの代替ではない。任意path/符号付き・範囲外FD表記/未知platformを拒否し、native診断/physical pathを例外へ出さない。親の配布・起動結線は別PG/PT gate。

Source/release/config/credential/data/log/runtimeの配置、環境差分、設定key、初期data、Flyway DB migration、
現行asset/metadata移行、切替・切戻しを実行前checkと証跡を含めて定める。

- 上位設計: UI 243、251、253～254、261、264
- 関連RD: SCP-002～SCP-005、MIG-DAT-001～MIG-DAT-008、MIG-001～MIG-008、SCM-001～SCM-006、
  FIL-001～FIL-005、TST-001～TST-005
- 関連QA/RDF/UIC: QA-007、QA-012～QA-016、QA-022、QA-024、QA-043、RDFなし、UIC-003
- 関連SS: [331_DB物理・DDL・index・権限設計](../330_データ・ファイル/331_DB物理・DDL・index・権限設計.md)、
  [342_Caddy・systemd・PostgreSQL・Java設定設計](342_Caddy・systemd・PostgreSQL・Java設定設計.md)

## 2. Directory・owner・Git管理

| Path | Owner/mode | 内容 | Git/release |
|---|---|---|---|
| `/opt/schubert-nk/releases/<version>` | root:schubert 0750、file 0640 | Immutable jar、DB migration、ops tool、manifest | Artifactはrelease package、sourceはGit |
| `/opt/schubert-nk/current` | root所有symlink | Active releaseへのatomic pointer | Git対象外、ターゲットversionはmanifest |
| `/etc/schubert-nk` | root:schubert 0750 | Rendered非秘密YAML/env/config manifest | TemplateだけGit |
| `/etc/schubert-nk/credentials` | root:root 0700、個別root:root 0600（SSC138） | root専用DB/MQ/AES/HMAC/backup配布元。serviceは専用LoadCredential private copyだけを読む | Git/artifact/normal log禁止 |
| `/srv/schubert-nk/data/assets` | data owner:schubert-read 0750 | Scenario/audio/video/musicの永続実体 | Asset本体はGit禁止、manifestは取扱承認後 |
| `/srv/schubert-nk/data/transfer` | schubert-api:schubert-web 0750 | API `.part/.ready`、Web read | Git禁止、次回朝削除 |
| `/srv/schubert-nk/backup` | schubert-backup 0700 | 7世代dump/config | Git禁止 |
| `/var/lib/schubert-nk/artemis` | schubert-artemis 0700 | Broker instance/journal/paging | Git禁止、config templateはrelease |
| `/var/lib/schubert-nk/maintenance` と `runs`/`attempts` 子dir | root:root 0700、file0600。共有祖先はroot:root0755 | SSC-055の不変run原本・activation/完了・active metadata。local永続RW、tmpfs不可 | 実体Git禁止、provisioning雛形/独立fixtureだけGit |
| `/var/log/schubert-nk` | service group 0750、file 0640 | File logを使う場合のみ | Git禁止、journald優先 |
| `/run/schubert-nk/<service>` | systemd RuntimeDirectory | Lock/socket/temp metadata | Rebootで消去可 |
| `/srv/schubert-nk/staging/<run-id>` | migration user 0700 | 移行中asset/manifest、対象run限定 | Go/切戻し完了まで隔離 |

Directoryはprovisioningで明示作成し、application起動時に不明rootを自動作成/chmodしない。
SSC-079/BUG-253/YKT-191: release/configの`root:schubert`0750/非秘密file0640は両Java serviceが`schubert`補助groupを明示して読む。service専用primary groupと既存asset/transfer用補助groupは不変。`/etc/schubert-nk/credentials` root:root0700とservice private LoadCredentialを`schubert`へ公開しない。実OS account provisioningとsystemd起動後読取・秘密拒否はLinux ITで検証し、templateのdirective照合だけで実配布済みとはしない。
SSC-020: Transfer rootはschubert-api:schubert-web 0750を維持する。APIは専用primary group＋schubert-web supplementary membershipで、新規作成した保持inodeだけをchgrpし、date0750/part0640へ確定する。既存date/part/readyのmode/groupを補正して受理しない。API/Web credentialとprivate runtimeの600境界を維持し、共有group追加を秘密fileの公開理由にしない。
Asset/transfer/backup/log/Artemis/stagingを同一または相互配下、またはsymlink接続しない。

## 3. Release package構成

```text
releases/<version>/
  web/web.jar
  web/lib/<具体dependency jar名>
  api/api.jar
  api/lib/<具体dependency jar名>
  operations/batch.jar
  operations/lib/<具体dependency jar名>
  db/migration/V*.sql
  config/templates/*.yml
  config/caddy/Caddyfile.template
  config/artemis/broker.xml.template
  systemd/*.service
  systemd/*.target
  systemd/*.timer
  systemd/caddy.service.d/schubert-nk-startup-policy.conf
  operations/bin/schubert-nkctl
  operations/runbooks/
  VERSION
  RELEASE-MANIFEST.json
  SHA256SUMS
```

`RELEASE-MANIFEST.json`はapp/protocol/schema/config version、Git commit/tag、JDK/build tool/dependency/BOM、OS対応、
全artifact hashを持つ。Release directory全fileを検証後にread-onlyにし、稼働中の上書きを禁止。

SSC178（内部署名配備補足）：Caddyは上記固定template及び単一 `systemd/caddy.service.d/schubert-nk-startup-policy.conf` を署名artifactへ含め、その他nested systemd path・任意drop-in名・任意wrapperを受けない。実効profileはSS342§3と親の前後観測で別確認し、BOM合格だけでCaddy起動合格としない。QA048050で承認済みV026/V027を新candidateへ含める場合、schema027・SCHEMA＋V001～027の28履歴を固定した独立期待値とする。旧25版署名release/profile/全原本/Backupを保全し、観測DB/manifestの件数をexpectedへ流用しない。専用M/A/DB所有・全停止・新candidate全署名/BOM認証・保存原本全値/全既存row/業務data/Backupの前後一致・新空table/既存row原値と新権限/NULL契約の後条件を確認し、必要migration以外の修復や旧SQL変更はしない。schema更新とruntime permit/業務ready/ITST合格は別操作・別認定である。
SSC-021のstorage version/hashもmanifestへ記載し、Web/API（batch使用時も）で同一artifactを使用する。Executable内へ同梱する場合もSBOM/hashの一致を検査し、異なるnative能力実装を混在させない。

## 4. Config file・設定sourceの優先順

SSC-083/BUG263補足: Java25標準のinstance mainを用い、native no-arg constructorは固定OS環境/sourceとOS終了要求を束ねる。package内限定constructorは同じmainの終了要求を独立検査するportであり、argvによる代替起動/fixture選択を公開しない。設定検査のIllegalArgument分類をassemblyへ広げず、未知assembly例外のidentityを保持する（BUG262/YKT196）。終了診断・Unit class名・native非成功codeは不変。coverage除外/安全gate迂回なし。

SSC-083/PG285（471 R1/D05）: 両Unitに指定済みの`ApiProcessMain`/`WebProcessMain`は引数0件だけを受け、argvによる設定上書きを拒否する。既存StartupInputsの必須環境位置・保持inode設定を検証してから本番assemblyへ渡す。設定不備は非成功70、既知IO失敗・必須assembly未結線は50。stdoutへreceipt/readyを発行せず、stderrは固定process停止/失敗診断だけとする。未知Runtime/Errorは成功へ変換せず固定uncaught診断で終了する。未結線の入口段階でHTTP/JMSを公開しない。限定smokeは実process受入R2/実NK比較R3の成功ではない。完成時はD01～04を同じ本番assemblyへ接続し、途中失敗と正常停止の全所有資源後条件を検証する。

| 優先 | Source | 用途 |
|---:|---|---|
| 1（低） | Jar内default | 上位で確定済みの非環境値、安全なfail-closed default |
| 2 | `/etc/schubert-nk/common.yml` | protocol/timezone/monitoring共通 |
| 3 | `/etc/schubert-nk/<web|api|batch>.yml` | Process別port/pool/path/retention |
| 4 | `/etc/schubert-nk/<service>.env` | JVM option、config file location等の非秘密 |
| 5（高） | systemd credential/config tree | DB/MQ password、AES/HMAC key、backup recipient等のsecret |

SSC-080/BUG-256/YKT-192: Web/APIの`<service>.env`は固定`SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk`＋LFの単一ASCII行のみとし、root:service0600で配る。重複/未知/secret/大小文字alias/空値/CRLF/placeholder/JVM optionを受けない。Java起動前はsystemdから受けた非秘密値を固定pathと完全一致検査し、任意別directoryへfallbackしない。YAML2層の保持inode読取とcredentialのprivate LoadCredentialは別境界。配布file実体、systemd managerの読取、service identity/ACLはLinux IT実測で確認し、Java Map検査だけでfile文法や実権限を証明したとはしない。

Command line引数でapplication property実値を上書きしない。未知key、重複・非推奨alias、placeholder未解決、
secretのYAML/env格納、型/範囲不正は起動失敗。Effective configはsecret値を`<redacted>`にしcanonical hashを保存。

## 5. 主要設定key

### 5.1 Common・Web

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.protocol.version` | `001` | 完全一致、UI 232 |
| `nk.time.display-zone` | `Asia/Tokyo` | Wire/viewだけ、DB/JVM UTC |
| `nk.monitoring.mode` | `STANDARD` | STANDARD/DEBUG、UI 252 |
| `nk.web.http.address/port` | `127.0.0.1` / `8080` | Loopback |
| `nk.web.management.port` | `8081` | Loopback、Caddy非proxy |
| `nk.web.mq.reply-timeout` | `2s` | 100ms..2s、UI 212/253 |
| `nk.web.mq.wait.initial/max` | `12` / `20` | max<=20 |
| `nk.web.session.idle-timeout` | `8h` | UI 226、無断短縮禁止 |
| `nk.web.session.max-per-user` | `2` | APIが最終強制 |
| `nk.web.storage.asset-root` | `/srv/schubert-nk/data/assets` | absolute real dir/read-only |
| `nk.web.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | absolute real dir/read-only |
| `nk.web.media.max-streams` | `20` | 1..20 |
| `nk.web.media.max-range-bytes` | `1048576` | UI 223/237と完全一致 |

### 5.2 API・JMS・DB

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.mq.url` | `tcp://127.0.0.1:61616` | Loopback/coreのみ |
| `nk.mq.sync-request/reply` | UI 231のAddress名 | 321のallowlistと完全一致 |
| `nk.mq.async-work/web-log/dlq/expiry` | UI 231のAddress名 | Unknown禁止 |
| `nk.api.sync-consumers.initial/max` | `4` / `8` | DB pool<=8 |
| `nk.api.async-consumers` | `1` | 固定、変更禁止 |
| `nk.db.url` | `jdbc:postgresql://127.0.0.1:5432/schubert_nk` | Loopback、parameter allowlist |
| `nk.db.pool.api.max/min` | `8` / `2` | UI 253 |
| `nk.db.pool.web.max/min` | `2` / `1` | UI 212の初期上限2、Technical schema専用 |
| `nk.db.connect-timeout` | `3s` | UI 212 |
| `nk.api.storage.asset-root` | `/srv/schubert-nk/data/assets` | read-only |
| `nk.api.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | write、secure root |
| `nk.inbox.reference/update-retention` | `24h` / `7d` | UI 251、324 |
| `nk.outbox.sent-retention` | `7d` | PENDING/ERRORは無期限 |

SSC-082（PG283）: 通常API/Webは専用DB roleを外部HTTP/JMS開始前の実Connectionで確認する。URLは既存非秘密設定と同じliteral IPv4 loopback `jdbc:postgresql://127.0.0.1:<1..65535>/<lowercase database identifier>`だけとし、query/fragment/userinfo/複数host/escape/先頭0 portを拒否する。APIの期待roleは`schubert_app`、Webは`schubert_web_session`で固定し、任意roleを設定から受けない。接続はautoCommit=true/readOnly=false、固定SELECTの`current_user`と`session_user`が両方期待role、`current_database()`がURL DB、`pg_is_in_recovery()`がfalse、結果は単一rowであることをadmission条件とする。null/欠落/SQL故障/不一致は固定非秘密診断で遮断し、credential/URL/SQL行値を診断へ出さない。検証するConnectionと失敗時closeは呼出し側の所有責務で、admission部品単体は接続を保持しない。既存§6.6 Inspector専用roleは混用しない。この部品のPT成功だけで実DataSource/Pool/外部main起動は認定しない。

### 5.3 Batch・backup

SSC068/PG186: 新規backup子directory用のprivate0700/create-new/保持FD能力を333§7.6へ定める。配布root・既存UID/GID/modeを変えず、生成主体はbackup専用UID/GID、root callerは独立metadataと停止/排他を確認する。実環境権限未検証を一般native temporary PTの成功へ含めない。

SSC059/PG166: 実artifact read-only照合は341 §6.5。root親が作るconfig.tar/credentials.tar.age/MANIFEST.jsonはroot:root0600、DB worker dumpは専用backup UID/GID0600、backup root/子は同専用UID/GID0700。親が信頼manifest bindingとroot admission・NAS能力を別確認し、保持inodeの全4file/metadata/hash/byte・再bindingを照合する。検証は生成/暗号化/fsync/DB成功を代替しない。実装/16PTは017038/039へ先行する。

SSC058/PG165: backupのMANIFEST.json固定値/byte schemaは341 §6.4を正とする。version8項目・recipient fingerprint・固定3fileとrun/両完全backup step handleを保存する。内容生成終了時刻とatomic確定後のstep終了を混同しない。codec成功だけで実file/hash/秘密暗号/DB binding/7世代を検証済みにせず、実体gateと世代管理は別必須。実装/独立16PTは017033～036へ追跡する。

| Key | Initial | Validation |
|---|---|---|
| `nk.batch.zone/schedule` | `Asia/Tokyo` / `05:00` | systemd timerと照合 |
| `nk.batch.backup-root` | `/srv/schubert-nk/backup` | absolute real dir、other root非重複 |
| `nk.batch.backup-generations` | `7` | 固定、短縮禁止 |
| `nk.batch.transfer-cleanup` | enabled | 取得ACKなし、次回朝 |
| `nk.batch.expiry-retention` | `7d` | DLQに適用しない |
| `nk.batch.log-retention` | `90d` | Security hold除外 |
| `nk.batch.run-retention` | `400d` | FAILED調査中除外 |
| `nk.batch.chunk-size` | notification/question 1000、log 10000 | 1..defined max |

## 6. Credential catalog・rotation

SSC168再隔離の終端補足（BUG541/YKT385）：publication→API→WEBの各sync後、全対象の不明が無い場合にも全3strict marker存在・共通INVALID/permit/owner/両launchを再観測して同Pair一致を必須とする。最後sync中の先行marker消失/共通source改変を復旧成功へ見せない。再隔離不明は同ownerのM/A保全、工具のA正常close自体が不明の場合はMを解放せず固定Aを再認証し、再隔離後に両lockを保持して次起動を隔離する。

| Credential ID | Consumer | 形式・rotation |
|---|---|---|
| `db-api`,`db-web`,`db-batch`,`db-migration` | 対応process | PostgreSQL SCRAM password、service別。`db-batch`はdumpへ使用しない |
| `db-backup` | backup unit | QA-043/UIC-003承認済みの`schubert_backup`専用SCRAM password。`schubert-backup` OS userだけへ配布 |
| `db-inbox-inspector` | 非公開Inbox保守検査processのみ | QA-046/UIC-006/SSC-049の`schubert_inbox_inspector`専用SCRAM password。batch/Web/backup/通常APIへ配布しない |
| `mq-web`,`mq-api`,`mq-maintenance`,`mq-ops` | 対応process | Artemis credential、Address権限別 |
| `web-session-aes-current/previous` | Web | AES-256-GCM、key version付き |
| `web-revoke-aes-current/previous` | Web | Pending context revoke暗号、session keyと分離 |
| `api-context-aes-current/previous` | API、非公開Inbox保守検査process（SSC-049/QA-046） | `auth_sessions.context_ciphertext`暗号、key version付き。batch/Web/backupへ配布不可 |
| `api-inbox-response-aes-current/previous` | API、非公開Inbox保守検査process（SSC-049/QA-046） | Inbox replay response暗号、context keyと分離。検査はreadのみ、batch/Web/backupへ配布不可 |
| `operation-hmac-current/previous` | API | 256 bit以上、HMAC-SHA-256 |
| `web-log-aes-current/previous` | Webのみ | Technical outbox保存・復号。API ingestへ配布しない（SSC-007） |
| `backup-age-recipient` | backup unit | 公開keyのみserver保持、private keyはoffline |
| Caddy TLS key/state | Caddy | Caddy専用OS権限、fingerprint管理 |

SSC104/PG324：root Cleanup oneshotへ配る`db-batch`は親root Morningと同じ固定batch roleの別systemd private copyであり、親Connection/sessionを共有しない。親M/A保持、子専用advisory、親再取得・同原本と真正Unit終端確認を全て要求する。非秘密`NKCLEAN1` requestはroot-owned private sourceから`LoadCredential`へ渡すが、それ単体を削除権限にしない。requestの既存file上書き・別runへの流用、secret/env/argvへの転記、未実装子Unitの成功扱いは禁止。具体source配置・内容読取/消去・終了時退役と実OS配布は後続PG/PTで検証する。

SSC104/PG325：固定sourceはlocal `/run/schubert-nk/cleanup-request/cleanup-request`、親directory root:root0700/tmpfs、file root:root0600/regular/nlink1/ACLなし。親rootだけがM/A/同原本照合後にUUID.partをCREATE_NEWし、全byte・inode・force/dir sync確認後に`cleanup-request`へnew-only公開する。既存同名やpartは衝突保全し修復/上書きしない。子終了後のreadback・同request完全一致と真正Unit全終端/DB/親状態確認後だけ限定retireする。`CleanupWorkerRequestFiles`は借用rootの狭いsource操作であり、実固定path選択・M/A・子実行・cleanup成功の権限を単独で与えない。隔離VMの実source配布・systemd LoadCredential読取は別gate。
SSC104/PG327：子の`RootReleaseAdmission.verifyCleanup`は、子自身の真正`schubert-nk-cleanup.service` root snapshotと同一でなければDB schema照会0回で拒否する。固定host-view承認原本/fullBOM・OS/JDK期待をfresh再読し、子専用固定`schubert_batch` Connectionで六列schema全行を照合する。親Morningのverify結果や任意公開digestは流用せず、照合後もM/A・run原本/両backup現物/子lockを別々に要求する。既存`verifyMorning`のMORNING専用契約は緩和しない。
SSC104/PG329：子Cleanupの固定private credential directoryは `/run/credentials/schubert-nk-cleanup.service` とし、真正root子Unitが起動時に`CREDENTIALS_DIRECTORY`と一致することを外側で認証する。borrowed保持rootに対しroot:root0500・tmpfs readonly・ACL0、`cleanup-request`はroot:root0400/regular/nlink1・同device・1～256byte、`db-batch`は従来の1～65536byteを要求する。前後inode/属性と全close後だけcanonical `NKCLEAN1` requestをdecodeし、所有byteは失敗含め消去。任意filename、source原本を子が直接読むfallback、Credential byteをargv/env/証跡へ出すことは禁止。private copy照合だけで同原本/M+A・署名release・DB lock・両backup現物・DELETE権限を証明しない。
SSC104/PG330：Cleanup子は固定private request受領後、既存`MaintenanceRunFiles`の保持scopeでdurable graphを読み取り専用2回照合し、`active`が同run/activation/cutoff、同runの未完了begin/anchor、当該done不在であることを確認する。graphの`pending=同run`は当該activationのdone不在を含意するため、重複したdone条件分岐を置かない。既存`resume`はroot原本をpublish/forceするため子から呼ばない。読み取りでpart/active/anchor/begin/doneを変更せず、欠落・別run/activation/cutoff・完了済・途中交換・読取/close不確定は固定非成功とする。原本照合は相関の一条件であり、親連続M/A、Unit全終端、DB advisory、両backup実現物、DELETE権限を証明しない。PT-OPS-MRF001以降で非変異と負境界を検証する。
SSC104/PG331：requestのMANIFEST SHAだけではbackup directory名を導出できない。子は固定保持backup rootをread-onlyで2回列挙し、最大4096 entry・名前重複なし・親rootの前後metadata一致を要求する。同run UUID suffixの候補だけを正規`yyyyMMdd-HHmmss-UUID`に限定し、`.part`/別run/未知名は選択せず、自runに見える不正名は安全拒否する。候補のroot-owned canonical MANIFESTを既存Readerの全保持/close契約で再読し、同run/cutoffとcanonical byte SHA256がprivate requestのlowercase digestに完全一致する候補ちょうど1件だけを返す。2回列挙set、選択後再読、前後root metadataが変われば拒否。これは未信頼file claimの選択だけであり、両backup DB成功row、同4file/size/hash/owner、親M/A/子lock/Unitを別途自己検証するまで削除0・非成功。PT-OPS-BMR017以降。
SSC104/PG333：子preflightは真正`CLEANUP` root snapshotを入口で再確認し、固定private requestを読み、durable原本の同run/activation/cutoffをread-only観測してから子専用DB sessionを開く。同sessionはfresh release/BOM/schema・advisoryを取得し、その同期callback内でPG332の4file/両SUCCESSを観測する。全close/DB rollback/Connection closeが完了してからprivate requestと原本を再読し、同snapshotを最後に再確認する。入口・終端のrequest/原本交換、clock/IO/close/DB不明は固定非成功。µs観測時刻を使い、前回runや親の検証値を流用しない。これは子の限定read-only preflightであり、親連続M/A・全固定actor終端・真Unit/削除/transfer/0・10の許可は後段で別検証する。
SSC104/PG334：子の外部Java入口は引数0件のみとし、自己`CLEANUP` root snapshot認証後、`CREDENTIALS_DIRECTORY`が固定private `/run/credentials/schubert-nk-cleanup.service`と一致することを検査する。保持rootから`cleanup-request`/`db-batch`を既存readerで読む。固定backup root `/srv/schubert-nk/backup`を保持し、固定NSSの`schubert-backup` UID/GIDをreader/verifierへ渡す。子専用DBは本番固定`jdbc:postgresql://127.0.0.1:5432/schubert_nk`を用い、既存release/schema/advisory及びPG332証明をPG333同期portに接続する。root/credential/backup/DBの全所有close・再確認が済むまで結果を返さない。外部入口のpreflight成功は削除・transfer/親M/Aの許可ではなく、それらが未結線の段階は固定非成功で終了し、`SuccessExitStatus`に追加しない。実Unit配備・親起動/終端を別に検証し、限定入口試験を全Cleanup成功としない。

Symmetric keyは最低32 byte、自動生成passwordは最低32 byte相当のCSPRNG出力とし、ID/versionと有効日だけmanifestに記録。Rotationは「previousを配備→current切替→
旧ciphertext/HMAC保持期間の読取確認→previous除去」の順。Unknown key versionはdeny closed、運用介入とする。

SSC-049/PG-D-122: 検査processの鍵は起動時に読取り後、不変のcurrent/previous snapshotとしてprocess終了まで保持する。鍵rotationは同じ保守OS lockの下で検査process停止を確認して行い、検査から削除までの途中close/rotationを禁止する。HMAC秘密値は検査へ渡さず、保持中HMACの読取り可能version名だけを非秘密設定として固定する。

### 6.1 Inbox検査のAES credential byte形式（SSC-049、PG-D-131）

検査へ配布するapi-context-aes/current・previousおよびapi-inbox-response-aes/current・previousの各fileは、ASCIIで `NKKEY1 LF version LF base64 LF` とする（斜線表記は本節の説明上の略称、正式IDは上表のハイフン名）。versionは既存codecと同じ1～16 byteの `[A-Za-z0-9][A-Za-z0-9._-]{0,15}`、keyはAES-256の32 byteを標準Base64・必須padding・canonical表現の44 byteへ符号化する。全54～69 byte、LFのみ、BOM/CRLF/空白/余分field/末尾data/未padding/非canonical末尾bitを禁止する。値そのものはGit/argv/env/ログ/証跡へ記録しない。今回の形式確定は内部credential搬送であり、保存済AES envelopeや電文を変更しない。

SSC-081（通常Web/APIへ横断）: `web-session-aes-current`、`web-revoke-aes-current`、`web-log-aes-current`、`api-context-aes-current`、`api-inbox-response-aes-current`、`operation-hmac-current`は、上記と同じ`NKKEY1 LF version LF canonical Base64(32byte) LF`の54～69 byteを必須とする。HMACの32 byteは§6 catalogの256 bit以上を満たす固定初期profileであり、保存済HMAC/envelope形式は変更しない。`db-web`/`mq-web`/`db-api`/`mq-api`は§6.6のInspectorDbCredentialと同じstrict UTF-8の1～65536 byte、末尾LF/CRLF一組だけ任意、空/BOM/NUL/内部CR/LF/不正UTF-8拒否。password/鍵値はGit/argv/env/log/証跡に保存しない。current10個は各serviceのUnit宣言と一致する必須fileで、別service ID・未知名を読まない。previousはroot管理rotation profileでUnitへ明示配布した場合だけ固定IDを追加でき、暗黙探索/不在fallbackはしない。読取後materialのpurpose分離・version検証と全所有buffer消去を必須とし、外部起動/実OS配布をこのbyte契約だけで認定しない。

InspectorAesCredential.consume(byte[])は入力arrayの排他的所有を引き受け、正常/不正いずれもfinallyで消去する。versionだけを非秘密Stringとして保持し、base64/keyをString化しない。decodeしたkeyは長さ/canonical検証後にprivate所有とし、失敗時のtemporaryも消去する。copyKeyは独立arrayを返しcallerが使用後消去、closeはprivate lockの下で所有keyを消去して冪等終了、close後copyKeyは禁止。version/状態だけの診断で値を出さない。Java/JCA内部の不可制御copyまで物理消去を保証したとは述べず、所有bufferの明示消去・heapdump非生成・process寿命の管理を組み合わせる。

元file0600とsystemd配布後のruntime権限は別物である。systemd 259の実装はroot所有fileへ対象UIDのACLを追加する経路と、対応filesystemによって所有者を移す経路を持つ。単に「runtime file owner=serviceかつmode0400だけ」とする実装は採用しない。後続readerは保持inode、regular/symlink/hardlink/サイズ、readonly/owner/実効ACLの専用主体限定、読取/close失敗を検証してからmaterialを渡す。ACL検証未実装を緩いmode判定で代用せず、main/専用unit/親processの鍵配布を完了にしない。[systemd 259 credential実装](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/exec-credential.c)、[公式credential契約](https://raw.githubusercontent.com/systemd/systemd/v259/man/systemd.exec.xml)を参照（2026-09-09確認）。

### 6.2 Runtime credential権限の限定（SSC-049、PG-D-132）

非公開検査processは非rootの専用UID（1～4294967294）で動作する。保持inodeの属性とaccess ACLは以下の2形式だけを許可する。ACL検査単体はfileを読まない。後続IO adapterが同じ保持inodeから取得した型付き属性、実際のfilesystem readonly flag、`system.posix_acl_access`を渡し、取得失敗を空ACLへ変換しない。

SSC-081: 通常Web/APIのsystemd runtime credential directory/fileにも同表を、それぞれの非root専用service UIDで適用する。検査用UIDや`schubert`共有groupを代入せず、root+対象service ACLと対象service owner+read-only filesystemの2形だけを許可する。password fileのサイズだけ1～65536、鍵fileは54～69。両serviceの`CREDENTIALS_DIRECTORY`は位置入力にすぎず、実root/fileを保持inodeで検証する前にsecretを読まない。

| 形式 | Directory | AES file | Access ACL |
|---|---|---|---|
| system manager root所有＋専用UID ACL | type directory、mode0550、nlink>=1 | type regular、mode0440、nlink=1、size54～69 | owner root、USER_OBJ=r-x/r--、USER=専用UID:r-x/r--、GROUP_OBJ=---、MASK=r-x/r--、OTHER=---の5 entryのみ |
| 専用UID所有fallback | type directory、mode0500、nlink>=1 | type regular、mode0400、nlink=1、size54～69 | access ACLなし、owner=専用UID、実filesystem readonly必須 |

typeを含むunix modeの完全一致を使い、symlink/FIFO/device/socket、setuid/setgid/sticky、write bit、fileのexecute、余分なhardlinkを拒否する。root+ACL形式は専用UIDがchmodできず、plain-directory fallbackでも安全性を保てる。専用UID所有形式はchmodでwriteを取り戻せないようreadonly filesystemを必須とする。root所有なのにACLなし、他owner/他UID/他group/余分entry（権限0でも）、mask/other許可、byte順/ACL version/entry順/不足/末尾dataの相違を拒否する。規定形式を満たさない現物のchmod/chown/ACL補正はreaderの責務にせず、設定不正で停止する。

Linux UAPI形式はlittle-endian version2の4byte headerと8byte entry（tag u16、perm u16、id u32）。5entry=44byte、名前なしentryのidはFFFFFFFF、tag順は1/2/4/16/32。modeのgroup bitはACL maskであり、GROUP_OBJ権限と混同しない。上記は汎用ACL parserではなくsystemd配布形の厳格allowlist。根拠: [Linux ACL xattr UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.16/include/uapi/linux/posix_acl_xattr.h)、[tag/permission UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.16/include/uapi/linux/posix_acl.h)、[systemd v259 file/directory権限設定](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/exec-credential.c)。環境259.5実測と保持inode/native読取/close/親gateは別PTで確認するまで未完了とする。

### 6.3 保持inodeからのaccess metadata読取（SSC-049、PG-D-133）

storageのInodeSecurityCalls/LinuxInodeSecurityはOwnedTransferDirectory callback内のcanonical `/proc/self/fd/<0..2147483647>`だけを受け、libc getxattrの固定名system.posix_acl_access、statvfsのST_RDONLY、geteuidを読む。API file adapterは同callback内でunix属性・ACL・filesystem flagを取得し、型/owner/permissionを確認してから内容を開く。FD/pathをcallback外へ保持・返却・記録しない。final symlink自体を保持するO_PATHは、readerのunix type検査で先に拒否する。

ACLはcaller指定上限1～65536byteの単回読取（inspectorは44）。size照会→再allocateのraceを作らず、ERANGE/上限超過/0byte成功/不正returnは拒否する。ENODATA/EOPNOTSUPPだけは「ACL値が取得されない」空結果であり、ACL不存在や権限許可の単独証明ではない（ENODATAはアクセス不可も含み得る）。その他EACCES/EPERM/EIO/ENOENT等は固定StorageIoExceptionで停止する。空結果は§6.2のroot+ACL形式では必ず拒否され、専用UID所有・mode0400/0500・filesystem ROの全条件を別途満たす場合だけ内容読取へ進める。POSIX ACLのgroup class mask0/other0は他主体の実効accessを許可しない。Read失敗を成功へ変換しない。Linux systemd local credential filesystemを対象とし、NFS等の異種ACLを一般に認可する機能ではない。

Java25公開FFMでLinux/glibcのLP64 x86_64/amd64/aarch64 ABIに限定し、必要symbol/OS/archが不明なら起動不可。statvfsは当環境libc6-dev2.43-2ubuntu2.4の/usr/include/x86_64-linux-gnu/bits/statvfs.hと照合した112byte/align8、f_flag offset72、ST_RDONLY=1。実PTは当機x86_64、他archの実動作は後続環境確認事項であり未実測を合格へ加えない。固定binding部分だけ既存PG-D-055同様restricted FFM warningを理由付き限定抑止し、null/他warning/coverageは除外しない。Test用call portはnative戻り値・errnoを決定的に注入し、実LinuxのACL/保持inode/UID/100並行と合わせて検証する。

根拠: [Linux getxattr契約](https://man7.org/linux/man-pages/man2/getxattr.2.html)、[statvfs契約](https://man7.org/linux/man-pages/man3/statvfs.3.html)、[glibc statvfs layout更新](https://sourceware.org/pipermail/glibc-cvs/2023q3/082782.html)、上記の導入済みheader。実credential・DB・service設定は変更せず、公開metadataだけの一時file/setfacl2.3.2をPT fixtureとする。

### 6.4 Private AES file reader（SSC-049、PG-D-134）

SSC-081通常Web/API readerの追加契約: §6.1で列挙したservice別必須5 IDだけを型付きallowlistで受け、caller文字列から任意file名を作らない。§6.2/6.3と同じ保持directory/entryの前後typed metadata・ACL/readonly・link/device/size、最大値＋1 byteのbounded READ、channel/entry/directory close完了、失敗時の一時byte消去と固定redacted失敗を満たす。AES/HMACはcodecに、DB/MQはstrict password codecへ独立所有copyで渡す。readerは別service ID、任意path、symlink/非regular/余分hardlinkを拒否し、失敗時に成功materialを返さない。root-manager由来credentialの実ACL/権限とservice起動はLinux ITで確認する。

API file adapter InspectorCredentialLoaderはborrowed OwnedTransferDirectory、InodeSecurityCalls、専用EUID policyを使い、AesCredentialFileの4固定名（api-context-aes-current、api-context-aes-previous、api-inbox-response-aes-current、api-inbox-response-aes-previous）だけを読む。Caller入力から任意pathを組み立てない。currentは必須。previousはentry openがENOENTでcallbackに一度も入っていない場合だけOptional.emptyを許可し、permission・途中消失・metadata/ACL/closeエラーをprevious不在に変換しない。previousの有無を鍵内容やdecode結果から推定しない。

loadごとに保持directoryを検証し、entry O_PATHのunix typeがregularであることを最初に確認してからACL/readonly取得へ進む。symlink/FIFO/device/socketの内容openやACL経由のtarget追従を行わない。UID/GID/mode/nlink/size/dev/ino/mtime/ctimeを型確認し、§6.2を適用。FileChannel READだけを開き、前後のchannel size一致、最大70byte buffer（正常上限69＋過長検出1）、EOFと実読取長を確認する。0byte readを無期限retryせず不正停止。読取後channel closeを完了させ、同保持entryの属性/ACL/readonlyと開始snapshot一致を再検証、entry close後に同保持directoryも再検証する。検査対象root/fileのchmod/chown/repair/書込み/再openによる差替えはしない。

全IO・entry close・directory再検証成功後にのみ、有効長をcopyして§6.1.consumeへ渡す。操作中70byte bufferは全終了のfinallyで消去し、parse側の所有copyもconsumeが消去する。失敗は固定InspectorCredentialException、原因/suppressed/path/鍵値を外へ出さない。入力nullはconstructor/境界契約で拒否し、NPEをcatchして正常扱いしない。Readerはrootを閉じず、mainが鍵codec/resourceと共に所有・closeし、root close失敗をprocess成功へ算入しない。4鍵の読取後のcurrent/previous version整合とcodec作成、親backup/OS lock/専用unitは後段の別責務。

PT035は実public temporary file/FileChannel/保持inodeと、明示したOS metadata/call fault portを組み合わせる。権限policyとnative取得は031/033で独立検証済み範囲へ追跡する。root-manager由来の実credential正系を当機で起動したとは主張しない。当機sudoは対話認証が必要であり、daemon/認証設定は変更しない。正式unitの実権限配布確認は権限のある後続Linux環境へ引継ぎ、PG/PTの権限緩和で代用しない。

### 6.5 検査内部の鍵snapshot・run接続（SSC-049、PG-D-135）

InspectorProcessは公開HTTP/JMS入口やOS process起動ではなく、private oneshot内で一度だけ呼ぶ同期serviceとする。constructorはborrowed InspectorCredentialLoader、専用SqlConnectionProvider、読取可能fingerprint version名の不変集合を受ける。root/DB datasource/OS lockはcaller所有。productionはSystem.nanoTime、PTはpackage内の鍵source/clock portを使う。Null/空集合/未知version名を起動契約で拒否する。

execute(run)はnull拒否後にprivate AtomicBooleanで1回だけ実行権を取る。競合/2回目は固定例外で拒否し、鍵再読取・別runへの流用をしない。開始時割込はflagを保ち、鍵/DB未accessのINTERRUPTEDを返す。4固定credentialを順に読み、current必須/previous任意を§6.4と同じ契約で扱う。各materialは直ちに操作内の所有集合へ登録してからcopyKeyし、途中load/copy失敗も既取得material/copyをすべて消去する。閉じたmaterialは設定失敗とし、NPEをcatchしない。

同purposeのcurrent/previous version重複はcodec生成前に拒否。ContextとResponseの全存在世代の鍵byteを定数時間比較し、purpose間の同一鍵は拒否する（version文字列のpurpose間一致は可）。既存AuthContextCodec/ResponseSnapshotCodecの保存形式・previous読取契約をそのまま使用する。応答・認証参照inspector、非認証22route inspector、InboxCleanup、InspectionRunExecutorへ接続し、鍵生成/取得、codec構築を全てDB処理より前に完了させる。fingerprintのHMAC実体は取得しない。

各codecは実行thread内に閉じて公開せず、全run/chunk終了後にのみcloseする。正常/保護WARNING/期限/割込/DB失敗/想定外例外のすべてでcodec→所有copy→materialを回収し、鍵の途中close/rotationを許さない。Mandatory JCA algorithm取得失敗も成功へ変換せずcallerへ通知。診断は既存InspectionExecutionの許可済status/countのみ。Java/JCA内部copyの物理消去保証は§6.1と同じ限定。

返却0/10/50は内部run結果であり、mainのroot/datasource close・DB credential読取・親backup実体/OS lock・systemd unitの成功を保証しない。構成不正はmainが70へ分類し、想定外runtime故障は正常化しない。SSC-049/PG-D-139～141によりQuestion/通知7routeを含む全31responseの保守検査を接続した。非認証検査の元22という上段はPG-D-135の初期範囲であり、現行の固定routeはSS324 §12.8～12.9/331 §3.10～3.11を正とする。通常Question業務writer/replayや全PG/PT・実NK CHRの完了ではない。

### 6.6 検査専用DB credential・接続（SSC-049、PG-D-142）

`db-inbox-inspector`は352 §11.1のUTF-8 passwordとし、独自の暗号envelopeやversion prefixを加えない。fileは1～65536byte、BOMなし・不正UTF-8なし。終端の改行は1個のLFまたはCRLFだけ取り除く（改行なしも可）。残るpasswordは空/NUL/CR/LFを拒否し、それ以外のUnicode・前後spaceはtrim/正規化せず保持する。自動発行時のCSPRNG 32byte以上というcatalog要件はprovisioning側で維持し、parserが文字列からentropyを推定しない。

InspectorDbCredential.consumeは入力byteの排他的所有を引受け、成功/失敗いずれも入力とdecoder一時bufferを消去する。passwordはprivate char[]、copyPasswordは独立copyでcallerが消去、closeはprivate lockで冪等消去、close後copyは拒否。診断は固定redacted値のみ。JDBCが要求するStringやdriver/JDK内部copyを物理消去できるとは主張せず、長寿命field/診断への格納禁止・Propertiesの即時clear・process寿命/heapdump無効化で限定する。

InspectorCredentialLoader.loadDatabasePasswordは固定1file名だけを必須読取する。AES loaderの保持inode/type/owner/ACL/readonly/前後metadata一致・channel/entry/directory close成功条件を共用し、最大65537byte bufferで過長を検知する。§6.2のfile permissionと単一link条件は不変、password用サイズだけ1～65536、AESは54～69のまま。任意filename引数やACL緩和を追加しない。

InspectorDatabaseConnectionsはloaderから受けたmaterialの独立copyだけを所有し、専用role `schubert_inbox_inspector`へfresh JDBC接続を返す（pool/共有connectionなし）。URLはliteral IPv4 loopback `jdbc:postgresql://127.0.0.1:<1..65535>/<lowercase database identifier>`だけ、query/fragment/userinfo/複数host/escapeを拒否。本番値は§5.2の5432/schubert_nk、PTは隔離port/DBを使う。固定接続propertyはuser/password/connectTimeout=3/ApplicationName=schubert-nk-inbox-inspector、loopback SCRAMを使い任意propertyを受けない。接続時だけpassword Stringを作り、Propertiesをfinally clear、元copyをclose時に消去する。

返却前にautoCommit=true/readOnly=false、current_user/session_userが両方専用role、current_databaseが設定DBと一致、回復中でないことを固定SELECTで検証する。違反/SQL故障/検証用資源close故障は接続も閉じて固定SQLExceptionだけを返す（原因/suppressed/credential/URL/SQL値を公開しない）。正常返却connectionはcaller所有、provider closeと競合するopenはprivate lockで直列化、既返却connectionを勝手に閉じない。DB role権限と保持・backupは既存SQL/owned cleanupが別途再検証する。専用process main/OS lock/実backup検査/unit起動の成功をこの接続部品だけで保証しない。

SSC090/PG305 backup追補: `backup-pgpass`はbackup固定UnitだけへLoadCredentialし、API/Web5材料やInspector DB材料を流用しない。共用InspectorCredentialLoader.readBackupPgpassは固定名、1～65536byte、systemd root/file ACL・同device・前後属性・closeを検査したcaller-owned raw byteを返す。Root ACL0440 sourceはlibpqで直接使用不可であるため、専用backup UIDのprivate tmpfs0700へCREATE_NEW0600 copyを作り、所有byteを消去してから保持FD経由でPGPASSFILEに渡す。全子終端後だけcopy消去/unlink/dirsync、不確定終端は保全・非成功。tmpfs/mode/source identity/固定Unit・role・全backup controllerの実接続を別gateとし、source読取単体をbackup成功にしない。

### 6.7 専用検査の操作内resource寿命（SSC-049、PG-D-143）

InspectorSettingsは非秘密のcredential directory path、§6.6 canonical JDBC URL、読取可能fingerprint version集合の不変snapshotを持つ。Pathは絶対・正規化済み・rootそのもの以外、URLは既存専用providerと同じ検証、versionは§6.5の非空集合/1～16byte形式。null/空/未知値はIO前に拒否し、toStringは設定実値を表示しない。既存InspectorProcess/providerの同じ検証をこの設定契約へ共有し、判定を複製しない。ここはenv/file parserではなく、後続launcherが渡す値の型境界である。

api.fileのInspectorApplicationはfile adapterとして低位DirectoryCalls/InodeSecurityCallsだけを使用する。execute(run)ごとに(1)全path segment NOFOLLOWでrootを開く、(2)既存readerでdb-inbox-inspector materialを所有、(3)固定role providerへ独立copy、(4)同rootのreaderとproviderからInspectorProcessを生成・同期実行、(5)provider/password/rootを逆順close、の順とする。鍵4個/copy/codecは既存InspectorProcessが操作内で所有・消去する。runはIO前にnon-null確認。各executeは独立寿命で、同run再開は永続状態を正とする。

成功/保護あり結果はroot closeを含む全終了後だけ返す。BUG-134/YKT-105: 開始時割込はrun null確認後・root/password IO前に判定し、flagを保持してINTERRUPTED/最後の確認状態なしを返す。読取途中の割込は既存IO失敗として全資源を閉じ、成功にしない。root open/close、credential load、構成不正/暗号primitive故障は例外で終了し、途中結果を返さない。通常DB障害/割込/時間超過は既存InspectionExecutionの非成功を保持する。ここでroot権限を緩和したり、DB credentialを他processへ渡したりしない。ログ/HTTP/JMS/別processを生成しない。PTは実保持inode/file/JDBC/永続SQLと明示synthetic OS属性・fault portを組合せる。実systemd credential正系、Java main/unit、親flock/backup実体/朝batch全順序は別gateであり本接続だけを完了証明にしない。

### 6.8 非公開launcherの入力・receipt・credential profile（SSC-049、PG-D-144）

SSC-049/PG-D-151（先行85eef317）: root静的fileのrender結果は`NK_INSPECTOR_DB_URL=<URL>`＋LF、`NK_INSPECTOR_FINGERPRINT_VERSIONS=<comma列>`＋LFの順に固定する。2行以外・空行・CRLF・引用/escape/コメント/space・未知/重複/alias key・run/credential設定混入は不正。URLは§6.6と同じ`jdbc:postgresql://127.0.0.1:<port>/<database>`、portは先頭0なし1～65535、DB名は`[a-z_][a-z0-9_]{0,62}`、query/userinfo/remote host不可。versionは1～65536 ASCII文字、comma区切りの各要素`[A-Za-z0-9][A-Za-z0-9._-]{0,15}`で空/重複不可。file全体は1～65848byte（key/各値の既定上限/LFの合計上界）。全byteを照合し、UTF-8非ASCIIも拒否する。親のInspectorStaticEnvironment.requireValidは固定診断だけを返し、nullはprogramming契約違反。任意shell/systemd構文を評価しない。親の保持inode/bounded IO/属性検査で得たsnapshotに使用し、子launcherの型検査・DB接続時の再検証を省略しない。雛形はDB名等をrenderし本検査に合格してから配置する。秘密実体・環境全体は保持/出力しない。

公開HTTP/JMSではないInspectorLauncher.mainをprivate unitの必須wrapperから呼ぶ。argvによる設定上書きは禁止し引数0個だけ。設定は以下の非秘密環境値から一度だけ型化し、現在日時や別runへ補完しない。password/AES/HMAC実値をenvへ渡さない。

| Key | 受理契約 |
|---|---|
| `CREDENTIALS_DIRECTORY` | systemdが設定するprivate root、1～4096文字、InspectorSettingsの絶対正規化path（`/`不可）。特定の未保証systemd内部path prefixを推測しない。保持inode/専用UID/ACL/ROは既存readerが毎回検証 |
| `NK_INSPECTOR_DB_URL` | 1～256文字、§6.6のcanonical loopback専用DB URL |
| `NK_INSPECTOR_RUN_ID` | canonical小文字36文字UUID、parse後toStringが原値と一致 |
| `NK_INSPECTOR_CUTOFF` | 1～32文字、UTC Instant canonical文字列と完全一致、InspectionRunの年/精度契約（microsecond以下）を維持。offset別表現/補完/丸め禁止 |
| `NK_INSPECTOR_FINGERPRINT_VERSIONS` | 1～65536文字のcomma区切り、空要素/重複不可、各versionは§6.5の1～16 ASCII。HMAC秘密値は含めない |

上記必須値の欠落/null/空/過長/NUL/CR/LF、`NK_INSPECTOR` namespaceの未知key・大小文字alias、CREDENTIALS_DIRECTORYの大小文字aliasをCONFIG70とする。無関係なOS環境値は保持・出力せず無視する。Map化前に消えるEnvironmentFile内重複やsource優先順は配備側validatorの責務であり、このlauncherのMap検査で検出済みとしない。外側null引数/portはprogramming contract違反であり、NPEを正常へ変換しない。

root所有の`/etc/schubert-nk/inbox-inspector.env`にDB URL/version名だけを置く。run ID/cutoffだけはroot所有maintenance controllerがOS flock保持下で`/run/schubert-nk/maintenance/inbox-inspector.env`（parent root:root0700、file0600）へ原子的にpublishし、systemd managerがEnvironmentFileとして読む。batch accountにこのfileの任意編集、任意環境/汎用systemd-run/sudo権限を付与しない。親の停止/lock/実backup・設定fileの検証/原子publishとrun bindingの実装は別必須gate。ここで未実装の親gateを代行済みとしない。

SSC-049/PG-D-149（先行17b06c0c）: 親が生成するrun専用fileは`NK_INSPECTOR_RUN_ID=<UUID.toString()>`＋LF、`NK_INSPECTOR_CUTOFF=<Instant.toString()>`＋LFの2行だけをASCIIで持つ。UUID/cutoffは既に確定したBatchRunと同一とし、現在時刻取得・丸め・再採番・推測補完をしない。InspectorRunEnvironment.encodeはcaller所有の新規byte配列を返し、requireMatchesは期待BatchRunから得るcanonical全byteとの完全一致だけを受理する。別run/別時刻、重複/追加key、引用符/space/CRLF/extra LF/NUL/高bit/欠落は拒否、nullは明示契約違反。非秘密identityだけでpassword/鍵/pathを含めず、固定診断に実値を出さない。file read前の容量・root所有/ACL/NOFOLLOW・実lock保持・atomic publish/再読/同inode・子の未稼働確認はpublisher/caller側の別必須条件で、このbyte codecでは認定しない。SSC-055の永続anchorを生成fileやメモリBatchRunで代替しない。

設定不正・credential読取/形式不正・暗号primitive構成不正はreceipt70、StorageIoExceptionは50、通常の実行結果はInspectionExecutionの0/10/50を維持する。予期外runtime故障は成功receiptを出さずJVM異常終了とする。mainの未捕捉例外handlerは固定`inspector failed`だけstderrへ出し、Throwable/値/stackを出さない。出力stream障害も非成功。全resource close後の結果からだけASCII `NKINSPECTOR1 <code> LF`をstdoutへ一度出す。JVM exit0はreceipt発行成功であって業務成功ではない。

必須POSIX sh wrapperは固定Java/artifact/classpathを実行し、JVM非zeroまたは不明/欠落/余分text/extra LF/不明codeを50へ分類する。exact receiptの0/10/50/70だけ対応exitで返す。引数/未render placeholderは70。SSC-053/BUG-137: shell変数はNULを保持できないためraw receiptを直接代入しない。Java stdoutへ終了code0ならASCII dot、非zeroならASCII !を付加し、固定`/usr/bin/od -An -v -tx1 -w64`へpipeする。全byteをhex化してからcommand substitutionへ入れ、正規4receipt＋dotの固定hex列だけ受理する。NUL・高bit・末尾LF数・不明byteを正規化しない。odの非zeroも50。末尾markerとhex化によりJVM異常/byte欠落を成功へ変えない。PTでは固定od呼出しだけ一時fixtureへ差替えたfault注入を明記し、本番の任意tool差替え権限を設けない。任意command/evalやsecret表示は禁止。これがOSへ公開する唯一の実行entryであり、Java main単独のexit0をparentが成功判定に使わない。親は同run/cutoffの永続progressを別途読んでattempt差分/最終件数を記録する。

unitのLoadCredentialは常にDB/current2の絶対source pathを指定する。previous2はroot管理rotation profileに応じて固定path行を追加する選択drop-in（なし/contextだけ/responseだけ/両方の4構成）。宣言しないpreviousだけreaderで不存在可。配布宣言したsourceの欠落/読取不能はunit起動失敗とし、空defaultへ置換しない。source省略によるmanager/credstore検索やSetCredentialの空値fallbackは使わない。rotation/profile切替は同じ保守OS lock下でprocess停止→credential/profile整合→daemon reload→次回起動とする。systemd259.5の導入済みsystemd.exec(5) LoadCredential/SetCredential節で確認（2026-09-09）。実root配布はLinux serverのITで確認し、PTの合成metadataで代用済みとはしない。

### 6.9 親の保持inode環境file reader（SSC-049/PG-D-152）

先行58f7e8b7。InspectorEnvironmentReaderは親file adapterが既に固定pathからNOFOLLOWで保持したdirectoryを借用し、既存名`inbox-inspector.env`だけを保持して読む。読取中は親がOS flockを保持しroot設定変更/子起動を禁止する。root/ancestorの固定namespace再検証は親が行う。readerが借用rootのpath選択やclose/作成/chmodをしない。

- euid0必須。static directoryはroot:schubert0750、fileはroot:schubert0640。期待schubert GIDは信頼できるaccount設定から解決した1～4294967295をconstructorで受け、対象fileのGIDから自己生成しない。runtime directoryはroot:root0700、fileはroot:root0600。
- directoryは通常directory/nlink2以上、fileは通常file/nlink1、同device。static fileは1～65848byte、run fileは1～110byte（§6.8のkey/UUID/32文字cutoff/LFの上界）。各metadataはmode/uid/gid/nlink/size/dev/ino/mtime/ctimeの型付き必須値。型判定前にcontent open・path-following xattr/FS照会をしない。
- access ACLなし。staticはext2/ext3/ext4/xfs/btrfs/tmpfsのlocal FS（RO可）、runtimeはRW tmpfsのみ。未知FS/属性/欠落/別inode/過長/不明read結果は拒否。default ACLは既存inodeを読む権限を付与せず、このreadonly部品の検査対象外。新規作成時のACLはpublisher側で別検証する。
- 上限+1のbufferと保持inodeへのread-only channelを使う。開始/終了sizeとmetadataを照合し、EOFまで読んだ長さが元sizeと同じことを確認する。read0、不正count/position、短縮/伸長/close失敗は非成功。追加1byteは過長判定専用で受理しない。
- 同名をもう一度O_PATHで保持してdev/ino・mode/UID/GID/nlink/size/mtime/ctime/FSと元snapshotを完全照合する。directoryのidentity/属性も前後照合。entry/channel全close後にstatic内容検査または期待BatchRunへの全byte照合を行い、caller所有の新規配列を返す。型/IO異常は固定StorageIoException、byte設定不正は既存固定IllegalArgumentException、null caller依存は明示契約違反。診断にpath/内容/cause/suppressedを出さない。

本部品は既存fileの読取だけであり、atomic publisher/親起動・子終了/backup/永続run原本を完了にしない。合成root/GID/tmpfsの単体fixtureと実root配備のITを区別する。

### 6.10 private原子公開の低位能力（SSC-049/PG-D-153）

先行67148c13。SS333 §7.3のprivate0600 CREATE_NEW/保持inode・単一名RENAME_NOREPLACE・directory fsync・検証済みentry unlinkを再利用する。上位publisherはroot:root0700の固定runtime・OS lock・子非稼働・期待BatchRunを確認してから、新規UUID.partへcanonical2行だけを書き、file fsync/byte再照合後に固定inbox-inspector.envへ公開する。既存targetを通常renameで置換しない。同runの既存公開fileは再読取/再同期で判定し、別run/不正fileは勝手に置換しない。公開後の終了/再試行・known partialの扱い・親からの固定namespace結線は上位publisherの次の詳細化/PGPT対象であり、本低位能力だけでは認定しない。

### 6.11 親run環境publisher（SSC-049/PG-D-154、先行aa2baa3a）

InspectorEnvironmentPublisherは借用runtime rootでprepare(BatchRun)/retire(BatchRun)を行うfile adapter。親は固定namespace/OS flockの全区間保持、root設定変更禁止、子unitが終端であること、永続原本に一致するBatchRunを独立して保証する。部品の成功をこれらの証明に使わない。借用rootを閉じず、private monitorで同instance操作を直列化する。

- 全入口はnull拒否、割込flag保持/euid0、§6.9のroot:root0700・RW tmpfs・access ACLなし・型付きmetadataを検査。共通EnvironmentInodePolicyへreadonly readerの判定を抽出し、静的root/file仕様は変えない。新規空fileだけsize0を作成直後の検査に許可し、公開/読取は1～110を維持する。新規fileにもaccess ACL不在を必須とし、継承ACLを含む不明grantは拒否する。
- 最初の固定target openだけがENOENTで、callbackに一度も入らずclose等の失敗もない場合を不存在とする。存在時は同runのcanonical全byte/属性を保持inodeから検証し、file force(true)→close→directory sync→同inode/全byte再読→root identity再検証の全成功でprepareを冪等成功とする。別run/cutoff/不正byte/型/ACLは置換せず拒否。
- 不存在時はrun.idのUUID.partを0600 CREATE_NEWで作成し即時FD所有。既存partはCOLLISIONで保全し、期待run名というだけで削除/再利用しない。上位運用が過去不確定・所有・子停止・公開状態を確認して解決する。最初に空file属性/同device、書込みはcanonical110byte以下・進捗count/position一致・0/不正結果拒否、開始size0/終了size一致、force(true)、全channel closeとinode再検証を行う。
- partを§6.9相当のbounded readで同run全byte照合してから固定targetへRENAME_NOREPLACEしdirectory syncする。公開targetのdev/ino/所有/mode/link/size/mtime/FSが書込済みpartと同じことを確認（renameに伴うctime変化は許容）、再度全byte/属性とroot identityを検証して返す。directory内容変更によるsize/mtime/ctime変化は許容するがdev/ino/owner/mode/link/FSの変化は拒否。途中に他root管理者が名前を書換えないことは親lock運用の前提。
- retireは同runの公開fileを保持/全byte/属性検証し、同名identity再確認後だけunlink+directory syncする。最初から不存在だけ冪等成功でrootを再確認。途中消失/別run/壊れたfile/close/sync/割込は成功へ補完しない。子非停止中のretireは禁止で、親が実終端を確認してから呼ぶ。
- 成功/失敗にかかわらず任意既存fileのchmod/chown、上書きrename、部分fileの無条件削除、失敗したrename/unlinkの逆操作を行わない。作成/公開/削除後sync失敗は不確定として保全・非成功。caller-owned一時byteは消去、IO診断は固定StorageIoExceptionでcause/suppressed/値を出さず、未知runtimeを正常化しない。runを新規採番/現在日時へ補完しない。

PTは孤立実inode/FFM・合成root/tmpfs属性・明示IO faultで全分岐を検証。実root/manager/親全順序/永続anchorは別PGPT・後続IT条件を維持する。

### 6.12 固定namespace・account解決と環境寿命（SSC-049/PG-D-155、先行023017b2）

BUG-155/YKT-120（先行d0308b55）: 正常上限がpipe容量を超えても終了待ちとwriterが相互待機しないよう、所有virtual taskでstdoutを並行drainする。親は5秒のprocess待機/exit検証後に読取結果を受け、失敗時は生存lookup子へTERMを要求してから全task終端を待ち、全stdioを閉じた後に返す。task終了前に共有byteを消去しない。既定のtrusted OS/NSSと子孫がpipeを保持しない前提のもと、TERM/pipe終端を待つcleanup時間を5秒の成功保証に含めない。TERMを無視する異常OSの強制終端を約束せず、その状態で成功返却しない。実pipe4096で65536byteの正常vector、超過、途中失敗、停止/割込と消去を再発防止試験にする。

ConfigurationGroupResolverの公開入口は引数なしresolve()だけ。固定argv `/usr/bin/getent group schubert`をshellなしで実行し、NSSの名前照会からGIDを独立取得する。group列挙・gshadow・任意key/optionsを扱わない。環境はPATH=/usr/bin:/bin・LANG=C・LC_ALL=Cだけ、stderr破棄、親env/secretは継承しない。5秒待機・stdout最大65536byte（65537で過長検知）・exit0・全stdio closeの成功を必須とし、timeout/非zero/IO/不明read/close/割込は固定IOException、割込flagを維持する。失敗後の生存lookup子にだけTERMを要求しSIGKILLは使わない。任意子孫がpipeを保持しないtrusted OS tool/NSS設定を前提とし、実際の未停止子検知は非成功のまま運用へ引継ぐ。

stdoutは13～65536byte、prefix `schubert:`、colon合計3個、終端LF1個、内部NUL/制御ASCII/DEL/追加LF/CRを拒否する。password/member fieldは空でもよく、内容を解釈/表示/保存しない（非ASCII byteはこの2fieldに限りopaqueとして扱う）。GID fieldは先頭0なしASCII数字1～10桁、1～4294967295。別名/別group/欠落/多行/空GID/未知byteは拒否。全stdoutをString化せずGIDだけ積算し、byte配列を全終了時に消去する。nullはprogramming契約違反として正常化しない。lookup失敗を対象fileのGIDで補完しない。参照資料: host GLIBC2.43-2ubuntu2.4、Linux man-pages6.17 getent(1)、2026-09-12。

InspectorEnvironmentFilesの公開factoryは固定/etc・/runとnative portを生成する。execute(BatchRun, Operation<T>)は開始時null/interrupt/euid0を検査し、親のOS flock保持・root管理変更禁止・現在子終端・backup/永続run原本一致を必須preconditionとする。Operationは同じrunの子処理が終端となるまで復帰せず、親file/root/namespaceを操作しない。

1. 独立GIDを取得。全segment NOFOLLOWで/etc→schubert-nk、/run→schubert-nk→maintenanceを各独立FDとして保持する。/etc・/run・/run/schubert-nkはroot:root0755通常directory、configはroot:schubert0750、maintenanceはroot:root0700。access ACLなし・同階層device一致、/etc系は既定local FS（RO可）、/run系はRW tmpfs。rootそのもの/固定祖先の作成/chmodはしない。
2. static fileのSnapshotとcanonical byteを保持rootから取得し、同inode/全byte/属性を検証する。runtime publisher.prepare(run)を実行する。
3. 直前に固定pathを全て開き直して各保持rootのidentityと比較し、独立group照会も同GID、static fileも元Snapshot/byteと一致することを確認してからOperationを1回呼ぶ。runtime fileも期待runへ再読照合する。根拠をcallbackへ渡すpath/FD/secretとして公開しない。
4. Operationの正常nonnull終了後に同じnamespace/group/static/runtime確認を再実行し、同runretireを行う。全所有root close成功後だけ結果を返す。callbackが例外/nullで終了した場合はretireせずruntime fileを保全し、親が子終端/復旧を判断する。途中IO/close失敗で成功を補完しない。
5. 各directory比較は内容変化で変わるsize/mtime/ctimeを除いた型/owner/group/link/dev/ino/FS/ROを一致させる。static fileは変更を許可せずctimeを含む全snapshot＋byte一致。同階層を同deviceとし/etcと/runのdevice違いは正常。最後の割込も非成功、IO診断は固定cause/suppressedなし、未知runtimeは回収後にescapeする。

固定pathに対するportability警告はBUG142/YKT112と同じ理由で公開factoryのexact diagnosticだけreview可能（owner NK-OPS-001、PG gate/OS/path変更時再審査）。coverage/null/securityの除外ではない。実root/systemd/OS lock連続性は本PTの合成属性だけで認定せず、子制御の実装と後続ITを維持する。

### 6.13 永続run原本・activation・completion（SSC-055/PG-D-156、先行b6b5f0f6）

DB停止前/reboot後の原本は`/var/lib/schubert-nk/maintenance/runs/<run UUID>.run`。runのUUID/cutoffを一度だけ固定し、batch_runs.started_at/現在時刻/既存progressで補完しない。DBはstep履歴であり原本の第二コピーを後付けしない。既存runで原本がない場合はresumeを拒否し、履歴とfileを保持する。runなしの新規開始にだけ親がUUID/時刻を採り、公開後に生成し直さない。

再開単位をrunと区別するためactivation UUIDを持つ。`attempts/<activation UUID>.begin`はrun/activationを束縛し、固定`active`はそのbeginと同じbyteを持つ。`attempts/<activation UUID>.done`はそのactivationの親morning完了であり、別activation/別runへ流用しない。既存UUIDの上書き再利用は禁止。completionはSUCCESS(0)/WARNING(10)だけ。個別backup失敗→削除skip→正常起動の許容WARNING経路を維持し、個別FAILED調査中を完了recordで解除しない。

全rootはprovisioningで作成済み、private root/runs/attemptsはroot:root0700、recordはregular0600/nlink1・root:root・access ACLなし。共有祖先root0755を勝手に0700へ変更しない。local永続RW filesystemで、tmpfs/remote/readonly/unknown・symlink/不明属性を拒否する。保持directory/inodeでのmetadata/名前の再取得identityを操作前後に照合する。全scopeを親OS flockで保持し、保守中のroot管理者によるnamespace変更を禁止する。原本の有効なbyteだけを読めたことでは配布・所有・排他を証明しない。

状態遷移とcrash条件:

1. 新規run原本をCREATE_NEW0600のpartへ書き、file force→no-replace公開→directory sync→保持readbackを確定する。続いてbeginを同じ手順で確定し、最後にactiveを確定する。active確定前に停止/update/reboot等の副作用へ進まない。
2. Reboot後はactive→begin→原本の全値一致を確認して同cutoffを復元する。active/原本不明・複数未完了begin・異なるrun・不明partは推測補完/無条件消去せず停止。active公開前の単独未完了beginを見つけた場合の再接続は、明示resumeが同runで全identityを再確認した場合だけ。自動的に別runへ取り替えない。
3. 明示resumeはactiveが同runなら同activationを継続する。既doneがあれば、親は既完了activationの回復として読み、前回の副作用を再実行したと数えない。activeがなく、そのrunの全activationが完了している場合にだけ新activationを作る。前回completionを今回成功に使わず、必要stepのskip/新attempt/backup例外をSS341に従って実施する。
4. 親が許容morning終端・実子終端・step記録を確認後、doneをdurable公開してから同じactiveを限定unlink/syncする。終了timeはrun cutoff以上、microsecond精度・UTC年0001～9999。process exitだけを完了にせず、失敗/interrupt/commit不明はactive/原本を保全する。同じdoneの再確認は全値完全一致だけを認め、別時刻/別statusへ上書きしない。
5. `runs`の原本退役は最新completionから400日超、全activation完了、active/未公開part/不明fileなし、batch_runs/Inbox progress/log progressの参照0をOS/DB lock下で再確認した場合だけ。先にrun限定のretirement markerをdurable確定し、既知のbegin/done/原本だけを限定削除、最後にmarkerを消す。中断時はmarkerを保持して新resumeを拒否し、同じ限定対象の参照0を再確認して冪等再開する。未完了・FAILED調査中・DB不通・不明runは保全。marker具体byte/DB照会/GC callerは後続PG/PTで先行仕様化し、本項目全体の未完了条件として残す。

PG-D-156のcanonical record（各行末LF、ASCII、以下の順序、空白/quote/CRLF/BOM/追加行/aliasなし）:

| 種別 | 行1 | 続く行 | byte長 |
|---|---|---|---:|
| anchor | `NKRUN1` | run UUID、cutoff | 72 |
| begin/active | `NKACT1` | run UUID、cutoff、activation UUID | 109 |
| done | `NKDONE1` | run UUID、cutoff、activation UUID、ended_at、`0`または`10` | 140/141 |

UUIDはlowercase36文字、時刻は`uuuu-MM-dd'T'HH:mm:ss.SSSSSS'Z'`の27文字、BatchRunの年0001～9999/µs範囲を維持する。business_dateは既存SQLと同じAsia/Tokyo変換から導出しrecordへ別値として重複保存しない。canonicalでない同値表記・うるう秒の自動正規化を受理しない。parserは構造的に有効な別runも値として復元するが、file store/親が期待する原本と全値一致を別途検証し、parser単体を所有/認証/同run保証にしない。

MaintenanceRecordsは3種encode/decode、MaintenanceActivationはBatchRun/activation UUID、MaintenanceCompletionはactivation/ended_at/0・10の型付きOutcomeを保持する。nullは境界で拒否し、byte入力の不正はraw cause/suppressedを含まない固定IOException、constructor不変条件違反は固定IllegalArgumentException。配列を保持/共有せず、recordのtoStringはidentityをredactする。記録実体はGitへ保存せず独立synthetic goldenだけを試験に使用する。永続file store・親unit/reboot・GC/DB照会の実装はcodecだけでは完了しない。

### 6.14 借用rootの永続record IO（SSC-055/PG-D-157、先行19e22eb4）

BUG159/YKT124（先行12446fed）: removeで最初からentryが不存在でも、親directoryのsync成功を必須とする。前回unlink成功→sync失敗の可視不存在を耐rebootの確定と混同しない。再同期に失敗すれば不存在でも非成功。純readのOptional.emptyは存在観測だけであり、永続化を約束しない。

DurableRecordFilesはpackage内のfile能力であり、既に固定namespaceを認可したOwnedTransferDirectoryを借用する。任意pathのopen/provisioningやroot closeをしない。各操作をinstance内で直列化するが、callerは別instance/processも排除するOS flockとroot管理者の変更禁止を全区間で維持する。private root0700、regular0600/nlink1、root:root・ACLなし、同device、既定local filesystem（ext2/ext3/ext4/xfs/btrfs）のRWだけを受理し、tmpfs/remote/unknown/readonlyを拒否する。既存static/runtime環境fileの契約は変えない。

read(name)の名前は固定activeまたはcanonical lowercase UUID＋.run/.begin/.doneだけ。.runは内容のrun UUID、.begin/.doneはactivation UUIDと一致必須。activeはactivation構造だけを保証し、begin/anchorとのgraphはcallerの別責務。nullはprogramming契約、名前不正は固定IllegalArgumentException、byte/IO不正は原因/suppressedなしのStorageIoException。不存在は最初のentry openがcallback未開始でMISSINGのときだけOptional.empty。途中消失/close失敗は不存在扱いしない。保持root/full file snapshot・bounded142byte読取・channel size/position/EOF・読取後の同inode/full metadataと同名再open・root前後を検証し、全資源close成功後だけcaller所有byteを返す。読取bufferはfinally消去。

publish(name, canonicalBytes, partUUID)はbyteを独立copyし名前/値を検証してからmutationへ進む。既存は全byte/元inode一致だけforce/syncし、内容を一切変更しない。新規はcaller指定UUID.partのCREATE_NEW0600→bounded全byte write/size/force→保持再読と元snapshot照合→no-replace公開/dir sync→公開直後snapshot・再読・同名の全metadata/ctime再照合。renameだけのctime変化は許すが、その後の変化を許さない。既存part・競合target・部分失敗は保全し、自動上書き/再生成/消去はしない。part UUIDは非秘密の操作識別子でありrun原本の再採番ではない。

remove(name, expectedBytes)はcallerが完了/GC条件を別に確認した後だけ使用する。初回不存在だけ冪等成功、存在時は全byte/元inode・直前full snapshot一致の後に限定unlink/dir sync。失敗時は逆操作や補完をせず不確実性をcallerへ返す。公開/削除のrootはidentityを前後比較し、自身のmutationによるdirectory size/時刻変化だけを許す。開始/終端割込とEUID0を検査し割込flagは保持する。owned channel/entryは全終了で閉じ、IO診断はscope終了後に固定化、未知runtime/NPEを正常化しない。

PT-BAT-046～057/017の009・010はliteral72/109/140/141byteと実隔離inode/native no-replace/fsyncに合成root属性・fault portを組み合わせる。固定namespace/実root配備・state graph/OS lock/親終端/400日GC/DB参照判定はこの低位能力で認定しない。

### 6.15 固定永続namespaceとrun lifecycle（SSC-055/PG-D-158、先行36b5f85b）

SSC178：親continuationへ渡す原本能力は、現在保持中のSession・捕捉activation・同thread・aliveに限定する。既存verify-only portの既定complete/完成検査は固定失敗で、権限を暗黙追加しない。pending時は既存observe、正規complete後はobserveStartupの完全done値とactive/pending不存在を前後照合し、pending検査を完成graphへ誤適用しない。別activation/期限切れ/別thread/既done別値は変更0、現在保持Session以外へ再生成・任意unlink・原本修復をしない。complete不明は正常帰還せず保全、全外側close正常と親結果は別gate。API/Webの既存start intentは同inode ownerのlive-ready専用capで退役し、半退役不明で残りを自動削除しない。Caddy送達・停止確認まで両intentを保持する。原本/Backup/Current baselineに新sourceの値を後付けしない。

SSC094/PG311 root morning接続補足: fresh runはM→専用db-batch接続/実role・RW・ReadCommitted/session advisory71419602→全3参照不存在照会→原本startの順とする。DB不通/不明を不存在として原本を生成しない。resumeは既存原本を先に照合できる。root専用LoadCredentialは固定 `/run/credentials/schubert-nk-morning-controller.service/db-batch`、root:root0500 directory/0400 single-linked file、readonly tmpfs・ACLなし・保持inode前後同一・同device・1～65536byteを必須とし、既存UTF8 password codecへ所有byteを消去付きで渡す。systemd配置の実属性は隔離VMのpublic材料によるmetadata試験で確認、secretを出力しない。既存非root credential policyをroot許容へ変更しない。非pool専用connectionは固定loopback `schubert_nk`、current_user=session_user=`schubert_batch`、非recovery/RW/ReadCommittedを接続ごとに確認し、session advisory排他をcloseまで保持する。BACKUP_DB/CONFIG両beginは同transaction・同runでcommitし、不確定commitではworker0回。callback/row/statement/connection所有と例外合成を明示し、null/未知を正常化しない。schema historyの既存batch読取権限はないのでfallbackを禁止し、限定投影/full release期待値との照合を完成Assembly前提として継続実装する。限定DB接続はschema admission完了ではない。

SSC055/PG159追補（先行4c5dcb85）: 新run start前のDB既存ID確認とresume整合・GC同run参照は331 §3.12/332の限定readを使用する。親がOS/DB排他を維持して全3参照0/identity整合を確認し、DB不通/不明/nullを不存在扱いしない。原本なしlegacyはprogressから復元しない。GCはread成功だけで開始せず、既定400日/全activation完了/marker確定の全条件を別途満たす。RunReferenceRepositoryの実装・単体合格は親/GC実装の完了を意味しない。

BUG159/YKT124（先行12446fed）: 再開は既存byteの可視性だけを成功条件にしない。全graph/対象条件を検証した後、選択runのanchor→対象begin→既done（存在時）→active（存在時）の順に同byte force/dir syncで再確定してから、active再利用結果を返す。activeなしresumeはanchorを再同期し、未完了beginならそれも再同期、新beginなら新規公開し、最後にactiveを公開する。completeはanchor→begin→active（存在時）を再同期した後、同値確認済みdoneを新規公開または再同期し、active退役・不存在を含めた親dir syncを確定する。全force/syncの失敗・null part supplierは非成功とし、前回の未確定commitをsuccessへ変換しない。byte/UUID/cutoff/mtimeは変更せず、全graphの期待値を再照合する。

MaintenanceRunFiles.createは固定/varとnative能力だけを構成する。公開execute(Operation)はcallerが保守OS flockを獲得し、root管理者のnamespace変更を禁止した区間でのみ使用する。/var→lib→schubert-nk（共有root:root0755）→maintenance→runs/attempts（private root:root0700）をNOFOLLOWで6個の独立FDとして保持する。全scopeはlocal永続RW・ACLなし、private3rootは同device、共有祖先の別local mountは許すが毎回identity/属性を固定確認する。applicationによるmkdir/chmod/修復なし。操作前後と各record mutationの境界で固定namespaceのfresh6rootを再openし元snapshotのidentityと比較する。自身のmutationによるdirectory size/mtime/ctimeだけはidentity比較の対象外、scan内はfull snapshot一致を要求する。

callbackへ渡すSessionはscope内だけ有効。各操作をprivate lockで直列化し、execute終端で無効化してから全rootを逆順closeする。callback例外/null/割込/任意close失敗では成功を返さず、既公開fileを逆操作で消さない。close後に保存したSessionを使用しても拒否する。操作を実行中の別threadがある場合はその終了を待って無効化し、owned資源を使用中にcloseしない。callerはcallback外へSessionや非同期処理を持ち出してはならない。IOはscope終了後に原因/suppressedなし固定StorageIoException、未知runtime/NPEは非成功を維持する。

scanはmaintenanceの全直下名（runs/attempts/activeだけ）とruns/attemptsの全直下名を、保持directoryのDirectoryStreamを閉じてから検証する。既知名だけをfilterして不明を見落とさない。null/重複/別parent/不正segment/stream故障・途中mutationは不正。runsはcanonical UUID.run、attemptsはUUID.begin/UUID.doneだけ。unknown/.part/GC markerは保全し通常new/resume/completeを拒否する。GC markerからの限定退役再開は別GC機能として未完了。既知fileは§6.14で全byteを読み、name↔ID、begin↔anchor、done↔begin↔anchor、active↔beginの全値一致を確認する。別cutoff/孤立begin/done、複数未完了beginを拒否する。

anchorだけでbeginがない状態はanchor公開後の中断を表すpendingとして扱い、明示同run resumeでのみ再接続する。未完了beginもpendingであり、pendingは全runで最大1つ。activeがあるときはそのbeginと同一で、他pendingは認めない。active＋同activation doneだけは完了後active消去前の回復状態として認める。複数孤立anchorや未完了beginとの混在は曖昧なため保全拒否する。過去の全完了runは複数保持できる。

| Session操作 | 前提と順序 | 結果/中断保全 |
|---|---|---|
| start(BatchRun, activationUUID) | null/型検証→全scan、active/pendingなし、run UUID未登録、activation UUIDは全履歴未使用。callerがDB既存legacy ID非衝突を別照会。anchor→begin→activeを各durable公開→全graph期待値と照合 | 同じ固定activationを返す。各公開途中の失敗は原本/partを保全、停止/update等はcallerがこの成功後だけ行う |
| resume(runUUID, nextActivationUUID)・activeあり | 全scan、active.runが指定runと一致 | 同activationとOptional completionを返す。doneありは回復状態であり今回の副作用実行成功とは数えない。勝手にactiveを消さず、親終端確認後completeへ |
| resume・activeなし/未完了beginあり | pendingが指定runだけ、anchor/未完了begin完全一致 | 同beginからactiveだけ再公開、同activationを返す。nextActivationUUIDへ取り替えない |
| resume・activeなし/anchorのみまたは全activation完了 | 原本必須、他runのpendingなし、nextActivationUUID未使用 | 新begin→active、原本cutoffを変更しない。旧completionを新activationへコピーしない |
| complete(MaintenanceCompletion) | 全scan、指定activationとanchor/begin一致、activeは同activationまたは同done確定済みの不存在。別active/別既done・doneなしでactive不存在は拒否。callerは実子終端/親の許容morning終端/DB stepを別確認 | 同doneは全値一致だけ、新doneはdurable公開→同activeだけ退役→全graph照合。同じcompletion再試行は冪等。別終了時刻/0↔10で上書きしない |

Session内の各publicationは非秘密UUID supplierからpart identityを採り、null/既存part collisionを成功にしない。run/activation UUIDやcutoffはcaller指定の検証済み値を再生成/丸めず、supplier値で代用しない。read-only scanで正常化/DB補完をしない。返す状態はimmutable activationとOptional completionだけで、directory/byte/FD/秘密値を公開しない。

本scopeは原本file lifecycleのPG/PTであり、OS flock実獲得・親process/DB stop/reboot/実子起動・step/backup・legacy DB衝突・400日GC/参照照会は別未完了条件。fixtureの合成root権限を実root配備済みとしない。PT-BAT-058～081/017の011・012で全namespace/全graph/crash/fault/close/null/並行/再開の独立期待値を検証する。

### 6.16 完全な退役計画による原本GC（SSC-055/PG-D-161、先行4d534ba9）

BUG172/YKT133修正前追補: metadata-only recoveryのanchor不存在は前回unlinkの耐reboot確定を意味しない。対象originalが全て不在と照合した後、planを一つでも消す前にmaintenance/runs/attemptsの3private rootをsyncし、前回の未確定unlinkをdurable化する。同期失敗では残存plan/markerを保持し非成功。最後だけのsyncではmetadata先行消去を防げないため代替不可。

§6.13のactiveなしは対象runのactiveなしを意味する。別runの有効なactive/pendingは§6.15の最大1件条件で保全し、現在のmorningのcompletion確定前に過去runのGCを行える。全namespaceのunknown/partは拒否する。通常start/resume/completeはplan/markerがあれば非成功、中断GCの回復を先に実行する。親の連続OS flock、同一borrowed ReadCommitted transaction/backendのDB advisory自己exclusive保持、子終端、管理者によるnamespace変更禁止を全区間で要求する。GC部品はOS lock獲得や親終端を代行しない。

Session.retirementCandidates()はimmutableなrun UUID文字列順のBatchRun一覧。planまたはmarkerがあればその唯一の対象runだけを返す。それ以外は全activation完了かつactive対象外のrunを返す。age/DB参照はこの列挙だけで許可済みにしない。Session.retire(run, now, RunReferenceRepository)の結果はABSENT（原本/plan/markerの初期不存在で退役成功とは区別）、TOO_YOUNG（最新completionから400日以下）、PROTECTED（対象active/未完了、または初期DB参照あり）、RETIRED（限定退役・最後の同期/照会まで成功）。run/now/repositoryのnullは契約違反、nowはUTC年0001～9999/µsであり現在時刻の内部取得・丸めをしない。原本の同UUID異cutoff、DBidentity不整合/不明/不通、plan開始後の参照復活は固定非成功で保全する。

退役は次の順序を変更しない。

1. 全namespace/full snapshotを安定読取、対象の全activation完了・active対象外・最新終了から厳密400日超・同run DB3参照0/identity一致を確認する。
2. `attempts/<activation UUID>.plan`へ各doneと完全同byteのNKDONE1をdurable公開/再同期する。全planは対象run一つだけ。marker前の部分plan再開は元の完全graphとの一致を確認し、不足分だけ追加する。既存不同byte・不明partを上書き/推測修復しない。
3. 完全plan集合のcountとdigestを確定し、`maintenance/<run UUID>.retire`をdurable公開する。digestはASCII `NKPLAN1\n`の後にactivation UUID文字列順の各canonical NKDONE1全byteを連結したSHA-256小文字hex。countは1～2147483647の正規十進で恣意的activation上限を設けない。
4. markerが保持されanchorが存在する間は全plan集合のcount/digest/最新完了を照合する。残存originalは必ず同planに一致し、planにないoriginalは拒否する。完全planから仮想完全graphを再構成して別runを含む全参照を検証し、削除済みoriginalを現在時刻や残存doneで補完しない。各activationのdone→beginを同byte限定remove/dir sync、その後anchorを限定remove/syncする。anchorが残る間はplanを一つも消さない。
5. anchor不存在時は対象original attemptが0であることを要求し、残存planはmarkerのrun/最新終了以下・canonicalであることを照合して限定remove/syncする。最後にmarkerだけをremove/syncする。削除済みplanを再生成しない。全plan/marker消去後も3private rootをsyncして不可視の前回unlinkを確定する。

各plan/marker公開・original/plan/marker削除の前、および最終scan後にRunReferenceRepository.readを再実行し3参照0/identity一致を要求する。最初から参照ありのPROTECTEDは副作用0、準備開始後の参照ありは非成功。各mutation境界で保持namespace、期待graph/plan集合を再照合し、他runのrecordを変更しない。これは排他規約を破るDB superuserとのatomicity保証ではない。部分失敗で逆操作・recursive delete・DB参照の期限による無視をしない。

| record | 正規ASCII LFの順序 | 長さ |
|---|---|---:|
| plan | 既存NKDONE1をそのまま使用。nameはactivation UUID | 140/141 |
| marker | `NKRET1`、run UUID、cutoff、latestEnded、preparedAt、count、digest、最後LF | 195～204 |

時刻は§6.13の27byte。latestEnded>=cutoff、preparedAt-latestEnded>400日、全時刻年0001～9999/µs。MaintenanceRetirementは不変型・null拒否・toString redact、MaintenanceRecordsは独立byte所有・再encode完全一致・固定不正診断。DurableRecordFilesの限定名へ.plan/.retireを追加し各内容IDと束縛、bounded bufferは205byte（最大+1）とする。old record/原本内容/外部処理は不変。SHA256取得失敗は資源close後固定IO非成功、未知runtime/NPEは成功化しない。

017/015・016/PT-BAT-090～113の独立literal/digest、厳密400日、全8参照組合せ、全crash phase/IO位置/close/並行/nullで検証する。GC成功はこの部品の条件だけであり、親morning/backup/実server/IT/ST完了を意味しない。SSC055は親への実接続まで継続。

### 6.17 許可根拠canonical観測（SSC108、PG379、実装前）

SSC132/BUG386 journal再読補足（2026-10-01、修正前）：上記SSC131 CLEAN行末をentries/raw_sha256/content_sha256の二hashへ拡張する。rawは初回全console実byteのhashを保持し、journalctl JSONのmember順が異なる再読でもrawを上書き/再生成して期待値に合わせない。content byteは`NKJOURNAL1\n`、全rowの元順でordinalを0から付け、各rowの既存必須8key＋存在optional2keyをASCII昇順に `ROW|ordinal|key|<actual decoded valueのstrict UTF8hex>\n` とする。MESSAGE/PRIORITY/全boot/Unit/Invocation/cursor/mono/realtime/存在SEQNUM関連を全部含む。既存strict parserでduplicate/未知/missing/null/type/foreign/error/intervalを拒否してから計算。decode済Stringのunpaired surrogateを置換文字で正常化せずUTF8 encoder REPORTで拒否、NFC等の文字正規化もしない。旧再読はentries/content SHA完全一致と既存全entry検査を要求、raw serializerだけの変化は内容改変と誤認しない。新raw SHAと旧raw SHAをcontent一致を理由に同値と記録しない。固定署名/原本/config byte契約は不変更。

SSC131・STOP_SET具体byte/旧世代収集（2026-10-01、実装前）：`NKSTOP1\n`＋POSTGRES同じ共通5key/Morning/Broker実Invocationを先頭に置く。固定8Unit順CADDY/WEB/API/CLEANUP/INSPECTOR/EXPIRY/BACKUP/ARTEMIS。各Unitは `UNIT|<固定service名>|<既定12property名>|<actual value UTF8hex>\n` をId/LoadState/ActiveState/SubState/Job/MainPID/ControlPID/Slice/Delegate/ControlGroup/InvocationID/StateChangeTimestampMonotonicの固定順、`LEAF|service|0/1\n`、`KERNEL|service|index|mode|uid|gid|dev|ino\n` を固定host根/sys/fs/cgroup/system.slice/optional Unit leaf順で置く。indexは0～4又は5、全整数は実unsigned canonical decimal、dev非負/ino正、leafPresentと5/6件一致、managerは既存quiescent/固定Unit/全GetUnitProcesses検査済。初期snapshotは同Morning root identityから取得する。

続けて `CLEAN|source|old_invocation|native_start又は-|native_end又は-|journal_upper_mono|entries|sha256\n` 一行。sourceはNATIVE_TERMINAL又はBOOT_JOURNAL、oldInvocation非zero32小文字hex、entries正/sha実全raw64hex、upperは正の実観測値。NATIVEは旧Inspector正常143全18field/同kernel/同bootのactual start/endを入れupper=endとし既存inspectStopped全entryを検査。BOOTはnative start/endを観測できないので二つとも`-`、actual最後row monotonicをupperとする（0/旧時刻を捏造しない）。固定journalctlの同boot/Unit最後row（reverse/lines1）と同filter最後のvendor2.56.0・schubert-nk-broker start row（固定grep/reverse/lines1）を各最大65536byte、元期限内/最大5sで取得。両actual Invocation一致・startMono<=lastMono、最後rowもpriority4～7/既存全key/boot/Unit/重複拒否。当該Invocation全journalを最大4MiBの既存streamingで取得し全entry/required startup3event/停止event/error無し/cursor一意/mono正かつupper以内を検査、さらに二anchor再読完全一致を確認して返す。latest不明/別generation/未開始/未停止/欠落を古い成功generationへfallbackしない。初期ARTEMIS manager/kernel前後同値を別確認。末段は旧Invocationの全raw再読・digest/entries/upper相関を再検査し、現fresh Brokerは別Live/全Opsで確認する。BOOT履歴欠落/新規初回配置の許容経路は未完成依存として追跡し、未根拠をclean成功へ昇格しない。

SSC130・BROKER_OPS具体byte（2026-10-01、接続前）：`NKBROKER1\n`とPOSTGRES同一の共通5key/Morning/Broker実Invocation先頭。以降BROKER、TOPOLOGY、SETTINGS、ACCEPTOR、ROLE、PRESSURE、JOURNALの固定group順。BROKERはname/persistenceEnabled/journalType/journalFileSize/journalMinFiles/journalPoolFiles/globalMaxSize/IDCacheSize/persistIDCache/maxDiskUsage/diskStoreUsageの固定順、`BROKER|key|actualValueのUTF8hex\n`。boolは0/1、整数はcanonical decimal、diskStoreUsageだけ検証済finite/nonnegative/<0.9のdouble raw bits16小文字hexをvalueとする。TOPOLOGY/SETTINGS/PRESSUREはSS321固定6address順、各address内のkeyはASCII昇順、`<GROUP>|addressのUTF8hex|key|actualValueのUTF8hex\n`。Topologyはaddress_exists/anycast/multicast/auto_create_queues/auto_create_addresses/queue_names/queue_exists/temporary/durable/auto_created/queue_auto_create/routing_type/queue_address/queue_nameを全部含み、queue_namesは実固定single Queue名、routing_typeは実enum名。SETTINGSはSS321検証済COMMON全22とcapacity4、JSON fieldの実canonical representationを値とし、未知vendor追加項目を承認fieldと混同しない。ACCEPTORは実single coreのname/factoryClassName/scheme/host/port/protocols/startedのASCII key順、`ACCEPTOR|key|actualValueのUTF8hex\n`、extraProps実emptyも先に検証する。ROLEはSS321固定12matchのASCII順、各実role nameのASCII順、`ROLE|matchのUTF8hex|roleのUTF8hex|<12bool>\n`、12permissionはbrowse/consume/createAddress/createDurableQueue/createNonDurableQueue/deleteAddress/deleteDurableQueue/deleteNonDurableQueue/edit/manage/send/viewの順で1byte0/1を連結。PRESSUREはcount/bytes/state（state実enum名）の全3key ASCII順。JOURNALは既存真正Summaryの実entries>0とsha25664小文字hexを固定順に `JOURNAL|entries|<canonical decimal>\nJOURNAL|sha256|<64hex>\n` とする。全raw journalを保存/再公開せず、元Summaryのfresh Invocation/boot/Unit/required events/全entry検査を先に行う。未知値/欠落/null/追加address/role/permissionを拒否、全frameはASCII LF/max65536。各値は同一実queryからsnapshotし検証後に返し、期待定数や再queryでexpectedを観測へ差し替えない。pressure/count/diskの合法変動はfresh判定、identity/config/topology/ACLは発行前後exact再検証。既存readiness APIは詳細検査へdelegateし、legacy合成callbackはissuer evidenceを既定拒否する。

SSC129・POSTGRES/RELEASE_BOM具体byte（2026-10-01、接続前）：両gateは`NKPG1\n`/`NKREL1\n`、既定共通5key、`morning_invocation_id`/`broker_invocation_id`の実値を既定順で先頭へ置く。POSTGRESは `login_role=<UTF8hex>`、`effective_role=<UTF8hex>`、`database=<UTF8hex>`、`auto_commit=<0/1>`、`read_only=<0/1>`、`isolation=<actual JDBC decimal>`、`recovery=<0/1>`、`advisory_lock=<0/1>`、`schema_rows=<decimal>` の固定key順。その後実schema全rowをinstalled_rank順で `SCHEMA|rank|version又は-|typeのUTF8hex|scriptのUTF8hex|checksum又は-|success0/1\n`。checksumは実signed32整数のcanonical decimal（0又は正負・先頭0なし、-0無し）、SCHEMA creationのversion/checksumだけ`-`、他の欠落をplaceholderにしない。固定role/DB/RW/READ_COMMITTED/非recovery/HELDとBOM全six-column一致を先に検証する。実ResultSetからRowを新規構築し、expected Row listを観測として返さない。

RELEASE_BOMは `release_version=<UTF8hex>`、`manifest_sha256=<actual64hex>`、`api_config_sha256`、`web_config_sha256`を固定順。`VERSION|key|valueUTF8hex`はapp/protocol/storage/bootstrap/schema/configの固定順、`BUILD`はjdkVendor/jdkVersion/mavenVersion、`PLATFORM`はosId/osVersion/architecture/javaFeature、`RUNTIME`はosId/osVersion/architecture/javaFeature/jdkVendor/jdkVersion、`ARTIFACT|pathUTF8hex|sha256`はsignedBOM全artifactのpath ASCII昇順。VERSION keyの実名/集合は既存ReleaseInventory閉鎖契約をそのまま用い、省略名を新keyへ転記しない。固定集合以外/欠落を成功化しない。値は保持実manifest/file検証、runtime独立観測、同shared実YAML effective parseからだけ取得する。UTF8hexはNFC等の自動変換なし、unpaired surrogate/malformed UTF8拒否、空値は既定契約で許容する値だけ。両byte最大65536、ASCII LF末尾、unknown/null/順序/重複/範囲違い拒否、完成byteだけSHA256。Gate encoder/観測recordはdataであり、同M/A/原本/期限/生Broker/全step/root再読を省略しない。残3gateの未定義codecを仮SUCCESSとして発行しない。

SSC128/BUG376（2026-10-01、修正前）：Borrowed Broker Liveのparent guardは真正Root/親PID/元期限/原本file/INVALIDと生Brokerの確認だけを行い、DB transactionを開始しない。Sessionが同advisoryを保持して全列再読する間にも呼ばれるためである。DB原本整合はBroker開始前、各Ops試行前後、Expiry/Cleanup再読の前後にtransaction外で明示検査し、Session自身のHELD/READ_COMMITTED/型付き全列確認を維持する。再読のtransaction所有はSessionだけ、guard側のcommit/rollback/autoCommit切替は禁止。6個のbind境界にある既知CleanupStoppedExceptionは固定非秘密IOExceptionへ分類し、Morning入口も既知停止だけ30へ分類する。未知Runtime/NPE/Errorの同一性・非正常化は維持する。拒否では許可0/INVALID、実完了stepをFAILEDへ書き替えない。

SSC127/BUG375（2026-10-01、修正前）：旧vendor Brokerの既知通常停止は、真正全kernel空/manager前後同一に加え、ARTEMIS固定target、同boot/nonempty Invocation、Code1/status143、start>0/end>=start、failed/failed/result exit-code（旧Unit）又はinactive/dead/result success（新SuccessExitStatus143 Unit）だけを独立停止profileとする。143単独は成功receiptではない。Native Broker baselineはこのprofileを起動対象のdataとして扱い、同Invocationの全console journalを固定読取/上限4MiBで再取得する。既存startup journalと同じ厳密JSON/全key/重複cursor拒否/boot・Unit・Invocation一致/priority4～7/AMQ224及びERROR・FATAL無しを要求し、全row monotonicは旧start～旧end内、vendorの`AMQ221002: Apache Artemis Message Broker version 2.56.0`と` stopped, uptime `を含む停止event必須。完了entries/raw byte SHA256と旧完全snapshotを同Live内へ保持する。元journalをfiltered成功logへ置換せずrawは所有内消去・Git非格納。欠落/未知/IO/別世代/遅延row/単独exit143/timeout/signalはstart0、reset-failedは禁止。正常inactive baselineは従来どおりfresh startのdataであり旧停止証拠のplaceholderにはならず、最終STOP_SET/全issuer gateは別に根拠を要求する。startup側NIO/active/started3eventと停止側1eventの判定を混同しない。Java25の128+signalは[OpenJDK25 Terminator](https://github.com/openjdk/jdk/blob/jdk-25-ga/src/java.base/unix/classes/java/lang/Terminator.java)で確認（10/1）、実143/AMQ221002はPG395の旧Brokerで観測した。

SSC126 root収集補足（2026-10-01、実接続前）：Morningの同callback内で、共有strict設定が返す6pathと固定NSS profileを使い、真正RootStartupContext前後確認付きでPID1 host能力とprivate能力をそれぞれ全segment NOFOLLOW保持する。hostはlocal RW・ACL無し・directory/nlink>=2・固定uid/gid/mode・非負dev/正ino、privateは同metadata/FSの保持inodeでありread-only sandbox viewのみ許容する。各保持IO前後と同名再保持のfull snapshotは一致必須。最終recheckのdigest対象identityはdev/ino/uid/gid/mode/hostFS/hostRW/ACLのみとし、保守によるsize/mtime/ctime/nlinkの変化はdigestへ混入しない（nlink>=2自体は毎回確認）。6path/dev+inoは相互独立、printable ASCIIかつ`|`無し。unknown/null/交換/読取/close失敗に成功fallbackを設けず、rootを作成・chmod・chown・修復するruntime能力は持たない。共通5keyは実INVALID Epoch原本から取得し、NKROOTS1の既定6行/10fieldを独立goldenで照合する。

隔離PG/PTの初期不足に限るtrusted operator手順は、既存署名release/pin/完全BOM・M/A・全8Unit停止・未配信request/intent無し・同未完了原本/INVALIDを先に検証する。固定2accountと3rootの全対象不存在をmutation前に確認し、root専用private領域へ既存NSS原byteを保存してから固定systemd-sysusers/new-only directoryを配置する。既存3root owner/mode/dev/ino、current/原本/releaseは前後不変。途中失敗は部分配置を保全して拒否し、自動repair/rerunしない。`/var/log`等OS既存祖先のowner/modeを変更せず、NOFOLLOW保持を使う。空ASSET rootをmaster移行・起動gate・業務ready・IT/ST受入と扱わない。

SSC124/SSC117：Root0700 cleanup-request namespace・同LoadCredential名を成功NKCLEAN1と失敗NKCLEANFAIL1の排他profileへ拡張する。NKCLEANFAIL1は最大1024byte/ASCII/LF/末尾LF、固定順 `run,activation,cutoff,boot,epoch,backup_invocation,backup_started_monotonic,backup_ended_monotonic,backup_exit,database,configuration`。UUID36桁小文字/UTCµs/非先頭0整数、normalexit1～255、monotonic1～U64MAX/開始≦終了。末2値は `id,attempt,business_date,started,ended,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed` の固定12要素。id1～999999999999/attempt1～99/JST business_date、両ID異・同run/開始/終了、cutoff≦開始≦終了。余剰/欠落/未知/非canonicalは拒否、全owned byteを消去する。Field claimsはdataであり許可能力ではない。親は同cycle完了済fresh typed receiptと実DB pairからだけ新規private sourceへ発行、子は同Root親/原本/INVALID/共通deadlineと、固定BACKUPの実全cgroup終端/manager前後一致・同Invocation/正常非0/時刻、最新DB全列一致を毎mutation前後に確認する。CleanupのBACKUP読取factoryはRoot CLEANUPだけ・固定targetで、start/stop/任意Unit能力を与えない。DB秘密/成功archiveは失敗profileへ入れない。UNKNOWNにはsix SKIPも許可せず既定保全。詳細PT291/292、上位外部仕様不変更。

SSC123/BUG368：Cleanupの正規退役済み既知正常30（failed/failed、Remainyes、Code1/status30/exit-code、Invocation存在、start>0/end>=start、PID/Job0）を、独立host全cgroup空とbus/kernel/bus一致を確認して次明示resumeの旧baselineへ保持できる。reset-failedや旧receipt再使用はしない。新Invocationの真正終端を別に要求する。Inspector/Expiry/UNKNOWNへの拡大なし。起動前拒否でrequest/ownerだけが残る場合、M/A・INVALID原本・全終端・元親dead・start.intent不存在・旧CleanupInvocation不変の全証明とprivate原byte保存後に既存typed retireを行う。delivery不明/intent有りには適用しない。

SSC122・BUG367：Root親kernel statusのprimary UID/GIDは4値とも0を要求する。Groupsは存在するsupplementary集合をそのまま観測し、空行は空listとして受理、missingは拒否、primary GID0を勝手に補完しない。Root systemd Unitのsupplementary空は異常ではない。ordinary Inspector/API/Web自己/wrapperのNSS全group一致・nonempty契約は従来どおり。親boot/PID/start/cgroup/NoNewPrivs・前後一致・絶対期限条件は不変更。

SSC120：真正Cleanup fresh正常30の閉鎖証明はSS341§7.3とする。部分DB実観測は拒否/正規退役用のdataでありprestart digest/起動許可の根拠へ転用しない。成功0/10 KEEP_ACTIVEと分け、failed stateをresetして成功へ合わせない。全7step不存在/RUNNING/terminalを実保存のまま保持し、request/maintenance-owner/cleanup-start.intent以外がCleanup namespaceに残る場合、又はInspector全Unit終端/環境不存在を証明できない場合、退役/許可発行0。正常退役後の明示resumeだけ新owner/Epoch/requestを発行し、旧claim再使用なし。

SSC119の共有親owner（実装前）：共通Linux64bit `clock_gettime(CLOCK_MONOTONIC=1)`のtimespecを整数nsへ厳密変換する。wall clock/JVMごとのnanoTime始点・子起動時再計時は代替不可、errno/負seconds/範囲外nanos/long overflowは固定非成功。親deadlineは真正Morning UnitのExecMainStartTimestampMonotonic（整数µs）＋30分と既存親budgetのabsolute deadlineの小さい方、同boot/Invocation/PID-startを再照合する。全子は同CLOCK_MONOTONICと現bootで期限前だけ処理する。

非秘密owner形式は`NKMAINTOWNER1\n`の後、`boot,run,activation,cutoff,epoch,morning_invocation,morning_pid,morning_start_ticks,cleanup_invocation,cleanup_pid,cleanup_start_ticks,deadline_nanos`の固定key=value行・最後LF、最大1024byte。UUIDはnil以外の小文字canonical、invocationはnil以外32hex、pidは2～2147483647、start ticks/deadlineは正規正十進long、cutoffは年0001～9999/µsのcanonical Instant。親→Cleanupではcleanup3値を全て`-`とし、Cleanup→Inspectorでは真正CLEANUP snapshotの3値を同じframeへ追加し、Morningと異なるpid/Invocationを要求する。部分欠落・未知key/順序/CRLF/overflow/再encode差は消去後拒否。claim parse成功単独は権限ではない。

親は同M/A/原本/current INVALID/Epoch/実Backup終端の範囲で固定`/run/schubert-nk/cleanup-request/maintenance-owner`をRoot0600/new-only/force/readback公開し、真正Cleanup Unitへ固定LoadCredentialで配布する。Cleanupが同scopeで固定`inspector-owner`をnew-only公開し、Inspector Unitはそのprivate copyだけを受領する。Root-only Epoch原本/鍵を普通Inspectorへ公開しない。Cleanupは親manager/kernel/原本/currentを再照合し、Inspectorは自己固定UID/GID/zeroCaps/cgroup/INVOCATIONとMorning/Cleanupの固定kernel親生存/boot/PID-start/期限を各実mutation境界で確認する。shell wrapperのUnit MainPIDとJava子PIDを混同しない。owner sourceは同child実終端/DB再取得/独立結果再読後に正規退役し、最後に各start intentを退役する。残owner/intent/env/partは次MorningのM内・原本/DB/停止前に拒否し、期限や旧same-runを理由に自動repair/reuseしない。

SSC119 Inspector接続前補足：固定NSS account/primary groupは`schubert-inbox-inspector`、追加groupは不変release/config読取の`schubert`と`schubert-read`だけを正規化昇順で比較する（API/Web groupを継承しない）。Unitは明示SupplementaryGroups/全Capability空/RemainAfterExit=yes。Java自己PID/start/4UID/4GID/group/boot/cgroup/zeroCaps/NoNewPrivsを独立再確認し、真正UnitのInvocation/activating-start/MainPIDを固定manager照会で照合する。MainPIDはshell wrapperでありJava自己PIDとは別でもよいが、wrapperも同資格/boot/cgroup/PID-startを二度観測し、照会前後で全identityが同じことを要求する。固定LoadCredential名`maintenance-owner`に上記inspector-ownerをコピーし、専用credential rootの固定NOFOLLOW/所有/mode/ACL/nlink/devを既存private readerで確認してconsumeする。run/cutoffが既存Inspector環境と一致し、cleanup親が存在することを鍵/DB前に確認する。後続mutation guardには親確認だけでなく自己＋wrapperの同generation再照合も含める。各Statementのtimeoutは共通残期限整数秒を切り下げ最大5秒、transaction-local statement_timeoutの実PG返値を厳密再読する。期限後commitの失敗をrollback済と誤認しない。

SSC109実装前補足：固定M/原本のshared祖先は真正PID1 host viewのlocalRWと、private viewの保持同inode/owner/mode/ACL/FSを独立照合する。strict sandboxの祖先だけROであっても拒否理由にしない。M本体の固定private app/lock、原本maintenance/runs/attempts、request/current、backupの実mutation能力にはprivateRWを従来どおり要求する。固定host根からのNOFOLLOW保持能力は読取検査専用で、write/publish/sync/unlinkをhost経由へ切替えてsandboxを迂回しない。host/namespace root由来は固定親RootStartupContextで先に証明し、IO前後に再確認する。HostSnapshot/privateSnapshotのdev/ino・metadata差/hostRO/不明は処理0・非成功。Aは既存StartupAdmissionFileがhost/private同inodeを照合済でありMの代替にしない。

NKPERMIT1の既存field/byteは変更しない。二つの根拠は非秘密ASCII/LF、末尾LF必須、CR/空白/未知/重複/順序変更/未実行のplaceholder拒否。UUIDは非zero小文字canonical、時刻UTC固定6桁microsecond、整数はunsigned canonical decimal（leading zeroなし）、modeは4桁octal、hashは小文字64hex。pathは設定のabsolute normalized値そのもの、ASCII printableで`|`/CR/LFを含まず、全segment NOFOLLOW・実保持root検査済の値だけを採用する。未対応pathを別表記へ自動変換しない。最大65536byte、SHA-256は完成したbyte全体に対して計算する。

両byte列の先頭はそれぞれ`NKROOTS1\n`/`NKPRESTART1\n`、次に共通5行を固定順で置く：`boot_id=<UUID>`、`epoch_id=<UUID>`、`run_id=<UUID>`、`cutoff_utc=<time>`、`activation_id=<UUID>`。同親の読戻し済INVALID Epoch/原本から取得し、run/activation/cutoffを再生成しない。

rootsは次の6行を固定順に続ける：ASSET、TRANSFER、BACKUP、LOG、ARTEMIS、STAGING。各行の文法は`<ID>|<absolute_path>|<dev>|<ino>|<uid>|<gid>|<mode>|<fs_type>|<host_ro>|<acl>\n`。devは0以上、ino/uid/gidは既存各role方針に従う。fs_typeは実hostFSの既存allowlist値、host_roは実hostmountの`0`/`1`、aclは既存方針のACL不存在を実証したときのみliteral `empty`。各rootのowner/mode/ACL/hostFS/相互非重複・dev/ino重複なしを全gateで先に検査する。mtime/ctime/sizeは保守で変化するためdigestには含めず、保持IOの前後・同名再保持中は既存full snapshotの一致を必須とする。identityやpolicy変化は保守後の許可発行前/後再照合で拒否する。

prestartは共通5行の後に`morning_invocation_id=<32hex>`、`broker_invocation_id=<32hex>`を置き、次の10行を固定順に置く：BACKUP_DB、BACKUP_CONFIG、CLEAN_NOTIFICATION、CLEAN_QUESTION、CLEAN_SESSION、CLEAN_INBOX_OUTBOX、CLEAN_LOG、CLEAN_BATCH_RUN、CLEAN_TRANSFER、CLEAN_EXPIRY。各行は`<STEP>|<row_id>|<attempt>|<started_utc>|<ended_utc>|<status>|<target>|<success>|<failure>|<bytes>|<reason>|<producer>|<producer_invocation>|<receipt>|<reference>\n`。row/attempt/run/cutoffは完全DBhandle、terminal結果はcommit後独立再読値、reasonはNONE又は既存閉鎖enumとする。producerはBACKUP/CONFIG/CLEANUP/EXPIRYの固定4値、子は実fresh32hex Invocation、親local CONFIGだけMorning Invocation。receiptは実正常終了の0又は許容警告10、真正Backup正常非0はその実exit code。signal/timeout/unknown/未実行はencode不可。

SUCCESSは実処理/検証済成果に対応、FAILEDは真に試行済の既知失敗/全終端/DB記録、WARNINGは既存SS許容の実警告だけ。SKIPPEDはBACKUP_UNAVAILABLEの削除対象かALREADY_SUCCESSFULの再検証済元成功handleだけ。referenceは通常literal `-`、ALREADY_SUCCESSFUL時だけ元成功を固定順`row_id,attempt,started_utc,ended_utc,status,target,success,failure,bytes,reason,artifact_sha256`で記す（SSC116/117）。元statusはSUCCESS、reasonはNONE。artifactが存在しない削除/Expiryは最後のfieldのみliteral `-`とし、元audit/END cursor等の完全DB結果を別gateで実再読する。元handleと今回SKIP handleの一致・旧receipt流用は禁止。未実装をFAILED/SKIPPEDへ代用しない。どのstatusでも必要な実producer終端を省略しない。Backup失敗を理由にTransfer/ExpiryをSKIPPEDへしない。

SSC117・BUG351：Expiryの通常実行NKEXPIRY1はskipped=falseだけを受理する。既成功再開は別canonical `NKEXPIRYSKIP1`とし、既存10fieldの後に`prior_step_id`、`prior_attempt`、`prior_started`、`prior_ended`を固定順で追加する（最大1024byte、ASCII/LF・末尾LF、各値canonical）。今回handleはSKIPPED/ALREADY_SUCCESSFUL/全0/ended=startedを独立再読し、参照は同run/cutoff・CLEAN_EXPIRY・異なるrow・小さいattempt・cutoff以上の開始終了・元終了≦今回開始を要求する。元handleのskipped=falseでauditを読取り、SUCCESS/正確cutoff-7日/before-after=success=target/failure0/error null/参照ended一致を検査する。fresh MQ selected=0とOps非criticalも必須。旧auditを更新・再purge・新stageへ流用しない。claimだけからskip成功や起動許可を作らない。

10step行に続いてPOSTGRES、RELEASE_BOM、STOP_SET、BROKER_OPS、BACKUP_RETENTIONの5gate行を固定順で置く。文法は`GATE|<ID>|SUCCESS|<evidence_sha256>\n`、evidenceも非秘密ASCII/LF固定byte：POSTGRESは固定role/DB/RW/isolation/schema version/hash、RELEASE_BOMは保持release manifestと全role artifact/config/hash検証値、STOP_SETは固定8Unitの12field/kernels全終端観測とclean journal確認、BROKER_OPSは現fresh Broker InvocationとSS321固定address/queue/policy/healthの独立管理観測、BACKUP_RETENTIONは今回backup結果と実7世代後条件/保全対象一覧とする。各既存gateの実結果から固定key順で収集し、caller指定の任意digestを受理しない。具体的field codecは当該gateを実接続する前に仕様/独立vectorへ追記し、未定義gateのdigestで発行しない。API/Web/Caddy readyとMorning completionは発行後でありprestartには入れない（循環禁止）。

issuerは同M/A内で発行直前と公開/readback後に現boot/INVALID Epoch/原本activation、全6root identity/policy、Broker Invocation、全完全DBhandle/terminal値、実archive（成功時）を再検査する。不一致/欠落ではISSUEDへ進めずpart/markerを保全する。子へdigestだけで実処理成功を捏造させない。公開vectorはPT仕様へ固定しproduction encoderをexpected生成に使わない。S0の文法確定は実collector/issuer完了の認定ではない。

SSC106/092の「receipt0だけでmarker退役」はSS341§5.1の真正FAILED経路も含めて補正する。正常非0/fresh/全終端/DB実FAILED記録後の同ownerだけが退役し得る。既知失敗への補正はUNKNOWN/signal/timeoutやrawclient成功を許可する変更ではない。

SSC134実装前補足：CONFIGは親の実config/credential bundle完成判定である。成功では既存archive/publish/DB確定、再用では実bundle/元成功pair再検証、真正worker非0では同ownerの実子receipt・明示stop・全終端・同request/begin/原本/INVALID/元期限を照合して上流失敗による完成拒否を確定する。失敗時archive/MANIFESTを生成しない。両開始済stepのFAILED記録はSSC115のbundle不成立として維持するが、この親操作を実呼出しせずCONFIG終端0を捏造しない。commit後の別transactionで現在pair全14列（id/run_id/business_date/step/attempt/started_at/ended_at/status/target_count/success_count/failure_count/byte_count/error_code/error_summary）を実読戻しし、再用は元SUCCESS pair全14列も独立保持する。操作・照合・readbackの全正常完了だけが同Morning Invocationの非任意CONFIG closure/local0を作れる。business FAILEDと完成判定操作の正常終端は別で、子非0をCONFIGへ転載しない。未知IO/close/SQL/期限/未実行/旧receiptではclosure不可。ALREADY_SUCCESSFULのBackup referenceのartifact_sha256は同実検証bundleのMANIFEST raw byte SHA-256、今回SKIPと元SUCCESSのrow/attemptを別保持する。六実SKIP/実Transfer/Expiry/全必須工程後の起動継続は不変更。

SSC135/BUG388：明示停止後は保持した停止前fresh真正Backup receiptに、同ownerのstop client正常終了・固定Unit全kernel終端・manager/kernel/manager一致を束縛する。全18fieldの完全GC cold（inactive/dead/Resultsuccess/Invocation空/code・status・start・end0/PID・Job空）は実結果未観測で、当回receiptを0で再生成しない。残存managerは同Invocation/normalCode1/実exit/start/endと全終端を再照合する。部分cold/別世代/変質/未知/signal/未stopは受理しない。M/A/原本/intent/同budget保持を途切れさせず、KEEP_ACTIVEは従来同fresh receiptの厳密再読を維持する。SS341§5.1の真正非0後の両FAILED/六SKIP/実後続とCONFIG完成判定もこの別停止証明を用いる。

SSC136正規発行接続補足：既存part force/readback・no-replace公開・ISSUED atomic置換・全byte再読の順序は不変更。permit公開直前とISSUED化直前に同原本INVALID/全実根拠を確認し、最終issued readback後は当回permit全byteのSHAで導出した厳密ISSUEDを期待して全実根拠を再確認する。どの三境界でも現boot/epoch/run/activation/Morning・Broker実世代/同M/A/元budget、6root identity/policy、現在/元DB全値、子結果/役割別全終端、release/config/実archive・retentionを確認する。Broker guardは当回正常readback結果だけで期待値を切替え、currentから任意値を追認しない。発行開始後の失敗では同bindingの固定revokeを行い、INVALID currentのdurable置換・全byte読戻しをM/A内で確定する。revokeは同Epochを失効する限定操作で、fresh invalidateの再発行ではない。既知INVALIDはそのまま再同期できるが、別binding/破損/不明currentを修復しない。旧permit/partは残して次回厳密gateで隔離する。失効/close/readback不明では所有保持・非成功を維持し、旧permitや別新epochへfallbackしない。発行完了はAPI/Web readyやMorning DONEと別である。

SSC136発行intent補足：固定 `/run/schubert-nk/startup/permit-start.intent` はroot:root0600・single-link・空file・ACL無し/tmpfs RW、同Morning M/A/原本/元期限内で発行前CREATE_NEW/force/readback/directory syncを確定する。既存intentは旧試行の隔離対象でreuse/repair/自動削除しない。Root向けpermit受理は当該intent残留を必ず拒否し、publisher内のissued readbackは同ownerのintent保持下で行う。全subordinate proof/publisher closeと最終実検証後だけ同inodeを退役する。退役後close不明にも外側M/A監督が固定namespaceでintent復旧と同attempt厳密revokeを行い、未確定は所有保持/隔離とする。Current/permit読取成功だけを実Root起動許可にしない。Root側の不完了原本/同Morning生存・M境界はS3の全gateに含めて閉じる。

SSC136所有scope補足：監督ownerは同原本continuation内・A取得前に固定directoryを保持する。Main/Stage内では借用し、発行rootと全nested資源を正常closeした後、A callback/lock closeを完了する。同M/専用DB/原本/元期限の後段でissued原byteを再読・publisher close・全gateを確認し、最後だけintent退役とcloseを行う。この区間の例外は同原本continuation内で固定intent復旧/同attempt失効/readbackを監督し、再open/close/原本不明なら正常unwindせずretainする。未完了activeのRoot受理は同boot/epoch/run/cutoff/activationの完全原本graph・真正Morning Invocation/PID/startTicks/元deadline内の生存と、正常A後の同親実S3 launch世代が必要である。死親/期限超/A-close不明/launch未接続はvalid permit・intent無しでも拒否する。完成後restart枝は同activationの真正done0/10・完全graph・active不存在を別検査する。RootServiceLauncherの現30拒否は全gate/同PID exec接続まで維持する。

SSC136/BUG391：intent退役後の原本owner/DB/credential closeとM内最後root検査も、同M callbackの当回abort専用監督で保護する。scope外からDB/原本証明を再利用せず、保存した同attempt invalid/permitとfresh固定namespaceだけでquarantine・厳密失効/readbackを行う。既に失効監督を完了した経路へ二重復旧を行わない。M自身の最終close不明とRootの正常S3 launch束縛は別gateであり、この監督だけでRoot起動受入にしない。

SSC144（PG407、実装前）：全停止したRoot正常30後の管理者復旧は旧処理の成功ではない。trusted operatorのM取得後・stop前に旧Morning/固定API又はWEBの真正18propertyと正常Code1/status30・実Invocation/start/endを保存する。A取得後、旧世代PID/start消滅と旧Morningを含む全kernel終端、boot/同run/cutoff/active/INVALID同Epoch、旧signed BOM/pinと全DB結果、raw permitのSHA/派生ISSUEDへの全byte照合、旧owner/launchの親子全bindingを再検証する。INVALIDから読む旧permit/owner/launchは相関資料だけでありRoot受理/起動権限ではない。候補署名/full BOM、旧原byteのprivate durable保存、全物理状態再照合の正常完了後だけ、保持した当回service intent→publication intentを型付き退役・sync・不存在再読する。旧処理close成功へ遡及せず、現在の所有解消を独立証明する。GC/部分cold/UNKNOWN/signal/timeout/別世代/残process/DB不通/IO/closeでは保全、旧done/SUCCESS/DB更新・任意unlinkは禁止。退役後にだけ既存fresh INVALIDの配備と通常明示同run resumeへ進み、新Invocationを旧receiptに混ぜない。PT299/300、SSC144/SS342§4・SS343§6.15～17。

SSC145/BUG410：SSC144の旧18propertyはstop前に二読し、旧実観測日時/元Source・全byte hashとともにroot private領域へforce/sync/readback保存してから停止する。次再試行でも真正同boot/元同Source/同旧owner/launch/原本を再照合し、旧receiptを新Invocationへ流用しない。停止後はSSC135と同じ捕捉済normal30＋完全GC cold＋全kernel/旧PID消滅を限定受理する。GCだけからreceipt30を補完せず、部分cold/unknown/別Source・別世代は拒否。今回既に独立toolで得た全18propertyを後刻保存する場合は観測時刻と保存時刻/原観測根拠を区別し、合成fixtureや現在のcold値を旧実結果へ変換しない。過去全DBのFAILED/WARNINGは履歴として不変保存し、退役・起動成功へ変換しない。

## 7. 環境差分


| 項目 | Local dev | PT/IT | Production |
|---|---|---|---|
| PostgreSQL/Artemis | Container/専用instance可、実製品同major | Java 25/PG18/Artemis導入minor | 単一server、loopback |
| DB | 個人専用DB | Testごと初期化 | `schubert_nk`、real data |
| Port/root | Workspace専用非衝突値 | Test host専用 | 本書のdefault |
| Credential | Test限定のrandom secret | CI secret store | systemd credential、0600、Git禁止 |
| TLS | Loopback/test CA | Test CA | Caddy internal CA/IP |
| Monitoring | DEBUG可 | DEBUG/STANDARD両方 | STANDARD |
| Asset | 最小fixture＋必要時read-only copy | Full sanitized/real authorized copy | Full 59,627 file baseline |

H2、in-memory JMS、UTF-8以外のwire、relaxed validation、ADMIN固定passwordでPostgreSQL/Artemis/securityを代替しない。
環境差分は`config/environment-matrix.yml`のallowlistと本表を照合し、業務仕様のprofile分岐を作らない。

## 8. 初期data

### 8.1 Migration固定master

| Data | 値 | 検証 |
|---|---|---|
| `games` | `(1,NUKITASHI1,NUKITASHI,1)`、`(2,NUKITASHI2,NUKITASHI2,2)` | 2件、code/order UK、UI 223一致 |
| Code/state/role | DB CHECKとJava enum | 全enumのDB/Java/wire照合 |
| Schema history | 期待Flyway version | checksum/installed rank正常 |
| MQ Address/Queue | 321の6組 | Auto-createではなくconfig初期化 |

### 8.2 Bootstrap account

SSC190（PG465、正常完了後の管理者code-only配備補足）：前親が正規DONEまで完了した場合の配備を、失敗復旧又はpending原本用の配備工具で代用しない。管理者は現boot・正規署名/current・親実正常終端の記録・完全DONE値・active/pending不存在・DB全既存値・Backup現物/Transfer・全startup原byte/metadataを再認証し、同M/A及びDB保守排他を取得する。生存Caddy/Web/API/Artemisは現manager/kernel/普通identity/INFO/socketを同世代で前後照合してから逆順に所有停止し、全対象Unit/kernelの真正終端を確認する。stop client成功やGC値だけで旧workerの正常帰還を認定しない。旧失敗/UNKNOWNを今回の正常終端に混ぜない。

全対象停止後、保持DONEを`observeStartup`の完全completionで再検査する。pending専用`Session.observe`へDONEを渡したり、active/pending/原本を復元して条件を満たしたりしない。旧ISSUEDのpermit/owner/launchは署名世代の相関資料であり再利用する起動権限ではない。管理者配備の既存`invalidate`で同boot/同保存activationの新INVALIDを発行し、旧permit/owner/launch原byteを全保持する。新permit/start/DDL/業務run更新0で正規candidate/BOM/approval/currentを切り替え、署名された新bootstrap Unitだけを既定disabledで配置する。全旧原本/DB/Backup/Transfer/record集合・新INVALID/署名・Unit内容・全scope正常返却を独立再試験してから次のbootstrap一回startへ進む。不明/半切替/close不明は保全・隔離・M/A保持、成功へ推定しない。切替後の通常Morningは新runを正規生成し、保存DONEをpendingへ戻さず原本/Backupを保持する。親30分/各Unit期限・既存コードの起動品質を緩和しない。

SSC189（PG465、専用Unitの起動/保守排他の内部具体化）：bootstrapは通常API/Web用のpermit・JMS・5credential組立を流用しない。専用Unitは既存schubert-api UID/GID/固定supplementary groups、全capability0、NoNewPrivileges=true、kernel cgroupが固定`/system.slice/schubert-nk-bootstrap-admin.service`であることを既存ChildStartupContext/FixedServiceIdentityで認証する。固定`/run/credentials/schubert-nk-bootstrap-admin.service`だけを受け付け、username/password/db-apiの3つを保持inode/ACL/read-only/bounded/strict UTF8で読む。通常API/Web credential enumへbootstrap秘密を追加しない。設定は既存API非秘密設定、DBは既存schubert_app admission、argv/秘密env/URLやrole overrideなし。前後同boot/PID/startTicks/identity/cgroupで世代を再検査し、全credential/DB/source/root資源が正常返却した後だけ0又は20を返す。実Unitは無効がdefaultで通常restartなし、0と既存skip20を区別して記録する。

初期作成TXは既存保守排他71419602に`pg_try_advisory_xact_lock_shared`で参加し、保守がexclusiveを保持していれば即時拒否・作成0、NULL/欠落/余剰結果も拒否する。その後のmembership71419601→table lock→存在確認はSSC188と同じで、共有保守lockはcommit/rollbackまで保持する。これはMaintenance namespace/原本/epoch/permit発行の権限ではない。実credential sourceは別sessionでLogin/変更/ADMIN確認を終えてから退役し、DB/原本/Backup/Current保全を独立検査する。固定Unitを署名BOMへ含め、未登録コードや私有classをProduction実入口の代用にしない。

- 現行`user_pass.txt`を移行せず、初期ADMINを安全なoneshot `schubert-nk-bootstrap-admin.service`で1件作成。
- Username/passwordはsystemd credentialから読み、passwordは画面と同じvalidation、`{pbkdf2-v1}`でhash化し、平文はmemory使用後zero。
- `app_users` 0件の場合だけ実行、複数回/既存Userありは無変更でexit 20。固定default passwordなし。
- 作成後に別sessionでLogin・password変更・ADMIN権限を確認。Bootstrap credential sourceは承認済み手順で無効化/削除。

SSC188（PG465、初期ADMINの内部transaction補足、RD/UI変更なし）：初期作成は通常の認証済みADMIN向けUser CREATE入口を偽のactorで呼ばず、専用oneshotから借用write transactionで行う。READ COMMITTED・autoCommit=false・readOnly=falseを必須にし、既存ADMIN membership advisory lock71419601→app_users SHARE ROW EXCLUSIVE table lock→全Userの存在検査→0件時だけINSERTの順とする。table lockは非協調INSERTも遮断し、commit/rollbackまで保持する。既存Userなら種類/statusを問わずexit20相当の非作成結果、hash化・行更新・監査追加なし。callerがcommit/rollback/closeを所有し、commit又はclose不明を正常成功へ変換しない。

usernameは画面の新規Userと同じNFC/trim/64byte・ASCII `[A-Za-z0-9._-]+`、comparison key Locale.ROOT、passwordは同PasswordPolicy/PasswordHasherを使用する。初期role ADMIN/status ACTIVE/version0、created_by/updated_by NULL（認証済み既存actorは存在しない）、日時は同一UTC値。初期作成の既存USER_CREATED ACTION/SECURITY監査は同transaction、actor列NULL、detailsに固定source BOOTSTRAPと新targetUserIdだけを記録し、credential/hash/平文を含めない。新しいaction/DIFは追加しない。既存DBrole/grantとV002/V005を再利用しDDL/既存migration checksumは変更しない。個別credential読取・専用Unitの同定、資源後条件、実Login/変更/credential退役は別途同じ経路のnative受入条件として維持する。

## 9. Flyway migration

### 9.1 責務分離

SSC095/PG312: 上記release配置は実Unitが参照する固定正本名へ統一、libをmanifestではwildcard扱いせず全具体fileをsize/SHA付きで列挙し未登録jar/symlink/欠落を拒否する。protocol/storage/bootstrapの複数配置は同版・同hash、jar内同梱SQLは外置きSQLと同byteを要求。既存RELEASE-MANIFEST.jsonにはmigration期待六列も含め、固定Flyway13.4/createSchemas=true profileのSCHEMA行(rank0/versionNULL/typeSCHEMA/script`"schubert_meta"`/checksumNULL/successtrue)とversioned SQLの全rank/version/type/script/checksum/successを明示する。期待値はrelease SQLから固定Flyway版で生成し運用DBの実測を採用しない。共用固定query `select installed_rank,version,type,script,checksum,success from schubert_meta.startup_schema_history() order by installed_rank` を借用connectionで実行し全行全列を照合、失敗/NULL/余剰/欠落/不一致はreadiness false。権限は331の限定投影だけ、migration credential/superuser fallback無し。この六列照合は固定versioned-SQL起動profileでありFlyway validate全機能の代用合格とは呼ばない。root承認digest/immutable release→全BOM→期待schema→親DB backupbeginの最終順を要求する。

- Migration実行は`schubert_migration`が`nk_owner`へ限定SET ROLEするoneshot。API/Web起動時にmigrate/repair/cleanしない。
- History tableは`schubert_meta.flyway_schema_history`、`validateOnMigrate=true`、`outOfOrder=false`、
  `baselineOnMigrate=false`、`cleanDisabled=true`。Migration checksum変更をrepairで隠さない。
- Application起動はmanifestのexpected schema version/checksumとDB historyをread-only検査し、不一致はreadiness false。

### 9.2 Initial sequence

| Version群 | 内容 | Transaction |
|---|---|---|
| V001 | extension/schema、owner/default privileges | DBA事前作業と分離 |
| V002 | Account/session/master table、PK/FK/UK/CK | 1 migration transaction |
| V003 | Question/message/log/batch/Web technical table | 1 migration transaction |
| V004 | Btree/partial index、小規模initial data | transaction |
| V005 | GIN/pg_trgm index、grant/view | Full data load前は必要indexだけ、後続で最終化 |

実装時の実version番号は上記責務順を崩さず、1つの巨大migrationへ集約しない。
`CREATE INDEX CONCURRENTLY`等のtransaction外DDLが必要な場合は個別migrationに分離し、失敗/再開手順を追記。

## 10. 現行data移行・inventory

| 対象 | Current baseline | NKの検証 |
|---|---:|---|
| Master file/総byte | 59,627 / 19,240,707,190 | 全file count/byte/SHA-256 |
| Scenario file/entry | 262 / 99,661 | DB count、display order、代表検索 |
| Audio metadata/link | 37,256 / 35,201 | File/hash、orphan/game不一致0 |
| Video | 20 | Stable logical ID/category/pair/order、Range |
| Music | 129 | SHA-256 logical ID、section/pair/order |
| Current log/account | 非移行 | NKは初期event/新規accountだけ |

### 10.1 ETL順

1. Current source/program/DB/materialのcommit/hash/path/mtime/size/countをread-only inventory。作業copyをstagingへ作る。
2. File pathをNFC・root-relative storage pathとsanitized display pathへ分離。絶対/path traversal/NUL/control/symlinkを拒否。
3. SHA-256/byteとcategory/pair、現行ID→NK ID/display order対応表をcanonical manifestへ作成。
4. `pg_temp`のstaging tableへCOPYし、件数・型・NFC/byte・参照を検査。Targetが空の初期DBへ1 transactionでinsert。
5. GIN/final index作成、ANALYZE、全FK/CK/UK/orphan/game不一致・link順を検査。
6. Asset staging全fileをmanifestで照合後、application停止中に確定asset rootへ同filesystemでatomic切替。
7. CHR、UI 254受入、backup/restore、morning runをrehearsalし、所要時間/disk peakを記録。

ID再採番は可だが、現行順を`display_order`に固定し、対応表をmanifestに残す。
Current bookmarkのDB ID互換を新しい要件として暗黙追加しない。

## 11. Deploy・application rollback

### 11.1 Deploy

SSC098/BUG305: Commons Logging1.4.0/JSpecify1.0.1（既存Web採用版）を親reactor管理へ統一し、全role同releaseのGA版一意を維持する。Maven局所convergenceに加え実resolved matrixでも検査し、候補外署名の前に複数版を拒否する。これを新しい許容差分やverifier/期待の緩和へ置換しない。

SSC097/PG315: 配備候補の検査はcurrentを変更せず、固定`releases/<既存version token>`を既存保持namespace/fullBOM検査へ渡す。候補/current外の信頼済み配備toolが固定pin・Ed25519で元manifest bytesを認証し、同digest/versionの全payload検査を完了してからだけactivationで原本を発行する。候補検査の公開返値はfile agreementに限りroot起動/permit権限ではない。trusted tool/pinの固定配置・由来・独立検証と発行のforce/close/atomic置換/directory syncをPTへ残す。将来の既存Production更新は旧承認release/旧schemaでbackup実成功→migration→新release/approval/current→再gateの順。新schemaを要求するMorning beginをmigration前backupへ使わない。専用PGPT初期構築だけはmarker・業務行0（既定seed除く）・未受入/未許可・全停止/復元点を確認して専用migration actorによりappend-only適用する。VM snapshotを業務backup成功へ代用せず、保留中の真正run/activation原本を同identityで保持する。

SSC096/PG313（実装前の固定契約）: 既定signature検証を省略しない。配備入力側で固定pinned公開鍵によるdetached signature検証成功後だけ固定root原本 `/etc/schubert-nk/release-approval/current` を発行する。親root:root0700、file root:root0400/single-link/ACL無し。固定ASCII1行列は `NKRELEASEAPPROVAL1\nversion=<既存release token1..64>\nmanifest_sha256=<lowerhex64>\n`、最大192byte、unknown/duplicate/欠落/NULL/CRLF/BOM/escape/末尾追加/非canonicalを拒否する。path/algorithm/keyは原本から選ばせない。原本の更新はM/A・全停止・permit失効・current切替を管理する配備処理内で行い、起動時の実測hashから承認原本を作るfallbackを禁止する。

全root前段（API/Webの!前段とmorning）は真正RootStartupContextを認証してからPID1 host-viewのこの同じ固定原本を保持read/recheckする。API/Web UnitはUser=serviceを維持し、root-only原本を通常LoadCredentialへ混ぜない。既存ordinary5secret catalog不変更。root承認version/digest→既存held current/release内の同一manifest bytes/version照合・strict parse→全BOM/共有artifact/同梱SQL・外部SQL/checksum→前後原本/current/namespace一致→全close成功後だけimmutable schema期待を返す。digestだけの既存sha256読取をfullgateへ読み替えない。

Runtime release treeはmanifest具体payload＋祖先directory＋固定RELEASE-MANIFEST.json/SHA256SUMSの完全集合、未知file/jar/空dir/symlink/重複aliasを拒否する。manifest自身はpayload hash列に含めず外部root原本digestで拘束、SHA256SUMS自身も除外してmanifest＋全payloadのcanonicalhash列と実bytesを照合する。detached signatureは配備入力側に保全しruntime treeへ格納しない（未検査の任意管理file除外は設けない）。署名検証/原本発行/全BOM未接続時はschema/backup/permit/Production受入を非成功のままとする。

SSC096内部具体化: 最初のruntime profileは固定thin-JARだけとし、shading/nested実行jarやJAR Class-Pathによる列挙外依存を受け付けない。manifestはformat/release/versions(app,protocol,storage,bootstrap,schema,config)/source(commit,tag)/build(JDK vendor/version,Maven version)/platform(OS ID/version,architecture,Java feature)/dependencies(coordinateと具体配置path)/artifacts(具体path,size,SHA256)/migrations(六列全行)を持つ。固定key集合/厳密型/duplicate/unknown/欠落/末尾tokenを拒否、path順・coordinate順を固定。相対ASCII pathの空/`.`/`..`/backslash/制御字/file-directory衝突を拒否し、manifest再serializeではなく原byteを署名/hash対象とする。共有coordinateの全配置jarは同size/hash、API jar同梱migrationと外置きSQLは全名前/byte一致、未知/重複ZIP entryを拒否する。VERSIONはrelease＋LF、schemaはSQL最終versionと一致。Build記録と実runtime互換条件を別検査し、未規定patch差を黙認しない。

固定JSON profileはformat=`NKRELEASE1`、上記top key順、source(commit40lowerhex/tag非空ASCII)、build(jdkVendor/jdkVersion/mavenVersion)、platform(osId/osVersion/architecture/javaFeature)、dependencies要素(coordinate/paths)、artifacts要素(path/size/sha256)、migrations要素(installedRank/version/type/script/checksum/success)の固定順とする。六versionは1～64byte token、Java featureは25、OS/build記録は実環境との別admissionを必要とする。1MiB原byte上限/UTF8 BOM無し/ネスト4/2048 artifact・512 dependency・1000 migration以内、numberは正規十進整数のみ、nullableはSCHEMA行のversion/checksumだけ。全lib jarはdependency具体pathと完全集合で一致、protocolはapi/web、storage/bootstrapはapi/web/operationsの各1配置・同version/size/hash、他coordinate複数配置も同size/hash。payload固定必須はVERSION/3実行jar/SQL列、config・systemd・runbook等の必須品は各起動/配備gateにも追跡し、不足を任意payloadだから合格にしない。payloadにはRELEASE-MANIFEST.json/SHA256SUMSを含めない。既にAPI/Webが使用するGson2.14.0をBootstrapの厳密stream parseへ共用、候補BOMからparserの依存/設定を選ばせない。これらは既存内部配備形式の具体化で外部業務仕様を変えない。

署名は固定Ed25519/pinned公開鍵とし鍵/algorithm選択を候補releaseに委ねない。検証・承認発行主体は既に信頼された配備側に置く。鍵custody/署名tool/version/入手元/独立公開vectorをPTへ記録し、秘密鍵はGitへ格納しない。activationはM取得→固定全対象停止/全終端→A取得/全終端再確認→新epoch INVALID永続確定→必要backup/migration/config→検証済immutable release・approval/current各atomic切替→再読全gate→新permit順。二つの切替間crashは不一致/INVALIDで拒否し旧承認/旧permitへfallbackしない。署名だけ成功してpayload/BOM未検査の段階では原本を発行しない。

1. Releaseを新version directoryへ配置、owner/mode/`SHA256SUMS`/manifest/signatureを検証。
2. Rendered configをstaging pathでschema/secret/path/port検証。Caddy/systemd/Artemis/PostgreSQLのvalidatorを実行。
3. Backup・停止・Flyway migrate・実効schema/grant検査。
4. `/opt/schubert-nk/current.new`を新releaseへ作り、`renameat`/`mv -T`相当で`current`をatomic切替。
5. Morning dependency順でstart/readiness/smoke、release/config/schema/protocol versionの一致を確認。

### 11.2 Application rollback

- Trigger: Startup/readiness、major functional/security/performanceのGo不可、またはmigration incompatibility。
- Caddy停止→Web/API/Artemis停止→NK可変data dump保全→schema compatibility判定。
- 旧applicationが新schemaを読めるadditive migrationなら`current`を旧releaseへatomic切戻し。
- 読めない場合は当日backupを別restore DBへ検証後、承認済みrestore手順でDB全体を戻す。Down migration/手修正しない。
- Rollback後も新release/config/data dumpを隔離保全し、調査前に上書き/削除しない。

## 12. 現行からの切替・切戻し

### 12.1 Cutover gate

- RD/UI/SSとQA/RDF/UICが必要状態、CHR baseline/harness、PT/IT/ST、full rehearsal、restore test、
  public 55160/TLS、定量count/hash/performanceが合格。
- 停止枠、Go/no-Go/切戻し判定者、判定期限、利用者周知、現行backup保持期間が承認済み。
- 現行program/DB/config/asset/Caddy/NAT/start手順はread-only保全し、NKが上書きしない。

### 12.2 Sequence

```text
Go一次判定
 -> 現行public入口停止
 -> 現行app停止＋最終inventory/hash/DB backup
 -> NK asset/DB最終load＋manifest照合
 -> NK PostgreSQL -> Artemis -> API -> Webのinternal acceptance
 -> Caddy/NAT 55160をNKへ
 -> external acceptance
 -> Go最終判定または切戻し
```

切戻し判定完了まで受入担当者以外の更新業務を開放しない。現行/NKを同時に本番更新可能にしない。

### 12.3 Rollback trigger・手順

Triggerはdata hash/count/FK不一致、Login/検索/media不能、message取違え/重複更新/質問消失、
security境界違反、backup/recovery不成立、公開TLS不能、停止枠内で是正不可能な性能未達。

1. NK Caddy停止、更新遮断。Web/API/Artemis停止。
2. NK切替後可変dataをtimestamp/manifest付きdumpとして隔離保全。現行へ自動マージしない。
3. 現行DB/program/config/asset hashを照合し、保全済み手順で起動。
4. Login/検索/Scenario/audio/video/music/logのsmoke、Caddy/NAT 55160/TLSを現行へ戻す。
5. External smoke後公開。原因、NK保全data、失われ得る更新、利用者影響、再計画を記録。

## 13. Migration/rollback証跡

- Source/target host、current/NK Git commit/tag、release/config/schema/protocol version、tool/hash、operator/判定者・日時。
- File count/byte/SHA-256、DB table/constraint/orphan、mapping count、表示順、CHR/test result、duration/disk peak。
- Backup/restore manifest、Caddy/NAT差分、public certificate fingerprint、Go/no-Go/rollback判定と根拠。
- Password/key/質問本文、credential実値、許諾上不要な個人・著作物pathは証跡へ出さない。

## 14. PT・IT・Rehearsal

- Configの未知/重複/範囲外/missing secret、root/port重複、effective hash drift、production profileのdebug設定。
- Clean OSでdirectory/owner/mode/systemd credential/release配置を再現、serviceごとの読み書き権限負test。
- Flyway validate/migrate/checksum mismatch/out-of-order/partial failure、applicationの自動DDL禁止、旧/new releaseのschema compatibility。
- Current full inventory、不正path/symlink/hash、件数差、ID再採番/display order、再実行、staging失敗・容量・中断。
- Release current切替直前/直後のkill、migration後旧app、backup restore、NK可変data保全、current公開への切戻し。
- 最低1回の全量rehearsalで所要時間、disk peak、停止枠、判定時刻を実測しrunbookに固定。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-039 | Config優先順をjar default→common→service→env→credentialに固定し、unknown keyを起動失敗 | 環境差分とsecret分離を再現可能にし、typo黙認を防ぐ | ConfigurationProperties/schema test |
| SS-D-040 | Flywayはapplication起動時validateのみ、migrateは専用oneshot、clean/repairは自動禁止 | 起動中DDL・checksum改ざんを防ぎ、rollback判定を明示 | Migration pipeline/IT/runbook |
| SS-D-041 | Current/NK切替中の一般更新を最終Goまで許可しない | 二重更新・自動マージ不能なNK質問/account差分を防止 | Cutover運用・ST acceptance |

## 16. 禁止事項

- Secret/asset/dump/log/runtimeをGit/release artifactへ含める、またはproductionの実値をdocument/templateに書くこと。
- Application起動時DDL update、Flyway clean/repair自動、適用済みmigrationのchecksum書換え、手動down migration。
- Current source/dataを移行toolから更新する、現行/NKを同時本番更新可能にする、Go前に現行保全を削除。
- 対象DB/root/release versionを識別せず、広範囲削除・schema drop・restoreを行うこと。
- H2/in-memory MQだけでPG/ITを合格、または環境profileでrole/owner/validationを無効化すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Directory/config/credential/initial data/Flyway/current migration/cutover/rollbackを詳細化。 |
| 2026-08-31 | 横断監査でmigration DB role名をUI 212の`schubert_migration`に統一。 |
| 2026-08-31 | 横断監査でWeb DB poolをUI 212の上限2へ修正し、Web revoke/API context/API InboxのAES keyを用途別に分離。 |
| 2026-08-31 | DB dump credentialをbatch保守用から分離する`db-backup`候補をQA-043/UIC-003回答待ちで追加。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、`db-backup`を専用backup unitだけへ配布するcredentialとして確定。 |
SSC061/PG168: 341 §6.6の真正root manifestはroot CREATE_NEW/0600・書込FD全close・fsync/atomic/再hashと、読取側のuid0/gid0/nlink1/ACL・namespace/全handle/name/hash検査を前提とする。backup user作成fileのchownで真正化しない。両step DB確定部品はこの前提の代用ではなく、生成/信頼reader・最新選択/7世代は後続で実装する。専用DB/OS資格と秘密鍵配布は変更しない。

## QA-048/049承認反映：migration・backup・切戻し（2026-10-03）

QA048のweb_receipt_references、固定cleanup function、明示Web/backup/batch権限は旧migrationを書き換えず実末尾の次versionでappend-only導入する。SS331 §9.4の3列・制約・index・PUBLIC禁止・権限負試験、backup manifest/inventory・一貫restore・cleanup callerを同変更として追跡する。Webへ業務schema権限を与える回避策は禁止。旧appへ切戻しても新tableを即DROPせず、業務側DBを正としてlocator欠落/孤児を現在API検証で拒否する。receipt値から業務質問を再生成しない。

QA049はsession暗号化内部JSON current write v2/legacy read v1とし、NKENC1/AAD/DDLを変更しない。v2書込み後にv1専用旧readerへ切戻すと、そのreaderはv2を正常復元できず既存fail-closed処理で失効し、利用者の再Loginが必要となる。切戻し前に影響session件数・reader/writer version・残るoperation tokenと業務側既存確定結果を確認し、v2からv1への完成印抹消やpending偽装で回避しない。業務Inbox/UKを削除せず、自動新token再操作をしない。混在reader/writerによる完成印喪失がない配備/切戻しを隔離PTで検証する。

QA050は2026-10-03に15分継続再試行とIT/ST性能問題時の間隔変更を利用者が承認した。期限NULL・保持/警告・旧revoke鍵保持はSS314/331の確定条件へ反映し、実装/DDL適用/PT/IT/STとWeb full readinessは未完了として管理する。

## QA-050承認反映：期限NULL migration・間隔調整（2026-10-03）

pending_context_revocations.expires_atのNN解除は旧migration不変・実末尾の次versionでappend-only導入する。既存暗号row/attempt/claim/lease/index/grantを保全し、未確認期限を8h等で補完せず期限だけの自動DELETEを停止する。nullable未対応の旧reader/cleanupへ切戻す場合は互換性と残row保全を事前確認し、NULLを推測値へ変えたりrow削除/旧鍵廃棄で回避しない。初期5秒/30秒/5分と継続15分で実装し、IT/STで性能問題が確認されたら利用者の承認方針内で間隔を調整する。変更値・測定根拠・対象設定/source・反映/切戻し手順、失効確認遅延への影響を記録し、同条件再試験後にUI/SS/台帳とmainの確定設計を更新する。試験前に根拠なく初期15分を別値へ変更しない。
# 設定file・directory・初期data・migration・切戻し設計

## SSC202 pending原本を保持した027→028限定移行（2026-10-06）
SSC202工具起動前失敗限定回収（BUG797）：参照子missing filenameの実exit2、SAVE/Ref/設定変更/start0を実証し、当管理Javaのboot/PID/ticks/Root/子0/専用DB/locksを現在値固定した場合に限りowned PIDへTERMし、消失・全peer/lock0・十Unit/kernel/全原値不変更を確認して別新scopeへ進める。回収は異常終了であり旧close正常化/一般UNKNOWN補修/業務Unit強制終了の根拠にしない。
SSC202同範囲起動前失敗（BUG798）：既知の署名base security取り違えが十Ref取得前に失敗しSAVE空/runtime空・全原値不変更の場合、固定child/parentのboot/PID/ticks/Root/argv/全task-childを認証して当child→parentのowned TERMだけで回収する。既DBidle TX期限後peer0は正常closeでなく、前後全原値・全peer/lock0と独立拒否再現を保存、新scopeへ別所有で進む。一般UNKNOWN・業務Unit強制終了・旧close正常化へ拡張しない。release原本Root:schubert0640と/etc配備Unit Root:Root0644は既署名profileのまま別検査し、権限を変更しない。
## SSC290 限定回収後の別fresh通常起動・同peer独立観測（2026-10-16）

QA047/BUG1332/YKT1098内の原因計測・新通常経路。対象7bb/PG3976/BOM0a409301/boot79aはSSC289回収で必要5stop/INVALID全33保全・別fresh独立post/全新scope正常が実0、元Root143/4152 actual255/4188 actual1は失敗のまま保全する。新通常起動は旧Rootの再送/旧run resumeではなく、別new-only予約と新run/cutoff/activation/epochによるordinary noargs一回である。元Root1800秒/既Unit期限・失敗逆順回収/全資源後条件を変更しない。現runtimeにはdirectory二だけで一回設定fileが不存在のため、不要な退役/Unit交換/reload/再配備をしない。

操作前に新十metadata Refと既host同inode排他を取得し、fresh current/source/BOM/全189署名/material/全32宣言/全24・原本Backup/鍵/native52/起動33・全Unit process/Job/kernel・DBpeer/advisory/flock0を既正常postと現在値へ束縛する。歴史原本WARNING10はdata-onlyで旧親正常authorityへ変換しない。新observerの実liveness/固定hash/同boot-sourceとquiescent frame、native52の私有copy/hash/容量、旧active不存在/INVALIDを確認し、同new-only一回予約/fsync/dirsync→再確認→正規systemctl start --no-block一回とする。既存予約・所有/応答不明では再発行しない。新INV/PID/元Unit deadlineから当親を捕捉し、Root→ordinary/同owner API-Web-Caddy/真正terminal/全24/全体seal・正規owned停止/native/別postを完了するまで通常受入れにしない。Main/業務期待値/署名済sourceを変えず、既3717/545/1643Main・署名/公開を理由なく反復しない。

独立observerのmanager transportは固定local system-busだけを使用できる。各読取は5秒の同一残budget、PID1/euid0/正規unique nameを前後認証し、そのunique peerの固定Unit object path/Unit＋Service interfaceから既18fieldを型検証・正規文字列投影する。可変state/ownerのcache・fallback・別endpoint・manager状態だけのreadiness認定はしない。全十Load/Refを保持し、元のkernel/argv/権限二読・manager sandwich・Root→ordinary捕捉・同parent/INFO/HTTP/owned socket/CA・hostname検証HTTPS200を全て維持する。元50ms観測周期/親deadlineを延長しない。逆順Unref/private bus正常返却後だけobserver正常閉鎖を記録する。

同transportの操作前資格は独立型/欠落/null/Job/path/owner変更/deadline/未知Unit反例、既oracle/loop AST同一性、PG4218の4 Unit×20回の全1440値が旧systemctlと完全一致・全原値/32宣言不変・両bus/十Ref正常である。測定は旧wall1.986779060s/CPU self＋child1.079296221s、新wall1.064313154s/CPU0.378011450sだが、旧Root timeoutの原因確定/新親成功を意味しない。設定を無断に緩和せず、具体的な原因は新同親の計測へ残す。

同source/boot/Unit INV/PID/start/argv/executable/Root UIDとpidfd生存を前後認証した新親だけに、既pg734/888型のJDK25 `jcmd Thread.print -l`を最大12個のnew-only sampleとして実行できる。親の元開始+1770秒未満に限定し、各jcmd20秒/host35秒の有限待機、親終了/異世代/不明なら不発行又は不受入れにする。heap/JFR/environment/VMflags/credential dump、signal/start/stop/Root偽装・延長を行わない。rawは私有0600、公開はbounded class/method frame/hash/所要時間だけ、内容値や秘密情報を出さない。sampleは診断のみで業務/PT成功やcoverageへ加算せず、失敗・未取得・欠測も保全する。

新工具の全emitted ABI/独立反例/静的0と同artifact固定、設計only main公開を新ordinary起動前に満たす。451/RD/UI/DIF/QA051finalは不変更で、品質・CHR・native CRC/session資格/正式PGPT/IT-ST完了とは別管理する。

## SSC289 旧SSH255・metadata-only retainerからの限定継続（2026-10-16）

SSC288の現cohortについて、元4152のSSH/host observerの真正終了はactual255であり143ではなかった。旧guest二管理者への一回pidfd TERM/terminalと旧PID・lock消失/全原値不変は別証拠として保存する。255を143又は成功/正常closeへ変換せず、255だけでguest停止成功と推定しない。元4188 actual1・Caddy既停止data・旧Root143も独立に維持し、未実施残5/独立postを補完しない。この段階以降はSSC288中の旧observer143固定要求を「真正actual255と別のguest二terminal/消失証拠」へ置換するが、通常Root/ordinary Unit/全新scopeの正常終了条件は変更しない。

4196 private6758d930bc6fb6b295274a05d4b58aba7b535909af8f263afe05f0ff43eecef6で認証したmetadata-only Python791348/t14602179/argvSHA172536db0a293878cb1780e85aa687b825c625a75a9d95fec914ecdf608d1520、PPid791346/session930、子0・単task、UID/GID/group0/元cap・NNP0、固定全5FDだけを回収対象とする。FD0..2は旧固定pipe12618427/28/29、3はlibffi.so.8.2.0、4はsystem-bus socket12616611で、各fdinfo/全9metadata/全byteと元値の同一性をfresh二読する。旧metadata Refの正常返却は不明、M/A/backend/advisoryは保持していない。元4152/4188/keeperをhotpatch・再起動しない。

新管理hostが既存同inodeの正規exclusive gateを取得し、別new-only root工具が新十metadata Refを保持して全189署名/material/32宣言/原本Backup/keys/native50/全24/33/runtime/残3ordinary本人DB両端・Caddy真正既終端を再照合する。固定retainerに限り既pidfd verify→耐久一回予約/fsync/dirsync→verify→通常TERM15秒→30秒以内PID消失を適用し、全旧lock/PID/原値を再確認する。sudo/host observer/VM/業務UnitへこのTERMを拡張せず、SIGKILL/forceunlock/DBterminate/resetfailedなし。

新十Refとhost排他を継続したまま、既資格4182の同byte partial6ae32eab/postc2acd4d2を別processで順次inspect→必要5stop/revoke→独立postへ実行し、各子のPID/source/hash/元終了値/ログ/一回予約を保存する。Caddy再stop0、既Unit期限と全189/全原値の各phase確認は不変。子の失敗・不明は自動再実行せず、外側の新metadata Ref/所有をUNKNOWN隔離保持する。stdout欠落/EPIPEでUNKNOWN保持を解除しない。全子の真正0/全新M/A・RODB・十Ref正常返却/全postを確認後だけ外側Refを正常Unrefする。旧metadata retainerのTERMを正常Unrefと報告しない。

操作前資格は同新artifact545bb84f5c6d58b9305ac4499a0f8afa916e2baee7dcba3c61547e1d30727cdbのPG4200 proof actual0/10:38:50Z/signals0/十Ref正常と独立3試験/全emitted静的0。設計only main公開後に一回recoverを許可し、証拠未回収だけで再演しない。QA047内の内部補足でありRD/UI/451/業務仕様/元Root1800秒/QA051finalは不変更。実残5停止/回収/独立post/native資格/正式品質は未受入である。

## SSC288 Caddy既終端・二管理retainerからの限定部分回収（2026-10-16）

QA047/BUG1341・1342/YKT1107・1108内の内部補足。SSC287の7bb/PG3976/BOM0a409301・boot79a・Root155272 timeout143 cohortだけに適用し、旧Root/旧工具4152の失敗を正常化しない。Caddyは旧INV a0c7fb91のinactive/dead/success/code1/status0・Main/ControlPID0/Job空・旧PID/kernel空を独立確認した既終端であり、観測だけを行い再stopしない。残順はWeb→API→Expiry→Artemis→Cleanupの必要5対象とする。

管理Java790010/t14181503/argvSHA ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2、親Python789928/t14180650/argvSHA c8c952de1cf05574e3fdcf5effc076e4aac73748367f49aac23f6cb6300e9fb6だけを旧retainer対象とする。fresh二読の全98/7FD・UID/GID/groups/cap/NNP・cgroup/session921・親子/全task・同source/executable/class/lib/全189署名entry/material・原本/全24表/Backup/keys/native/startup33・普通actor/TCP両端を照合する。JavaのM/A sole二FLOCKと各lock FDの同OFDをkcmpで認証し、未認証/余剰/不一致は操作しない。期限切れDBbackend/advisory0は旧close正常ではない。

新十metadata Refと同inode host gateのqueued successorを保持する。元host observer595379/t14277246/argvSHA7bfafc9766fc7469583dd5e760d92c745ef1e14708f53706bfce601b0c003248のsole gate所有を認証した上で、既pidfd verify→耐久一回予約/fsync/dirsync→verify→通常TERM→15秒terminal待機をJava→Pythonの二対象だけに適用する。Javaが未reapなら同start/旧PPidのzombie・FD0/lock0だけを許し、生存/異世代は不可。親TERM後30秒以内に両PID消失、全旧管理lock/advisory0、全原値不変を確認する。sudo/host observer/業務Unit/VMへsignalせず、SIGKILL/forceunlock/DBterminate/resetfailedなし。元4152の実143を元observer/manifestから回収し、正常終了へ置換しない。

metadata Refを切らず元host gateの自然返却・同inode継承を認証し、別new-only controllerのfresh M/A・batch RO/同peer・十Refによるinspect正常返却を先行する。Ref keeperは別post完了まで保持し、5対象の正規一回停止・真正terminal/普通native二file・canonical INVALID revoke/既全33保全・全新scope正常・別fresh独立post後に正常Unrefする。未知/ack欠落/終端不明なら新所有/証跡を隔離保持し、同操作を再送しない。実行中4152/frozen5fdbはhotpatchしない。

全32設定宣言の照合は既契約のExecStart/ExecStop path・argv・ignore_errorsおよび他全fieldを保持し、systemdが変えるstart/stop時刻・code/status/PIDを宣言同値比較へ混入しない。動的値は別の同世代真正terminal条件で省略なく照合する。普通poolはSS342のAPI最小2/最大8、Web最小1/最大2の範囲とし、各peerの固定role/app/本人両端socketを認証、停止済みroleは0とする。固定総数3・現在値だけの一般化・未知peer許容をしない。全署名189/原値/Unit世代を各phaseで再確認し、当source native CRC/session・coverageは後続独立資格であり回収だけでは受入れない。

実証前提：PG4160全原値/宣言/98・7FD二読、PG4182同固定3artifactの実proof actual0・signals0・十Ref正常返却、独立14工具試験/静的0。これらは実TERM/5stop/postの成功ではない。設計only main公開を実操作の先行条件とし、RD/UI/業務仕様/Root1800秒/各Unit期限/451/QA051finalを変更しない。

## SSC287 failed-DONE現cohortの新所有による限定正規回収（2026-10-16）

QA047/BUG1332/YKT1098の内部復旧補足。SSC286と同じsource7bb/PG3976/BOM0a409301・boot79a・Root155272/Inv820851b8/run dc0cb75f/actd9d58371に限定する。元PID1 Starting→JobFailed、Unit timeout143・1800.068969秒、原本.doneWARNING10/ca7829dbを独立に照合し、旧Rootの正常terminal/真正DONE/closeや停止権限を合成しない。元Root/Backup/ADMIN/配備/公開/reload/VMを再演せず、元Root30分・各Unit期限・451は不変更である。

新管理者の固定工具はM→A・専用batch RO transaction/71419602/heartbeatを実際に保持し、同DB peer/両端socket・本人PID/start/argv・両実lock FDを認証する。十metadata Refを保持し、fresh boot/current/BOM/全187署名・全32設定/Unitfile・全24表・原本Backup/credential/旧proof/nativeと、現API758821/t13004447/Inv c9444dbf、Web759868/t13005817/Inv af0eb750、Caddy761848/t13009050/Inv a0c7fb91、Artemis714533/t12903932/Inv9cb091b8の完全な元certificateを二読再認証する。NSS/UID-GID-groups/全cap0/NNP1/cgroup/task/FDとDB普通app二・web一を新管理接続と区別する。固定署名/source/所有・全原値/Unit宣言は各phaseでも再照合する。UNKNOWN/余剰owner・peer/旧Root再生存/異世代は操作しない。

実start順Cleanup→Artemis→Expiry→API→Web→Caddyに対し、必要な逆順を **Caddy→Web→API→Expiry→Artemis→Cleanup** に固定する。各対象は実現在世代と新所有のverify→root私有new-only予約/全write/fsync/dirsync→verify→通常systemctl stop一回→同世代真正terminal/kernel全空・旧PID消失/所有再確認→耐久結果を必要とする。既inactive正常Backup、未実行Inspector/Adminへ不要stopを送らない。既終端/予約済み/途中不明の操作を無条件再発行しない。Caddy/oneshotの既正常terminal条件、ordinary API/Webのcleanup完了→process stopped→native完了journal/同PID-UID-boot-inv・普通143の停止data条件、Artemisの同世代/vendor AMQ221002 stop条件を再利用する。API/Web普通143は旧Root143の正常化を意味しない。

native profileはSSC193/194・354の既契約のまま。固定agent **output=none,append=false,dumponexit=false** と同ordinary role/Invocationを照合し、vendor destfile/appendへ変えない。停止前には不存在の `ordinary-api193/<同INV>.terminal.exec` と `ordinary-web193/<同INV>.terminal.exec` の固定new-only二fileだけを当該Unitの真正停止後に許す。旧全nativeのmetadata/全byte/hashは不変、親directoryのinode/owner/mode/link等は不変、entry追加によるsize/mtime/ctimeだけ有限差分。新fileは実NSS uid/gid・0600/link1/noACL・同device/上限/実byte hashを照合する。header/native完了journalだけでCRC/session/source資格やcoverageを受入れず、別の独立資格を後続へ残す。

六対象の全正常停止、全24/原値、普通DB pool0・本人RODBだけ、同scope所有が成立した後だけ、Production typed StartupPermitFilesを使い当current ISSUEDをcanonical INVALIDへrevokeする。epoch.currentの固定keyは既SSC089どおり **cutoff_utc**、独立oracleはstateとpermit_sha256=-以外の全byteを保持する。既33entry（permit8/owner8/launch16/epoch.current）は保持、epoch fileの正規atomic replacementと親directory有限metadata差だけを許す。当cohortにはpermit-start.intent/service start.intentが存在しないので、生成・退役・owner/launch/permitの任意削除はしない。

新scopeのDB rollback/close・M/A・十Refを正常返却し、別fresh新M/A/RODB/十Refの独立postで同source/全187/32設定・全24/原本Backup/keys/旧native＋限定new二file/全33/INVALID・全業務Unit/kernel/process/DBpeer/lock・scope返却を再確認するまで回収受入れとしない。未知・close失敗は隔離/新所有保持、SIGKILL/DBterminate/forceunlock/resetfailed/期限延長・原本書換・旧成功の補完はしない。回収は旧失敗の正常化でも次のRoot起動許可でもない。最終全emitted ABI/独立反例/同artifact readonly実資格を操作前に満たし、操作/別post/実装PTの完了は台帳で別管理する。RD/UI/業務仕様は不変更で新QA不要。

## SSC286 failed-DONE・普通四actor保持時のreadonly費用測定（2026-10-16）

BUG1332/YKT1098・QA047既承認内の内部診断補足。対象はsource7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976/BOM0a409301、boot79a3260a、Root155272/Inv820851b8/run dc0cb75f/actd9d58371のtimeout143と、真正原本.doneWARNING10が共存する現cohortに限定する。4052 private732bec2c…c6da6はdata baselineであり権限ではない。SSC266の旧DONE無し/soleArtemis、正常親専用4042の条件へ当状態を仮構成しない。

新管理profileはM→AをProductionの固定inode/host-private契約で保持し、実batch専用RO transaction/71419602 advisory/本人backend・TCP両端・heartbeatを認証する。独立observerは十Unitのmetadata Ref、全状態/32設定/Unitfile bytes、署名187/current、全24表/原本Backup/credential/旧proof/nativeを前後二読する。普通API app二接続/Web web一接続は同ordinary PID/start/argv/Unit世代とclient/server各socket inodeへfresh再結合し、DB総client0や古いbackend番号を要求しない。未知/余剰peer、原値不一致、lock競合、期限/close不明では測定を受入れない。

当固定Javaはcaller入力を取らず、保持M/A・RODB内のMaintenanceRunFiles.Session.observeStartup二回（全graph同値・固定activationとWARNING10）とverifyRetainedの費用・実metadata呼出数のみ計測する。設定/原本/DBの書込、permit/epoch/intent操作、サービスsignal/Root再start/reload/配備は0。所有返却はDB rollback/close→M/A正常返却、observerによる本人DB/advisory/flock消失・同四actor/全原値不変→十Ref正常返却を確認する。UNKNOWNをnormalへ補わず、実close不明は隔離する。数値は診断だけで、親正常完了・業務受入・native coverage・回収許可ではない。30分budget/全fresh proof/451/RD/UIは変更しない。実装/PT・新停止profileは別の未完事項である。
