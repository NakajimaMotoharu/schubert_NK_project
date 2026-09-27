# 限定FD継承PT仕様（PG291、未認定）

NK-OPS-001、Storage `LinuxExecDescriptors.create/withInherited/inherit/set`、RD SYS-002/004・OPS-009、UI212/251、SS341/342/343、SSC086、471 D04/05。所有済みで入場済みのA/proofを借用し、FD128～65535の異なる2個、初期FD_CLOEXECだけを検査する。inode/readonly/seal/fresh許可/UID/secret cleanupは別root gateの必須責務であり、本処理の合格だけでは起動を許さない。

| Test ID / JUnit method | 操作と独立oracle |
|---|---|
| PT-OPS-XFD-001 / opsXfd001ExactlyTwoFlagsRestoredInReverseOrder | 128 GETFD→SETFD0→129 GETFD→SETFD0→callback→129 SETFD1→128 SETFD1のliteral順。callback正常も元flagsへ戻す。scope正常はexec/起動成功ではなく、exec前にkernel観測するための操作契約 |
| 002 / opsXfd002EveryNativeFailureAndPartialTransition | 全6 syscall位置に-1/未知2、GETFD0（初期CLOEXEC欠落）を注入。後続callback拒否、移行済み全flagsを逆順復元。close/unlockは0（借用FDの所有を奪わない）。fixed UNAVAILABLE/cause・suppressedなし |
| 003 / opsXfd003IoAndUnknownBodyPreserveOwnership | callback IOExceptionは固定失敗、Runtime/Errorは元identity、全復元順序維持 |
| 004 / opsXfd004CompoundCleanupUnknownPriority | 通常body＋復元unknownはunknown優先、bodyと復元が同unknownでもself-suppressionを起こさず、残FD復元。期待優先は442 Resource契約、Production expected生成なし |
| 005 / opsXfd005NullDescriptorAndBoundaryContracts | 127/65536両FD、同一FD/null拒否、128/65535境界正常scope、実Linux未割当FD拒否。入力違反でnative0 |
| 006 / opsXfd006PlatformAndSymbolContracts | Linux3arch binding、未知OS/arch・missing fcntl/null拒否。fcntl command1/2、variadic signature内部固定 |
| 007 / opsXfd007ConcurrentDisjointCapabilities | 32独立pair・8thread、各6 native/復元、合計192、caller所有capability間の混同なし。共有FD同時close/reassignはtrusted caller禁止契約 |
| 008 / opsXfd008RealExecInheritsSameFlockUntilProcessExit | test-only childが保持NOFOLLOW temporary empty inodeをread-onlyで再open、F_DUPFD_CLOEXECにより128/129を所有予約。actual `withInherited`＋`LinuxProcessExec`でsame PID Python ELFへexec。Pythonのfcntl GETFD=0と独立PIDを検査。root側のutil-linux競合exit20、子stdin release/exit0後exit0。2FDは同OFD test fixture、sealed proof/root gateそのものではない |

fixture `LinuxExecDescriptorsChild`はmain/test隔離で、実JDK25/Linuxとpublic temporary bytesだけ使用。秘密/DB/JMSは0。初期child syscall open/dup/flock/closeはtest-only FFM。negative/compound/parallel/境界は独立literal matrix。実行・対象commit・version・全Storage coverage・結果は098/PG291 manifest。起動許可/A物理owner/admission/sealed proof/root全gateは未実装、R2/R3へ加算しない。
