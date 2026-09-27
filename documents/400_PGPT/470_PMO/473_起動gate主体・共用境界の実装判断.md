# 起動gate主体・共用境界の実装判断（SSC084）

## PG299継続：現在permitと既存morning接続review

2026-09-27、既存Astra/high補助1名への対象限定read-only review完了。親が採用する順序はM→MaintenanceRunFiles原本start/resume→固定対象停止→A→全Invocation/cgroup終端再確認→新epoch INVALID確定→DB/schema/advisory lock/run原本照合→実backup→成否依存cleanup→独立transfer→Broker→Expiry stage commit確認→実purge/after観測→terminal commit/readback→全root/Ops/schema/Broker/current step照合→permit公開→ISSUED(epoch,digest)確定→A解放→API/Web ready。未実装をFAILED/SKIPPEDへ置換せず、実走査対象0件だけ正当な成功とする。

MaintenanceRunFiles.complete/.doneは後続Caddy/smoke等のmorning終端後なので、permit発行前提にはしない（循環）。当日begin skipped=trueも現在run/boot/BrokerのExpiry証拠ではなく、実成功attemptを特定・再照合する接続が必要。現在原本は/run専用namespaceとし、永続root専用DurableRecordFilesやMaintenanceRunFiles namespaceへ混在しない。再発行ごとに新epoch、INVALID確定前mutation0、ISSUED不確定はA内完全一致readback時だけ確定、欠落/破損からpermit/DBによるISSUED復元は禁止。/run原本はbackup/切戻し対象外で、旧permitだけの復元を拒否する。rootが現在原本まで同時に巻き戻す運用をファイルだけで防げるとは主張しない。R2でtimer/update/reboot全体の受入を残しても、起動前backup/cleanup/transfer省略や初回保守免除は導入しない。全結線・実NK受入は未完了。

## PG294着手前：root/child bindingの最小契約review（SSC086/087）

Astra/high read-only限定reviewを採用する。kernel proc/PID1/system manager/boot/自己PID-startticks/固定Unit MainPID-InvocationはA前の由来確認、A直後のidentity再確認、exec直前の同一性確認に分ける。固定system bus照会のみを使用し、環境由来bus overrideは使わない。

公開packetはversion/固定field名/順序を含むcanonical ASCII LFとし、service・boot・Invocation・同PID/startticks・既知の予約A FD/devino・release/config/root/Broker/current permit bindingを束縛する。proof予約FDはseal後に割り当てられるためpacketへ入れず、番号を128/129と推測しない。子は狭い2FD入力を検査し、両CLOEXEC成功を必須として、rootUID/GID0・regular0600・nlink0・size上限・seal15のproofだけを読む。AはrootUID/GID0・regular0600・link1・empty・readonly FDとpacket devinoを検査する。実flock取得はroot固定発行経路＋同OFD継承の信頼契約であり、属性だけの証明としない。

子の独立再観測は自己boot/Unit/PID/startticks/固定service UID-groups-zeroCaps、読めるrelease/config/app rootだけ。Ops・root私有root・root-only permitは真正なfresh root proofの検査結果として受領し、子への再読権限や秘密を増配しない。root全secret/JDBC/JMS close失敗ではexec0、子失敗時はbusiness cleanup後Aを最後にcloseする。

現在permitにはrun activationと別の現在epoch原本を必要とする。同run resumeや再発行でepochを再利用せず、root現在原本のepoch/digestとpermitを一致させる。変更前失効が未確定ならmutation0、crash/不確定publishは拒否。旧permit復元/古いactivation流用は不合格。現在原本はbackup/切戻しから復元せず、復元・再設定もM/A内で旧許可失効→新世代発行する。この契約と実クラッシュ/古いpermit復元試験を満たすまで全起動を許可しない。実装は未完了、進捗加点なし。

## PG291着手前：SSC086の同PID privilege phase

PG292/SSC087追補（host adapter code前）: Astra限定reviewはhost FS後発RO remount/古いpermit bind/別A inode/最終service能力の4反例を提示。VMのNativeHostViewProbeをProtectSystem=strict/NoNewPrivileges/PrivateTmp/ProtectHome下で実測した。native保持host `/proc/1/root`→NOFOLLOW runはRO=false、private runはRO=true、devino/owner/mode同一。一方Java FileStore(host held FD)はcanonical pathをprivate namespaceへ解決しRO=trueで、最初の仮説試験は不合格。native statvfsに切替えた009だけ限定成功。この事実からsandboxを緩めず、root専用read-only host DirectoryCallsで現在host状態を検査する。PID1/boot/proc由来・A cross-namespace・permit可視性のadmissionはまだ未実装。root actor以外への能力配布/FS policy緩和はしない。Source/SS変更はSSC087先行、Mは従来RWのまま。

VM試験007/008で同OFD/readonly/CLOEXEC/固定group/zeroCapsを実測したが、shell試作品はProductionへ移さない。Java直接root前段→native execve(setpriv固定引数)→Java固定service後段を選び、まずStorage native exec境界と独立argv/env oracle・実外部execをPG/PT並行で作る。次にA/sealed proof/現許可/全root/Ops/schemaを同経路へ追加する。未完成部分は拒否のまま、Unitは受入前に変更しない。

Astra/high限定reviewの採用条件: Mは親全体、Aは起動観測からreadyまで。同PID execでSCM_RIGHTS/ACKは不要。親はA取得後に固定全対象のInvocation/cgroup終端を再確認し、A内で旧許可失効後だけ変更、必要工程後だけ新許可を確定する。旧Expiry成功だけを保守終了としない。全設定/release/root/Broker/鍵変更もAを守る。起動はA取得前に業務資源0、A取得後はread-only。!はSupplementaryGroupsも解除することと、readonly Aはkernel上LOCK_UN可能なtrusted能力であることを明示する。これらはSSC086としてcodeより先にSS正本へ反映済み。RD/UI公開挙動/秘密配布/最終service権限は不変更。

