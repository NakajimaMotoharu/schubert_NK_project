# 2099 Qualified型修飾とConstructor期待入力の分離仕様

2026-10-27、G03.01/群2445開始.25/1/3pp cap10、source370/正常10632変更0。前2098のnamed候補77は「変数77」ではない。new WebLogDispatcher.Reportの型修飾名等も保守的に残した未整理identifier候補であり、ここでconstructor headと実入力を区別する。

元first-argumentの行/hashを保持し、new直後から実引数括弧までの型名だけを除く。型名と同じidentifierが引数にもあるnew T(T)は、後者を除外しない。数値suffix L/lは直前数字tokenとbyte上連続する場合だけ区別し、standalone Lをliteralとして認定しない。残りの文字/数値/boolean/nullだけの26候補を原owner型束縛・Main値保持constructorへ照合する。残51名候補/66method候補はpendingのまま、元23/既是正二を新成果へ加算しない。

起草時はsuffix処理前の25/52を記載したが、BUG1857/YKT1608でExpiry Observationの固定millis literal一が追加され26/51へ訂正。元77内の精密化でありscope/開始見積を増やさず、元失敗/調査時の数値は台帳と結果へ保存する。

操作は同じ原168/source/公開metadataからの静的読取のみ。元Test/fixture/Root/DB/鍵/graph/native/VM/外部操作0、別harness・target classload/compile・製品PT/新coverage0。元Main constructor本文分類と現source SHA/実ownerの一致を示し、全case fixture・実環境の独立oracleや動的成功までは認定しない。結果2100・同番号manifestへcommand/時刻/source/hash/actual exit/反例/未確定を保存する。

独立postは元77 raw AST span・元row参照/hash・実constructor headだけの除去を別手順で確認し、new T(T)/未知型/standalone L/型owner偽装等のmetadata反例を拒否する。原owner/cost/正式1964-53/17-190/工数null/QA051final・全安全HOLD不変更。保留二witnessはname inventoryから除外し内容read/hash/probeを行わない。
