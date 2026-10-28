# Scenario最大snapshot純memory・単体テスト仕様

群SCENARIO_SNAPSHOT_MAXIMUM_MEMORY_ORACLES3_V1/event2780、主担当WBS-P008-05は元logicalのScenarioDetailSnapshot実rowで確認。原2/5/9pp cap10、新窓used1残99/reset1793774153・次点検5/残10新規停止、source42ae/save94c0a5fbfからMainを変更せず新whole Test一つ/3methodを追加する。

SS332§4.2は音声展開後最大10,000recordをimmutable snapshotへ取得し、その後にfileを書く。SS333§3～4は最大10,000/record4,800byteと、全件sequence及び各recordのbyte検査をI/O前に要求する。Main ScenarioDetailSnapshotはJDK immutable list/純protocol codecだけ、DB/query/file/Native/Root権限を持たないことを本文で確認した。package persistenceというだけでDBを実行せず、実DB/保持snapshot/原本/Backup/鍵/VMへアクセスしない。SCNRSP01のmetadataは既型のINLINE・file項目なしを固定fixtureにし、snapshot以後の201件FILE切替や4,800byte書込み/実readbackを本試験の成功へ加算しない。

| Test ID | 新しい入力/操作 | 独立期待・根拠 |
| --- | --- | --- |
| PT-SCN-SNAPSHOTMAX-001 | narration/音声なし、Entry ID/sequence/line1..10000の配列をsnapshot化、その後caller list変更・clear | size10000・先頭1/末尾10000と本文固定値を保持し返却list変更不可、metadataは元immutable値・toStringはrecordCount10000だけ。SS332 immutable/最大許容 |
| PT-SCN-SNAPSHOTMAX-002 | 同じ10000fixtureのprefixを越えた中間/末尾でEntry sequenceだけ飛ばす | LayoutValidationExceptionで全件の連続sequence検査を拒否、caller入力不変更。先頭/最後だけの検査では満たせない位置を固定 |
| PT-SCN-SNAPSHOTMAX-003 | 第10000recordの本文だけSCNRSP01本文上限4096byteを1byte超過 | FieldEncodingExceptionでSnapshot公開前に拒否、先頭9999件が正常でも末尾byte検査を省略しない。ASCII length4097は独立入力上限 |

原ScenarioRepositoryTest（DB同居）にはnull/10001/FILE-modeの既ケースがあり、これらの抽出・複製や元wholeの実行はしない。ScenarioQuerySnapshotのnullケースも旧Request whole内にあり新規化しない。今回の最大許容/長list中間/末尾フィールドという未追加oraclesだけを新しい独立wholeへ作る。fixtureは公開固定数値/合成文字列で、expectedは1..10000/明示位置/固定本文・ASCII byte数/SSのsequence定義から作りproduction methodでexpectedを生成しない。

実行は新source固定→正常六compile一回/NullAway/format→新whole3/一suite専用JVM240/heap768MiB→局所PMD/CS・六SB→同一exec/XML/CRC/全artifact/全1843Main・全旧1972Test同byte/新一を独立照合→Program008/trace索引。APIの実行probeはSnapshotと新Testだけ、protocolは既review済み固定codec/value closureに限定、全persistence query/DB/JMS/Graph9/VM/Root/native/実FS・保留二工具0。未測定counterは未測定のまま、旧successや別sourceexec合算0、全451/正式1964-53/17-190/工数null/QA051finalを変更しない。結果/実測/未達/Source・hashは2415へ保存する。

## 2026-10-28 BUG2025/YKT1773・期待例外の層訂正

初版002のPermanentProtocolException/003のMessageEncodingExceptionは取り違えであり、source0a8485983の13098は1成功/2失敗・actual1のまま保持する。SS322§11にbyte超過はFieldEncodingExceptionと明記され、immutable semantic validatorの既layout契約はLayoutValidationExceptionであり、receiver/JMS body異常やwhole-message registry異常とは別である。既FieldCodecTest/semantic validator既契約とも照合済み。input/数値/byte期待/拒否要求を緩和せず、Main/上位仕様を変更せず二つの強い正規型へ訂正する。元Test全文はPG13100、初版の当仕様全文/hashはPG13101-snapshot-spec-original-v1へ保全し、元誤記・失敗を消さない。訂正後は別source/runの全3で再認証し旧成功一件も新sourceへ流用0、追加source再認証1を元群の手戻りとして記録する。
