# 425 専用LAN PGPT環境・移送記録

## 2026-10-17 同一VM online容量拡張（QA052、追加install/再起動/削除0）

既QEMU10.2.1の正規Unix QMP口をmini経由sudoで利用し、同QEMU4599/t101242/argvf765c39c/hostbootc796・guestboot79aのままactive childだけ56→72GiB（60129542144→77309411328）へ一回拡張した。SO_PEERCRED4599/0/0、exact node-name `#block113`、既host空き約134.6GB・16GiB拡張＋10GiB保全guardを認証。active一個とreadonly backing三個を区別し、全三backingのQEMU FD O_RDONLY/九metadata before=afterを要求する。稼働imageへのqemu-img resize/copy、旧backingの変更、shrink、root直接SSH、socket権限緩和は実施しない。

手順は既2012/2868の同bootオンライン契約を継承した新工具 `pg4570_capacity_current_post.py before`→`pg4572_capacity_online_grow.py`→`pg4570_capacity_current_post.py after`。既growpart `/dev/vda 1` とresize2fs `/dev/vda1`を各一回、M→A/十metadataRef保持・全十Unit/kernel空の境界で実行。新namespace/一回QMP予約・partition/resize予約をfsyncしてから発行し、応答欠落時は元予約/実disk状態から回収する。**この手順は実行済みなので再発行禁止**。既cloud-guest-utils/e2fsprogs/util-linuxの利用で追加導入0、既version/出所の環境契約を継承する。

実run=4570before38462actual0→4572grow58870actual0（18:02:21～25Z、operator2383c30b3）→4574独立post92632actual0（18:02:41Z）。root開始sector2324480/partitionUUID F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C/filesystemUUID92978eec-7925-481e-8629-5b963d59ced1/他三partitionは不変。root size/lastlbaだけ33554432sector増加、空き24334848000byte/12GiB guard維持。source964e/PG4432/署名187/全24/32設定/19Unit/原本Backup鍵/native58/startup37・全11二読SHAf14b97d2・全資源を独立再照合0。元read権限/層数/ローカルsudoPTY解析の拒否とremote0回収は別保存、過去欠測を補完0。

公開証跡=018_NK-OPS-001/993・PG4592 manifest SHA c61bdb7499253af8d6a6293eb438d388bc7ead17440e96d0be1f9344f9e6a0b8。完全QMP/geometry/DB/鍵/前後像はW/PG379とLAN/guest root-private namespaceにのみ保全。後続IT/STへの復元では現job/owner・VM停止/保全を認証し、容量を元へshrinkせず新保全ディスクを確保してから個別判断する。容量確保をPGPT正式品質/ITST合格とはしない。

## 現在の追加工具・再現・復元差分（2026-10-12 07:37JST）

公式Ubuntu aptでACL2.3.2-2/setfacl-getfacl2.3.2を追加、root-private `/runs/PG1460-acl-package-v1` の導入前inventory/apt logを保持。既host抽出PostgreSQL18.6（Ubuntu18.6-0ubuntu0.26.04.1）のbin/lib/share/libpq627fileを同SHAで専用server `/tools/postgresql18/usr` へ配置、postgres/initdb/pg_ctl/psql/dump/restore六version/ldd欠落0。DB・credentialはコピー0、裸機PostgreSQL service導入/起動0。Node24.19.0、固定ShellCheck0.11.0は既資格hostの実byteを専用toolsへhash照合で配置し、server.info/host復旧署名秘密鍵転送0。QEMU10.2.1追加は既§5と同inventoryを復元対象にする。

server fixtureはSCHUBERT_PG_ROOT/SCHUBERT_SHELLCHECK/明示private diagnostics dir、親umask0077/子Maven0027/heap768M/worker1/明示tmpを固定。JAVA_TOOL_OPTIONSを除き厳密子stdoutへ起動bannerを混入しない。systemd259.5のvendor xfs警告を捨てず、独立project Unit lookup＋三implicit target stub、project不正directiveの検出/positive stderr空を検証する。旧1459/1460/1461/1466/1467/1468失敗source/target/XML/private fixtureを保存し、是正後PG1471 selected21/1474 XML・static・Mainbyte資格を別証跡とする。新全6はtools/quality/pg1476_corrected_server_six.py（new-onlyで同slot再発行禁止）。

PG1434独立転送closing0→1435新COW cold bootは実完了、現在QEMU13204/guestboot3d69・forward OS23837/tool24937。元三層disk/failed/native/stash7/原本Backupを保持、RAM/旧run/permit復元0。再起動はしていない。Root1456のtimeout143/partialは移送受入や旧tool正常closeへ変換しない。

IT/ST復元時は専用job/VM/DB/forwardの現在所有と未回収保全を認証→正規停止/保存→追加apt package一覧と導入前inventoryの差だけ評価する。acl/QEMU依存の無条件autoremove、全専用領域削除、未知owner killはしない。専用tools/source/cache/runs/VMは保全してから別退避の判断へ、秘密DB/logとCurrent baselineのGit格納禁止を維持。netplan eno2.optional=true/実LAN正常を読取確認済み、ネットワーク/SSH設定変更及び確認目的reboot0。

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
