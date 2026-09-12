# NK-BAT-001 backup manifest横展開・独立期待値

PG165/SSC058、BUG182/YKT143先行9447f481、BUG183/YKT144先行d4c89df4。実装・探索段階、正式認定待ち。実artifact/DB両step成功/親全体ではない。

## 1. BUG182/YKT143: 歴史timezoneの根拠と全対象

独立一次資料: [IANA tzdb asia](https://data.iana.org/time-zones/tzdb/asia)（2026-09-13参照、Zone Asia/TokyoおよびJapan Rule）。1887-12-31 15:00 UTCより前のLMT +09:18:59、以後+09:00とJapan夏時間規則を使用する。SS341 6.4のAsia/Tokyoは固定+09:00とは異なる。期待値は一次資料のoffsetを手計算しliteralとして記載し、Productionや同じZoneId呼出しから生成しない。全UTC manifest timestamp自体は不変更。

| 対象／検索結果 | 修正・確認内容／非該当根拠 | 再発防止・再試験 |
|---|---|---|
| BackupManifest/BackupManifestValuesTest BAT182 | 誤った0001/1582名の固定090000期待3行を091859へ訂正。ProductionはSSどおりAsia/Tokyoで不変更 | LMT3日・1887遷移直前/直後・1948夏時間・1952標準・9999年境界を独立literal化 |
| BatchStepAttempt/MaintenanceActivation | 既存businessDateに固定+09変換なし。既存現代/上限期待は正当 | BAT134既存temporalContractAndBusinessDayへ1582-10-04T14:50Z→10月5日を両型で追加 |
| BatchRunRepository | Asia/TokyoのSQL業務日・Java bind。旧歴史fixtureは00UTCで同日という正当な期待、誤+09名前なし | BAT146既存historicalUtcAndFixedRunDayへ同1582T14:50Z→10月5日の独立SQL行を追加。全10時刻×3timezone再試験 |
| JstWireTimestamp | 既存Asia/Tokyoの17桁。上限/拡張年拒否を変更しない | PRO003-T03へ15821005000859000の独立LMT encode/parseを追加 |
| ScenarioFileWriter/TransferStartupProbe | 既存LocalDate/Asia/Tokyo、現代9月日付と年幅検査。歴史時刻へ固定09:00の時分を置く箇所はない | 既存ScenarioFileWriterTest/TransferStartupProbeTestを全reactorで再試験 |
| API LogVectors/UserQueryReplay/UserMutationReplay、RunReferenceBoundaryTest | 明示Asia/Tokyo fixtureまたは現代日時のwire/業務日を扱う。今回の全年代固定offset誤りではない。既存期待を書換えない | 各既存PTの全reactor回帰 |
| WebSecurityAuditTestのZoneOffset.ofHours(9) | 現代2026年のfixed Clock zoneであり歴史wire期待ではない | 同既存PT回帰 |
| その他srcの0001/1582等 | UUID/番号の0001一致は時刻対象外。JDBC UTC歴史ベクトルはPG160の独立SQL、地方名の時分ではない | PG160/PG164の6日×3zone等は全reactorで維持 |

検索はrgで全src *.javaのZoneId.of("Asia/Tokyo")/ZoneOffset.ofHours(9)、歴史date/命名/DateTimeFormatterと各呼出しを確認した。単なる検索件数で完了にせず上表の根拠・追加試験と正式回帰を必要とする。

## 2. BUG183/YKT144: 固定LFとformatter

| 対象 | 是正／非該当根拠 | 品質確認 |
|---|---|---|
| BackupManifestCodec.encode/STRUCTURE | format本文から末尾LFを分離、出力へ固定LFを直接concat、構造regexにも固定LFを直接追加 | 965byte固定SHA256、CRLF/余分LF/改変/unknown拒否、全分岐/static |
| MaintenanceRecordsほか永続codec | 固定LFの直接連結、String.formatやplatform %nでない | BAT038～045ほか既存独立golden、全reactor |
| TypedFieldValues.requiredInstant | String.format %017dのみで改行なし | Protocol全PT、static |
| ScenarioRepository.search / OutboxJmsSender | %02d/%03dのみで改行なし | API全PT、static |
| JstWireTimestamp.formatという検索一致 | メソッド名一致でString.format呼出しではない、DateTimeFormatter使用 | Protocol全PT |

全ProductionのString.format/formatted/%n/固定LFを検索し、実formatter3既存＋新codecと偽一致を個別分類。platform %nへ変えてprotocolを変更したりsuppression/coverage除外で回避しない。

## 3. 独立byte/全境界

実装前の035手書goldenは965bytes、SHA256=733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e。独立3file量1/512/200→713、設定量712。最大許容長vectorは1873bytes: 7token各128、schema3、id各12、attempt各2、size各19桁（3074457345618258602/同値/3074457345618258603で合計Long.MAX_VALUE）、固定UTC6/UUID/hash。4096は受信上限であり1873超を正規JSONとして受理する意味ではない。

BAT188は965の全byte位置×tilde/NUL/非ASCIIの2895改変を拒否。BAT189は数値/UUID/hash/date aliasとdate自動補正、BAT190は全可変fieldのNULL・構造unknown/duplicate/missing/order/escape、BAT191は0/1/4095/4096/4097 byteと境界null。BAT192はbyte所有、BAT193は64並行・返却array独立。token/size/時刻/両完全handleを033の値8 PTで検証。digestは申告値であり実file hashの証明ではない。

実traceはBAT186のProduction encode実値をgolden照合した後にtarget/backup-manifest-tracesへ保存する。020 collectorと019 canaryは別の固定literalで照合しfixtureファイル自体も固定値と比較。全27 Batch test class=18 Program/9 OPS、Batch263=Program193+OPS70、API側のOPS24は重複加算しない。新16 Test IDの全位置欠落/未知/重複/失敗/skip/flaky等を負canaryで拒否。15collector/38scopeは不変。

## 4. 探索実行履歴（正式source認定には流用しない）

- explore1: /tmp/pgpt-manifest-explore1.log、06:21:51 JST終了、11.646秒、exit1。新16中failure1（BUG182）・他15成功、Storage8成功。全合格としない。
- explore2: /tmp/pgpt-manifest-explore2.log、06:23:48終了、21.536秒、exit1。Batch32/Storage8 PT成功、static1（BUG183）で非合格。
- explore3: /tmp/pgpt-manifest-explore3.log、06:26:14終了、36.131秒、exit0。Batch48/Storage8/Protocol4成功、新4class/18method/134line/50branch missed0、選択3module static未解決0。raw探索は正式08ではない。
- 019 canary31と017別1、計32件が /tmp/pgpt-manifest-canary1.log /tmp/pgpt-manifest-canary017.log でexit0。最大長1873補強後の選択再試験と全module正式回帰は別に記録する。
- explore4（最大長補強後）: /tmp/pgpt-manifest-explore4.log、06:33:00 JST終了、20.211秒、exit0。新16/Storage8成功、新4class/18method/134line/50branch missed0、選択static未解決0。020の独立16method inventoryと実BAT186 traceを直接照合PASS、golden resource SHA256不変。01931＋0171を /tmp/pgpt-manifest-canary2.log /tmp/pgpt-manifest-canary017-2.log で再走exit0。利用枠残41%、全reactorへ進む。

環境421 Java25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0/Ubuntu26.04.1。sourceはdev-foundation、親d4c89df4上の未commit候補。全正規run/targetCommit/OS/JDK/command/日時/exit/coverage/static/BUG/SSCとinput-output hashを017/evidence/manifest.jsonへ確定するまでBUG182～183/YKT143～144は未完了。SS058も実manifest値契約の範囲を超えてbackup全体完了とはしない。
