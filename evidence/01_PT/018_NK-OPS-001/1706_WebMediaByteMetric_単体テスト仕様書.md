# 1706 Web media byte metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252/SS333351/PG-D565、MediaBytesMetricRecorder constructor/record/statuses/detailedMetricsRequested、Mode.parse/values/valueOf。新MEDIABYTE001..008＋必要既Web43を当51/7で普通実行予定、source固定後7770正常六compile（classpath metadata明示）→7772普通JUnit→7774独立四100/CRC/static→7776全1770→7778全117/101trace→7780生成既14＋新Mode2/current ordinary/raw全理由→7782公開scan、1707結果へ全hashを結合。

SS351 `nk_media_bytes_total`のlabel name3だけ、既MediaType3×内部の閉Mode3（INLINE/DOWNLOAD/RANGE）×既MediaRangeService/WebMediaAuditの終端status4（200/206/416/503）=36counterをDEBUG事前登録、STD詳細登録0。modeはSSのInline/download/Range三分類を内部閉enum化した供給観測であり、disposition/Range/header/実HTTPからの判定hookを本群で追加しない。認証/業務API段階の401等は既HTTP metricの責務で、このdelivery-only部品へ自由statusを通さない。bytesはcaller供給非負long、負/null/未知mode/statusは両modeで例外、zeroはbyte増分0であって観測不在/要求成功ではない。binary64丸め/MAX、provider部分加算を保持し、実配信量/受信ACKやexactly-once/再試行を捏造しない。

| Test ID | 入力・操作/独立期待値 |
|---|---|
| MEDIABYTE001 | 手書3type/3mode/4statusの全36系列・Counter型/label key3・初期0、任意ID/URI/body labelなし |
| MEDIABYTE002 | 全pairへ1/2/0を供給して3、MAX longをbinary64へ明示丸め、別pair不変・系列増0 |
| MEDIABYTE003 | Mode手書三literal→各typed定数/strict parse、空・lowercase・未知/null拒否、values配列分離/全valueOf/未知/null、status固定四と返却List不変。生成2methodは独立直接契約 |
| MEDIABYTE004 | 両modeでnull type/mode・未知status直前直後/範囲外・負-1/MINを拒否して既値不変、STD詳細0、constructor null/未知mode拒否 |
| MEDIABYTE005 | 第2counter factory Runtime/Error同一identity、登録2/残1/close0、caller finally close1 |
| MEDIABYTE006 | increment前/増分済み後のRuntime/Error同一伝播・呼出1・補償/再送/close0、partial増分はそのまま非成功 |
| MEDIABYTE007 | 64fixtureの供給pair/byteから呼出前に独立集計した全36期待値、並行結果/有限future・別owner7独立、系列36不変 |
| MEDIABYTE008 | 同seriesのforeign Gaugeをcounterへ置換せず例外・同一meter/値7/close0 |

実stream/HTTP/Browser/Range解析/file/JMS/DB/Root/VM/配備操作0、既endpoint/service/audit/SS期待値の変更0。既pure enum/SDKだけを通常PTで使用、未知class初期化probe0。provider failureをcatch/format/graphwalk/再試行/正常化しない。registry lifetimeはcaller、namespace/filter/source/asOf/terminal byte真正性と実hookは別未受入。

開始3/5/9pp上限10はfresh receipt→event1926へ保存（実eventを照合）、共有旧markerlast27区間/累積・専有N-T/工数null/元90再基底化0、原-v4-v5不変更。期待値は固定literal/fixture scalar集合、production methodから生成0。実日時/OS/JDK/tool/branch/source/command/actual exit/input/期待/実際/coverage/関連BUG/hashは1707と元manifestへ記録。正式1964/53/QA051final/PTALT0/whole451-native-CHR/actualHOLD維持。
