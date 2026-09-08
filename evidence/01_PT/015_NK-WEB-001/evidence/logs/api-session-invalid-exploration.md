# 業務API0102・local session破棄の探索記録

正式認定: 未実施。探索成功をProgram完了へ算入しない。正式clean verify後に確定する。

NK-WEB-001、PT-WEB-158～165、PG-D-117、SSC-048。FUN-001/AUT-001～004/MON-004/TST-001～005、UI221/222/226/232、SS313/314/351/352。toolchainは421、独立入力/期待/fixtureは001 §14.13。

| Run | 終了日時（JST） | 結果 | 非格納raw log SHA-256 |
|---|---|---|---|
| api-invalid-20260909-explore-01 | 2026-09-09 03:23:04 | exit1、testCompile。新規PT fixtureで既存authenticate戻り値Optionalのunwrapが2箇所欠落。既存契約へ照合し修正。未実行/非合格、production障害ではなく初期PT準備不備のためBUG対象外 | 4c59a706907519487d903499b6a043a4ba94d1d3e1e9576217df4e9bc159f56e |
| api-invalid-20260909-explore-02 | 2026-09-09 03:24:18 | exit0、新8件＋既存error10/access6/audit6のWeb30、Protocol5/Storage16 PASS。新mapper/handlerと変更audit/accessのline/method/class/branch100%、NullAway/format/Enforcer PASS、SpotBugs0 | 63ba58cc5d57ba1ec122b263e4f6a8406ce8f91d14f07205d070e589722cdaf6 |
| api-invalid-20260909-explore-03 | 2026-09-09 03:26:10 | exit0、response二段目status/commit getter、request method/header/URI故障、並行全username集合も追加し同30/5/16 PASS、failed/error/skipped0、静的解析0 | 1f2d681a68768dc28b29363addc26c9f4e4149677707ddf69442f4ae4d9f9ae9 |

command（repo root、JAVA_HOMEは421のJDK25.0.4）:

```text
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=ApiSessionInvalidTest,ErrorMvcTest,SessionAccessFailureTest,WebSecurityAuditTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

Spring Session4.1.1 release sourceのHttpSessionWrapper.invalidateはcurrent request session/cacheを消去してdeleteByIdを呼び、commitSessionはresolver.expireSessionを呼ぶ（383～388、219～224）。既存production adapter/lifecycleのhash限定削除へ接続し、DB行消失とMax-Age=0/Secure/HttpOnly/Lax/Path=/を独立確認した。failure時にはlocal行が残ることもあり成功を推定しない。API0102は既にAPI無効が確定した境界なのでpending_context_revocationsを作らず、未確定Logout期限RERUN-001とは分離する。

固定ResultCode→HTTPの12行期待、GET302/POST・HEAD・AJAX・media401、表示用actor/CSRF全消去、既存SESSION_EXPIRED INFO監査の固定metadataだけを確認した。通常HTTP入力のcodeやqueryは判定に使わず、fixture endpointは検証済0102の明示doubleである。100並行の各username/role/UUIDと全row消失、旧request取得→新Login fixation→旧request失効という制御順序で新rowが残ることを確認する。これは全業務decoder/controllerの接続・実NK Characterization・IT/ST完了ではない。

Login後の実CSRFは次のPOSTへの入力だけに読み、期待値生成には使わない。error DOM/HTTP status/Location/Cookie属性/SQL後条件は独立固定値。raw Cookie/session/token/password/context/鍵/DB dump/JVM出力はGitへ格納しない。実行環境・sourcecommit・Test ID対応・coverage・sanitized XML/hashは正式manifestに記録する。
