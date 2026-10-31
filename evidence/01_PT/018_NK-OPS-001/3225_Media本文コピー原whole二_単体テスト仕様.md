# Media本文コピー原whole二・単体テスト仕様

2026-11-01/PG-D1035/Production6b53/normal14216/dev-foundation/開始HEAD8a44a792f6f526b94a98c6bb82caf8d8a9661d4c。NK-MED-001/FUN005～007/PER004～006/UI237/SS333§10～11、既Program009仕様MED006/007を適用。全原Test184行/Main39行読取、主F03/基礎P009-04参照追加0、開始0.5/1.5/3共有pp cap10・専有費/N/T/工数null。

PT-MED-006: Test生成byte(i*17+3)の自己TempDir synthetic.bin1,048,580byte、offset3・length0/1/65536/65537/1048576の独立Arrays.copyOfRange、write最大65536/正確な出力長/position=3+length/caller source・target非close/nonflush。手書きChannel最大read3/offset5/length12と0length position100も検証。
PT-MED-007: source/target null、負offset/length/Long.MAX+1、size外/size・position・read・write IOException/read0/EOF、固定message/cause無し/suppressed0/資源非close。二回目read故障は先頭三byteだけ残り成功扱いしない。NPEを正常catchしない。

Testのみ自己一時fileをwrite/open/close、Productionは借用SeekableByteChannelのsize/position/readとOutputStream.writeだけでfile open/close/flush/permit取得をしない。実原本・media認証/保持inode/LinuxDirectoryCalls/秘密鍵/Root/VM/DB/JMS/HTTP/Graph・実回収/退役/配備0、既held全体からの部分抽出0。TempDir等の資源利用があるためpure-value共有v3のscopeを緩めず専用postで正直に開示する。

原whole二を変更せず一回実行、Target MediaBodyStreamer全1Source1physicalのline/method/class/branchを除外/人工到達/exec union0で測定し未達は保持。独立oracleはSS333とTest literalのみ、Productionからexpected生成0。checked16572→16574受動whole/CRC/四held六native/Root27不在→16576独立→同Source registry/WBS。F/E/S/flaky/notrunは加点0、manifestに環境/command/時刻/branch/commit/exit/input期待/actual/XML/coverage/hashを保持。実media/Range HTTP/認証・Program全体・正式1964/53/歴史17/190/QA051final/HOLDへの昇格0。
