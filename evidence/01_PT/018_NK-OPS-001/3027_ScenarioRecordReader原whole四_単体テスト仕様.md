# ScenarioRecordReader原whole四・単体テスト仕様

2026-10-31／PG-D968／NK-SCN-001、RD FIL006/007、UI234/237、SS322/323/333§6。Production6b53/normal14216/branchdev-foundation固定。群3369開始1/3/7共有pp cap10固定、3370で誤primaryP00903を元canonicalReader P00806へ追記訂正、例外共有P00904追加費用0・元event保存。原Test四件/一suite、Main Reader/IntegrityException二Sourceの全Code二を測定する。新source PT未登録・先行索引0を確認。

対象Main・Test・ScenarioFileFixture全文、呼出codec/semantic/recordの固定契約・既当source独立証跡を照合。独立Fixtureはproduction encodeを呼ばず、4800byte space基底にoffset0 ID12/12 sequence6/18 line8/26 type/164本文/4260 audio3をUTF8 literalで配置。SHA256はJDKから独立計算、実鍵/認証用途0。数値IP等なし。JUnit own TempDirの公開合成fileだけ、実業務store/原本/Currentbaseline/鍵/DB/JMS/network/VM/Root/native/Graph0。最大48,000,000byte・親JVM期限180秒・通常JUnit終了cleanupだけ、共有ファイル削除0。

Test ID：
- rd03GoldenRecordsThrough48000000BytesHaveBoundedBuffersAndImmutableOrderedValues：1/201/10000record、4800/964800/48000000byte、entryId50000-index/sequenceindex+1/line42/narration/本文/optional空をliteral照合。7byte分割でも最大buffer4800、二pass総読取2*4800*count、rewind1、caller channel保持、immutable。
- rd04NullNonfreshClosedAndExactLengthHashFailuresNeverCloseCallerChannel：null二・position1・閉channel・length0/4799/4801・SHA各32byte一bit差は各期待例外、hash先行でrewind0。
- rd04ZeroProgressReadSeekFailuresAndContentChangedAfterFirstHashAreRejected：ZERO/IO/EOF_ZERO/SEEK/SECOND_IO/MUTATE、全IOException/caller保持、MUTATEでrewind1/9600byte。合成失敗文字列は元fixture、raw実privatepathなし。
- rd04ValidHashesDoNotPermitInvalidBytesOrSequenceAndBadHashPrecedesDecode：reserved末尾、mandatory ID空、UTF8不正、非NFCはvalid hashでもPermanentProtocolException。sequence2 descriptorcount1でLayoutValidationException。元reservedに全0hashではdecode前FileIntegrityException/rewind0。

normalhash1d0a3dee、二Mainと原Test/fixtureのhashはPG15854固定定数、当normal snapshot/現src/当Jar closure完全一致を実行前照合。工具共有reporterの既12check proof参照・成功確認再演0。通常fresh Java25.0.4/JUnit13.4/JaCoCo0.8.15、fresh javac -proc:none -Xlint:all -Werror/固定6MainJar/依存、原4だけ選択。command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15854_scenario_record_reader_four_pt.py。

PG15856は当exec/CRC/session/XML/全Source四counter・四held/六native trueprobe0を受動測定、未達/private constructor等を除外せず正直に保持。PG15858独立oracle/全result/HOLD境界を照合。元4成功後は再演せず、scope/index/cost保存へ進む。未実行・Failed/flaky/skipped/not-run・代替reviewをPASSにしない。coverageは実測前未確認、NPE二negativeと静的normal14224を併用、全phase100宣言0。障害は修正前915/916。正式1964/53/17/190/工数null/QA051final・全HOLD維持。
