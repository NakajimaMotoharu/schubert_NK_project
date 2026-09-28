# 237 NK-OPS-001 ready未通知成功拒否PT仕様（PG359）

Program ID NK-OPS-001。対象 `ServiceStartupAdmission.execute/ReadyOnce` とAPI/Web両ProcessMainの共通起動gate。RD SYS-002/004・OPS-009、UI212/243/253、SS342/343§6・SSC086/087、BUG-320/YKT-252。Production業務assemblyはまだ未結線で、実Process readyをこのPTだけで認定しない。

| Test ID | 事前条件・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-STARTADMIT-009 | 正当なAPI/WEBの固定公開packet・子identity/config/release観測で、configured/unconfigured callbackをready呼出なしでreturn | SS343の「readyまでA所有」から、正常returnを非成功IOException、ready release0、最終A close1。公開diagnosticに秘密を含めない。修正前RED1PT/F1を保全 |
| PT-OPS-STARTADMIT-010 | ready一度成功後の二重呼出、未ready return後に逃したcallback、正常ready return後の逃したcallback、ready release時のIOException/Runtime/Errorを業務が捕捉してreturn | 既定一回以外を非成功、FD final close1、release失敗を成功へ転換しない。完了後の遅延releaseを拒否。callback失敗/秘密値を露出しない |
| PT-OPS-STARTADMIT-001～008 | 既存順序、null/欠落、NSS/config/release/proof、並行32scope、native FD拒否 | 既存SS343の入場順・最終closeを維持 |

期待event順とrelease回数はSS343§6の「readyまで保持、失敗はcleanup後close」から手書きし、Production method出力でexpectedを生成しない。Null・欠落・未知は001～008、例外・再入/遅延は009/010、並行は008で網羅。実行環境Linux/JDK25.0.4/Maven3.9.12、branch`dev-foundation`。限定command `./mvnw -o -f src/schubert-nk-bootstrap/pom.xml -Dtest=ServiceStartupAdmissionTest test spotbugs:check jacoco:report`。共通security gate変更なのでsource固定後、Production6 clean test/static/coverageを実行し、結果、対象commit、全4指標、エビデンス/hashを238へ記録。未組立API/Web native mainや実NK CHRを合格に加算しない。
