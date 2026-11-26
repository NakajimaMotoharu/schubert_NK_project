# Backup終端行の読み取り境界

NK-BAT-001、OPS-009、UI251、SS331 §8.3・SS341 §6.6・SSC134、WBS-P017-06/2。対象はBackupStepRepository.readTerminalと返却Terminalの値契約。

| Test ID | 合成入力 | 独立期待値 |
| --- | --- | --- |
| PT-BAT-TERM001 | 14列をJDK ResultSet proxyが返す。固定run/handle、SUCCESS・1/1/0/26、終端時刻 | 全14列の型を固定順に読み、借用rowのclose・nextを呼ばない。各成分、空診断、固定文字列、値等価とhash lookupを確認。 |
| PT-BAT-TERM002 | SKIPPED、合成 handleのskip=true、4counter 0、ALREADY_SUCCESSFUL固定診断 | 期待の終端・理由・4counterを保持。skip=falseのhandleではSQLDataException。 |
| PT-BAT-TERM003 | ID・run・日・step・attempt・開始・現在より未来の終了を一つずつ変更 | それぞれ正規handleと照合不一致でSQLDataException。 |
| PT-BAT-TERM004 | 未知status/理由、負counter、開始前の終了、raw診断不一致 | 成功に変換せず、未知行値を診断に転載しない。 |
| PT-BAT-TERM005 | 必須12列を各NULL、Java引数の不在 | DB行のNULLはSQLDataException。Javaのnonnull契約違反は入口で拒否。 |
| PT-BAT-TERM006 | Terminal値constructorへ非Backup step、skip/result不一致、診断code不一致 | 型と意味の不一致を拒否する。原データの所有権を変更しない。 |

既PG45674はJDK代理の16でouterの未到達4行・8分岐とnested Terminalを残した。元16と新6は現正規三JARの同一runで測定し、既実行と生counterを合算しない。支持型の不足は別に残す。実運用のDB、原本、退役、ファイル操作、保留ISSCOMPはこの試験に含めない。

PG45826は22件成功、TerminalのhashCodeだけ未測定。BUG-3933で単一不変MapからJDK HashSetを使う照合に改め、独立に読み取った等価の二値で登録と検索を確認した。同じ正規三JAR・一つのexecによるPG45828は22件成功、outerとTerminalの四種生測定の未到達0。実JDBC／所有権移転は未確認。 [再試験](evidence/PG45828-current-backup-terminal-real-hash-twenty-two/manifest.json)
