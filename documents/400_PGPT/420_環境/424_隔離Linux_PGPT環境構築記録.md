# 隔離Linux PGPT環境構築記録

2026-09-30 S1再開：既存overlay/seedを保持してQEMU PID11690へ復帰、SSH/PG18online。旧Morning test-only Unit/drop-ins、Backup本体/pgpt309 drop-in、Artemis本体、vendor Caddy本体/NK drop-inはVM private `/var/lib/pgpt-s1-preservation/unit-originals-complete.tar`（root:root0600/親0700、30720byte、SHA256 `1becfb4fca51ee39bc6ac1ab0bf3bfc49614b95468efc2c7d1fbf98534a80eaf`）へ退避。tar一覧exit0、全既存対象を事前FragmentPath/DropInPathsで解決した。初回archiveは未存在artemis.service.dでexit2のpartialとして別fileを0600保全し、完全退避扱いにしない。実Unitの置換・drop-in移動はまだ行わない。復旧は完全archiveの対象だけを元path/owner/modeへ展開しdaemon-reloadし、保存したUnit状態と照合する（原本/credentials/release/DBはarchive対象外・不変更）。

同VMの独立namespace診断（SSC109/BUG327）：host `statvfs`は/run,/var,/var/lib,/var/lib/schubert-nk,/srv/schubert-nk/backup全RW。transient `pgpt-s1-namespace.service`、Typeoneshot/ProtectSystemstrict/ReadWritePaths backup限定/NNP/root限定CAPSYS_PTRACE+DAC_OVERRIDEでprivate前4祖先RO/backupRW、exit0・cgroup終了、--collect済。Production Morning/Backup成功ではなくshared ancestor policyの反例とする。privileged設定を広域RWへ緩めず保持host/private同inode照合へ補正する。

## 2026-09-27 PG300 backup crypto環境限定確認（未受入）

既存開発host private recovery agekey（600、親700）からage-keygen1.2.1で公開recipientを抽出し、値をlog/Gitへ出さず隔離VMの`/etc/schubert-nk/credentials/backup-recipient`へroot:root0600 new-only install。既存credentialがあればbyte一致だけ確認し上書きしない。秘密identityはVM/server/backupへ配布0。VM age1.2.1が公開53byte fixtureを暗号化し、cipher SHA256 `ccd903671fd2cd90ad6015da63cdcd29a0604cc07e6343aad149770a2d0ece8a`。開発host age1.2.1でのみ既存private identityを使い復号し、原文/復号 SHA256双方 `05ed26fbce72508865be120e9c236bbcf8242d313ac917e7bb02c44fa46cbaad` とcmp成功。plaintext/cipher/recipient/identityはwork/pgpt-vm/private Git外に保持。これはtool取得/設定/recipient互換だけで、実DB dump/credential archive/backup publication/DBstep成功/retention/fullgateは未実装。

再現: 初回だけ固定private agekeyに`age-keygen -y`を行い公開recipient fileを生成（値非表示、600）。marker pgpt-r2-20260927-01を確認したVMへ公開recipientと非秘密fixtureだけ転送し`age --recipients-file <public-recipient-file> --output <new-cipher> <public-fixture>`。cipherだけ開発hostへ戻し`age --decrypt --identity <host-private-key> --output <new-restored> <cipher>`→cmp/sha256。鍵再生成/既存key overwrite、private key転送、復号実体Git格納を禁止する。本操作中のProduction回帰sourceはb22c7abd3で不変更。

## 2026-09-27 PG300必須backup準備（未受入）

隔離VM marker pgpt-r2-20260927-01を照合してUbuntu26.04配布APTからageを導入。実dpkgはage1.2.1-1build1、postgresql-client-18 18.6-0ubuntu0.26.04.1、tar1.35+dfsg-4ubuntu0.4、guest kernel7.0.0-31。`sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y age`→`age --version`/`pg_dump --version`/`pg_restore --version`/`tar --version`で再現する。private install logはwork/pgpt-vm/private/PG300-backup-tools-install.log、raw logをGitへ格納しない。

