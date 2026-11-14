# 音声link結合・独立20仕様

NK-MIG-001/MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC355、WBS-P01903.02。

SS34310.1.4・SS331/V002・UI2424.4/4.5のaudio_files/entry_audio_links整合を、bootstrap.migration.AudioCopyDatasetに具体化する。RD MIG-DAT-001/MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI227/242/254、WBS-P01903.02。constructorは検証済みScenarioEntryCopyBatch、AudioFileCopyRowのList、宣言link六field ListのListだけを受ける。既Row/Batch/Writer/codecの全byteと既外部値を変更しない。実Current/素材採取/全件数/ID対応の正当性・実DB/COPY SDK/Rootnative/全ETL/HOLDは別未完。

audio_filesの全id一意と(game_id,storage_relative_path)一意を確認する。Entry batchのimmutable id/gameを索引とし、link全行のentry_id/audio_file_id/game_id/link_type/display_order/created_atの順を固定、六列以外/null fieldを拒否。二IDはcanonical正N12、game1/2、link_type voice/se/bgm/otherだけ、display_order canonical1..999。entryとaudioの各参照先が存在し、それぞれgameがlinkと一致することを要求。PK(entry,audio,type)とUK(entry,type,order)を両方確認。同一entry/audioを別typeで持つことは許容する。orderの有限domain1..999とUKにより各entry/typeの件数<=999を構造的に保証するため、重複する到達不能なcount>999 branchは作らない。999行正常と1000行の不正order/重複を独立fixtureで検証する。

created_atはcanonical UTC Instant・0001..9999/µs、entries/audio/linkの全時刻が一つに一致する。空・audioのみ・entryのみを許容するがlinkだけの未知参照は拒否。宣言audio/link順はそのまま保持し、IDやlink orderを再採番/正規化/補完しない。private list snapshotと深いlink snapshot/変更不能getterを返す。Audio/Entryの必須fieldはfinal constructor確立済みのinvariantからのみ読む。null batch/list/list要素/row/fieldは固定IAE、toStringも固定redactedで実ID/path等を出さない。

writeAudio(writer,sink)/writeLinks(writer,sink)は既PostgresCopyTextWriterへ各rowを渡す。audioはfields参照Listだけを集め、全COPY byteを追加保持しない。Writer/sinkは借用、null writerは固定IAE、null sinkはWriterの既固定IAE。IOExceptionは同一instanceで伝播、close/flush/commitせずpartial prefixは残り得る。transaction/公開/DB成功とみなさない。

PT-MIG-AUDIODATA001..020: 001手書きaudio/link二stream全golden、002両空/空entry/audioのみ/entryのみ、003audio id重複、004同game path重複/別game許容、005未知entry/audio、006entry側game不一致、007audio側game不一致、008六field/二N12/game/type/orderのgrammar/null、009PK重複と別type許容、010UK重複、011全row共通時刻、012link時刻UTCµs境界/形式、013null入力collection/要素/row、014深いimmutable/alias/宣言順、015二借用stream/null writer/sink、016二経路IO障害同一instance/closeflush0・再呼出、017999境界/1000不正、018input再順序の宣言順保持、019finite8worker64task/Future5/finallyshutdownNow-await10の独立golden、020redaction/拒否後独立正常。

Entry必要whole72＋AudioRow16＋Writer12＋新Dataset20=whole120、全9Main17physicalを同source/単一exec/Root通常静的/NullAway/lintWerror/独立CRC-init/XML/四100/実Code差で照合する。新20だけを定義数に加算、必要支援は旧成功の確認再演/別source合算0。追加不足1.75/5.25/10.5未較正を詳細+PG20 1.1/3.3/6.6cap7、必要normal120 .65/1.95/3.9cap4へ分離する。元費用/SV上限保持、専有費/実token null。小metadataとメモリsinkのみ、実DB/全ETL/全451/ITST/HOLD解除0。
