# NK-OPS-001 Web起動入力結線単体テスト仕様書

Program NK-OPS-001、PG279。Class/method `WebStartupInputs.<init>/load`、`WebStartupInputs.Values`。RD SYS-002/004・AUT-002、UI243/253、SS342/343 §4/6、PG-D-276/278/279。Fixtureは公開非秘密YAMLを返す隔離sourceと合成systemd environment Map。実credential内容、DB/JMS・外部main・OS ACLは対象外。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-WEB-INPUT-001 | 手組common/Web YAMLと2正規env | `load`1回 | source WEB指定1回、common DEBUG、Web port8080、`/run/credentials/schubert-nk-web.service`をliteral照合。SS343層順/LoadCredential私有位置 |
| PT-OPS-WEB-INPUT-002 | credential位置欠落 | constructor後のsource呼数 | 固定拒否、source0回。秘密位置不在時に非秘密file読取を始めない |
| PT-OPS-WEB-INPUT-003 | source checked失敗とconfig path異常 | 2別fixtureをload | checked例外identity維持、config異常は固定redacted拒否・source0回。異常原因を混同しない |
| PT-OPS-WEB-INPUT-004 | null source/env/result field | constructor/Values | nullはNPE。NPEを正常・設定不正へ変換しない |

正常・異常・null・例外を含む。credential位置の境界/並行はPT-OPS-CREDLOC-001～005、YAML負例/並行はWEB-CFG/LOADへ追跡。再送は起動入力に非該当。Productionでexpectedを生成せず、coverage除外なし。選択commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-web -Dtest=WebStartupInputsTest test`。正式command/日時/commit/coverage/結果/BUG/証跡path/hashは075と同Program manifest/resultsへ記録。
