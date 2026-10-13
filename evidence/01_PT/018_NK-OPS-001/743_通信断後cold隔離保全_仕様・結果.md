# PG2200/2201 通信断後の現chain保全・管理隔離boot

Program NK-OPS-001、SS343 SSC165/174/206/264、QA047/052、451。Production source3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8は照合基点。正式1964/53/全leaf0は不変更。

PT-OPS-2200-001: LAN現QEMU/listener不存在・全chain FD holder無し、空20GiB超、二chainサイズ/形式/backing/dirty/corrupt/snapshotの独立固定期待値。原active48GiB→base40GiBを両hash/identityで保全。new-onlyCOWを原activeに重ね、qemu-img compare正常0、元二file全hash/identity同一を後確認。既diskへのrepair/resize/削除はしない。

PT-OPS-2201-001: 上記actual0のみを入力とし、同新COWだけ4vCPU/8192MiB/KVM・SS343既basic.target/明示network-ssh-postgresql/masked timers-paths設定で一回management boot。新reservationが既存在なら再発行拒否、旧RAM/run/permit復元無し。これは旧bootの正常停止/native又は新業務readyを保証しない。新bootのDB・原本・Backup/current/Unit/資源の再認証は別工程。

独立工具test4PASS/static0: 固定隔離argv、abc固定SHA256/inode属性変化、耐久receiptO_EXCL、foreignSourceと既reservationのlaunch前拒否。command=PYTHONPATH=tools/quality python3 -B -m unittest pg2200_outage_cold_preservation_test。fixture期待値はproduction methodから生成せずliteral使用。実PG2200/2201は未実行、結果/hash/終了codeは追記する。

通信断前actual2182payloadf24aa08e/2184payload9953fc6a/2186payloada4a72fccはW/PG379各manifestに保存済み。2182真正DONE10/1650.231989秒、2184全24DB0/HTTP-session-SENT222/Backup2/七SKIP/警告1、2186全187/32/四owned封緘0。旧boot全ownedstop/nativeは未実行、OS再起動から正常closeを推論0。22時現在LAN新boot e2aa2502/QEMU無し、2187は通信経路255で未実行。私有raw/credential/DBdump/実session/tokenは本証跡に格納しない。