2026-09-27。471の同一受入R1～R3を阻止する内部依存だけを対象とする。Astra/high補助1名の読取reviewを親がSS/code実物で照合。新しい受入分母や進捗加点は作らない。

1. SS321 §10/342 §4の管理readinessには専用Opsが必要だが、SS343/Unit/catalogはAPI/Web各5秘密だけ。普通serviceへmq-opsを加える方式は禁止。SS341のroot起動順controller内で独立管理sessionを所有する。
2. SS343のbackup0700/Artemis0700/staging0700は他主体の私有root。API/Webで6rootを開くことは不可能で、modeを緩和しない。既存StorageRootInspectionの型/SDS/dev/inoだけを全owner/mode/ACL保証へ読み替えない。root管理側で全配置を、app側で許可rootと保持能力だけを検査する。
3. WebLogApplicationRuntimeは内側DB/JMS probeより先にreply/replayを開始する。必須外側gateを完了してからruntimeへ入る。ServiceDatabaseAdmissionだけではschema/Flyway一致は保証されない。
4. Web parserのDB/MQ5key欠落はBUG261/YKT195で修正。共通sourceへ移さずweb.ymlの正規service設定として扱う。
5. API-localのcredential/JDBC部品をWebから参照/複製しない。共用bootstrap artifactの責務は厳格byte material/保持inode reader/固定role JDBC admissionに限定し、業務repository/HTTP/JMS認証modelを移さない。Storageのnative-only/no-JDBC制約は維持する。artifactとpackageの具体変更・全coverage/collector移行は着手時に追記する。

root→service gateの最小契約候補: 固定/run namespace root所有・app書込不可、bounded canonical regular/link1、NOFOLLOW保持inode/ACL前後検査。固定unitとfresh実Invocation/boot/release/config/root identities/Broker invocation/実Expiry outcomeに束縛し、再起動は毎回新規。時刻だけ・static OK・Inspector receiptの流用は禁止。親は既存maintenance排他とconfig/root/broker安定を観測→公開→子admissionまで保持、start不確定なら子の実終端を確認前に排他解除しない。子はgate欠落/古い/不一致/cleanup failureで非acceptingを維持し、独自singletonをshutdownまで保持する。本候補は未実装であり未認定。実runtime healthは別途継続する。

環境確認: host UID1000、systemd system/user running、sudo -nはinteractive認証が必要。unshare -Urは成功したが複数service UID/root所有配備を証明していない。host既存/etc/Unit/権限へ勝手な変更はしない。privileged隔離配備の最小手順を具体化した段階で、必要ならQAを先行起票して利用者へ支援を依頼する。現時点は独立実装・非特権の限定PTを継続できるため全体停止しない。

## 共用artifact具体化（PG289、着手前）

PG290着手前追補（SSC084/D01・02・05）: API-localの所有scopeを共用`ServiceProcessResources`へ移し、固定Service/credential location/DB URLと各module専用PoolFactoryだけを借用入力とする。Web→API production依存/秘密増配を作らず、同一所有・消去・例外規則を再利用する。共用artifactのHikariはpool寿命型だけの依存、API最大8/min2・Web最大2/min1の生成は従来の各module factoryに残す。共有scopeは業務runtime開始の許可ではなく、未結線mandatory gateを依然拒否する。共有fixtureで両固定role/部分失敗/並行・nullを先に試験、実LoadCredential/SCRAMはVMで別検証する。

着手後の確定差分: RequiredColumnは移動対象から外し、業務APIへ残す。共有11classと9suite/2fixtureの実ownerは`tools/quality/bootstrap_ownership.py`の固定catalogで管理する。ServiceDatabaseAdmissionは自身のSQL NULLを固定08001へ拒否し、業務API libraryには依存しない。既存Production poolとの結線はAPI側Resource PT、shared sourceの全物理接続は独立Hikari fixtureで試験する。

`schubert-nk-bootstrap`をStorageの後、API/Webの前に置く。資格情報のstrict material/保持inode reader・固定role JDBC admission/sourceだけを移動し、Storageはnative-only/no-JDBC、業務API・HTTP/JMSは各moduleに残す。既存binary/package/Test IDを維持するため移動対象の`dev.codex.schubert.nk.api.file/maintenance/bootstrap/database`名は互換名として保存するが、artifactにAPI業務class/起動entry/DB migrationを含めない。WebのProduction依存はこのbootstrapだけで、業務APIへのtest-only依存は既存PT用途のまま。package名を理由にartifactの実依存を混同しない。

移動対象: InspectorAesCredential/DbCredential/CredentialAccess、AesCredentialFile/InspectorCredentialException/InspectorCredentialLoader、ServiceCredentialException/Reader/Set、ServiceDatabaseAdmission/Source、RequiredColumn。単体suiteと共通試験fixtureも同artifactのtest scopeへ移動し、既存API/Web PTが必要とする公開試験fixtureのみtest-jar経由で参照する。production循環・複製は作らない。内部配置変更でRD/UIの外部仕様/資格情報配布/権限は不変、SSC084範囲内。

POM/common security境界の横断変更に該当するため、移動後は変更moduleの全PT/coverage/静的解析と既存負canary・実owner照合を先に実行し、451全回帰を次の業務結線より先に実施する。正式run triggerは「SSC084 shared artifact/POM横断変更」、対象R1 D01/02/05。歴史証跡のpath/hashは書き換えず、新source/runにのみ新ownerを適用する。
