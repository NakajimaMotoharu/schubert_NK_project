# 290 実Cleanup・内部Inspector接続 実行結果（暫定・未受入）

PG390選択・2026-09-30 18:23:07 JST：Storage3/Bootstrap4/API12/Batch72=91PT F/E/S0、4module SpotBugs各0。commandは289の追加owner/privateコピー/Root期限/Inspector remain条件/Step・Log期限境界と既存影響suiteを選択し、既定JDK25.0.4/Node24.19.0・offline Maven3.9.12でspotless:apply test spotbugs:check jacoco:report。log `work/pgpt-runs/PG379/pg390-cleanup-owner-guard-final.log` SHA256 f3082f8fc894cde2fa3b1ae0f5e1170e223e279f4d26490e82cd8b801eb46e31。BUG362新native限定noRemain拒否、BUG363境界3及びpre/postcommitを再試験済。途中3runは不合格として保存（初回新試験Optional/OptionalInt型、role既定30min/旧固定SQL probe適用、BUG363、close key名）。期待値は独立literal/実PG後条件、Productionで生成しない。selectedは全module/全coverage/実VM受入でなく、同S2変更群のnative caller接続後にsource固定・全6/真正Unit結果を集約する。

PG389全6の確定追補：Source8d5994e779bba71bd1e4c3c859241a84ff29e483、2026-09-30 17:48:13 JST、2,581PT/380suite F/E/S0/SpotBugs6各0。manifest `evidence/provisional/PG389-inspector-owner/manifest.json` SHA25695121fedbbbf919073793d0854178a24dd54bc8446d4c1a0e532f0c617b47ac5。host残B/L/M/C=408/1315/292/25、native coverage100%未達。BUG362のnative Inspector yes比較はこのSourceで未修正（汎用projectionはnoも解析する）、次Sourceでbaseline/heldだけを補強し独立no拒否を再試験する。BUG356～361の直接原因は全6の同Sourceで再確認、残nativeは引き続き未受入。installerは内容同hashのまま`tools/quality/vm/050_s1/pg389_provision_inspector.py`へ保管し、既配置VMで再実行しない。

仕様289/SS341§7.3・343§6.17/SSC119。PG389のSource `24ed4e271e6e10d47302103969050f3d3f57e05e`（実装bab5bad44＋全回帰command固定）で、選択203PT/4module static0、2026-09-30 17:16:34 JSTを確認。共通CLOCK_MONOTONIC frame/golden、Root deadline IO/null、2Root親、普通Inspector自己＋別shell MainPIDのkernel/manager二回一致、DB DELETE/commit境界、型付き0/10・Inspector明示stop→全終端→reacquire→DB→env/owner→intentの順序をhost独立fixtureで試験。全6回帰/同byte nativeは実行中又は後続、未網羅100%を認定しない。Source六回帰manifestで結果を確定する。

## 隔離VMの接続前環境

実行command: `sudo -n python3 /home/ubuntu/pg389_provision_inspector.py`。作業領域script SHA256 `7d5e16c83a8070758eaf04d14cdfaf1cc157d4c5959f7d42add0ee5bfa729b83`、終了code0。Ubuntu26.04/PG18.6、instance固定 `pgpt-r2-20260927-01`。既存M/A inode/Root0600をNOFOLLOW保持・非blocking flock、current INVALID、固定9Unit inactive/failed・MainPID/ControlPID0、既存OS accountなし／DB専用roleのpassword未設定を先行確認し、new-only構築。既存file/account/passwordがあれば上書きせず停止するscript。今回再実行は行わない。

- `schubert-inbox-inspector`: UID991/GID976、group976/982/986（専用primary、schubert-read、schubert）を独立`id`で確認。nologin/nonexistent home、API/Web group継承なし。
- `/etc/schubert-nk/inbox-inspector.env`: Root:schubert0640、DB5432/schubert_nk・fixture version v1。既存envなしから新規作成。
- `db-inbox-inspector`: Root:Root0600、新規ランダム値をVM内生成し専用DB roleへ設定。値・hash・DB dumpはGitへ出さない。DB role login=true/superuser・createdb・createrole=falseを独立SQLで確認。鍵2種の既存Root0600は変更しない。
- Source Unit/ownerはまだ配布・起動していない。実VM releaseはPG387、Inspector inactive/dead/PID0、permit0。これらの環境事実をCINSPECT実受入へ読み替えない。

provision固定receipt SHA256 `b5d47c480ca49062030b582d9413943f226bd0d0ec82c603517af54c158281f5`、独立metadata/role/Unit/current観測log SHA256 `e2baea369c6c0d0d75e1089b1bcf9ee1106c4c495740dc28524ee06f58dfeeed`（作業領域PG379配下）。原本run/cutoff・旧DB12行・4file・復旧点・秘密鍵は保持。installerは通常Unit起動・release切替・permit/approval発行を行わない。

## 残る実受入

CEXEC001～003/CINSPECT001～004の真正外部経路はNOT-RUN。Root request publisherの閉鎖owner型→同Cleanup DB/advisory内の6step→実Inspector→Transfer→親再取得/独立全DB再読→request/owner/intent退役を結線する。Backup真FAILED時の6SKIP・Inspector/DELETE0とTransfer実行、Artemis Requires下Cleanup再実行0、Expiry/prior監査・正規issuerは別残件。S1実30分UNKNOWN、native100%・API/Web業務起動/CHR・正式全scopeは未完のまま、工程完了を宣言しない。
