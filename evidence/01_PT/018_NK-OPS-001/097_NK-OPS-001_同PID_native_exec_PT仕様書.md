# 同PID native exec PT仕様（PG291、未認定）

Program NK-OPS-001、Storage `LinuxProcessExec.create/replace/vector/validate`。RD SYS-002/004・OPS-009、UI212/251、SS341 §3/5・342 §4.2・343のSSC086補足、471 D04/05、473。native-only Storageへ低位FFMを置き、root固有の固定command/UID/groups/gate検査は今後のlauncher所有とする。ここだけの成功を起動許可/R2/R3へ算入しない。`LinuxProcessExecChild`はtest-only外部JVM fixture。

| Test ID / JUnit method | 目的・入力・独立期待値 |
|---|---|
| PT-OPS-EXEC-001 / opsExec001LiteralVectorsAndArenaLifetime | retained `/proc/self/fd/17`、4 argv（日本語/空を含む）、順序違い2 env。literal argv、key昇順の独立2env＋各vector終端NULLを検証。戻り失敗後全arena dead |
| 002 / opsExec002EveryNativeReturnIsRedactedFailure | native戻り-1/0/1/int両端は全UNAVAILABLE/causeなし/suppressedなし、各1回。実Linux未知FD ENOENTも同診断、errno/argv/envを出さない |
| 003 / opsExec003InputNullAndPathContracts | raw path/他PID/負・符号・leading0・int超過・過長・child拒否、null API/collection要素/ctorを契約違反としてnative0回。外部processは固定診断で非成功とする後続gateが別途必要 |
| 004 / opsExec004VectorAndStringBoundaries | argv1/64成功側・0/65拒否、env0/32成功側・33拒否、文字4096/4097、env key64/65、NUL/CR/LF/TAB/DEL、空/lowercase/先頭数字/等号key。期待上限は仕様literal、Production methodでexpected生成しない |
| 005 / opsExec005PlatformAndSymbolContracts | Linux amd64/x86_64/aarch64 binding、未知OS/arch・missing execve/nullは拒否。native symbolの選択は内部固定、caller指定不可 |
| 006 / opsExec006UnknownFailureIdentityAndArenaClose | 注入Runtime/Errorは元identityで伝播しarena全close、正常失敗へ降格しない |
| 007 / opsExec007ConcurrentInputsRemainIndependent | 32並行・8thread、各独立argv/env文字値の一致と32 native呼出し。複数copy混同なし |
| 008 / opsExec008ActualReplacementKeepsPidAndOnlyPreparedEnvironment | 実外部JDK25 child→保持NOFOLLOW ELF `/usr/bin/python3.14`へexecve。OS child PIDと置換後`os.getpid()`が一致、exit0、1固定行以外出力なし。親に置く無害env canaryとPATHが置換後不存在。expected PIDはOS Process API、env/出力は独立literal。Production service/privilege dropの受入ではない |

事前条件: Linux x86_64、JDK25.0.4、保持directory/nativeアクセス、host Python3.14 ELF。fixtureは秘密0、DB/JMS接続0。実行は `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 PATH=$JAVA_HOME/bin:$PATH ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage spotless:apply clean verify`（shellの代入順は実際には絶対JDK binを指定）。Java4指標各100%、instruction missed0、NullAway/Werror/SpotBugs0、Failed/Error/Skipped0を限定合格条件とする。coverage除外/unknown正常化/無意味assertは設けない。結果098/manifest/hashと一意対応。未検証のroot実態・現在許可・A/sealed proof・schema/Ops・業務runtimeは後続で、現在Production mainは安全に拒否する。
