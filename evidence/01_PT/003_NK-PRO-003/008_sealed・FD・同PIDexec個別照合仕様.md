# sealed・FD・同PID exec個別照合仕様（BUG1291未完）

WBS-P003-06、2026-10-15、Production a9/PG2802。全専有五path＝LinuxExecDescriptors、LinuxFileLock、LinuxProcessExec、LinuxSealedProof、LinuxStartupAdmission。全内部SAM/OwnedDescriptor/FdOwner/Lease/Identity/Attributes/NativeIoを各outer familyへ含める。485/hashと一致、専有RD空、終了依存P002-02は同source受入済み。counter100だけで受入しない。

正本origin/main756a891d9のSS343 SSC086/087・PG293/295/296/297補足（同PID/二FD/close-only/初期CLOEXEC/Root metadata/現在binding）、SS341/342と、既018/003/097/099/100/102/111の仕様を適用する。過去PG291～297文書の「未結線/未認定」は当時の履歴であり、現在低位host試験成功を現在Root/permit/業務全体成功へ拡大しない。逆に旧記述だけで現配備を未実装へ巻き戻さない。

## 全scope・Test ID・独立oracle

候補五Test各八methodに、LinuxFileLockのstartup側を検証するLinuxStartupFileLockTest八methodを加え、**計六class48実method**を原Storage23/163から対応付ける。ID/class/method/元ordinal/case名SHA/原XMLとTest byte hashはPG3316、現在未変更の当六Testが同byteであることを照合する。PG3326の是正後Storage163にも当六classが含まれるが、BUG1291のoracle未解消をその成功で隠さない。

| 全対象method群 / Test | 独立期待値・資源後条件 |
|---|---|
| LinuxExecDescriptors factory/withInherited/inherit/set / XFD001～008 | 異なる128～65535の借用二FD、初期GETFD=1→SETFD0を二個、callback後逆順SETFD1。全六syscall位置の-1/2や初期0で後段拒否・移行済みflag全復元、borrowed close/unlock0。IO/unknown/複合は独立Resource優先表、null/127/65536/同一FDは操作0。32独立pair×6call=192、実child同PID exec・独立Python GETFD0・util-linux flock競合20→child終了後0。root authorizationそのものではない |
| LinuxFileLock create/bind/heldPath/tryExclusive/acquire/locked/OwnedDescriptor / FLOCK001～008 | admitted held inodeをREAD+CLOEXECでopen、flock flags6、-1/errno11だけempty/callback0、他errorは固定UNAVAILABLE。OS flockとfcntlの非相互作用、外部flockと双方向競合、回復後再取得、元inode名置換に対する独立元byte3,5,8/置換byte1、32競合一winner・31rejected。callback null返却はNPE伝播・所有FD解放、IO/close/unknown複合も全owned一close/原因redaction、借用元handleは保持 |
| 同tryExclusiveForStartup/acquireStartup / AFD001～008 | open17→F_DUPFD_CLOEXEC1030/min128→reserved同OFD flock128→callback→close128→17のliteral順。dup -1/元17/範囲127/65536、全partial/各close失敗、unknown複合で所有済だけ一close、競合callback0。別sealed proof不変65,66,67、外部flock20→終了0、16競合一winner。従来MのtryExclusiveはdup0/FD公開0、callback7のまま。readonlyはkernel unlock権限attenuationではなくtrusted close-only契約 |
| LinuxProcessExec create/replace/vector/validate / EXEC001～008 | held ELFの/proc/self/fd正規形、argv1～64/env0～32、文字4096・key64境界、control/DEL/null/欠落/不正pathを拒否。日本語/空を含む四argv・昇順二env＋終端NULLを手書きliteralで検査、native全戻値は非成功、unknown identityとArena終端。実外部JVM→Python ELFは独立OS child.pidと置換後PID一致、準備envのみ・canary/PATHなし、exit0。**EXEC007の32並行は下記独立oracle不足のため未受入** |
| LinuxSealedProof create/bind/withProof/prepare/read/closeOwned / SEAL001～008 | 手書きNKSTART1＋公開fixture24byte、flags3/mode384/ADD_SEALS1033:15/DUPFD1030:min128、逆順二close。全create/write/seal/dup/close故障、size1/8192/0/8193、partial write/read各3byte・offset、seal全不正、empty/oversize/nativeerror、borrowed readはclose0。実memfd mode0100600/nlink0/四seal15・write/truncate/grow拒否・scope後read不可、32個の各入力PUBLIC-i byteとreadを独立照合。copy消去・Arena一scope、秘密byteを入れない |
| LinuxStartupAdmission create/withAdmitted/attributes/NativeIo/FdOwner/Lease/records / CHILDFD001～008 | 128/129別・初期CLOEXEC0→両1、proof root regular0600/link0/size1～8192/seal15、A root0600/link1/empty/readonly(flags0又は32768)・devino非0を手組metadataで検査。全field欠落/型・境界・各六syscall故障、proof IO/null/size不一致/close失敗、全unknown/複合時proof→A一close。callback前proof close、公開65,66,67byte、終端0消去、ready Leaseを32並行closeしてもA一回だけ。実ordinaryUID proofはroot metadataを偽造できず拒否、根拠不足を成功へ補完しない |

