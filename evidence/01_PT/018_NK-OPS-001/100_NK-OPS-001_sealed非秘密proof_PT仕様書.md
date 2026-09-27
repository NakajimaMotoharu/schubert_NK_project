# sealed非秘密proof PT仕様（PG292、未認定）

NK-OPS-001、Storage LinuxSealedProof.create/withProof/prepare/read/closeOwned、RD SYS-002/004/OPS009、UI212/251、SS341/342/343、SSC086、471 D04/05。anonymous memfd固定名/CLOEXEC/ALLOW_SEALING、mode0600、四seal15、FD128～65535をcallback内だけ借用、全close/入力copy消去。root由来/現起動bindingの上位admissionが欠ければ本proofだけで起動しない。

| Test ID / JUnit method | 操作・独立期待値 |
|---|---|
| PT-OPS-SEAL-001 / opsSeal001LiteralBytesFlagsOrderAndScopedClose | ASCII literal NKSTART1＋public_fixture・LFの24byte、memfd flags3/fchmod384/write/ADD_SEALS1033:15/DUPFD_CLOEXEC1030:128、callback読取GET_SEALS1034:0、reserve→original逆順close各1、入力不変 |
| 002 / opsSeal002AllCreationSyscallFailuresAndCleanup | create/mode/write/seal/duplicate/両close位置の故障、write0/-1/超過、reserved127/65536。未取得FDをcloseせず、取得済みを全close、fixed UNAVAILABLE/cause・suppressedなし |
| 003 / opsSeal003ReadSealEmptyOversizeAndNativeErrors | seals-1/0/1/7/14/31拒否（読取0）、空/8193byte拒否、pread-1/超過拒否、実未割当FD拒否。借用readでclose0 |
| 004 / opsSeal004BoundaryAndPartialIoIndependentVector | 1/8192byte独立'a' vector、write/pread各3byte partial、8192まで全一致/正しいoffset、reserved65535境界 |
| 005 / opsSeal005NullAndPlatformContracts | null API/ctor6port、0/8193 length、127/65536FD、未知OS/arch・全6symbol欠落拒否、Linux3arch binding、input不正でIO0 |
| 006 / opsSeal006UnknownCompoundAndAllOwnedClose | callback ordinary/Runtime/Error×cleanup通常/unknown。ordinary＋cleanup unknownはunknown優先、同unknownの自己再throwもidentity維持、全owned close各1。優先は442独立契約 |
| 007 / opsSeal007RealMemfdModeSealsAndMutationRefusal | 実Linux memfd mode0100600/nlink0/24byte、4seal/read一致、write/truncate/growが全IOException、内容不変、scope終了後FD読取不可。host UID1000の低位試験でroot由来を証明しない |
| 008 / opsSeal008NativeConcurrentProofsNeverMix | 32 native proof/8thread、各独立public ASCII byte vector一致、CLOEXEC/reservation所有の混同なし |

native009別観点: 専用VM root、ProtectSystem=strict/NoNewPrivileges/ProtectHome/PrivateTmp下で、固定proc1rootから保持host runへNOFOLLOW open、native statvfs privateRO=true/hostRO=false、devino/mode/UID/GID同一。Java FileStoreはhost FDでもprivateRO=trueになるので現在host RWのoracleに使わない。test-only tool NativeHostViewProbeは全root/起動許可admissionではなく限定仮説試験。実行command/sourcehash/coverage/結果は101/PG292 manifestと環境424。Production Unitにはまだ変更を入れない。
