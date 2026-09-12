# NK-BAT-001 run退役単体テスト仕様書

SSC055/PG-D-161、先行4d534ba9、OPS-009/DAT-009/UI251/SS311/331/332/341/343 §6.16。実装前仕様。Program NK-BAT-001、MaintenanceRetirement/MaintenanceRecords/DurableRecordFiles/MaintenanceRunFiles.Session.retirementCandidates・retire。

Fixtureは隔離native inode/合成root属性と実PostgreSQL18.6/V018の借用batch connection。親OS lock実接続は別未完了条件。cutoff=2025-01-01T00:00:00.000000Z、latest=2025-01-02T00:00:00.000000Z、400日丁度=2026-02-06T00:00:00.000000Z、+1µsを成熟とする。期待recordは手書きASCII LF、digestはそのliteralへの独立計算で固定値化しProduction encode/readからexpectedを生成しない。input/outputはsynthetic UUID/timeのみ、実session/credentialを保存しない。

| Test ID | class/method | 目的・入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-090 | MaintenanceRetirementRecordsTest.literalMarkerAndPlanHash | 手書きNKRET1/NKDONE1 literal、独立SHA256、長さ195/204・count1/MAX・順序を完全比較 |
| PT-BAT-091 | MaintenanceRetirementRecordsTest.temporalAndCountInvariants | 400日丁度/+1µs、latest=cutoff/未満、年0001/9999、nano、count0/負/MAX、digest大小/非hex |
| PT-BAT-092 | MaintenanceRetirementRecordsTest.nullAndOwnership | 全constructor/codec引数null、caller byte非共有、immutable equality/hash/toString固定redact |
| PT-BAT-093 | MaintenanceRetirementRecordsTest.malformedMarkerBytes | 長さ0～205、全byte位置変異、高bit/NUL/CRLF/追加/欠落/空行を拒否 |
| PT-BAT-094 | MaintenanceRetirementRecordsTest.markerAliases | UUID大文字/短縮、時刻offset/閏秒/桁不足、+count/先頭0/overflow/誤magicを拒否 |
| PT-BAT-095 | MaintenanceRetirementRecordsTest.boundedStorageRecords | 実隔離inodeでmarker最大204/oversize205、全read/publish/remove・unknownruntime/close非成功 |
| PT-BAT-096 | MaintenanceRetirementRecordsTest.planNameBinding | plan/retireの名前と内容ID全一致・別UUID/別種record拒否、既存record契約保持 |
| PT-BAT-097 | MaintenanceRetirementRecordsTest.concurrentCanonicalRecords | 共有不変値を別threadでencode/decodeしliteral一致、互いの配列非共有 |
| PT-BAT-098 | MaintenanceRunRetirementTest.candidatesAndProtectedRuns | 空/完了複数runの順序・不変List、active/未完了対象保全、別run有効active/pending保全 |
| PT-BAT-099 | MaintenanceRunRetirementTest.strictAgeAndLatestCompletion | 最新終了採用、400日丁度TOO_YOUNG・+1µs成功、now年/nano/null、未来完了保全 |
| PT-BAT-100 | MaintenanceRunRetirementTest.referenceCombinations | 実PG V018、3参照全8組合せ、空だけ許可、PROTECTED副作用0、別run非影響 |
| PT-BAT-101 | MaintenanceRunRetirementTest.missingAndContradictoryIdentity | ABSENTは退役と区別、同UUID異cutoff/DBidentity不一致/孤立originalを拒否 |
| PT-BAT-102 | MaintenanceRunRetirementTest.newRetirementPreservesOtherRuns | 複数activationのdone→begin→anchor→plan→markerの限定順序、他run byte不変 |
| PT-BAT-103 | MaintenanceRunRetirementTest.preMarkerPlanRecovery | 部分plan/全plan・marker前中断、原本全graph再検査・同byte再同期・不足追加、part拒否 |
| PT-BAT-104 | MaintenanceRunRetirementTest.markerOriginalRecovery | marker確定後の各done/begin/anchor削除境界から回復、plan全数保持、消失対象同期 |
| PT-BAT-105 | MaintenanceRunRetirementTest.metadataOnlyRecovery | anchor/original0・plan部分/0から回復、残存original/別run plan拒否、marker最後 |
| PT-BAT-106 | MaintenanceRunRetirementTest.planCompletenessAndDigest | plan欠落/追加/不同byte/count/digest/最新終了不一致、正規UUID文字列順 |
| PT-BAT-107 | MaintenanceRunRetirementTest.namespaceAndForeignArtifacts | unknown/part/複数marker/複数plan対象/symlink/属性/途中graph mutationを保全拒否 |
| PT-BAT-108 | MaintenanceRunRetirementTest.referenceReappearanceAndDbFaults | 各mutation境界の参照復活/SQL失敗/identity変化、同borrowed connection保全 |
| PT-BAT-109 | MaintenanceRunRetirementTest.publicationAndDeletionCrashes | 各durable公開/unlink/sync後中断、再開の許可対象不変・part非自動修復 |
| PT-BAT-110 | MaintenanceRunRetirementTest.everyIoFailurePreservesState | 正常traceの独立固定call inventory各位置へIO failure、非成功/資源0/別run保全 |
| PT-BAT-111 | MaintenanceRunRetirementTest.scopeNullAndInterruption | callback/返値/引数null、初期/終端割込flag保持、NPE/runtime非正常化 |
| PT-BAT-112 | MaintenanceRunRetirementTest.concurrentAndClosedScope | 同Session直列化・close待機・閉鎖後拒否、別instance排他はcaller責務 |
| PT-BAT-113 | MaintenanceRunRetirementTest.resourceCloseAndDigestFailure | 6root/reader/writer/list全close・複合故障、SHA取得失敗固定化、cause/suppressed秘密なし |

全正常/境界/異常/例外/null/再実行/並行を実装と並行して検証する。line/method/class/branch100%、NullAway/SpotBugs/Spotless/全reactorを必須とし、skip/flaky/failed/not-runを算入しない。初期TDD未実装の失敗は障害扱いせず、実装済み仕様逸脱は915/必要時916を修正前起票する。コマンド・対象commit・日時・環境・終了code・coverage・BUG/SSC・manifest/hashは016とevidenceへ実結果のみ記録する。予定formal PT-WEB-20260913-04だが未実行のため合格認定しない。