公開Test helperのFFM/proxyは実kernel観測・故障portのみ、private FD reflection/internal API/coverage除外なし。FactoryのLinux許可arch文字列検証は同host bindingであり実ARM機認定ではない。canonical fresh proof・boot/Unit/現在permit/BOM/role/原本/Root/owned停止はconsumerの別必要条件。本五低位能力のhost成功で実root権限や業務readyを発行しない。DB transaction/MQ再送は当低位scopeに非該当。

## BUG1291/YKT1057・独立反例（未是正）

修正前ac1e30afeで起票。PG3340-before/41858 actual0、固定75fd443f3、10:50:35.467266～10:50:40.224668Z。actual正常literal selector一件成功、正常並行一件成功、**同じ並行入力だけをargv/envともPRIVATE_COMMON_WRONGへ置換した私有shadowでもactual一JUnit成功**。falseNegative1、反例拒否0、PT/coverage新加点0。Production Main/Jar/lib/元Testは不変更・同hash、shadowだけprivate新classへcompile、元成功/失敗/全raw保全。

現Exec007は二actualvectorの相互一致と回数32を検査するが、各threadの独立入力fixture+iとの対応を検査しない。単なる追加propertyとして残せても、独立入力/並行取違えの受入根拠には不足。各threadの独立fixtureをcallbackへ別束縛し、argvとenvそれぞれを手書き入力からassertするTest-only是正が必要。normal literal/concurrent成功維持＋同私有誤実装がAssertionFailedError由来で拒否されること、関連Storage/必要一whole/native同byte資格まで未完。

YKT1057の他対象非該当根拠：XFD007は各pairの予約範囲・call総数/所有復元を検査しpayload routingを持たない、AFD007/FLOCK並行は同inodeの単一winnerと独立外部lock後条件、SEAL008は各taskの独立literal PUBLIC-iをreadと照合、CHILDFD007は同Leaseのclose一次性を独立closed一覧P,Aと照合する。Protocol P09は既d45aec8f1でUI由来独立384byteへ是正済み。検索だけ完了にせず、Exec007修正と実再発防止の残を維持する。

## 現在の判定

contract/scope全五pathは上記で照合、qualityはBUG1291が未完なので**NOT_ACCEPTED**。同sourceStorage四100/静的0・全3702成功/実native28が存在しても、このoracle不足を受入へ読み替えない。稼働3330の固定Testを変更せず、真正終端後の次是正群へまとめる。正式1964/53・工数null・QA051final保留・原/v3見積・全PGPT/ITST未完を維持。
