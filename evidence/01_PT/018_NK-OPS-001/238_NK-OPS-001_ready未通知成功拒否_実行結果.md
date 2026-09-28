# 238 NK-OPS-001 ready未通知成功拒否PT結果（PG359）

状態: BUG-320の共通起動gate直接修正とAPI/Web横展開限定PTは成功。実Production Web/APIの業務assembly、R2/R3、全4指標100%は未認定。仕様・独立oracleは[237](237_NK-OPS-001_ready未通知成功拒否_単体テスト仕様書.md)。関連RD SYS-002/004・OPS-009、UI212/243/253、SS342/343§6、SSC086/087、BUG-320/YKT-252。

2026-09-28 JST、branch`dev-foundation`、source/test/spec/台帳commit `081279909`。Linux kernel7.0.0-34-generic、JDK25.0.4、Maven3.9.12、SpotBugs4.10.4.0、NullAway0.14.1、JaCoCo0.8.15、Node24.19.0。`ServiceStartupAdmissionTest#startadmit009...`を修正前に実行し、format修正前の未実行exit1と区別して、意味あるRED1PT/F1（ready未通知正常returnなのにIOExceptionなし）を確認。修正後、同suite10PT F/E/S0、SpotBugs0。API/WEBのpacket別未ready returnを拒否、正常readyは維持。二重release、callback脱出後呼出、IO/Runtime/Errorが業務内で捕捉されても非成功、最終A close1を確認。新`ReadyOnce`の限定JaCoCo missed instruction/branch/line/method/classは0/0/0/0/0。

共通security/起動所有境界の変更で、456へ事前triggerを記録し、同source固定でProduction6 `JAVA_HOME=<JDK25> PATH=<JDK25/Node24優先> ./mvnw -o -q -Dmaven.repo.local=<固定toolchain m2> -Dnk.pt.repository=<本tree> -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean test spotbugs:check jacoco:report`を実行、exit0。全357suite/2,445PT、failed/error/skipped0、静的6module0。Module別Protocol80/17、Storage149/21、Bootstrap177/22、API744/123、Web555/85、Batch740/89。

JaCoCo XML missed branch/line/method/class はProtocol0/0/0/0、Storage0/0/0/0、Bootstrap37/11/4/0、API1/19/3/0、Web1/19/3/0、Batch21/267/102/12。全Production100% gate不合格。Raw XMLはGit外targetのみ。全357 XML path順SHA256列のSHA256 `8ac5197e66c0fe778f00489ab61d3d7a7fe1c5407163a93f303ae12afd625e2a`、STARTADMIT XML SHA256 `39fb1b2d954f480ccaa9107e8d8ec9e71fdb96d5ed5c6430f4c90a65fdf96beb`、Bootstrap JaCoCo XML SHA256 `b70d1a6e8f0920c6d3169c27e6c34ec9cf5171d435dd08e7fb6d88b1119e82b3`。sanitized manifest `evidence/provisional/PG359-ready-required/manifest.json`。

BUG-320の直接原因は修正・再試験済み。YKT-252はAPI/Web実業務callback、外部mainの実readiness/正常停止/故障後条件まで未完了。正式認定source`858713c0bf310ae8bf62078b0a1cedbce4e968db`/run`PT-WEB-20260925-24`/1964PT/53scope、全体中心48.3%（42～54）据置。実NK CHRは未実行。
