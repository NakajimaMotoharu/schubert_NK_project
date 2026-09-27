# Host read-only SPI / 起動A能力PT（PG293、未認定）

Program NK-OPS-001、RD SYS-002/004・OPS-009、UI212/251、SS341/342/343、SSC086/087、471 D04/05。
対象はStorage `LinuxHostDirectoryCalls.create/openRoot/openDirectory/openEntry/close` と全mutation拒否、`LinuxFileLock.create/tryExclusiveForStartup/acquireStartup/locked`。通常Mは従来のFD非公開契約を維持する。

| Test ID / JUnit method suffix | 事前条件・入力・操作・独立期待値 |
|---|---|
| PT-OPS-HOST-001 FixedKernelAnchorAndNativeFlags | root UID fixture。固定 `/proc/1/root`、flags589824/mode0だけopen。Arenaは退出後無効。PID/proc由来はcaller別必須 |
| HOST-002 NoFollowChildrenAndOwnedCloseForwardOnly | 子directory/entry/closeを既存NOFOLLOW SPIへ同FD/名前でforward、literal呼出順。新root以外のmagic-link例外0 |
| HOST-003 EveryMutationRefusedWithoutDelegation | file/directory/private作成、publish/unlink/syncの全7経路を拒否。delegate mutation0、固定UNAVAILABLE、原因/suppressed0 |
| HOST-004 UidGateAndNativeFailureNeverFallBack | UID -1/1/1000/65534/MAXはopen0、UID0/open-1は固定失敗。private root fallback0 |
| HOST-005 UnknownFailuresKeepIdentityAndArenaClosed | injected Runtime/Error元identity、Arena消費、再試行0 |
| HOST-006 NullPlatformAndSymbolContracts | constructor/factory null、未知OS/arch、missing open拒否。Linux amd64/x86_64/aarch64固定binding |
| HOST-007 ActualOrdinaryUidCannotOpenHostAnchor | 現host非root UIDでactual create/openRoot拒否（root環境なら試験失敗、skipしない）。root正系はnative010で別実測 |
| HOST-008 ConcurrentScopesKeepOnlyOwnPointers | 32 callback/8thread、各自pointer寿命・close/結果一致、capability共有なし |
| PT-OPS-AFD-001 ReservedSameOfdScopeAndReverseClose | admission済みheld `/proc/self/fd/9`。literal open17→dup(1030,min128)→flock128(flags6)→callback→close128→17 |
| AFD-002 ContentionAndOtherNativeErrors | flock -1/errno11のみempty、他errno4/9/22/37と未知戻り拒否。競合callback0、逆順close |
| AFD-003 EveryPartialAcquisitionClosesOnlyOwnedDescriptors | open-1、dup -1/元FD17/範囲127/65536、各close失敗。取得済み所有FDだけ1回close、二重close0 |
| AFD-004 UnknownAndCompoundFailurePriority | 通常/unknown body × close通常/unknownを442契約literalで判定。元unknown優先、残所有FDもclose、秘密診断なし |
| AFD-005 InputNullMissingPortAndBindingContracts | null/不正held/dup port欠落/missing fcntl拒否、上限65535正常、入力違反syscall0 |
| AFD-006 RealNativeFlockAndSeparateImmutableProof | actual readonly Aの予約128以上と別sealed proof FD。独立util-linux flock競合exit20→callback終了後0、proof四seal15/不変公開bytes |
| AFD-007 ConcurrentOnlyOneCallbackOwnsA | 同一NOFOLLOW temporary inode、16競合、保持中winner1/callback1、終了後取得可能 |
| AFD-008 ExistingOrdinaryMaintenanceScopeNeverExportsFd | 従来M callback literal7、dup0、FD非公開、通常解放後取得可能 |
| PT-OPS-XFD-008（強化再試験） | test-only childでProduction A→sealed proof→限定inherit→native execを合成。Python独立oracleはsamePID/FD128・129 GETFD0、proofseal15/public20bytes、競合20→子終了後0。通常UID prototypeでroot authorizationではない |
| PT-OPS-NATIVE-010 / NativeHostDirectoryProbe.main | 隔離VM root・ProtectSystem=strict/no-new-privileges/Home/PrivateTmp下でProduction host SPI→保持run native statvfsはRW、privateはRO、unix dev/ino/uid/gid/mode同一。実Unit/proc由来/現在permit/A全gateは未認定 |

期待値はliteral syscall/順序、独立OS kernel/Python/flock観測で算出し、production処理からexpectedを生成しない。fixtureは公開synthetic inode/bytesだけ。全null/失敗/境界/並行と借用/所有の寿命を検査、業務再送は対象外。実行command/version/commit/hash/counterは103とprovisional PG293 manifest、旧PG291のhelper/hashは履歴として変更しない。
