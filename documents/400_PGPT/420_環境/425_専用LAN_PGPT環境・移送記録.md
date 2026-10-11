# 425 専用LAN PGPT環境・移送記録

## 1. 承認と境界（2026-10-12）

QA052回答により専用server `192.168.1.131`をPG/PTへ使用する。後続IT/ST用へ戻せるよう、PGPT領域・工具・VM・port・設定・権限の差分を記録する。本記録はIT/ST合格や正式PGPT受入ではない。元tree・stash7・Current baseline・原本・Backup・旧失敗/heap/VM/nativeは保全する。

SSH ED25519 pinは `SHA256:D2SRHH06v5k3NLTxDhtS6CWmTkigjotrA7l6XaXWcfA`。`tools/quality/lan_server.py`はcredential読取前にpinを検証し、miniだけで接続、必要時mini経由sudoを使用。passwordをargv/env/log/Gitへ格納しない。server.infoやhost recovery/signing private keyをserverへ転送しない。直接root SSH・SSH設定緩和・未使用NIC再設定・確認だけのrebootは0。人のnetplan optional:true是正は現物で確認した。

## 2. fresh実測と隔離配置

Ubuntu26.04.1/kernel7.0.0-38/x86_64、80論理CPU、MemTotal143641932kB、MemAvailable141703008kB、load0/0/0、root空き209789136896byte、root KVM API12。host空き65458716672byte。serverには既存java/mvn/qemu/psqlが見つからず、既存業務serviceを置換していない。server空き10GiB以上＋必要保全量を開始/移送/終了で確認する。

専用新領域 `/home/mini/schubert-nk-pgpt` はmini所有0700。tools/source/runs/m2/transferを分離。JDK25.0.4、Maven3.9.12、固定offline repositoryは承認済host toolchainをrsyncコピーし、既存入手元/導入記録421を継承する。新version選定・未記録dependency更新ではない。出所はhost `/work/toolchain`、再現commandは `python3 -B tools/quality/pg1429_server_setup.py`（new-only、同slot再発行禁止）。

sourceはtracked snapshot `2c29d7a17a5eca2f61b24e99af13260a3c286a09` のsrc/POM/mvnw/.mvn/characterizationのみGit archiveで固定。archive SHA256 `f12e38a72f25fc233a42d3eff05e660d708bde9716a31d3c3f255fada824a3a1`を両hostで照合、PG1429 exit0/13.395秒。Main基準769は不変更。私有証跡 `/work/pgpt-runs/PG379/pg1429-lan-environment-v1`。工具全tree・同Main class-byte資格は追加検証中で、archive一致だけから正式品質へ加算しない。

## 3. 試験と稼働

pin不一致/空key/mini欠落/別address/専用region外の独立工具試験5件PASS（Production PTへ加算0）。PG1430はserver上のfresh target、固定4suite28PTを最初の環境資格として発行。dependency compile/test-compile/test-jarはPT成功へ加算せず、batch selectedのfresh XML/FES/not-run/Spotless/NullAway/SpotBugsを別に照合する。Maven worker1、heap768MiB、私有tmpを使用、80並列はしない。現時点はRUNNINGであり未合格。既成功host28PTの新製造実績へ重複加算しない。

## 4. VM移送とIT/ST復元の制約

現在hostにQEMU/Java/Maven生存なし。旧PID/boot/session/permitは現在値へ流用しない。active→instance→cloud-imageの3層はqemu-img infoで全dirty/corrupt falseを観測したが、旧guest正常poweroffや旧工具正常closeの証明へ変換しない。移送する場合はoffline owner/file-open guard、全chain identity/hash前後、論理compare0、server copy/hash、private permissions、10GiB cushionを要求する。新CPUへRAM stateを復元せず既承認cold隔離契約へ戻す。DB/原本/Backup/release/現bootUnitは別再認証、旧/runを復元しない。

現段階のserver変更はminiの専用領域のみ、system package/service/firewall/SSH/netplan/KVM group変更0。将来の追加差分はここへ追記する。IT/ST復元はjob/VM/portの所有と保全完了を確認後、専用領域を保全場所へ退避し、実変更だけを明示して戻す。承認なしの全root cleanup・DB dump公開・旧保全物削除を復元手順としない。

## 5. 追加資格・変更（2026-10-12）

PG1430 selected28/fresh XML/FES/not-run0/Spotless・NullAway・SpotBugs0/exit0、開始19:23:16.325184Z～終了19:24:24.299723Z。JDK248file/Maven97fileをhost/server全SHA比較し一致、protocol/storage/bootstrap/batchの全Main class byteをPG1279資格JARと比較し一致。safe manifest SHA `ae42c24ee6f2384848bdf387119ac7f708a53ba9b76f952c500f7271ad6fec88`。server環境限定資格であり、新Production test/正式全6/全coverageへ加点0。工具試験は追加後8件PASS、BUG1097 lexical path逃逸を修正、YKT866全固定operand/現owner0700/non-symlinkを再確認した。

コピーしたQEMU distributionの初回version probeはserverのlibpixman/liburing欠落で非成功（VM未起動）。公式Ubuntu aptの `apt-get update` と `apt-get install -y --no-install-recommends qemu-system-x86 qemu-utils` をmini経由sudoで実行、両exit0。versionはいずれも `1:10.2.1+ds-1ubuntu3.2`。私有導入記録server `/runs/PG1432-qemu-package-v1`、apt log/root0700を保全。system package追加を「変更0」のまま扱わず、この追記を現行差分とする。IT/STへは追加package/dependencyの実inventory/apt記録を引き継ぎ、必要性不明な依存を自動autoremoveしない。SSH/netplan/service/firewall/group設定変更0。

PG1431 offline source全3層hash/identity前後不変・new standalone guest logical compare0、new guest26627211264byte、元internal snapshotは元instanceに保持し新imageのRAM/snapshot/backingなし。copy0後のserver全hashは60秒deadlineでTIMEOUT/exit1、completedmanifestなし、未受入。BUG1098/YKT867先起票、別PG1434 read-only closingだけを240秒上限で実行中。convert/copy/VM startを再発行しない。PG1431の失敗をPG1434成功へ読み替えず、独立closingを別証跡にする。server.info/host private keysは移送0、seedはpassword/runcmd/rootSSH許可なしの既存public authorized-key seedを使用し、host秘密鍵はhostに保持する。

QA052回答台帳だけをmain起点隔離branchへ反映、PR104正規merge、main `f0a4d9a52425b76e2580827ffe1ac645f25c2766`をfetchで確認した。工具/code/evidenceはmainへ混ぜていない。アプリPR添付は上限100件で拒否、既添付を削除して回避0。QA051保留は不変更。
