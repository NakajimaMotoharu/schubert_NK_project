# PG3210 隔離Unit・旧factory拒否fixture仕様

NK-OPS-001/SS343/451、PT-OPS-3210-001～004。P017-01.03（原本/JDBC/lock例外・後条件）とP017-06（Backup bridge）内の独立異常PT。Production a9、3694＋native27/残652L131M5C481B。除外/削除/反射/無意味assertで残五匿名classを消さず、既default factoryの厳密admission拒否を実kernelで検査する。現段階は環境工具の純試験のみ、VM/業務実行前。

## 目的と承認内境界

利用者の専有aru承認（QA052/2026-10-12指令）に従う試験fixtureであり、成功済み業務経路を新VMで最初から再演するものではない。現Production VM/Root/Unit/原本DB/Backup/鍵/Currentbaseline/native22は不変更。Source a9の既資格済み全1643Main/79resource byteを読み込むnegative harnessだけを予定し、継承diskの旧Source042を新sourceの正常配備・old permit/authority・native成功と扱わない。Production sourceの変更/再署名/再配備/通常Morning/Backup/ADMIN/新permitは0。

対象=MorningControlScope.executeOwned/executeOwnedEpoch/executeResumeOwned/executeResumeOwnedEpochのdefault匿名original adapterとMorningBackupStage.resumeの匿名scope。Hostでは実Root kernel gateで先に拒否されるため、別の**実systemd Unit/PID1/proc/root UID/cgroup/INV**を持つ完全隔離fixtureで、悪いrelease approvalの所定拒否までを検証する。

単にIOExceptionが出たことだけでは合格にしない。各caseでRootStartupContextの実二読成功、正確に制御した `/etc/schubert-nk/release-approval/current` の不正公開vector/正しい0400型inode、独立OS read到達witness（inotify等）、callback0/DB接続0/stop0/permit0と資源後条件を必須にする。早い別gate失敗は未実装又は不合格として保存する。観測期待値は固定SS guardと独立fault vectorから作り、Production method/coverage自体からexpectedを生成しない。

## 容量・原VM保全

2026-10-15読取でaru free153567436800bytes/available memory135943077888bytes。原QEMU4599/t101242/argvf765c39c/hostbootc796は現在値と一致、QEMUはこの一件だけ、port22224 listener0。既三backingは全て原QEMUのFD accessMode=O_RDONLY、QCOW dirty/corrupt=false、仮想48/48/40GiB。新工具は原VMの稼働active diskを一切コピーしない。

元backingはpg2200/pg1435/pg1431の三不変layer。歴史PG2810の論理compare成功manifest SHA03d0ace38e19d1cff3b2676c84d238b823cee9eb8af4c275941ac06312903d9dに封印された全identity/全内容hashを、今回もfresh検証する。単に今回の入力を自身の期待値にしない。新-only OUT `/home/mini/schubert-nk-pgpt/vm/pg3210-legacy-negative-v1` のCOWだけを作成・論理compareし、全三原layerを再hashする。

最大見積=48GiB COW＋8GiB転送/工具＋8GiB証跡/fixtureデータ=64GiB、別20GiB保全余力、空き84GiB以上必須。新VMは2CPU/4GiB、available memory12GiB以上、primaryの既8GiB/4CPU等を変更しない。主VMのexact PID/ticks/argv/exe/hostboot/全三backing read-only FDを各phaseで認証し、未知QEMU/port所有があれば操作しない。

## 起動と所有

3210工具は旧2810の一回工具preserve/bootを再実行しない。新-only preserve/boot reservation・結果・ログ・disk/QMP/serial/PIDを別領域へ作る。元kernel/initrd/seedの固定hashを照合、cold basic.target/明示SSH/PostgreSQL・timer/path maskを維持、保存RAM/旧run/旧permitを復元しない。別22224→guest22、restricted user-network、新MACを用い外部業務への到達を禁止する。QEMU起動は唯一のdurable予約後一回。

起動後はfixtureの新PID/ticks/argv/bootを認証するまでguestへ設定変更しない。3212の管理forwardも新local22224専用、host pin確認後mini認証、password/鍵の値をargv/log/Gitへ出さず、guest私有鍵をserverへ転送しない。原22222 forwardは保全する。forwardの一回所有を記録し、終了は同PID/ticks/argvを再認証したpidfd TERM/有限待ち/port消失とする。UNKNOWNは保持、force/retry0。

fixture内の業務Unitはbasic隔離の停止を維持する。負例Unit名がMorningと同じでも、プログラムは別の負例harnessであり通常Morning開始とは認定しない。必要なruntime Unit/fixed bad approvalはfixture COW内だけに新規配置・制御する。原VM/共有backing/host Unitは変更しない。悪approvalの元byte/inode等は私有保全し、原Baseも不変のまま保持する。実mode/ABI/fault到達仕様は実発行前に追加する。

## 受入・終了条件

純3210二試験で全Primary field変異/全backing writable・bool/extra QEMUを拒否、新COW path/port/2CPU4GiB/basic mask/無RAMrestoreを固定。全Python static0。実preserve/bootは別資格、起動だけでPGPTを加点しない。全予定negative case/独立witness/同Main-member CRC-session/原本DBBackupの全24限定不変/全Unit-kernel/全actor-client-advisory-flock/forward/fixture owned poweroff・disk解放までの安全終端を記録して閉じる。原VMは保持する。

event0820で開始見積 .75/2.5/6週次共有pp（P017-01.03=.65/2/5、P017-06=.1/.5/1）を固定、環境費込み。過去N11移設/既full成功/原-v3へ二重計上しない。実費/実N-Tは不明ならnull。実現不能な候補はその範囲だけ保留し独立host作業へ進む。正式1964/53・工数null・QA051final保留、残>1継続/<=3保全/<=1停止・追加reset/課金0・副担当起動0を維持。

## 環境実績（2026-10-15 13:38JST）

208acafec/3210stage207b1a92、preserve42456/boot36105全actual0。fixtureQEMU445092/t3906100/argvf67196ed、new bootdd710ec8、全十Unit/Job/Main/Control0、別ownedforward64142/SSH171602-t3913396/local22224を実認証。Primary4599/boot79a/22222は不変更。JDK25.0.4/busctl、旧filesystem currentPG2654とapproval0400root0/hash7c22aaffをRO確認。これはLoaded a9を置いた正常配備ではなく、継承したforeign dataに対する独立negative fixture。旧042のexec/nativeは一切合算しない。

追加予定Test ID=PT-OPS-LFACT001～007。001 fresh owned、002 fresh owned epoch、003 resume owned、004 resume owned epoch、005 backup resume、006 fresh外側alias、007 resume外側alias。全て元仕様の厳密release拒否を検査し、業務callbackは呼ばれた時点でFAIL。各caseで独立inotify read witnessとD-Bus Manager GetUnitの監視barrier/no StartUnit-StopUnit等・DB/lock/permit不変を結合する。単なるIOExceptionやcoverage hitだけでは合格にしない。現caseコードはformatter済み未compile/未実行、環境成功をPT合格へ加算しない。
