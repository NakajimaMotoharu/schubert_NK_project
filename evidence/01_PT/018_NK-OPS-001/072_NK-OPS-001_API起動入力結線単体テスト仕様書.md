# NK-OPS-001 API起動入力結線単体テスト仕様書

PG361追補（未受入）：`ApiProcessMain.startNative`にAPI借用credential→別profile JMS contextとDB pool事前probeを既存`ServiceProcessResources`所有scope内で結線。関連RD MQ-001/003/006/008・SYS-004、UI231/253、SS311/321§6/342/343、PT-JMS-024/025とPT-OPS-API-MAIN。独立期待は親root/A・設定・credential・DBを先行し、SYNC/Web Log各FQQN接続を検査してから業務runtimeを開始すること。現入口はその後`unassembledStartup`で必ず拒否し、実成功/readiness/停止後条件はまだ試験対象外。root/Unit/正規releaseを迂回したfixture起動を合格にしない。実外部受入時に同classのnative line/method/branch、失敗時全資源close、秘密非出力を追加PT・sanitized証跡で証明する。

Program NK-OPS-001、PG279。Class/method `ApiStartupInputs.<init>/load`、`ApiStartupInputs.Values`。RD SYS-002/004・MQ-001、UI243/253、SS342/343 §4/6、PG-D-276/278/279。Fixtureは公開非秘密YAMLを返す隔離sourceと合成systemd environment Map。実credential内容、DB/JMS・外部main・OS ACLは対象外。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-API-INPUT-001 | 手組common/API YAMLと2正規env | `load`1回 | source API指定1回、common DEBUG、API pool8、`/run/credentials/schubert-nk-api.service`をliteral照合。SS343層順/LoadCredential私有位置 |
| PT-OPS-API-INPUT-002 | credential位置欠落 | constructor後のsource呼数 | 固定拒否、source0回。秘密位置不在時に非秘密file読取を始めない |
| PT-OPS-API-INPUT-003 | source checked失敗とconfig path異常 | 2別fixtureをload | checked例外identity維持、config異常は固定redacted拒否・source0回。異常原因を混同しない |
| PT-OPS-API-INPUT-004 | null source/env/result field | constructor/Values | nullはNPE。NPEを正常・設定不正へ変換しない |

正常・異常・null・例外を含む。credential位置の境界/並行はPT-OPS-CREDLOC-001～005、YAML負例/並行はAPI-CFG/LOADへ追跡。再送は起動入力に非該当。Productionでexpectedを生成せず、coverage除外なし。選択commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api -Dtest=ApiStartupInputsTest test`。正式command/日時/commit/coverage/結果/BUG/証跡path/hashは073と同Program manifest/resultsへ記録。
