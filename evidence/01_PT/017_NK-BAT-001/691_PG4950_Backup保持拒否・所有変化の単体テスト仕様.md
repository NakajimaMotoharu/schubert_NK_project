# PG4950 Backup保持拒否・所有変化の単体テスト仕様

## 2026-10-17 11:38JST fixture ABI是正・new-onlyPG4952

元PG4950 actualMaven1/qualification1を結果692へ保存、batch testCompileのGuard void lambda型誤り（BUG1395/YKT1161）。Production Main/設計は正しく変更しない。Guardの実abstract契約は`long remainingNanos()`、default`check()`が正の時間を検査するので、合成残1,000,000nsを返し実checkを通すfixtureへ是正、初期1＋四member各2＋post前1＝10観測を独立にassertする。Io三methodのNullable契約も明示し、nullstreamをNPEへ読み替えない。既期待4unlink順/未知byte/empty-only除去0/FD帰還は不変更。

新`tools/quality/pg4952_backup_retention_selected.py`/W`pg4952-backup-retention-selected-v1`へ固定Testsourceをnew-only保存し、全109/10suite・format-before-PT・実static・五methodcounter・三module全Mainbyteを同条件で再資格する。元PG4950の14部分を新109へ加算0、旧slot上書き/手動`-rf`/古いsource継続0。新harnessの実Guard宣言/long返却/10観測も独立3工具0、実PG4952はまだ未発行。

## 対象・正本・範囲

Program NK-BAT-001、WBS-P017-05（manifest/hash/commit/7世代prune）、BAK/BKO/OPS-009・UI251・SS341§6.3/343/SSC133/451、既仕様001/687/082と対応。対象MainはBackupManifestReader.retentionNames/retentionRoot/retentionDirectory、BackupArtifactVerifier.removeRetainedのpost-delete二callback。Production Source04bbdb73b532537e3546191d72dee913b17629a0/PG4860/BOM083・全3761/551/1647/当native10streams12pointは既資格の履歴として保存し、今回のTest追加を算術加算して全体合格にしない。

Main実装/SQL/DDL/OS authority/動作は不変更、既package内Io/security/clock portと公開合成archive・実Linux held FDを用いる単体試験だけを追加する。運用backup/root・実DB・VM/通常Root/既Bootstrap/署名を操作しない。read系拒否では内容/metadataを維持、削除系負試験はJUnit専用temporary childの固定四fileだけを実unlinkする。未知memberの保全と非recursive/empty-only除去拒否を検証し、実運用削除の権限をfixtureから推定しない。

## 独立入力・oracle・Test ID

Fixtureは既BackupArtifactFixtureの公開dump/config/ciphertextと手作りJSON。固定manifest SHA256 `bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370` は既独立vector（Production encoder/verifierでexpectedを生成しない）。`verifyWithin`の実返却はremoveRetainedへ渡す**事前条件の能力data**であり期待値ではない。削除名/順序・残directory・未知fileの期待内容とscope後条件は下表のliteralで独立に定義する。

