# NK-DAT-001 全Inbox候補・限定削除SQL単体テスト仕様書

## 1. 対象（V010実装前）

V010予定: maintenance_lock_inbox_backup / maintenance_next_inbox / maintenance_delete_inbox、列grant。NK-DAT-001/MQ-008/OPS-009/DAT-009、UI212/241/251、SS324/331 §3.6/352、QA-046/UIC-006/SSC-049/PG-D-124/BUG-014/YKT-012。結果016。SQL単体は暗号・業務参照検査の証明ではない。独立の公開synthetic body30byte（復号不可）とJDK SHA-256、literal UUID/SQLSTATE/DB後条件、production DDLの隔離PGを使用する。

追補PG-D-139/SS331 §3.10: V015の4照会をPT051のROUTESへ追加し、同じNONE/全5型付きref/owner/token/24h/SQL guard行列を28routeで実施する。拒否routeはQSB/NTC/QDL/ZZZ。既存24routeの期待値は不変。新照会暗号/Java接続・独立goldenは041/PT161～168へ追跡し、SQLだけで復号合格とはしない。

## 2. Test ID（初回仕様の履歴、最新結果は016）

| ID / method | 事前条件・入力・操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-049 / catalogAndColumnCapabilities | V010適用、各roleでcatalog/実SELECT/EXECUTE/DML/SET ROLE | owner/definer/search_path/UTC固定、検査roleに2公開functionとUser2列/Scenario2列だけ。helper/password/他列/任意DML/他roleは42501 |
| PT-DB-INBOX-050 / candidateOrderStateAndUnknownRoutes | 複数COMPLETED/ERROR/PROCESSING、未期限・同cutoff・unknown route、cursor | 最大1 UUID順、unknownも候補だが削除false、PROCESSING/未期限除外、cursor後だけ、最後0 |
| PT-DB-INBOX-051 / canonicalRoutesReferencesAndTokens | 24 REQ/RSP対応、各owner/token/ref許可と不許可、state/version異常 | canonical対応とSS331形態だけSQL削除可、各typeの不整合/7未実装応答/未知routeはfalse、他table不変 |
| PT-DB-INBOX-052 / exactRetentionCutoffAndReplay | query24h/更新168h、±1µs、UTC/JST、全有限/無限日時、created/completed順 | 最短保持未満・cutoff同値保持、正当期限削除1、rollback復元、再走/既削除false |
| PT-DB-INBOX-053 / argumentsHashAndTransactionBinding | NULL各引数、無限cutoff、hash31/32/33、同/別Message、同/別xact、暗号文変更 | 22023/falseの明示表、古いhash/xact不可。SQLがpublic synthetic cipherを削除できても暗号証明と数えない |
| PT-DB-INBOX-054 / referencesStayLockedUntilTransactionEnds | AUTH_SESSION/USER/SCENARIO_FILE候補、別connection NOWAIT update、存在/欠落 | 対象参照/Inbox/backupが検査TX中55P03、終了後更新可、非対象row更新可。欠落は候補返却のみ |
| PT-DB-INBOX-055 / backupGateAndSnapshotRace | 不足/別run/別JST日/終了なしbackup、advisory競合、待ち中別backup追加 | 55000/55P03、単一locked snapshotに両backupがなければ失敗、次TXで成功。全future期限付き回収 |
| PT-DB-INBOX-056 / migrationAndExistingAuthenticationRemainCompatible | V001～009hash、V010適用・再実行、既存認証SQL契約と新query対比 | migration10/再実行0、旧hash不変、既存認証の権限/168h/lock維持、Java検査/oneshotは別未完了 |

## 3. 証跡と合否

toolchain421、root clean verify/関連全PT、SQL全IF/WHERE/NULL/競合matrixを016へ追跡する。実行日時/branch/source/command/exit/環境/expected/actual/BUG/SSC/hashはsanitizeしたmanifestへ格納。Java4種coverage100%は全reactorで確認し、SQLへ架空JaCoCo値を付けない。failed/flaky/skipped/not-runは未完了、IT/ST未実施。
