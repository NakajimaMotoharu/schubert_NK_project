# 313 NK-OPS-001 初回cold・fresh Broker証拠

2026-10-03 JST。RD SYS004/MQ/OPS009、UI251/253、SS341/343 SSC131132/165166、BUG532/533、YKT377。旧停止結果の正常化・初回coldを旧成功とする改変はしない。

## 対象・独立oracle

MorningPreviousBroker.capture/collectForStartup/NoPrior.recheck/Closed.recheck、MorningBrokerExecution.executeの2readiness callback、MorningProcessMain末段/issuer、MorningGateEvidence.stop、固定tmpfiles。旧4 STOP golden・旧journal goldenは不変更。

| Test ID | Fixture・入力/操作 | 期待値・独立根拠 |
|---|---|---|
| ISSCOLD001 | public18field cold、固定全boot read空2回。旧normal/BOOT historyも選択 | NoPrior別型・boot一致/read2、旧経路はClosedかつ1/6実read。架空Summary/receipt無し |
| ISSCOLD002 | 空→空白/非空/JSON、partial code/status/Result、IO/unknown/error/null/4MiB超過/live baseline | 拒否・unknown同一throwable・取得済buffer全消去、empty成功fallback無し |
| ISSCOLD003 | typed Liveのfresh7、独立startup3event、callback2回→末段再読、null/別thread | journal full無filterコマンドのliteral一致、intent退役前に両検査、後段再検査、別thread拒否 |
| ISSCOLD004 | 独立fresh golden＋遅延旧6、foreign6、prestart、error、重複、surrogate、2回目だけ旧6追加 | 拒否/retained、intent退役0。Productionでexpected生成しない |
| ISSCOLD005 | actual Live previousが別baseline、fresh lawful append | mismatch時read追加0、同fresh世代の正当追加は再検査成功、全buffer消去 |
| ISSCOLD006 | 実型8Unit snapshot、公的固定kernel present/absent | 独立既存UNIT/KERNEL literalに新 `NO_PRIOR|BOOT_JOURNAL_EMPTY|2|0|0` を追加した2保存goldenとのbyte一致。oldInvocation/start/end/upper/digest捏造なし |
| ISSCOLD007 | 保存旧6のClosedとfresh7型Live | 旧generation再読は従来通り成功、旧全content改変拒否、null拒否 |
| PT-OPS-LOCK-008 | 固定tmpfiles全行literal | expiry-requestを含む固定4namespace/new-only/boot-only、lock f!維持、既存lock置換なし |

## 実行・認定

PG429修正版full：Source `c3d9a3bdd5f5d3ad3ba8d0ed96e6816f7ca40bfd`、2026-10-03 01:46:37 JST/15m54/exit0、2898PT/438suite/FES0/static6zero。全6manifestSHA `98e810528f10f7c7f61299e73ee1e55f9df3150e48683e7927ccdfddf412eaed`、logSHA `c7138c12c409a16e340e08de92b64799135b94b503cb32ba387a728eaf839bb2`。host miss B1230/L3467/M564/C39、Source352比+2/-1/-1/0。NoPrior型本体のmiss全0、collectForStartupの3guard分岐とClosedの2branchは下記追加8で確認する（旧capture/nativeは別未達）。署名PG429181artifact/manifest39983 SHAade367a4は原署名成功後fullBOMが新tmpfiles layoutを拒否、BUG536/SSC167へ先行起票、currentPG428/permit0不変。実NoPrior/freshBroker/親ready/Webは未実行。

ISSCOLD008追加（PG430同契約）：独立18field literalの部分cold Invocation/start/endを新旧collect双方で拒否しquery0、保存Closedの別thread/query0と追加の有効旧entryによるentries相違を拒否・buffer消去確認。旧golden/期待値は変更しない。

PG429初回full（Source075a864d8）は2026-10-03 01:28:04 JST/exit1、Batchの追跡Javadoc改行をspotlessが拒否。5module成功を新Source合格へ流用しない（BUG535/YKT378）。新Sourceの実結果はfresh全6後manifestを正とする。BUG533 negative/BUG534 sealed cast是正は新7PT・旧golden・static0で再試験し、BUG526全callerをYKT379で横断確認する。

開発選択v4：2026-10-03 01:16:02 JST、89PT/14suite/FES0、SpotBugs6module0、strict compile/format成功、終了0。logSHA `07e4b820173743003d685436b1c86fc24e81f501bd3c19307c5ef260500f184c`。後続追跡commentだけ更新後、全6 fixed-sourceで改めて確認する。v1 exit1 no-tests、v2 1failure、v3 PT成功/static1は合格扱いしない。

開発選択は実在6module suite群（FieldCodec/LinuxSealedProof/FixedServiceIdentity/TransferRootInspection/WebProcessMain/RootStartupContext/MorningServiceReadiness/MorningStartupLaunchOwner）へ上記群とMorningPreviousBroker/StopEvidence/BrokerUnitCycle/MaintenanceFileLockを追加する。`failIfNoTests`は無効化しない。v1 no-testsとv2 wrong-negative失敗logはprivate保存し合格算入しない。source固定後451所定の全6 clean/format/testCompile/PT/静的6/coverage/jar/runtime BOMを実施し、同source署名候補を正規配備後に通常Morningを一度実行する。

次外部観測は同保存原本・元親30分/各Unit期限でNoPrior実2空read→freshBroker全journal/intent退役前検査→正規issuer→captured Root/ordinary API same-peer ready→API保持Web起動。Web unassembled/Caddy/保持原本DONE/intent正規退役/native ordinary coverage/CHRは未完であり、本試験だけで親0/正式100%を宣言しない。全scope正式認定はrun24/1964PT/53scopeのまま。

環境：Linux host、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0/既存strictNullAway。対象commit、command/hash・集計counterは `evidence/provisional/PG429-full-cold-broker/manifest.json` の実収集後結果を正とし、未存在時は未実行。native旧Source結果を加算しない。実行日時/branch/source/exit/FES/coverage/BUG/SSCはmanifestへ集約、raw journal/認証情報/privatelogはGitへ入れない。
