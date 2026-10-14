# 容量前提拒否・オンライン拡張・新ordinary入場

2026-10-15 JST、QA052既容量承認/SS343353/SSC264・451487、BUG1253/YKT1019。正式1964PT/53scope/leaf受入差0/工数率null、当a9のordinary全体受入は未完。

## 失敗と原因確定

28aaade95のPG2864v1/session93740 actual1、payload8c9cd6d7cb5234c28d1656a57725e591eb8ebd64ed0dd0b379db37e51dc8878b。actualstdin行310は容量>=12884901888byte条件。ExecStart条件は308で通過しており、parser仮説は独立literalと実noargs宣言で非該当と確定。ゲストfree12560904192byte/約11.70GiBの正規安全拒否で、PG2866/session4670 actual0の別full24/32/187/原本Backup/oldDONE/七phase/RO/十二roles/resource0・v1guard/start両不存在を確認。PG2864を再発行せず失敗payload/log/manifestを保全、容量閾値緩和0。

## オンライン環境是正と独立再試験

専用LAN/容量確保のQA052承認と既2012オンラインgrow契約に基づき、現在QEMU4599/t101242/argvf765c39c・hostbootc796・QMP SO_PEERCRED4599/0/0・新guestBOOT79aへ新規束縛。host空き157000122368byte、旧三backingのopenFDは全O_RDONLY。新active COWだけ48→56GiBの正増分、QMP一回→guest現M-A/FLOCKと全十Unit/kernel空のままgrowpart一回→resize2fs一回。reboot/poweroff/shrink/copy/既物削除0、旧三層全metadataとQMPbacking JSON不変、current/全原値不変。

| 実施 | command | 実結果 |
|---|---|---|
| 原値・容量・未発行before | `python3 -B tools/quality/pg2866_network_capacity_before.py` | actual0/session4670、geometry SHA716c660c…/disk48GiB/oldStart0 |
| actual工具oracle | `python3 -B tools/quality/pg2868_network_online_capacity_test.py -v` | 一試験PASS、ownership/oldFDro/固定8GiB/不許可操作禁止 |
| onlinegrow | `python3 -B tools/quality/pg2868_network_online_capacity_grow.py` | actual0/session63588、sameboot/QEMU/diskinode、rootstart/UUID/type・他part不変 |
| 別全post | `python3 -B tools/quality/pg2870_network_capacity_post.py` | actual0/session93835、全current24/32/187/原本Backup/oldDONE/資源0/全geometry、free20858265600byte |
| capacity負例/完成graph | `python3 -B tools/quality/pg2872_network_newcurrent_once_test.py -v` | 二試験PASS、12GiB最小/直前/null/bool/未知・全独立scope |
| 新規ordinary v2 | `python3 -B tools/quality/pg2872_network_newcurrent_once_v2.py` | actual0/session13026、v1は再発行0、durableonce予約後noargs外部start一回 |
| newRoot読取資格 | `python3 -B tools/quality/pg2874_network_newcurrent_live_binding.py` | actual0/session10565、sameboot/newsource/新run・Root安定sandwich |

PYTHONPATHは835と同じ。工具source4ba77abb4/b112f2cc777786c07c3ac004ffbecda4da3392d2/306c0f44a0455a98f745337f6853017669e5c47b/6435660be、Production Source `a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25`／PG2802／BOM37bf。Java25.0.4/既Ubuntu専用VM、tool版・source・実時刻・command・exitは私有manifestに固定。

旧2012/2178/2684は当時のgeometry/保全native/正常actualによる歴史非該当、元証跡変更0。新2864/2872のみcold空native13directory/旧native輸入0を明示。2810 host20GiBは独立cold保全契約を維持。上記全対象の修正/非該当・再発防止・実再試験を根拠にBUG1253/YKT1019工具/環境範囲完了、Root全体/正式品質と区別する。

## 実証跡hash

基点 `/home/mini/codex/project1/work/pgpt-runs/PG379/`（私有、Gitへraw DB/credential/key/session/token保存0）。

- `pg2866-network-capacity-before-v1/manifest.safe.json`：payload `cc2c68e19c0480886528484a6bc1f4b24083697c17213c5fa96480325dfd1f93`、partition before `716c660caeee0696485fb1b505bdb7f516720eac9bb12e2d848fc0a45da4df05`、afterは837と同ecee7f3e。
- `pg2868-network-online-capacity-grow-v1/manifest.safe.json`：19:09:57.380341Z～19:10:01.096733Z、LAN payload `57e99ef7c1b09030866f4ebca3ad686e5d8cd94fc6e25e1cb9095fb88d79e002`、guest `06c77ec4ff3217744766ec4355a8af515982d00c8daaa4b0e359bcb7d629bf1e`。LAN私有 `runs/PG2868-grow-v1`、guest私有 `pg2868-network-online-grow-v1`。
- `pg2870-network-capacity-independent-post-v1/manifest.safe.json`：payload `8936184c7d3e1095469ee9c7f310770edbe1aba716b3f829e25a4d329af56ed3`、after `ecee7f3e149ee12afa74c43d1e8c47f3246acf67e25c542b4ab10c10fb11fe5a`。
- `pg2872-network-newcurrent-noargs-once-v2/manifest.safe.json`：19:12:09.923853Z～19:12:27.118730Z、payload `f3853d92e514f7a4d506839dfda18cc27c3a87692bb88731adcee91431a53a65`。保存v1/root0を後続成功へ合算0。
- `pg2874-network-newcurrent-live-binding-v1/manifest.safe.json`：payload `fa0133484070836f139768a1bcbfc56d2032b4f6e82c0fdd99b3480a3bb0b9fb`、active SHA `b50c1dfe794d39eff87dfce24b8389b2ba25824bf1fe51e9079526ef1a8973a4`。

## 実行中／未完

当Root27414/t439678/argv868a3462、boot79a、Job11471、Invocationd4197711cfc54770a4ac7c8d90a3a576、run0dc63b79-3f9a-450c-b2a6-56f86272d272、activation74729e17-91c0-43e7-b01f-74f9e6461d6a、cutoff2026-10-14T19:12:28.842213Z、元1800秒。新observer45010/pg2862-parent-watch保持（readonly/automaticstartstop0）。client0/livebinding0は親DONE成功ではない。次同observer/Rootへ継続、same-root API/Web/Caddy/真正terminal/当全24/全体seal/ownedstop/当native/Browser/CHR/四100/451/trace/引継ぎ。旧source042 native・既Root/Backup/ADMIN・配備/拡張は再演0。
