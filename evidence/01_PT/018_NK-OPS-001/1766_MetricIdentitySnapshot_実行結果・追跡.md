# 承認済みmetric名snapshot 是正PG/PT結果

NK-OPS-001/RD171/UI252/SS311351/411、1765/PG-D598・group1992、主WBS-P018-09/C07参照0加算、開始1/3/6pp/cap10不変更。候補source **f775f095c0721340c20376b8d37d8baa2e97bc21**、未配備/実runtime UNKNOWN-HOLD。

## 新規発見・是正と確認可能な増分

新独立MIDNAME001～004 **4 Test ID**。Web Counter/Gauge/Timer、API SummaryすべてでMeter.Idの承認名を後で再読取る不備を、実装変更前のe5f0/既normal8368同Jarに対する8380で再現（全4failure）。XMLは全四ともexpected line72の非承認名不在assertで失敗し、後続の非catalog fixture名が実textへ出たことを確認した。これは公開SDK stubだけの普通PTで、実外部入力/通信/VM/DBを使っていない。

BUG1701/YKT1452先行起票→**f775f095c0721340c20376b8d37d8baa2e97bc21**で四対象の取得直後にnonnull String nameを一回copy、namespace照合とgroupingに同じ値を使用。単位/label/value/snapshot/IO/borrowed/generic public API/SS/POM不変更。新4＋必要既API24+6/Web16×3+6×3=96、同source **100件/9suite** F/E/S/aborted0。新4を既96と別に数え、原4失敗を合格へ書換えない。

## 実行・同source品質

JDK25.0.4/Maven3.9.12/offline/cleanenv/公式SDK1.7.0/明示empty config。公開manifestは `evidence/provisional/<PG名>/manifest.json`、元snapshot/command/OS-JDK/source/branch/日時/exit/input/expected/actual/XML/log/exec/coverage/staticは `/home/mini/codex/project1/work/pgpt-runs/PG379/<同名小文字slot>/`。各snake_case工具を既PYTHONPATH下の `python3 -B tools/quality/<entry>.py` で実行、新only完了slotを確認目的で再演しない。ルートfixture1777c471をfresh classpathへ同梱/照合。

|段階|真正結果/manifest SHA256|
|---|---|
|PG8380-metric-identity-host-v1|旧e5f0/4全failure、Test compile0→JUnit1、原XML/execを保持。**dd3b3b9e8c22a229483d02ee826525d16def51ab881832b8fcc2c85bdfe3ab09**|
|PG8382-metric-identity-six-compile-v1|新f775正常六package/NullAway/Spotless0、PT0/UNRUN。**3e5b5fa6e22805dde3d851e880ba74d27713b854e7aa1d9aa694fa94669f73b5**|
|PG8384-metric-identity-full-host-v1|新4＋必要既96=100/9全成功、一exec。**2520ca00c89cfa91866cea441d22a866173a03578f323eb1d156eccf99424ecc**|
|PG8386-metric-identity-post-v1|四exporter＋byte不変WebMetricTextの実5、line216/method29/class5/branch112 **全miss0/100%**、CRC0/一session/union0、PMD-CS-SB-missing0、七receipt反例。**9c32ed6d3cc5addb8319c943241e360053d4c12d03050342a88bbb5d7531febf**|
|PG8388-metric-identity-six-trace-v1|全1805physical/167source-owner、四既Mainだけname-copyのexact機械差分/全他1801 raw-debug同byte/原1669同byte、全旧Unit/POM/config/input不変。五architecture0＋現責務七metadata反例/Bootstrap34限定責務/既test-only edge保持、target init0。**746732b59daf1d0aebb1ba090b8997df3df185ee3a80e8680563d34c11d58ee4**|

全五工具は前置set-e/Pyflakes実0、全ownjob真正終端。旧catalog Main/14は当変更のcallerではなく同byteなので確認再演しない。全四100は当実5の実測で全製品/whole451の100ではない。原4222や別sourcecounterを合算しない。

## YKT1452全対象と再発防止（限定CLOSED）

|対象|是正/非該当・根拠|
|---|---|
|API ApiDurationMetricExporter|二回名読取を一回copyへ、MIDNAME004＋必要SUMENC24/API接続6を新sourceで確認|
|Web Counter/Gauge/Duration各exporter|全三を同様是正、MIDNAME001～003＋各16/接続6を新sourceで確認|
|WebMetricText|labelだけを扱い名の選択/groupingを行わないため非該当、新100の実5scope内で全branchを実証|
|WebMetricCatalog|一回のname lookupからimmutable Labelsを返し当grouping再読取に非該当、source/physical同byte。後続codec接続ではcaptured nameと検証済みLabelsをmodelへ直接渡す要件を維持|
|source/descriptor/責務/元失敗|四exact name-copy以外の既input不変、全metadata/byte-ownerを新100/実5へ結合、元0/4は原source/receiptと保持。API/Web相互本番依存やBootstrap拡張なし|

BUG1701/YKT1452は全対象是正/非該当と新source同品質を1766へ結合して限定CLOSED、完了日2026-10-24。検索だけ完了/期待値修正/解析抑制0。

## 費用・次工程・未受入

開始27、15:43JST fresh28残72/reset1793382075、丸め共有差1ppは他chatを含むため専有費/tokenへ変換しない。usage **02fbcf5ee7125fa83d1b70fb7b6659d6293543e60c2cd53e85974cb2a4ceea4c** /15:42:07JST、明示record0/完全性未証明・N/T/工数null。元/v4/v5/旧窓欠測/90再基底化0不変。新品質観点4、発見/是正、必要既96の再資格を分離する。

当区間1759～1766の新Test IDは22+22+14+4＝62、新MainはCounter/text helper/Gauge/catalogの4。各source/runは異なるため四coverageや180試験の実行数を一つの正式runへ合算しない。formal1964PT/53scope/原190新受入0、QA051final/PTALT0、whole451/CHR/F03Root11とactual VM/Root/DB/鍵/native/permit/配備・拒否未特定HOLDを維持。PGPT全完了/IT-ST完了とはしない。

次公開scan/保存/push後、新bounded群でWeb catalogのcaptured name/immutable Labelsを三exporterのmodel生成時に直接接続し、generic APIは維持。その後pure mode/scrape policyへ進める。別preflight後のmutable rereadだけの保証を避け、actual endpoint/owner操作は行わない。通常区切り/commit/報告/PMO返答待ちで停止しない。
