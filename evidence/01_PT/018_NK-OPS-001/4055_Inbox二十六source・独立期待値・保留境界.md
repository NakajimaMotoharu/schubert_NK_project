# P00601 Inbox 26 source・独立期待値・保留境界

Program NK-MSG-002 / RD MQ006010/FUN103105、UI213231236241242、SS324。origin/main設計の版・hashと26 owned source全hashはPG26616 manifest。

- CanonicalField/CanonicalRequest/OperationFingerprint/WipingByteArrayOutputStream：SS324§3 NKOP1 magic/LP各長big endian/順序、NFC UTF8、null FFFFFFFF/empty0、HMAC-SHA256。OperationFingerprintTest全5の固定hex/OpenSSL期待値を確認。SecretBufferTest全3の独立DataOutputStream/JCA、旧arrayと全capacityのzero、null/境界/例外の全文確認。まだ新current実行なし。不正UTF16置換の到達性は既globalYKT2328未解決対象であり、疑いを再現前の欠測として保存する。
- InboxRequest/Completion/Execution/ResultReference/BoundInboxExecution等：PT-IDEM004006/B01B04。owner N12と匿名、token8layout、参照tag union、日時/metadata/null契約、保存元PKの独立期待値。InboxModelTest全5全文確認。全Bound4/JDBC11は実DB/鍵classへ依存するためwhole HOLD、method選択で回避しない。
- JdbcInboxCoordinator/Consistency/MessageStageGuard：Message/token2検索、全identity/HMAC、23505 savepointの一回再読、caller TX commit/close非所有。readonly inspect一SELECT、snapshot置換rowlock/旧暗号全byte比較/件数1、retention初回completion基準、256fair lock/interrupt。PT-IDEM RO01RO04/SR01SR03、P00401/P00503 exit依存。actual Temporary/KeyRing/DB runtimeは保留、PG sourceレビューをPT PASSにしない。
- KeyRing/SnapshotCodec/ResultBoundCodecとidentity/value/exception：DAT009、SS324§6/15・352。version denyclosed/constant-time/wipe、NKENC1/JDKlevel3/AESGCM/AAD/1000000・1050000制限/NKREF1をsource照合。FingerprintKeyRingTest3、ResponseSnapshotCodecTest7、ResultBound8はwhole HOLD。actual class binaryの読取・hash・compile・initも行わない。

`python3 -B evidence/01_PT/018_NK-OPS-001/input/1284_inbox_public_contract_audit.py` は公開sourceと公開metadataのみの照合、真正終了0。新product実行0、新定義0、原625 /1 .087/.227/.455ppの期待値対応準備のみ完了。/2、元190、全451/正式認定は未受入。価格減額は工数率・専用実費ではない。日時/branch/core source/各Test source・定義数・未確認のoracle全文範囲/実行結果hashはPG26616 manifestを参照。
