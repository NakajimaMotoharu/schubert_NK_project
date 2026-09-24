# NK-OPS-001 service credential reader単体テスト仕様書

Program NK-OPS-001、PG281/SSC-081。Class/method `ServiceCredentialReader.<init>/read`、`ServiceCredentialException.<init>`、共通低位`InspectorCredentialLoader.readService/readOptional/readFile`。RD SYS-002/004、UI243/253、SS342 §4.2・343 §6.1～6.4。fixtureは非特権private temp file/実Linux保持inodeと、明示して注入する合成root所有/対象UID ACL/readonly metadata。実systemd managerが配布したcredentialを読んだと扱わない。全入力値は公開PT専用合成byte、結果内に秘密値・raw session等を残さない。返却byteはcaller排他所有、試験のfinallyでzero fill。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-CREDREAD-001 | SS342両Unitの固定10 ID、手組ASCII passwordと32byte zero key形式 | service別に`read` | 各fileの手組byteと返却byteが完全一致。root/file属性前後2回、content open/close各1、操作buffer消去。ID/形式はSS343/076から独立転記 |
| PT-OPS-CREDREAD-002 | API root、Web ID・null契約 | cross-service/null/ctor null | Web IDはcontent IO前に固定redacted拒否。nullはNPEで正常化しない |
| PT-OPS-CREDREAD-003 | 欠落/symlink/directory | DB固定IDを読取 | 全て固定拒否、content open0。保持entryのtype先行検査 |
| PT-OPS-CREDREAD-004 | synthetic root/file ACL/readonly故障、実非特権file | KEY読取 | 不正metadataはcontent open前拒否。実非特権fileをroot-manager正系と偽認しない。§6.2/6.3 |
| PT-OPS-CREDREAD-005 | KEY 0/53/70、password 0/65537、device/late inode改変 | KEY/PASSWORD読取 | ID別54～69/1～65536、same-device、前後metadata一致。不正は結果なし、close完了。§6.1/6.4 |
| PT-OPS-CREDREAD-006 | IO port故障8種 | open/read/short/zero/size前後/close/root後変化 | 全て固定拒否・一時buffer消去・部分結果なし。既存Inspector共有経路の故障契約 |
| PT-OPS-CREDREAD-007 | entry close故障とborrowed root | KEY読取・root再使用 | close失敗を成功扱いせず、readerは借用rootを勝手に閉じない |
| PT-OPS-CREDREAD-008 | 同一固定公開KEY、32 independent task | 8 threadで各reader/read | 全返却は同じ手組byte、各返却array独立所有・消去。共有mutable secret cacheなし |

正常/境界/異常/null/例外/並行を網羅。再送はfile readerに非該当。ACL内容期待はSS343の固定Linux UAPI goldenを既存PT-DB-INBOX-113～140へ追跡し、本PTではその政策を実reader経路へ結線確認する。Productionからexpected生成しない。coverage除外なし。選択commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api -Dtest=ServiceCredentialReaderTest test`。正式command/日時/branch/commit、coverage、結果、関連BUG/SSC、証跡path/hashは079と同Program manifest/resultsに記録する。
