# 1702 Web media stream metric 単体テスト仕様書

実行経路追補（2026-10-24、期待値不変更）：BUG1671の前提工具是正により、7730元正常compile→7740 metadata-only→7741 receipt guard→7742初回普通35/5→7744独立post。7732の結果serialization障害BUG1672は7750で元architecture両exit0/出力を回収（再解析0）→7734/7736/7738へ結合。旧7726はpre-begin failure/PT未開始、7728はUNRUNのdraftで成功に含めない。元計画の経路は履歴保持、真正結果/hashは1703参照。

NK-OPS-001/P01809/C07/RD171/UI252/SS333§11～13/SS351§6・8/PG-D563/group1922。MediaStreamsMetricRecorder constructor/record/missing/snapshot/detailedMetricsRequested/private value。既ProtocolのMediaTypeはAUDIO/VIDEO/MUSIC literalだけのpure enumで全source初期化を読取済み。新classは供給active stream数のGauge表示だけで、実media open/close/認可/Range/file read・HTTP/Browser/JMS/DB/Root/配信上限の変更をしない。

DEBUGは`nk_media_streams`/Gauge/label`media_type`だけ、AUDIO/VIDEO/MUSICの固定3seriesを事前登録、初期/欠測NaNと真0を区別。STDは登録/保持0、既HttpMetricContractのstrict mode契約を再利用して未知modeをechoしない。値は独立非負long、16/20/21等を勝手にclamp/加算してadmission結果を捏造しない。LongMAXはsnapshotに原値保持、SDKdoubleの表示丸めは明示する。metric観測自体は実20 stream admissionや16 warningの受入ではなく、外側source/lifetime/警報は別未受入。AtomicReferenceのOptionalLongを一回取得してvalueへ渡し、present/getの二読競合を作らない。registry lifetime/同名namespaceはcaller所有、部分factory失敗後の残meterをretry/closeで解消したとしない。

| Test ID / method先頭 | 入力・操作/独立期待値 |
|---|---|
| MEDIASTREAM001 / mediaStream001 | 手書3labelと1metric/型Gauge/label key1/全pair、初期全NaN・snapshot empty/登録3/close0 |
| MEDIASTREAM002 / mediaStream002 | AUDIO1/VIDEO7/MUSIC19独立、全typeで0/16/20/21を原値表示、MAX long保持とdouble9.223372036854776E18、系列不変 |
| MEDIASTREAM003 / mediaStream003 | AUDIOだけmissing→NaN/empty、他2/3と旧OptionalLong1不変、再missing後真0回復 |
| MEDIASTREAM004 / mediaStream004 | STD全type記録後も保持/登録0、null registry/mode・空/小文字/未知modeは既strict契約で拒否 |
| MEDIASTREAM005 / mediaStream005 | 両modeのnull type/record/missing/snapshot・負-1/MINは既観測を消さず拒否、DEBUG既7保持/close0 |
| MEDIASTREAM006 / mediaStream006 | 第2Gauge factoryのRuntime/Error同一identity/呼出2/残1/NaN/close0、caller finally close1 |
| MEDIASTREAM007 / mediaStream007 | 64callerを3type別の入力集合/独立double集合へ照合、完了後fixture100/101/102の最終公開も確認、別owner MUSIC99/他unknown/3系列ずつ不変。Production accessorからexpected生成0 |
| MEDIASTREAM008 / mediaStream008 | foreign Counter同seriesを置換せず例外、同一meter/値7/close0 |

期待値はSS/既MEDIA1024型のliteralと入力fixture scalar/集合から独立。Production hash/methodで期待値を生成しない。新generated型なし、既Web5型14methodを当ordinary/実byte/JDKへ別結合。正常六reactorで全Main/Test compile-package後、その**同source**のWeb test/main/六Jarと実外部classpathで明示5JUnit classだけ普通実行する。古いM2 internal snapshotはexternal集合から除外し、既Jarや旧27の結果を新sourceへ流用しない。固定launcher5class/35case・skip/abort/container失敗0/単一JaCoCo sessionを元XMLと独立postで照合、四100/NullAway-SB-CS/PMD全理由を検証する。テスト発見のためunknown/Root classを試し実行しない。

元製造新8＋必要既Web27を当35/5suite・10Java/実10＋metadata1予定、全1767Main/113source/98追加physical・旧111src不変2新予定。7730正常六compile/PT0→7726普通JUnit→7728独立→7732全Jar→7734trace→7736review→7738公開scan、1703結果へsource/run/日時/OS-JDK-tool/branch/command/actual exit/XML/input/CRC/四counter/static/BUG/hashを結合。全六Jarがclasspathにあっても選択対象は既安全4class＋新pure1classのみ、actual Root/サービス/networkは起動しない。

開始3/5/9pp上限10/fresh2/98/reset1793382075、旧markerlast27との区間/共有累積・専有N-T/工数null、元90/原-v4-v5/usagecursor再基底化0。正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLD維持。導入/install/M2上書き/券消費/課金・実VM/DB/JMS/Root/key/配備/実stream/HTTP/Browser操作0。
