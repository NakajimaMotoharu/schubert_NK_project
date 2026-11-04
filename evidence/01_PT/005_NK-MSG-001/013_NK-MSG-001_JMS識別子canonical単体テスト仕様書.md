# NK-MSG-001 JMS識別子canonical単体テスト仕様書

対象はAPI JmsMessageGuard.read/parseUuid、Web JmsReplyDecoder.decode/parseUuid。RD MQ008、UI232 §3/6、SS321 §8、SS322 §5、BUG2263/YKT2008、着手凍結692。独立期待は既存仕様のlowercase canonical UUIDとwire/property完全一致。最初の期待・操作は692へ実行前凍結し、本書は原再現後に集約した。

| Test ID | class/method | 入力・操作 | 独立期待・根拠 |
|---|---|---|---|
| PT-JMS-CANON-001 | JmsMessageGuardTest#identityPropertiesMustRetainExactLowercaseCanonicalUuidText | 既own JMS proxy・有効request。NKMessageID/correlationをliteral lowercase二UUIDへ設定、一回read。各fieldへuppercase/短縮/部分短縮/前space/後spaceを一個ずつ置換、計11 vector | 正規形だけ受理し二metadata文字列がliteralと一致。他十入力はPermanentProtocolException。UUID数値同一でもUI232の完全一致を満たさない。 |
| PT-JMS-CANON-002 | JmsReplyDecoderTest#identityPropertiesMustRetainExactLowercaseCanonicalUuidText | 既独立LOGRSP01 S/S、data24/total280 golden。wire byte24/60へliteral二UUIDを書き込み、propertyも同値。各field同五alias、計11 vector | 正規形でbody全byteとliteral correlationを保持。十aliasはPermanentProtocolException。byte offsetはUI232の1起点25/61より計算、production encoder不使用。 |

期待値はliteral `0000000a-000b-000c-000d-00000000000e` / `0000000f-0010-0011-0012-000000000013`。正常/境界・null/欠落/空/未知値・route/body異常は変更対象に対応する既6 Testずつも全件実行する。各新methodは有限2×5表を完走し正常1+異常10、計22 vector。並行/再送は本helperが無状態であることと既body snapshot契約を保持し、実broker/transactionの受入は含めない。

環境はtoolchain JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/PMD7.28/Checkstyle14.3。原実行PG18634は旧Main6b53・新Test二methodを選択、compile0/unit1/2failureを保持しPASSに算入しない。PG18636は二Main＋二Testのcompile/format/CS0、PMD raw10はthread専有Map/standalone definingloader/Proxyの同一identity equalsで局所非該当。全体F03のゼロ指摘ではない。

修正sourceのcommit固定後、同じdriver greenで二全class14 Testをfresh実行し、実XML/終了0と二対象physical classのline/method/class/branch未達0、exec/CRC/session/Sourceと独立期待を照合する。NullAway/必要全Main build等は別の真正結果で確認し、未実行を合格扱いしない。初回実行command・入力hash・原XML・環境・sourceはPG18634/18636と693のmanifest。Green/coverage/再試験結果・修正commit・証跡hashは014へ記載予定、現在未実行。旧sourceの成功coverageを新二Sourceへ転用しない。
