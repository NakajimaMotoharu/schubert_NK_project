# Speaker含む六表宣言master組立・独立仕様

NK-MIG-001、RD MIG003005006/MIG-DAT005/FUN004/DAT004/TST、UI223242254、SS311/331/V002/343 SSC364367368369。既MigrationCopyDataset五表API/byte/旧全Testは維持し、MigrationMasterCopyDatasetを追加する。constructor(Nullable SpeakerCopyBatch, Nullable MigrationCopyDataset)は両nullを固定IAE、SpeakerCopyBatch.validateEntries(content.scenario().entries())でspeaker IDとgame一致/共通時刻を照合し、さらに六表全行created_atを一つのSetで検証し最大一時刻を要求する。entries空でもspeakerとfile/audio/mediaの異時刻を検出する。空の六表は許容し、Current175件や名前導出・DB target空を推定しない。宣言ID/行順/値を変えずfinal深いimmutable二部品を保持し、speakers()/content()で同instanceを返す。新row/COPY実体の保持や全byte事前生成を追加しない。

writeAll(Nullable writer, Nullable speakers,files,entries,audio,media,links)は七借用引数全部を最初のwrite前に検証する。Speaker→files→entries→audio→media→linksの固定六stream順で既writer/各部品へ委譲、null引数時は六sinkに一byteも出さない。close/flush/commit/rollback/retry/driver/DB/socket/実master操作0。最初のIO/runtime/Errorを同instanceで伝播し、既送信prefixは保持し後続streamへ一byteも書かず、callerが正規rollback/discardを判断する。新diagnosticとtoStringは固定redacted、入力/例外/rowのlog0。Immutable annotationは既provided jsr305の同契約を使用、filter/抑制/依存追加0。

PT-MIG-MASTER001..020: 001六stream全literal golden/順/borrowed所有、002全空、003両constructor null、004未知speaker FK、005他game FK、006speaker-entry異時刻、007entries空speaker-file異時刻、008entries/file空speaker-audio異時刻、009speaker-media異時刻、010speaker空narration許容/対話拒否、011七引数各null前検証全sink0、012各六位置IO identity/prefix/後続0、013各六位置Runtime identity/後続0、014各六位置Error identity/後続0、015途中二byte IO prefixとcloseflush0、016immutable getters/保持元list変更隔離、017固定redaction、018拒否後fresh正常/副作用0、019game2と境界ID/共通µs/任意宣言順保持、020finite8workers64/Future5/finallyshutdownNow-await10。goldenはV002六表列順から独立literal、期待失敗/順/partialはmemory sinkから独立作成しproduction expected生成0。

新20＋必要既pure-data363=whole383、全22Main35physicalを一source/一exec/Root compile-NullAway-lintWerror/静的/全CRC-init/default＋無filter全Code四100で確認する。三つのJDBC staging96は依存しないため確認再演せず、原PG31676の証拠を参照する。新組立が依存するpure-data全閉包を必要回帰とし、元成功確認目的の再演ではない。旧24 migrationMain/既459Test定義sourceは不変。実Current/175/全原表IDmap/DB COPY/sequence/ANALYZE/全移行/Rootnative/CHR/global451/ITST/HOLD未受入。

不足追加1.65/4.95/9.9pp cap10はPG/独立20と必要383・補完全Codeを含む。metadata工具修正BUG2911は内包/追加費0、元費用・S/V・群開始値保持、実専有費/token null。既五表とSpeaker承認SSの内部接続具体化でRD/UI/DDL/権限変更・QA不要。
