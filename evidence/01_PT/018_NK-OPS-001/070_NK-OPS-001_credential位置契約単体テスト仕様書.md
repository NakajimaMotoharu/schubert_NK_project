# NK-OPS-001 credential位置契約単体テスト仕様書

Program NK-OPS-001、PG278。Class/method `ServiceCredentialLocation.read/directory/toString`。RD SYS-002/004、UI243/253、SS342 §4.2・343 §4/6、PT-OPS-CREDLOC-001～005。対象はsystemdがJava processへ渡す**非秘密のdirectory位置**だけ。実credentialの保持inode・owner・ACL・read-only・内容・version、実OS配布、Web/API mainは別gateであり、本仕様の成功に算入しない。Fixtureは合成Mapと公開pathだけで、秘密値を使わない。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-CREDLOC-001 | systemd正規keyと無関係PATH | 合成`CREDENTIALS_DIRECTORY=/run/credentials/schubert-nk-api.service`、PATHをread | pathは同literal。診断は固定`[REDACTED]`でpathを出さない。SS342のLoadCredential private directory契約 |
| PT-OPS-CREDLOC-002 | 必須・絶対・非root境界 | 欠落、空、相対、`/`を各read | 全て固定不正。SS343のprivate root・固定process起動前fail-closedから独立期待 |
| PT-OPS-CREDLOC-003 | 別名/曖昧path/制御文字 | lowercase/重複大小文字alias、`..`、NUL/CR/LFを各read | 全て同じ固定不正、環境実値を診断へ出さない。SS343の未知alias/placeholder拒否とcredential権限境界 |
| PT-OPS-CREDLOC-004 | 1～4096文字・null | 4097拒否、4096受理、null key/value、null Map | 長さ上限とnull契約を独立literalで確認。Map自体nullはNPEで正常化しない |
| PT-OPS-CREDLOC-005 | 不変snapshot/並行 | 8 thread×32 fresh Map read | 全て同じ公開固定Path。OS環境全体をcache/保持しない |

再送は位置値に非該当。正常/境界/異常/null/例外/並行を含む。Production methodでexpectedを生成しない。Coverage除外なし。選択commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage -Dtest=ServiceCredentialLocationTest test`。正式command、環境・branch/commit、coverage、実行結果、関連障害、証跡path/hashは071と同Program `evidence/manifest.json`/`results.xml`へ記録する。
