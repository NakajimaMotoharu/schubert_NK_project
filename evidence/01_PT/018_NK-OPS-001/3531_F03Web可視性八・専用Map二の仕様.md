# F03 Web可視性八・専用Map二のsourceレビュー仕様

NK-OPS-001/F03、Main28af。計画895、原.5/1.5/4pp cap5 ordinary。RD SYS002004/MON003/OPS009/DAT009、UI212243251253、SS321/343/342/352、各Main classの既存責務に追跡する。

PT-OPS-VIS10-001: WebNativeRuntime replies/replay/retry/http/managementの5 raw。全field宣言・書込・全読取・ownerLock/stop/ready/healthyを照合し、単一reference公開と複合graph受入を区別する。
PT-OPS-VIS10-002: WebManagementServer.startedとArtemisReplyConsumers.stopping/startedの3 raw。書込lockとlock無しread、one-way flagの可視性・AtomicBoolean併用・正常return/未知停止を照合する。実provider・JMS/HTTP/worker/closeは実行しない。
PT-OPS-VIS10-003: ReleasePayloadVerification.jars/checksumsの2 raw。全map参照・二つのnew owner入口・同期call順・Contentsへのmutable map非exportを確認する。HashMapという名前だけでは除外しない。実file/hash/signature/Rootは実行しない。
PT-OPS-VIS10-004: 元1491 raw/ordinalと先行327・今回10・残1154の完全非重複partitionを独立postで再構成、unique1439/duplicate52組、全Main/POM/JAR・source範囲・canonical設計原文hashを確認する。MorningDatabaseSession volatile7は全状態機械の根拠不足で未分類に保持する。

期待値は承認SSとMainの全writer/reader構造・元rawから手書きした024各reasonであり、production methodを呼ばない。実行は env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run evidence/01_PT/018_NK-OPS-001/input/024_f03_visibility_map_decisions.json、次に同post。未使用PG19850へ一度、Pythonのmetadata読取保存のみ。Java/fixture/PT/解析再演なし、追加抑制なし。

動的並行/unknown/provider/ownership後条件は各rowに未実施として保存し、PASS/coverage/正式受入へ換算しない。全F03/451未受入、正式1964/53・技術46・原80結合16/元282交差28・新leaf0・工数null不変。証跡PG19850のmanifest/review、実環境・日時・HEAD/hash/終了はmanifestと3532参照。
