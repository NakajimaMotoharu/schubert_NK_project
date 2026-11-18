# SSC-456 Storage固定名称の単体テスト仕様書

NK-OPS-001、UI243/253、SYS-002/004、SS342／343 §6.4／SSC-081、A2-29.01、P003-07、BUG-3226／YKT-2675、451。元PT-OPS-CREDID-001～004とPT-F03-ENUM-STO001の五件および元期待を保持する。

PT-OPS-CREDID-005はSSの固定名称十件を独立入力とし、正規lookup、未知・空・余白・表記差・null、forService null例外と固定診断を確認する。PT-OPS-CREDID-006はKindの固定二名称、順序、値配列の防御コピー、未知・nullを確認する。元二service隔離・固定順と新境界の全7件を同じ単位で実行する。

Java25/MavenでStorageのMain 25と物理79を正規build。位置が変わるclass、元javac用switch helperの消滅、public ABI、単一execの全raw、XML、初期化を独立照合する。期待はSS固定入力とTest literal。実credential、配置、実OS・JMS・DB・並行service処理は対象外。各command、環境、exit、結果、hashはmanifest。
