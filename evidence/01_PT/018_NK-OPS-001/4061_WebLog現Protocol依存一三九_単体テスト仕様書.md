# WebLog 現Protocol依存139 単体テスト仕様書

Program NK-MSG-002 + NK-PRO-001～003 / WBS-P006-04・P002/P003。SS324§9/352 NKENC1、UI23523362336byte/QA054、451、BUG2648のProtocol修正後の依存再資格。CoreMain629/変更済Protocol8bの現byteをsourceへ一致させる。新Main/Test定義を追加せず、旧codec9の成功を新sourceへ移植しない。

対象: WebLogPayloadCodec全method/Identity.aad・uuidBytes/EncryptedPayload constructor/copy/redaction/PayloadExceptionとReason全code、package annotation。Protocol現176physical全体と既130ケースを同一runへ含める。

- PT-IDEM012015原codec9全method: UI独立byteoffset/2336 wire・DataOutputStreamのAAD8field・固定JCE envelope、NFC・REQUEST action QA054承認golden、Message/Correlation/row/keyVersion binding、tag/全範囲改変・不正wire/長さ/null、current/previous/unknown/close、caller clone/wipe、private lock/100nonce/200並行、自己所有JVM内JCA provider不足と復元。元25760の独立期待値・原9 sourceを保持する。
- Protocol原130全fixture: 26312の独立golden/byteoffset/typedsemantic/null/未知/境界とstrictUTF16 U16/PATH4の新6定義をそのまま使用し、依存3source修正後の176physical/163positiveCRCと基準100を保持する。expectedをproduction methodで作らず、独立期待値のコードを再利用する。ケース名のリストは実値oracleではなくTest ID inventoryとして扱う。
- 通常実行は全9+130=139、whole class選択のみ。28実JUnit classをcase集合から導出し、Java source/helperファイル数と混同しない。F/E/S/aborted/not-runを合格へ算入しない。

build/static: Web Main5source/6physicalはcurrentと同じsource/hashを持つ既normal出力・NullAway・Main PMD/Checkstyle・SpotBugs classStats6の指摘0を範囲限定再利用する。Web jar全体をhash/readせず、予め固定した6class payloadだけを読み、full182componentへ配置。actual4 entryは読取/hash/compile/initしない。Test9だけを現Protocol jar・6classでfresh compile、元Test static判定は同一source・同一rulehashで再利用。ProtoMain/Test/resourceの既現compile/counter/staticは固定byteを再利用し、単独130の確認再演はしない。

runtime: JDK25.0.4+7/JUnit1.13.4/JaCoCo0.8.15、自己所有単一JVM/並列off/session PG26686-WEBLOG-CURRENT139。component全182physicalをreport対象とし、標準record/enum/switch-map filterと自然noCode以外の手動除外/旧exec合算0。全positiveMain CRC・classinit・one-session・XML・六counterを独立postで照合し、line/method/class/branch各miss0を要求。source/run/環境/command/終了code/期待値・実値・hashはmanifestへ記録する。新coverageはこの139runだけから算出する。

command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1308_weblog_current_qualifier.py prepare`、1309独立preflight、固定Main/Test git sourceを指定して `run <commit>`。元9・現Protocol130の成功を算術加算して現139成功にせず、真正新XML/終端を必要とする。PG26678 compile0/PG26684 preflight0は製品PT PASSではない。

actual credential/鍵・原本・DB・JMS/broker・VM・Root・startup/service/permission操作0。原startupError経路/actualWebStartup依存等のP00604終了条件、全451/元190/正式認定をこの純粋codec群だけで閉じない。費用は着手前.25/.65/1.3pp cap2のSOURCE_REQUALIFICATION、元費用を保持し、専用実費はunknownのまま記録する。
