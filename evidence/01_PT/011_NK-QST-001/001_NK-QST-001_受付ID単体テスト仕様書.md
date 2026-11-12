# NK-QST-001 受付ID単体テスト仕様書

2026-10-28追加（Question command共通値P01103）：2410/2411・PT-CMD-TIMEBOUND-001～003、新QuestionCommandTimeBoundaryTest whole3。UTC0001/9999のmicro秒端点・submicro秒と負epochのfloorを独立UTC literalで確認、保存Message/Correlation不変更。旧DB同居ケースの抽出0、当Program全体/実DB/正式受入にはしない。索引evidence/command-time-boundaries/manifest.json。

2026-10-28失敗後回復追補：新`PT-QST-RNGREC-001～004`は[2397](../018_NK-OPS-001/2397_P011公開受付ID生成回復_単体テスト仕様書.md)へ一意参照。元RID001～008全件＋新四件を同source十二/二suiteで実施し、固定provider失敗後に別自己workerから同generator再利用/部分候補非流用を検証。公開受付IDは認証能力ではなく実key/session/credential/DB操作なし。元Testの固定public file一件だけfresh自己CWDへ許し、全集合/139byte/hashを独立検証する。source/run/TestID別索引は`evidence/public-receipt-recovery/manifest.json`。

PG-D-188。RD QST002/ASY001、UI224§3/236、SS312§7/331§6.1。対象QuestionReceiptId(value)とQuestionReceiptIdGenerator.create/generate、関連methodを各Test IDへ対応。質問受付DB/Outbox/再送/認可は別の未完了範囲。

| Test ID（PT-QST-） | method | 入力・操作 | 独立期待 |
|---|---|---|---|
| RID001 | exactAlphabet | 32文字を各26回反復、公開固定値を構築 | 全32候補を受理、value等値・hash・表示値保持。0..7だけへ狭めない |
| RID002 | lengthBoundaries | 0/1/25/27/4096文字 | 固定非秘密例外、26だけ許容、trim/padなし |
| RID003 | characterBoundaries | 全26位置に小文字/I/L/O/U/space/control/非ASCIIを注入 | 全拒否、NFC/大小case/曖昧文字置換しない |
| RID004 | independentRandomVector | 0..25次いで31..6の固定index列 | 0123456789ABCDEFGHJKMNPQRS / ZYXWVTSRQPNMKJHGFEDCBA9876（32文字表を独立計数し各26文字と照合）、32boundを毎回確認 |
| RID005 | randomFailure | 各0..25位置で同じ例外を注入 | 同一例外伝搬、残り乱数取得0、ID返却なし・fallbackなし |
| RID006 | nullAndFactory | value/null乱数port、公開factory生成 | null契約拒否、factoryは26許容ASCII、実乱数の一意性を確率的合格条件にしない |
| RID007 | concurrentCalls | 同一generatorに並行64呼出、固定cyclicindex port | 26取得のinterleaveなし、全返却値を独立通番oracleと集合/重複数で照合 |
| RID008 | equalityAndPublicEvidence | 同一/相異public値、失敗message、固定vector trace | 等値/hash契約・toString/診断はREDACTED・公開vectorのみ保存。表示用値はvalue accessorのみ |

期待値はProductionのalphabet/helperで作らず独立literal/BigInteger等の別算定を使う。正常/境界/異常/null/並行/例外を網羅。DB再送/衝突は本部品非該当として別writer仕様へ残す。constructorでinvariantを確立、NPEをcatchして成功にしない。新Java全line/method/class/branch100%、既存全回帰/静的解析と新scope整合が正式認定条件。実行日時/tool/commit/command/結果/hashは002とmanifestへ後記、未実行を合格にしない。


WBS-P011-01公開source契約/独立期待値/TestIDは[4095_P01101質問受付ID入力原三source契約対応.md](4095_P01101質問受付ID入力原三source契約対応.md)。metadataのみ、新PT/coverage/正式受入0。

[4096通常PT](4096_P01101質問入力原十六件と独立RID009含む全一五九通常PT仕様.md): source1e433/Main1cc、27170/27174全159成功/全191scope四100、元16と新RID009一件・第三KeyRingHOLD/原/2/451/正式未受入。


WBS-P011-02公開source契約/独立期待値/TestIDは[4097_P01102質問原子受付原source契約対応.md](4097_P01102質問原子受付原source契約対応.md)。metadataのみ、新PT/coverage/正式受入0。

[4098 既存受付ID回復通常PT](4098_P01101既存受付ID回復四件と関連九件通常PT仕様.md): 27204/27208同source13成功、Main2四100、既存4を新定義に加算0、元KeyRing/DB終了依存HOLD。


WBS-P011-03公開source契約/独立期待値/TestIDは[4099_P01103質問command時刻原source契約対応.md](4099_P01103質問command時刻原source契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P011-04公開source契約/独立期待値/TestIDは[4100_P01104Web受付参照原四source契約対応.md](4100_P01104Web受付参照原四source契約対応.md)。metadataのみ、新PT/coverage/正式受入0。