| Test ID / method（BackupRetentionRejectionTest） | 事前条件・入力・操作 | 独立期待値・理由 |
|---|---|---|
| PT-BAK-4950-001 / backup4950001NonrootNamesCannotReadOrMutateTheBorrowedRoot | 合成euid1000でretentionNames(100) | UNAVAILABLE/causeなし、euid観測1/attributes・names読取0、四filebyte不変/借用root以外全FD・stream・channel正常帰還。最初のroot契約拒否。 |
| 002 / backup4950002LateOwnerChangeRefusesTheOtherwiseStableNames | namesの正常held読取後、第二euid観測だけ1000へ変化 | UNAVAILABLE/causeなし、euid2/openNames1/closeNames1、全内容不変/資源正常。前後同ownerが必要で、前半だけ成功でも返却しない。 |
| 003 / backup4950003NonrootRetentionMetadataIsNeverADeletionProof | euid1000でretentionRoot(100) | UNAVAILABLE/causeなし、euid1/attributes0、内容不変/資源帰還。root metadataを不正ownerでproof化しない。 |
| 004 / backup4950004NonrootChildClassificationCannotAcquireAnEntry | euid1000でretentionDirectory(固定DIR,100) | UNAVAILABLE/causeなし、euid1/openEntry0、内容不変/資源帰還。拒否前にchildcapabilityを取得しない。 |
| 005 / backup4950005MissingPostDeleteStreamRetainsTheDirectoryAndReturnsAllHandles | 合成有効admission後、固定四file実unlink後のpost-delete openNamesだけnull | UNAVAILABLE/causeなし/NPE0。実unlink順がdump→config→encrypted credential→MANIFESTの固定literal四件だけ。postcall1/empty-child remove呼出0、childは存在し空、全FD/channel/stream帰還。部分削除を全成功にせず原directoryを勝手に再作成しない。 |
| 006 / backup4950006ConcurrentUnknownMemberIsPreservedWithoutRecursiveDelete | 同専用temp childで最後のIo boundaryへ`public-foreign-member`/`keep-public\n`を一件挿入 | UNAVAILABLE/causeなし、固定四unlink後にpostcall1、remove呼出0、child/未知fileとliteralbyteが残る。未知fileを削除/recursive削除しない。実thread/VM並行成功とは別のIo linearization反例。 |

6件は正常制御の関連既存suiteと併走し、両側条件を網羅する。null streamは明示許可されたIo異常でNPEではなく固定例外を要求する。他のnull/欠落/空/unknown/サイズ/digest/再送/並行/close故障は既Reader/Verifier/Retention/Publisher/Codec/Commit単体試験の独立fixtureを関連回帰する。新6件だけでprogram全観点完了とはしない。

## 実行・品質・source区分

工具`tools/quality/pg4950_backup_retention_selected.py`、hostLinux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/GJF1.36.1/Spotless3.10.2/NullAway/SpotBugs4.10.4.0。新testをGJFで正規化済み。required reactorはstorage/bootstrap/batch三module、実suitesはServiceConfigFilesTest/ApiNonSecretConfigTest＋batch既存七suite/新一suiteの合計10、非対象moduleへのfailIfNoTests緩和0。全JUnit method名を固定snapshotから独立抽出しXML actualと一致を要求、F/E/S/flaky/rerun/not-runを成功に加算しない。

実commandはclean/push後`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes runtime> python3 -B tools/quality/pg4950_backup_retention_selected.py`一回。git archive固定Testsourceをnew-onlyW/pg4950-backup-retention-selected-v1へ保持し、三module **format0→全PT→freshJaCoCo→SpotBugs** の順。begin/owner(PID/start/argvSHA)/実command・env・終了code/XML/hash/Input不変・loghashを保存し、応答欠落を理由に再発行しない。formatter失敗はPT-not-run/actualMavenExit nullで拒否する。

MainSourceは現04bb、Testsource/操作HEADは新commitとしてmanifestへ別記し、三moduleの**全Mainclass inventory/byteを実3761/1647資格PG4846のphysicalSHAと一致**させる。Mainの不一致/欠落なら別Sourceとして拒否。target五method（reader三＋removeRetained二lambda）はline/method/branch各miss0、fresh静的三module0を実測後だけ限定達成とする。全program/class coverageや全scope同一run/四100・正式認定は別条件で、全体旧3761/715/146/9/442に新selected件数/counterを無条件合算しない。

着手前subset低.2/標準.7/高2共有pp（event1117）、主担当P017-05だけへ計測・依存module共通費再加算0/個別費N-Tnull。実Maven/新6・関連全PT/coverage/static/対象commit/公開manifest/BUGとhashは実行結果692へ後記する。工具scope/欠落/format順/Main/source/全staticnamespaceの独立3管理試験は成功、Production PT加算0。現時点で実選択PTは未実行、未完/失敗を成功にしない。
