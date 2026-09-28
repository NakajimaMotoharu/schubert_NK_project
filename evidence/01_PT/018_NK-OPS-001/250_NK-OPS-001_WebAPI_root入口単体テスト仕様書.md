# NK-OPS-001 Web/API root起動前段入口 PT仕様（PG370）

対象予定class `RootServiceLauncher`の`main/run/preflight`。RD SYS-002/004/OPS-009、UI212/251/253、SS311/342 §4.2/343、SSC086～089、471 R1/D04/D05。未完成のroot issuer/permit/A/proof/FD/execve/Unit/業務readyを成功にしない。固定Web/APIのroot actor→固定NSS→現行承認releaseの読取順を開始入口で明確化する。`RootReleaseAdmission.create`はrelease/OSのみでschema/permitを証明しない。

| Test ID | 目的・fixture/input | 独立期待値 |
|---|---|---|
| PT-OPS-RMAIN001 | 固定`WEB`を合成Admissionに渡す | WEB一回呼出、全gateが戻ってもexit30。起動成功0を返さない |
| PT-OPS-RMAIN002 | 固定`API`を合成Admissionに渡す | API一回呼出、exit30。Webと混同しない |
| PT-OPS-RMAIN003 | 引数0/2/小文字/任意option・空 | Admission呼出0、argv拒否exit70。service選択口を2 literalへ固定 |
| PT-OPS-RMAIN004 | Admissionの既知IOException | raw causeを出さずexit30。NPE等programming failureは成功に正規化しない |
| PT-OPS-RMAIN005 | null引数/null依存、反復呼出 | null契約で拒否、状態/permit発行のcacheなし |
| PT-OPS-RMAIN006 | public main/非公開constructor、Production preflightの固定依存をsource構造確認 | root context→NSS→releaseの順。未接続の実root/同PIDは合格に含めない |

期待exit codeと呼出順はSS342の失敗閉鎖/固定2 service及びMorning既存外部entryの30/70契約から独立literalで定義し、Production関数でexpectedを作らない。JDK25.0.4/Maven3.9.12で`./mvnw -o -q -Dmaven.repo.local=<fixed> -Dnk.pt.repository=<tree> -pl src/schubert-nk-batch -Dtest=RootServiceLauncherTest test spotbugs:check jacoco:report`。実行source/結果/hashは後続251に保存。外部VM/Unit、main `System.exit`を同JVM PTで合格に読み替えない。秘密fixtureなし。
