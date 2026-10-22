# 観測schema行の純粋境界仕様

事前訂正（BUG1624/YKT1377）：共通guard実一覧は12method/七suite・六module。下記15/8・23/10という初期予定は未実行の誤記として保全し、正規初回 **23/11**（guard12/7＋既関連8/2＋新3/2）を固定する。初回定義23/10はinventoryで拒否/Production未起動、独立期待値・Main・全旧Test/gates・開始予算は不変更。既設pyflakesを含む完全PYTHONPATHで全quality commandを実行する。

新管理二は初回一ERROR（BUG1625/YKT1378、text=Trueのstdout mockをbytesで返したfixture）を修正前起票し、全mockをstrへ直して各guard到達call数も確認、管理二/pyflakes0。当初suite定義失敗/環境import失敗/管理ERRORはいずれも初回Production PT起動前、元失敗を保持する。Production Main/独立golden/全旧Testを変更せず、初回選択23/11の原結果はまだ未実行。

PG-D508、P018-03.02。開始前予算低.1/標準.3/高.8週次共有pp、共有選択実行費は1498/P017-10だけに計上し二重加算しない。原/v4/専有費null/正式1964-53/17-190/工数nullは不変更。

## 対象と許可範囲

MorningGateEvidence.postgresの**メモリ上の観測値→byte**のみ。RD SYS004/DAT009/OPS009・UI251253・SS343 SSC129のNKPG1固定順/六schema field、同SS固定BOMの1000 migrations以内、SS342/451へ対応。既MorningGateEvidenceTestの固定role/DB/RW/read-committed/advisoryHeld値と公開固定UUIDは単なるrecord data。実DB接続・ResultSet・advisory取得・Root/current/permit発行・VM・cohort・Backup・retention・private file操作は一切しない。PT_DEFAULT、拒否された検証やその代替ではない。

既実装のnonempty/<=1000/同BOM完全一致、各rank==indexをレビューした。SchemaHistoryAdmission.RowはSQL rank1..999を受理し、Contents/DatabaseInspectionはimmutable listを保持する。1000正常はSCHEMA rank0＋SQL1..999。1001異常は末尾にvalid Row999の重複を追加し、constructorの拒否とserialization検査を取り違えない。rank不連続は同じ二行[SCHEMA0,SQL2]をBOM/actual両方へ渡し、単なるBOM不一致で早期拒否させない。既Mainは仕様どおりと判断し、coverageのための変更はしない。

## PT-OPS-PG-ROWS-001

fixtureは固定INVALIDの公開相関record・固定DB情報、各migrationを公開literalで作る。正常1000行を独立に構成した**全byte golden**と比較する。expectedは固定NKPG1/header/DB key順、SCHEMA0の固定hex、SQL1..999のrank/version・script UTF8hex・signed checksum=-rank・成功1をSS順に組み立て、Productionのheader/hex/encode/parserを呼ばない。versionはLocale.ROOT三桁、scriptはVxxx__row.sql、UTF8hexはJDK HexFormat（期待値の独立変換）だけを使用する。

次に1001行はIOException、rank2がindex1に現れる同BOM行列もIOExceptionを期待。元wholeのmiss line364/369に対応し、最大値を到達不能扱いしない。borrowed record/listの入力内容が変わらないことも確認する。null/空/欠落/不一致は既PTにあり変更せず、新Testで無意味な件数加算をしない。並行/再送/DB後条件/実所有は純serializationには非該当で、当検証からそれらを成功認定しない。

1498二Testと合わせ新三method/二class。初期15/8は新Testだけの予定で未発行。最初の実行前に既関連Acceptor三/GateEvidence五を未変更で加え、六guard12＋既関連8＋新3の実declaration **23/10** を確定する。新二fileはpure data、旧Acceptor suiteの自己所有有限loopback brokerだけは既通常PTとして区別し、当schema Testは接続0を維持する。全851 Mainと全既Test/gates固定、新Test二fileだけ追加。format/compile-null/Werror/六SpotBugs/元XML・全Main原Jar同byte/対象実counter・TestID joinを照合。MorningGateEvidenceのretention.kept列等は未実測のままであり、postgres一methodからclass全体100/Root完了へ補完しない。

正しい既PGの点検と不足PT追加でありPG省略ではない。仕様違反が判明したら修正前に915/916、上位変更なら所定RDF/UIC/SSCを併用する。現状は未試験で合格/実測/leaf/代替へ加点0。必要全体は一変更束にまとめ、同source旧成功の確認再演を避ける。全Root/native/実環境HOLDとQA051final/PTALT001002未特定を維持する。
