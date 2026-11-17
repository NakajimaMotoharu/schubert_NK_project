# BackupManifestCodec 単体テスト仕様

NK-BAT-001、WBS-P017-05とF03。SS333/343、SSC058、451、BUG-3213、YKT-2664。元035のPT-BAT-186～193、値試験を含むwhole16と手書goldenを不変で使用する。新PT-BAT-186-NAMESPACEはfinal class、private constructor、static fields/methodsを確認し、専用fixtureから1回だけ呼び、固定 `AssertionError("static namespace")`、causeなし・追加例外なしを確かめる。アクセシビリティはfinallyで元に戻す。

試験CWDは新規の自有作業slot。既存fixtureの相対 `target/backup-manifest-traces` に合成JSONだけを記録する。動作、レコード、DB、配備、権限、鍵は本試験に含めない。対象Main/Testと依存のSHA、コマンド・環境・数値終了、元goldenの一致、全物理Code及び試験数はPG38220以降の公開manifestに記録する。新しい例外は内部型の不変条件に限り、encode/decodeの契約は不変。
