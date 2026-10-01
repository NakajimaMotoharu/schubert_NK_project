# NK-OPS-001 Root起動世代接続 単体テスト仕様書

関連: RD SYS002/004・OPS009、UI212/251/253、SS342§4.2/343§6.15/6.17、SSC137・D04/05。全試験は未実行から開始し、先行TDD失敗を障害扱いしない。Production同Sourceのhost/native coverageを採取、除外追加なし、四指標100%未達を明記する。

追加依存/採取計画（S3同接続、実装前）：ROOTELF001～006はpublic ELF64/LE/x86_64固定hexと独立CLI SHA、typed Unix全field/ACL・security.capabilityのENODATAのみ不存在、EOF/無進捗/例外/byte寿命/unknownをhost検証。ROOTPROOF001～004は17fieldの手書き全frame/固定NSS/A三値を期待値とし、service/binding/nullを負検証。ROOTTICKET001～004は実Root三値の全相違・当回intent/旧intent拒否・欠落待機期限を検証。ROOTUNIT001はAPI RequiresにExpiry無し・After順有り、普通5credentials不変更を固定text oracleで確認。Root実gate/native→held setpriv→同PID API50と全通常cap0/2FD再消費を次外部観測とする。Root成功execは旧JVMのshutdown hookを実行しないためdumponexitだけでRoot全coverageを採取できない。部分agent dumpを成功全coverageへ混ぜず、同Sourceの真正kernel execve拒否の負系（候補strace -Dの当回Root第2execveへEACCES、Unit MainPID/自己gate/全kernelを維持できた場合のみ）で全Root実gate/FDと失敗closeを採取する。未成立ならnative fault/coverage未達を保持し、Productionをtest hookで置換・除外しない。ordinary側は自role本来のJVM/own config/private5 credential/DB/JMS/ready契約を別検証する。

LAUNCH001～006: 手書きNKLAUNCH1全byteと固定SHA/明示fieldを独立oracleとし、API/WEB encode/decode・末尾LF/順序/未知/欠落/非ASCII/非canonical数/zeroUUID/zeroInvocation/null/境界/長さ/全field差/非秘密toStringを検証。ownerは既存独立NKMAINTOWNER1 literal、実permit SHAは明示64hexでありrecord自体をauthorityにしない。

LAUNCHFILE001～006: 合成tmpfs/rootはfixtureと明示し、保持実file/root属性・new-only/readback/force/dirsync、既存artifact不変、当回epoch/owner/service/permit/child三値の全一致、古いcanonical artifact保全、part/intent/未知名拒否を確認。IO/close/未知identity/null/並行/異threadと変質時は発行成功0/修復0を要求。Production encoderでexpectedを生成しない。

ROOTLAUNCH001～006: 手manager/kernel固定vectorsから、真正Morningだけが対象API/Web Rootの二読一致を取得し、当回自世代であることを確認。別PID-start/Invocation/boot/cgroup/manager drift/死親/期限を拒否。parent A正常close→commit→owner→start正常client→Root観測→ticketの順、未知delivery保持、全private観測close後にだけexecを要求する。

S3実VM終了条件: 外部同Morning M/原本/正規issue→A後owner/実Root ticket→全native gate→sealed proof/A二FD→同PID/startTicks/Invocationを維持してsetpriv/Javaへ置換。ordinary UID/GID/全group/五cap0・秘密/host FD非継承を独立kernel観測。同Source各実exec/class mismatch0。ordinary未assembly50は非成功/cleanup/DONE無しを要求し全readyへ加算0。全業務ready→API/Web/Caddy→done0/10→全close→真正Morning0/10とcompleted restartは別受入。FAILED-GC/UNKNOWN/hard-timeout/M最終close不明負系は残契約として追跡する。

実command/OS/JDK/branch/Source/実行日時/終了code・結果/coverage/BUG/YKT・manifest/hashは298へ実測後に保存する。現時点の実行・coverage・受入は未達。
