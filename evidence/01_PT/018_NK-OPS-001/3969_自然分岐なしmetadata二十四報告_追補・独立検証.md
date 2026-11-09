# 3969 自然分岐なしmetadata 24報告の追補・独立検証

対象BUG2601/YKT2297、上位仕様・test oracle変更なし。実装済みinput931はclass補助件数を0固定としていたため、修正前PG25510で旧manifest/XML/hashを固定。対象は983の明示24動的postのみ。SourcePG/PT_HOLD/非実行は対象外。原artifact・source・classfile・counter・成功失敗証跡を上書きしない。

新input983は公開XMLからclass/sourceを別々に導出し、missing BRANCHまたは分母0をN/A/percent nullとする。非空未網羅をN/Aへ置換せず、Source非空LINE/METHOD/CLASS/BRANCH gateと区別。任意欄欠落はreported null/DERIVEDであり0へ補完しない。重複counter、非ASCII整数、負値・不正型を拒否。input984は独立に24×2scopeを再集計し原24manifest/coverage/testcase hashを確認、全counterの一致、literal/型/欠落/境界20checkを実行した。

結果PG25512=0、PG25514=0。1訂正=25288 reported class0/actual2(State/Operation)、2任意欄導出=24874 class2/24922 class4、21一致。Source件数と非空四counter gateは24全件不変。元XMLから既記録515case pair/57wholeを確認したが、製品実行0・新規試験0・新leaf0・coverage unionなし・正式認定変更なし。zero denominatorを100%にしない。

再発防止：旧931等の凍結post出力定数を新規templateとして転用しない。以後983のclass/source別実XML導出と984のN/A/欠落/型/未網羅反例を適用する。全体451/wholeMaven/外部HOLDは維持。原開始見積り1/3/6ppを改訂せず、追加発見とtoolmetadata補修を別記する。

実command: `python3 -B evidence/01_PT/018_NK-OPS-001/input/983_natural_branch_metadata_audit.py`、`python3 -B evidence/01_PT/018_NK-OPS-001/input/984_natural_branch_metadata_independent.py`。いずれもpyflakes0確認後の本体初回0、Java/製品/PT再実行なし。全path/hash/実日時はPG25512/PG25514 manifest。
