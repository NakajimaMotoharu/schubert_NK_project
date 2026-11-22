# NK-MED-001 Media三namespaceの静的検査と通常試験仕様

WBS-F03/2-2-b／P009-04、SS333／352／354、451 §5、YKT-2863。現Web同candidateの五Main、13実行対象物理とProtocol5補助を使用する。HTTP、実FileStore、外部環境、保留試験は含めない。ローカル所有の一時fixtureのみ使い、終了時空を確認する。

| 証明ID | 対象と独立期待 |
| --- | --- |
| PT-MED-STATIC001 | HttpByteRangeParserがfinal／private constructor一件、他memberはstatic。 |
| PT-MED-STATIC002 | ContentDispositionFactoryがfinal／private constructor一件、他memberはstatic。 |
| PT-MED-STATIC003 | MediaBodyStreamerがfinal／private constructor一件、他memberはstatic。 |

三項目はclassfileの `javap -p` で証明する。旧private反射3件は履歴とし、coverageと通常選択へ加算しない。旧PG41260の残25を同選択で保持する。Rangeの正常・境界・416、公開reason値、表示用headerと自己所有fixtureは元期待を維持。25のうちfixture試験1は製品試験に含めない。新単一execのJDK、CRC・生coverageを旧結果へ合算しない。再現コマンド、全選択case、元のhash、静的証明はPG42914／PG42916の公開manifestで追跡する。
