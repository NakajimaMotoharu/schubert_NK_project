# 子2FD admission PT仕様書（PG297・未認定）

NK-OPS-001 / LinuxStartupAdmission.create/withAdmitted/attributes/FdOwner.close/Lease.identity-close/NativeIo、RD SYS-002/004・OPS009/UI212・251/SS342・343/SSC086・087、D04/05。
2FDは別128～65535。取得直後のCLOEXEC0を確認し両方1へ変更。proof regular rootUID/GID0/mode0600/link0/1～8192bytes/seal15、A regular rootUID/GID0/mode0600/link1/empty/devino非0、F_GETFL0またはO_LARGEFILE32768のみ。文法/current bindingはcaller別必須。borrowed公開bytesはcallback後消去、proofはcallback前close、Aはoutermost/readyでclose-only one-close。

| PT-OPS-CHILDFD Test ID | fixture/操作・独立期待値 |
|---|---|
| 001 | literal fcntl順序GETFD2→SETFD2→seal→flags、独立ABC3bytes/root metadata、proof129先close/A128後close、byteswipe/earlyready one-close |
| 002 | 全FD下限/上限外/同FD/nullはsyscall・close0 |
| 003 | 各fcntl故障・非inheritedflags・seal≠15・readwrite/path/append等拒否、O_RDONLYとLARGEFILE正常 |
| 004 | 両FD全7属性欠落/型/null、uid/gid/mode/link/size/device/inode境界、proof1/8192正常、unsigned devino保持 |
| 005 | byte数不一致/read/attrsIO/null、proof close失敗callback0/byteswipe |
| 006 | body/close通常・未知組合せ、identity優先/全取得owner各1、A readyclose失敗二重close0 |
| 007 | 8thread/32 readyclose＋outer cleanup、A closeちょうど1 |
| 008 | 全factory/native symbol/null/OS ABI、actual非root memfd/読取、未openFD拒否（root正系はnative015） |

native015独立工具はactual root context/A/sealed公開literal→同PID exec/setpriv→専用API UID/GID/明示groups/5caps0/NoNewPrivs→native child2FD→proof先close/A ready境界closeを実測。canonical current proof/全root/Ops/schema/業務readyは未認定。期待値はliteral syscall/OS/固定PUBLIC-ROOT-FD、production encoderから生成しない。112/provisional PG297へcommand/version/hash/results。再送はこの低位admission対象外。
