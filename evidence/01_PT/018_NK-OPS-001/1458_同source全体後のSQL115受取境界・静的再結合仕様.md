# 同source全体後のSQL115受取境界・静的再結合仕様

Productionは2d4633fb2、PG6634全体中につきMain/Test固定。ここで用意するreader/管理TestはProduction PTへ加算0、PT/VM/DB/遠隔jobの起動0。元全体の真正結果とPG6636原資格が揃うまではpublic成果を生成しない。期中の全体実行は別campaignへ変更・再起動しない。既JDBC1625の.5/1.5/4、JMS1658の.3/1/3、K01の開始見積、原-v4を保持、参照費重複0/実N/T・専有費null。

## PG6638 SQL catch115（scope限定）

仕様312/SSC328～330、BUG1592/1593/1595/1598・YKT1345/1346/1348/1351。入力6624 inventory SHA `e2aa6e25e9f090767dc88fc8fa8e0821aa979aee4a8f874d1372f27d77509c4a`、stable旧113＋新114115を維持。今回三JMS MainにはSQL catchがなく、115の各source fileは6624時と同byteであることを検査し、catch変数/開始行/body token hash/全ファイル集合を照合する。

56箇所は捕捉変数のfatal分類が最初の実行文であることを検査。106(Session)/114(Inspector factory)だけはowned rollback/closeを先に完了する承認済み例外で、その後の分類を確認。残57は列挙した16route群（owned rollback rethrow、qualified secondary attach、Outbox setup/final receiver、readiness capture/finally/final guard、Web manual、REQUEST projection、Receipt primary/replace table、Revocation captured/combine、Session/Inspector secondary）へ一意に割り当て、無条件の「非該当」にしない。Receiptのunknown-primary marker/両SQL分類/直接Errorの既順位を、一般fatal優先へ変更しない。

`pg6638_current115_receivers.py`は元全体/collector receipt/public qualification/cases hash、全851Main、元六coverage XML hashと各sourcefileを照合。current class-level regression referenceとaggregate guard line counterを保存するが、個別Testが各faultを起こした因果の証明とは呼ばない。未hit/欠落counterはnull/実値のまま、全branchの証明へ外挿しない。成果は115のPG受取routeレビュー＋同source原全体の再結合であり、acceptedSites=0/PT追加0/全nonSQL網羅0を維持する。

管理Test `pg6638_current115_receivers_test.py`は57routeの全数/重複/欠落拒否、誤捕捉変数・conditional guard拒否、cleanup例外の限定を検証（3件終了0）。最終実行は既PYTHONPATH三path＋`python3 -B tools/quality/pg6638_current115_receivers.py`、PG6634/6636の真正0後だけ。

## PG6640 F03 current raw1404の再レビュー・原XML結合

元6632の1404 raw diagnostic/processing error0/六SpotBugs0/Checkstyle0を入力し、PMDのwarningを削除・suppressしない。旧6528/f39の完全source-file診断順・全座標・rule・text hash等が一致する1186は旧rationaleの再認証対象、うち11保留は保留維持。新sourceの28file/218は全raw ID別のsource spanと規則・所有/例外契約を再レビューする。

変更範囲の215はcurrent source contextごとに明示：owned rollback/close後のgraph保持、cause/linked duplicate前分類、直接Error順位、same-Throwable identity、SQLstate23505前fatal、既bounded interrupt観測など。単語だけで例外を許すのではなく、原source span/該当componentの独立旧新Test・SS根拠・原XML hashを個別rawへ保存。Code scanからPASS/counterを作らず、sourceの218件をPT合格へ加算0。

WebRequestLogProducer.localのsink Runtime catch/terminal callback Runtimeの3診断は、wrapped fatal graphの適用性を別途PGレビューするため`LOCAL_SINK_GRAPH_APPLICABILITY_PENDING`として未分類維持する。215/3は静的草稿の実読取計数であり最終受入ではない。RootFailedStartRecoveryの旧11は既存manifestだけ参照し、追加のcohort調査・実装・実行や代替PTへ進まず保留。これらを具体的拒否対象と断定したPT例外へ自動変換しない。PTALT001/002対象未特定/代替完了0は維持する。

`pg6640_current4158_static_join.py`は、全851/1667の原static/whole byte一致を確認し、source/case hashが同じ当全体の原XMLだけをcurrent refsに使う。過去のPASSは輸入せず、wholeCase refなしで任意の空配列承認をしない。raw順/ID/1404全数を保持し、215＋旧rationaleの分類と保留14（予定）を分ける。F03Accepted=false/正式更新0、残る懸念を合格にしない。

管理Testは初回のunknown path入力でIndexErrorだった草稿を、名前抽出の`[-1]`へ変更してValueError拒否の期待値を不変で満たした（新未実装fixtureの初回TDD、Production障害ではない）。最終3件終了0/pyflakes0。同source原全体/6636後だけ`python3 -B tools/quality/pg6640_current4158_static_join.py`を一回実行、結果/残未分類を1459以降へ記録する。Main/TestやCurrent baselineへの変更0、全体/native/CHR/四counter/451/traceの終了依存を減免しない。
