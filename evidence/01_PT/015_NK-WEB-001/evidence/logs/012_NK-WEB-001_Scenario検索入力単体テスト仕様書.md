# Scenario検索入力単体テスト仕様書

2026-09-20正式16で8PT認定済。実行結果013/manifestを参照。以下の未実装表記は仕様先行時の履歴であり、現在は013の正式認定を正とする。

NK-WEB-001/ScenarioSearchForm、FUN003/TST001～005、UI222§5/6・223§3・234§7、SS313/352、SSC072/PG199。HTTP非依存の入力snapshot・validation・typed要求生成。未実装・未実行、正式認定数へ算入しない。

| Test ID | method | 入力・操作 | 独立期待 |
|---|---|---|---|
| PT-WEB-214 | web214CanonicalRequest | 欠落/全7field、各game/type/voice、trim/NFC | literal optional/string/enum/page100要求値、AND条件保持 |
| PT-WEB-215 | web215ByteBoundaries | q/chapter256・speaker128 byteの前後、合成文字 | NFC後独立UTF8長で境界受入、超過error、切捨てなし |
| PT-WEB-216 | web216UnicodeAndEnums | control/不正surrogate/未知enum/HTML文字 | control/Unicode/enum固定error、通常HTML文字は表示用に保持・後段escape前提 |
| PT-WEB-217 | web217BindingAllowlist | 未知/空/大文字名、0/2値 | 未知・複数pollution拒否、typed要求なし |
| PT-WEB-218 | web218PageBoundaries | 空/0/負/1/999999/超過/int境界/overflow/plus/指数/全角/leading zero | UIの非正数1補正、正上限・grammar・int overflowを独立literal判定 |
| PT-WEB-219 | web219InvalidCannotRequest | 複数field違反、invalid要求生成 | deterministic closed issue集合、要求生成拒否・raw診断なし |
| PT-WEB-220 | web220NullOwnershipRedaction | null各境界、input list/map変更、返却変更 | null contract拒否、snapshot不変、固定toString、値漏れなし |
| PT-WEB-221 | web221ConcurrentValidation | 64独立入力並行 | 混入なし、各literal条件とpage一致 |

期待値はUI/SSの明示値と独立fixture文字列から作りProduction methodをexpectedへ使用しない。全新class/method/line/branch100%、NullAway/SpotBugs/既存回帰を要する。controller/MQ未接続のため「送信0」はinvalid要求生成禁止の境界に限定、HTTP全経路成功としない。013/manifestへ実行日時・command・commit・OS/JDK/tools・exit・input/expected/actual・coverage・BUG/SSC・hashを成功後保存する。
