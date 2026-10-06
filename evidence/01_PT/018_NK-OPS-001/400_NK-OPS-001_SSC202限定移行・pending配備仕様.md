# 400 SSC202 限定移行・pending配備仕様

2026-10-06 23:35 実限定移行受入：PG490-native-v2/session98243/hostSSH3967978は実exit0・10.67s、M→A→実batch DB/advisory→十Ref/全kernel・私有restore point正常検証→署名V028一件→既catalog/24業務table不変→profile schema一値→全新scope正常帰還→complete.private。ProductionSource38899a05b5c2daeecfc5af8ea5ae748e29954c60/候補BOM652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c、operator sourceは別dirty/hash記録（Production src/POM差分0）。before75966f…/after2def81…/正常receipt35f38e874196fd43304478bbe8c932ee58a7a888462a6069d874a772bcf80d62、restore dump97a9e9…はRoot私有のまま。公開manifest52e052814515479be6902fd13d88aa8d76068e149371eaac283785723d73bd11。新schema28SQL/SCHEMA含む29履歴/最終028・profile028、currentPG486/全432十四列/全24table・config（profile一値以外）/Unit/原本/Backup32/Transfer2/epoch不変更、start/permit0。一般復旧・旧UNKNOWN正常化・親全体/CHR/native coverage/正式/ITSTへ算入0。MIG202004～006の当固定native正常は確認、MIG202007 fault・008pending公開・009全親は未完了。

工具点検BUG795（profile ACL/metadata）・BUG796（旧role略称）を修正前起票、YKT566567、pinned旧primitive/既staged draftv1不変更。新callerへRoot:schubert0640/single-link/noACL/親Root非writeable・前後metadataを追加、実五business roleと専用ExclusiveLock/正常releaseを補足。host Java21/Python16+18+5計60独立assertions0、Werror0、guestv2 Java21 actual0、Rootprivate工具v2全byte/hash照合。現SRC/工具hashの実native正常まで証拠を分離し、旧36assertionsを新sourceへ流用0。MIG202002/003の固定境界・本正常所有は受入、任意fault全網羅・全工程は未受入。

Program NK-OPS-001、関連RD OPS009/OPS011・UI251・SS331/341/343/353、SSC200201202・BUG788/YKT562。対象は隔離PG/PT VMだけであり、IT/ST・正式合格を宣言しない。

## 固定事前条件と独立期待値

PG489-v1/source `a52a6274ebabb924838524671c00dd72c63ae806` は全体不合格（399/BUG793794）。修正後の新fixedsource PG489-v2でfresh全六module実終了0/XML FES0・source/JAR/hash・静的六module0を照合してから候補を作る。旧PG486 source2e017・BOM230c6174・schema027を旧署名と全artifactで認証する。新候補は旧V001～027全byte不変、V028一件のみ追加・独立CRC32/Flyway履歴一致、schema028・profileのschema一値delta。新profileを旧Backup manifestへ適用しない。

VMのboot/PID/Invocation/全Unit/kernelは実行前に現在値を再取得する。保存時のboot e07aa706・親INV861427/failed30・CleanupINVc887/active-exited/正常0は比較要求であって生存証明ではない。現在pending91a748・cutoff2026-10-06T12:06:14.564793Z/activation179758・INVALID・全432batch/24業務table・Backup32/Transfer2・空三request/全原本/config/nativeを新所有下で実認証する。読取診断をM/A/DB/十Ref authorityへ代用しない。

## Test ID / 操作 / 独立oracle

| Test ID | 操作・観点 | 独立期待値・実行状態 |
|---|---|---|
| MIG202001 | 候補生成・旧artifact/SQL照合・V028追加 | 旧186artifactを認証、許可JAR/schema/profile/新SQL以外不変、187artifact・SQL28/SCHEMA含む履歴29。固定旧hash＋独立line CRC32。未実行 |
| MIG202002 | 不正source/digest/既候補/未知SQL/既履歴変造/profile追加delta | new-only拒否、guest操作0、秘密ログ0。未実行 |
| MIG202003 | 新M/A/DB排他・固定十Ref・before-image | same peer/PIDticks/backend/boot/loaded identity/原本全graph、各前後原値一致、DB/request/epoch/Unit書込0。未実行 |
| MIG202004 | 正常private restore point→V028のみ | 子実正常終端、PGDMP/list正常・fsync、migration一件/Flyway29履歴、全24tableと旧全値不変。未実行 |
| MIG202005 | function/owner/UTC/search_path/EXECUTE検査 | 一関数・nk_owner・固定設定、batchだけEXECUTE、API/Web/Inspector/Backup/PUBLIC拒否、基表grant変更0。DDL literal/独立catalog query。未実行 |
| MIG202006 | profile027→028公開、migration後condition | schema文字列一値だけ、Root:schubert0640/single-link/atomic/sync/readback・旧profile保存、全原本/Backup/Transfer/current/approval/epoch/Unit不変。未実行 |
| MIG202007 | 任意段失敗/timeout/unknown/close/fault | 私有証拠と所有/隔離を保持、再発行/repair/clean/手DB更新/正常化0。正常scopeに算入しない。未実行 |
| MIG202008 | 別正常pending code-only公開 | current/approvalのみ正規delta、epoch/全pending graph/全業務/Unit不変、新署名/BOM/source一致・全新scope正常帰還後だけ次段。未実行 |
| MIG202009 | 元runの一回用resume→全親→退役 | 独立二引数/全effective/全所有・durable一回予約/observer先行、30min/Unit期限・API所有保持Web/Caddy/DONE/逆順TERM・元Backup原値/日次SKIP維持・全終端後の正規退役。未実行 |

## 観測準備（受入に非加算）

元Log/Inbox二rowのlive readonly独立SQL actual0。元原本cutoff一致・ENDがcutoff以上元SUCCESS終了以下・全counts/cursor整合と全row SHA256を確認した。私有 `work/pgpt-runs/PG379/pg489-prior-progress-observation-v1.private.json` hash `76fee06f46baaefdd8f51b2049b909f6fe9086e9a203dbdd308615d3bc54b8a8`。raw cursor/秘密/DB実体公開0、authority/start/write0。PG489元原本読取証拠は399へ追跡。これらはfresh owned native gate/移行/親成功ではない。

## 実行・証跡・coverage

2026-10-06 22:53：限定migration工具を作成、compile-v1は初期import/classpath不足で終了1（工具未実行、正常/Production PTに非加算）、新onlycompile-v2はJDK25 -Xlint:all -Werror終了0・独立Java20assertions/Python profile delta16assertions終了0。private WorkPG379/pg490-migration-{compile,oracle}-v1/v2.private.log、classes pg490-migration-tools-v2。null/source/digest/追加引数/旧新schema/他profile値/原byte保存・metadata/未知対象変更拒否を検査。これは工具純粋境界だけで、owner/fault/native migration/全親は未試験。移行工具/API sourceを固定した新全回帰と署名候補の成功確認前にguest実行0、MIG202001/003～009未実行を維持する。

工具command/source/OS/JDK/branch/終了コード・入力の非秘密hash・独立期待値・実際値・関連BUG/SSC・manifestは実行時に追記する。未実行・中断・拒否をPASSへ加算せず、私有ログ/credential/dump/session/tokenをGitへ保存しない。工具の独立境界/fault試験とProduction同source coverageを混同しない。現時点で本仕様のMIG202001～009は未実行、正式run24/1964PT/53scope/48.3%を更新しない。