同APT由来/usr/bin/age-keygenを開発hostのwork/toolchain/age-1.2.1/binへscp、SHA256 0cadbef602a8849c9522869ff4007e66df1ec1cd00bc1e7c0b6ab2f08a95643d、version1.2.1。recovery private keyは開発hostのGit外0700private領域でage-keygen -oにより新規生成し、VM server/backupへは配布しない。内容・raw generation logはGit/チャット非公開。実archive生成/復号rehearsalは未実行。

VMの未存在schubert-backupのみsystem/no-create-home/nonexistent/nologin/専用groupで作成し、getent実UID992/GID977（fixture限定、Production固定数ではない）。未存在/srv/schubert-nkとbackupのみinstall -dでroot755/専用backup700へ新規provision、既存pathは変更しない。applicationの自動root作成/修復ではない。parent M/anchor・Productionbackup service/pgpass/tar/age生成・真正manifest/DB step確定は未実装で、この準備をbackup合格へ算入しない。

2026-09-27 PG297追補: 同隔離VM /opt/jdk-25.0.4だけをroot:root所有へ変更（chown -R root:root /opt/jdk-25.0.4）。root管理runtimeを通常ubuntu accountが更新可能なままにしない。update-alternatives --install /usr/bin/java java /opt/jdk-25.0.4/bin/java 250004で固定/usr/bin/javaを供給、resolved target/version/root755確認。host /etc/runtime不変更、既存VM DB/Artemis稼働継続。native015 root→samePID→setpriv→専用UID/明示groups/zeroCaps/2FDは試験用公開packetに限る成功、Production全起動未認定。

2026-09-27、471 R1～R3用の専用fixture。ホストUID1000ではsudo非対話不可、user namespace mountもerrno5005で拒否された。一方/dev/kvmのmini ACLはrwであり、ホストの/etc/UID/Unit/権限を変えずKVM VMを構築できた。IT/ST本番serverの確認ではない。

| 対象 | 実version・入手元・確認 |
|---|---|
| QEMU | 10.2.1、Ubuntu apt `1:10.2.1+ds-1ubuntu3.2`、jp.archive.ubuntu.com/ubuntu resolute-updates。host apt installせずwork/toolchain/qemu/packagesへdownload→dpkg-deb -xで専用rootへ展開。system .deb SHA256 `46bfa5208c570f47d380bc68ff3988684dd016c629b75260776f469a67d7e116`、utils `a21829cf2388bbf31a2890aa94a757519a048391fcdaabfa0a5b9347ac3e7e54` |
| Guest image | Ubuntu26.04公式cloud image、2026-09-19更新。`https://cloud-images.ubuntu.com/releases/resolute/release/ubuntu-26.04-server-cloudimg-amd64.img`、SHA256 `4908fb59ccd4e87ae4e8e973b7ef56f535448eacb24a87fd787270c0048987bc`。同releaseのSHA256SUMSをHTTPS取得しsha256sum --check成功。GPG検証済みとは主張しない |
| Guest runtime | Linux7.0.0-31-generic、cloud-init done、systemd running、sudo -n可。KVM初回PID38082、4vCPU/8192MiB、40GiB sparse qcow2 overlay。PIDは再起動で変わる |
| JDK | 421登録済みhost OpenJDK25.0.4+7-1-26.04-UbuntuをVM /opt/jdk-25.0.4へ転送しversion一致 |
| DB/ACL/crypto | VM aptでPostgreSQL18.6 `18.6-0ubuntu0.26.04.1`、acl2.3.2-2、openssl3.5.5-1ubuntu3.5導入。初期DBはfixture defaultでSS342適合をまだ認定しない |
| Seed | 既存xorrisoでNoCloud cidata ISO。public SSH keyのみをuser-dataへ供給。初回seed SHA256 `3d0bf8036b27f80fe18432663c5bb1cb1bbcf0403b506ec577c8aa76e04b6106` |

