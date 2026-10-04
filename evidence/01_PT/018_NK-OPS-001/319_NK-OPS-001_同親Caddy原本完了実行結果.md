# 319 NK-OPS-001 同親Caddy・原本完了 実行結果

2026-10-04 20:06 JST。仕様は318、SSC178・NK-OPS-001/OPS009/UI251253/SS341342343。限定host結果であり、親の実起動・全coverage・工程完了・IT/ST認定ではない。

## 実source/runと結果

branch `dev-foundation`、HEAD `1ef0e4cbc9c33c3eac5446d13b35f57415626c44`＋PG455同親変更群。commandは `bash /home/mini/codex/project1/work/pgpt-runs/PG379/pg454_selected.sh parent455-selected-v4 1ef0e4cbc9c33c3eac5446d13b35f57415626c44 <manifestのexact21Testclasses>`。2026-10-04実終了20:01:52 JST、実exit0。Protocol5/Storage7/Bootstrap11/API6/Web8/Batch109＝146PT・21suite、F/E/S各0、SpotBugs全6module0、NullAway compile成功。OS/JDK/tool実設定、開始/終了時刻、source/diff/archive/log hashは安全manifestに記録。

src/tools全fileの実行前hashが終了後すべて一致。全6targetを私有 `work/pgpt-runs/PG379/pg454-parent455-selected-v4-frozen/{module}/target` へ捕捉し、各actual targetとの全file diff一致を確認後に固定解除。collector profileはこの捕捉後に既存工具へ追加したもので、別のProduction版を試験したと扱わない。

安全結果：[manifest](evidence/provisional/PG455-parent-selected-v4/manifest.json)、SHA-256 `8d9e134aac99cc401b29f6025484fc68f3c1c63e7c51bc37d8b2d38b158e43f9`。JUnitのproperties/stdout/stderrを除去。原始log、source tar、実native私有材料・DBはGitへ入れない。Current baseline・旧原本・Backup・stash7は不変更。

## Test IDの独立確認と残条件

| Test ID | 実class/method群 | host実結果 / 独立oracle | 未受入条件 |
|---|---|---|---|
| ORIG455001～007 | MorningOriginalCompletionTest.orig455* / NewRun.scopedOriginalProof / Resume共通cap | 同thread/alive/activation、固定µsのDONE全値、一回だけ、既done時刻/outcome不変、default拒否、foreignthread/前後root/files IO/Runtime/Error・公開不明poisonを確認 | 実保持Session/全原本inodeのnative完了 |
| PARENT455001/002/004 | MorningCompletionEvidenceTest.parent455* / evidence.constructor,verify,completion | hand-written DB rows/receipt fixtureに対し新/再使用SUCCESS0、実失敗Backup＋六SKIPPED＋Transfer/Expiry続行WARNING10、全DB再読順・各故障/欠落/nullを確認 | 実DB十step/audit全値、実Caddyを含む親経路 |
| MAIN455001～003/PARENT455003 | MorningCompletedMainTest.main455* / parent455003 / Main.runCompleted,ControlScope.protectGraph | literal0/10/30/70、typed値だけではclose failureを成功化しない、未知/runtime/fatal同一性、期限切れinnercapを使わないouter-stop observer順を確認 | 最後のMを含むnative scope正常close・UNKNOWN保全 |
| CADDY455001～005 | MorningCaddyReadinessTest.caddy455* / readiness.profile,ready,listeners,kernelAddress | fixed manager/Invocation/PID・actor、独立procアドレス/FD inode、HTTPS200と全前後順、profile全field異常、5guard/10IO故障、redirect/HTTP異常を確認 | 実Caddy開始前profile/validate0、本人kernel/socket/TLS証明書・hostname検証 |
| CADDY455006～008 | CaddyPublicConfigurationTest.caddy455* / config.site | 手書きSS directive golden、IPv4/IPv6、未知IP/config/HTTP downgrade拒否、配備templateと独立directive一致 | 実固定config/公開CA inode/validityのnative読取 |
| CADDY455009/010 | ChildCaddyTest.caddy455* / ChildStartupContext.verifyCaddy | literal Caddy unit/cgroup・NSS/kernel二読、Artemis/foreign group/cap/NNP/世代交換/default port拒否、観測byte消去 | 真正manager/kernel/Caddy ordinary actor |
| PARENT455005～007 | ServiceIntentReadyRetirementTest.parent455* / Attempt.requireRetained,retireReadyAfter | API/Web/Caddy client、退役前後gate、一回だけ、前失敗保存/後失敗再退役拒否、worker用途拒否、null | 実同inode WEB→API退役・両intent連続fence/半退役UNKNOWN |

期待値は手書きliteral順/固定UUID・µs時刻/Unit・HTTP・SQL形fixture。Productionからexpectedを生成しない。以上27新PTに既存14suite/119PTを含む146件であり、別source/runを加算しない。

## coverageと不合格runの保全

11対象classの全counterをmanifestへ保持。全class counter miss0だがline/method/branchの未網羅があり `coverageGateAccepted=false`。特にMorningCompletionEvidence B22/L3/M0、CaddyPublicConfiguration B78/L94/M13、MorningCaddyReadiness B19/L22/M3、MorningStartupLaunchOwner B78/L336/M28が残る。既存native/親接続面も未実行で、除外追加・到達不能・component成功による親成功認定はない。詳細値はmanifestを正とする。

v1はBatch型接続compile不合格、v2はNullAway Nullable結果でBatch PT未実行、v3は146PT F/E/S0だが不要抑制2でactual1、Batch jacoco:report未実行。v3はBUG662/YKT467修正前登録、全source hash/6targetをそれぞれ `pg455-selected-v{1,2,3}-modules` に保存。誤った同名target混合集合 `pg455-selected-v1-frozen` は実byte証拠に採用しない。各失敗は合格へ算入せず保持。v4は不要抑制だけ除去し6static0へ是正した限定結果、共有所有群fresh全6/修正commit・native受入は別残件。

次は同S3署名27migration/Caddy signed template/drop-inの必要内部依存→固定source fresh全6→正規candidate/BOM/Backup/現boot・所有再認証→同親API保持WebCaddy/DONE/intent→実NK CHR-A01/L01/native100/正式同source/run。正式 `PT-WEB-20260925-24 / 1964PT / 53scope / 48.3%` は据置。
