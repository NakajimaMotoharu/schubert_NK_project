# 278 NK-OPS-001 実Morning→同owner Backup一往復

2026-09-30 JST。Program NK-OPS-001/NK-BAT-001、OPS009/BAK001/BKO001、UI251/253、SS341/342/343、SSC107～114。仕様272/275/276/277の実外部観測。IT/ST・全PGPT・S1全条件の合格ではない。

## 実行・独立期待値

Source `a6b5c7c8b021c4b391b3af90572eab5d0eac8ab1`、dev-foundation。Ubuntu26.04隔離VM pgpt-r2、JDK25.0.4、PostgreSQL18.6、age1.2.1、JaCoCo0.8.15。真正Production thin-JAR release0.1.0-PG385。固定別配備Ed25519 pinで元byte署名、177artifact/61runtime依存/23SQLの全BOMとhost ROを確認し、同原本保持・新INVALID・Rootapproval400/current絶対selectorを再読。runtime permit発行0。外部commandは `systemctl start schubert-nk-morning-controller.service`、既存明示resume引数を真正Mainへ渡す。no-block client終了を合格にしない。

PT-OPS-BARCHIVE001/POS、PT-OPS-BGATE010/VM、PT-OPS-BREQFILE010/VM、PT-OPS-MDB016/VM：原本run/cutoffは変更しない。旧両attemptをABANDONEDとし、実開始UTCのattempt3を同sessionでcommit、旧request世代を独立DB照合して正規退役/新公開。実workerのfresh Invocation、exit0、明示stopと全cgroup終端、実3artifactのhash/size、MANIFESTと両DB SUCCESS、元原本/current再証明、request→最後に同inode intent退役を期待する。

Productionでexpectedを作らない。実tarをGit外privateへコピーしPython標準tarfile/hashlibと固定構成集合（config7/credential16）で確認。ageの独立CLI復号はclient private keyで行い値は出力しない。dumpは実pg_restore --listの終了0と224entryを確認する。MANIFESTの期待run/cutoff/DB実handle/start時刻は原本・独立SQL実値と照合し、全3fileのサイズ・SHAを独立再計算する。

## 実結果

Morning Invocation `68b5e9d1bda54e21b808a7325838a22a`、worker Invocation `a7d870091a45446fa19aa1506b01783f`。後者はPID1 journalの許可field（UNIT/INVOCATION_ID/JOB_RESULT/時刻）から独立採取し、start done→明示stop doneを確認。stop後GCでInvocationID空になることを未起動と誤認しない。生journal messageやcommandlineは保存しない。

Backup final directory `20260930-120030-31100027-2222-4333-8444-555555555555`、MANIFEST966byte/hash `f751b608de3d33eddb82acbbd35a437a3b5bf8782fb3e3f56414ac0a12985f30`。実config20480byte、credential暗号archive41160byte、dump170806byte。全3hash/sizeがMANIFESTと一致、config7/credential16はregular entryの固定集合、復号成功、pg_restore-list終了0/224entry。両DB attempt3 SUCCESS、旧attempt1/2 FAILED/ABANDONEDは保持。request/intent0、両Unit PID/ControlPID0、job空、全終端をProductionが再確認して返る。

外部Morning終了30はS2/S3未接続の**部分実装の非成功**。全Morning成功・正式PT・StartupPermit発行へ読み替えない。Backup正の一往復/開始前失敗からのresumeのみ実証した。worker失敗・UNKNOWN/hard-timeout・S2保守・issuer/APIWeb/CHRは未受入。

## Coverage・証跡

同じ真正JARへのagent採取：parent25324byte、worker3078byte。class byte mismatchは拒否する。全Java4指標100%ではなくnative reachability証跡。host selected68PT F/E/S0/static0。同source全6回帰は12:29:25 JST、2542PT/371suite F/E/S0/static6module0、manifest ceaa2229…へ確定。最初のNode PATH誤指定によるWeb2error/full途中停止は別FAILED manifestへ保全し合格にしない。host欠落B/L/M/C全体290/1110/253/23、前PG384からのgraph差分+21/+16/+2/0。Batchの同byte host+実parent/worker unionは179/460/99/11（host249/1040/240/23から70/580/141/12解消、class不一致0）。他module native unionは未採取で全体100%未達。開始PG378の72/433/149/17は別graphの基準として保持し、正式合格へ混合しない。

関連BUG327/330/340～345/347/348、YKT259/262/270～275/277/278。native manifestと実artifact独立oracleは `evidence/provisional/PG385-native-deployment/`、同source全6は `PG385-backup-expiry-wiring/`。raw archive、dump、age/署名private key、credential実体は全てGit外private。