QEMU依存qemu-system-common/data、seabios、ipxe-qemu、libaio1t64/libfdt1/libpmem1/librdmacm1t64/libslirp0/libndctl6/libdaxctl1も同apt元から専用rootへ展開。LD_LIBRARY_PATHはwork/toolchain/qemu/root/usr/lib/x86_64-linux-gnu限定。host libraryを上書きしない。shared test-jarは既存Maven cacheのmaven-jar-plugin3.4.1を固定使用する（未cache3.5.0のoffline未開始試行は不認定）。

## 再現と保全

1. 固定packageをapt-get download→専用rootへdpkg-deb -x。QEMU --versionとldd不足0、base imageと公式SHA256SUMS一致を確認。
2. work/pgpt-vm/privateを0700、新規SSH keyをssh-keygenで生成しprivate600を維持。password認証/root SSHを無効にしたNoCloud seedへpublic半分のみ供給しxorrisoでISO生成。private key/known_hosts/console/image/VM内credential/DBはGitへ入れない。
3. qemu-img create -f qcow2 -F qcow2 -b <検証済base絶対path> instance.qcow2 40G。base不変、既存overlayを上書きしない。
4. 専用PIDfile/port衝突確認後、qemu-system-x86_64へ -name pgpt-r2 -machine q35,accel=kvm -cpu host -smp 4 -m 8192 -L <専用root>/usr/share/qemu -bios <専用root>/usr/share/seabios/bios-256k.bin -vga none を指定。overlayはvirtio qcow2、seedはreadonly cdrom。networkはuser,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22、virtio-net-pciのromfileを空、display/monitorはnone、serial/PIDfileはwork/pgpt-vm内、daemonize。初回VGA ROM不足試行は未起動、-vga noneで解消。
5. SSHは127.0.0.1:22222/ubuntu、専用鍵・known_hosts・IdentitiesOnly/BatchMode。初回accept-newは自分のVMだけ、以後StrictHostKeyChecking=yes。sudo -n true、systemctl is-system-running、cloud-init status、pg_lsclustersを確認する。root操作はこのVM内fixtureだけ。
6. 停止はVM内正常shutdown、実QEMU PID/command終端確認を優先。無関係processをkillしない。現在は起動したままnative PT準備に使用中。

Production main成功、専用service UID/LoadCredentialの実属性、全root/OS排他、Ops readiness/Expiry、SCRAM/password配布、業務handler、実NK CHR-A01/L01は未達。一般ubuntu UID1000をProduction serviceへ読み替えず、必須gateをfixture/root権限で迂回しない。
# SSC181 Caddy NSS限定配備記録（2026-10-05）

Ubuntu26.04 shadow-utils `passwd 1:4.17.4-2ubuntu3`、実helpのgpasswd root指定は`--root`/`-Q`（`-R`はrestrict）。実固定サービスUID993/GID978を変えず、distributionのwww-data(33) memberに含まれていたcaddyだけを管理者が削除する。systemd `SupplementaryGroups=`空だけではNSS initgroupsを消せないため、Production identity gateを緩めない。

再現：330仕様/331結果に従い、現boot/同signed source/全9停止/真正M-A-DB・原本Backup/DB281全列/startup13を認証→new-only私有chroot literalで`gpasswd --root <fixture> -d caddy www-data`検証→root0700/0600 SAVE `/var/lib/pgpt-s1-preservation/pg460-caddy-nss`へgroup/gshadow/passwd/nsswitch/既存backup before-imageを同期→同全gate下で`gpasswd -d caddy www-data`→group/shadowの当member以外・primary/他member/自動backup・全業務値/所有正常帰還を照合。32独立fixture（host25含む）及び実管理actual0、actual groups978のみ。生NSS/gshadow/原本/dumpをGitへ出さない。未知の場合は隔離/保有し、無差別usermod、サービスからの自動NSS再設定、旧before-image丸ごと復元をしない。既存signedPG459/source8e97/027は再配備/DDLせず新onlyguardで親一度を実行中、親/CHR/coverage正式受入は別。
