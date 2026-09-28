# NK-OPS-001 固定setpriv→Java引数 PT仕様（PG369）

対象予定class `FixedServiceExecArguments`のconstructor/`arguments`。RD SYS-002/004/OPS-009、UI212/251/253、SS311/342 §4.2/343、SSC086～089、471 R1/D04/D05。既存`LinuxProcessExec`/`LinuxExecDescriptors`の上位で、固定Web/API NSS `FixedServiceIdentity.Value`からのみsetpriv引数を組む。root preflight/許可、held ELF、環境allowlist、余剰FD消去、実Unit/execは別の必須gateであり、本classは実行権限を与えない。

| Test ID | 目的・fixture/input | 独立期待値 |
|---|---|---|
| PT-OPS-REXEC001 | Web UID998/GID980/groups980,982,986 | SS342 Web JVM exact options、`setpriv --reuid=998 --regid=980 --groups=980,982,986 --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs`、固定`/usr/bin/java`とWeb jar/class。shell/init-groups/env-secret/任意commandなし |
| PT-OPS-REXEC002 | API UID999/GID981/groups980,981,982,986 | 別のAPI JVM memory options、同capability drop、固定API jar/class、API group明示。Webと混同しない |
| PT-OPS-REXEC003 | null service/identity、不正ID境界 | nullはNPE、`FixedServiceIdentity.Value`既存invariant拒否。任意argv/config injection口なし |
| PT-OPS-REXEC004 | 同一builderの反復/並行取得・返却list変造 | 固定不変配列で同じ値。返却listは変更不可、credential/原本を参照しない |

期待argvはSS342のUnit Java行及びsetpriv公式option仕様から、Production builderを呼ばず試験内literalとして作る。`LinuxProcessExec`による同PID実測は既存PT-OPS-EXEC/XFD、真正root preflight/Unit外部受入は後続。JDK25.0.4/Maven3.9.12で`./mvnw -o -q -Dmaven.repo.local=<fixed> -Dnk.pt.repository=<tree> -pl src/schubert-nk-bootstrap -Dtest=FixedServiceExecArgumentsTest test spotbugs:check jacoco:report`。対象commit、JUnit/JaCoCo/hash/全回帰は次番号の結果へ。RED/failure/skipを合格に含めない。synthetic数値のみ、秘密情報なし。
