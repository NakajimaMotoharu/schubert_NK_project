# NK-OPS-001 Artemis実効role PT仕様

PG241。RD MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §10/13・342 §4、SSC-075/YKT-185。対象は稼働BrokerのCore管理`getRolesAsJSON`を用いる`ArtemisRoleReadinessClient.verify`と共有管理client。業務6 Addressと`activemq.management.#`の実効role/権限を、SS321 §10および承認済み`broker.xml`の固定表と比較する。アプリroleに管理権限を渡さない。JAAS user/password provisioning、個々の操作可否、Expiry purge、Queue閾値、journal復旧、親起動の代用にはしない。

| Test ID | 事前条件・fixture・入力/操作 | 独立期待値と根拠 |
|---|---|---|
| PT-OPS-MQ-016 | 隔離Artemis2.56.0を実security有効、Ops credentialで起動。7 matchの実効role JSONをOps Core managementで読む。アプリroleも管理を試す | SS321 §10固定表のWeb/API/maintenance/Ops権限だけが存在し、全queue/address create/deleteや余分なsend/consume/manage/view/editは拒否。借用session開、一時返信Address残存0。アプリrole管理拒否 |
| PT-OPS-MQ-017 | 独立literal role JSONの7 matchを1役割/1権限ずつ欠落・過剰・未知role・重複・空へ変異 | 各matchのrole集合と13 permission booleanが固定表に完全一致しなければ拒否。期待表はproduction parserから生成せずSS321/`broker.xml`の表で構築 |
| PT-OPS-MQ-018 | null reader/session/JSON、壊れたJSON・型誤り・provider/encoder/cleanup fault、borrowed session | null境界はconstructor/verifyで拒否、外部値異常は秘密causeなし固定redacted例外。共有2秒管理reply/cleanup契約を維持。failed/skippedは合格にしない |

正常時の許可集合: `nk.sync.request` Web send/API consume/Ops browse、`nk.sync.reply.web` Web consume/API send/Ops browse、`nk.async.work` API send+consume/Ops send+browse、`nk.web.log` Web send/API consume/Ops browse、`nk.dead.letter` Web+API send/Ops consume+browse+manage、`nk.expiry` maintenance consume+browse/Ops consume+browse+manage、`activemq.management.#` Ops send+consume+manage+createAddress+deleteAddress+createNonDurableQueue+deleteNonDurableQueueのみ。各役割の列挙外permissionはfalse。`nk_ops`実credentialは管理専用でapplicationへ流用しない。

PG/PTを並行し、選択Batch test、Batch全PT/coverage/static、正式全reactor、018 collector/全scope/hash、負canaryを実行。日時/OS/JDK/tool/branch/commit/command/exit/input/expected/actual/coverage/関連台帳/hashは045とmanifestに固定する。credential/password/raw session/tokenを保存しない。検査は起動前Ops session直列実行。管理要求失敗時は上位起動を中断し再試行、業務message再送は本単位の責務外。
