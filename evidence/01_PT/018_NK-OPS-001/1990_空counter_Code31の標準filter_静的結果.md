# 空counter・Code31の標準filter静的結果

2026-10-26、1989/群2244/WBS-G01、source8ba82083ec65abc6373b8454576dcbaee7d3e621。原空counterのCodeあり31class・全49method・実opcode794は、固定JaCoCo0.8.15の標準filterで全て除かれる構造と確認した。**理由説明は完了、除外承認・実測coverage・G01/451受入は未完**。原Code/元counter/未到達probeは不変。

|機構|対象class|対象method|独立確認|
|---|---:|---:|---|
|SyntheticClassFilter|19|19|ACC_SYNTHETICのswitch helper clinit全範囲|
|PrivateEmptyNoArgConstructorFilter|12|12|private/()V、ALOAD0→直接superのnoarg init→RETURNだけ|
|RecordsFilter|6（上段のうち空record6と重複）|18|Recordをsuperとする生成toString/hashCode/equals、invokedynamicを用いる原命令|

class重複を足さず31、method合計49。通常Code12は空record6＋空constructor6、生成Code19は別。既1383の一utility ctor、Protocol4/16missの既対応は歴史参照に留め、新製品PTや元計画消化として加算しない。標準filterで除かれる理由が分かっても「Codeなし」「全probe到達」「0/0=100」とはしない。生成Code全命令を要求coverageの適用対象から外す承認は別条件のまま。

primaryは既classをASMのbyte arrayとして読み、公開Filters.allへ原metadataだけを渡してignore命令範囲を収集した。target Jarはreader実行classpathになく、対象define/load/init/invoke/exec採取はない。独立postは別JDK javapの原31class/全49method/794opcodeと三固定filterのbytecodeを照合した。javapの-classpathは解析入力の探索先であり、対象classを業務実行するclasspathではない。全constructor/record生成methodの原descriptorとopcodeを照合し、8件の誤範囲・欠落・機構別誤命令・誤昇格を拒否した。これらはmetadata工具検証であって製品PT0。

## 証跡・工具手戻り

本Program evidence/provisional配下：

- PG9854-empty-code-standard-filters-v1/manifest.json：e7bd95804e49ae9a47e1d3422d7af901c2bfaff0278141913919bc6152aed548。`python3 -B tools/quality/pg9854_empty_code_standard_filters.py`、reader Werror compile0/標準filter範囲読取0。method-filter-ranges.jsonに全49method、class-filter-contexts.jsonに31原metadataを保持。
- PG9856-empty-code-filters-post-v2/manifest.json：0442a4e6053bfe937265cfa8bbac1e87c927650a29494cd9be64290787b74cc1。`python3 -B tools/quality/pg9856_empty_code_filters_post_v2.py`、exit0。independent-method-mechanisms.json、original31-bytecode.txt、pinned-standard-filters.txtに独立根拠を保存。新JDK起動0、元post V1で完了した二JDK0を当source/原工具hash/出力hash一致後に回収した。

BUG1770/YKT1521：元post V1は二javap成功後の表示guardでexit1。`// String ()V`を引用符付きと誤認したもので、primaryの標準filter範囲は正常。元source b7b4c513・namespace・実receipt/二出力を保持、別V2で実String/matcher名を照合した。元JDK出力hashはa39e7c5a5d4c6a14a0235713b615e09c03389e0ad194051ad0328baffa297452、bd6039999e5bb43b4f10bff1d0050fdff32006e60a29bab1c01b4398a69ace8a。任意opcodeを無視するsyntheticに誤命令負例を置かず、private ctorの意味的負例へ限定し、全8拒否を確認した。旧9844のenum/handler parserとprimary9854のASM範囲は当表示guard非該当。工具scope検証済み保存commit待ち。通常工具失敗でありplatform拒否ではない。

生成codeの独立review承認・必要な同source/run/runtime/native・四counter100/全scope/CHR/451は別。Graph9動的、全actualHOLD、G074493、全WBS監査HOLD、正式1964-53、個別17/190、QA051final、工数nullは不変。次は他の許可済み独立PG/PTの実source/oracle不足を確認し、同じ成功群や標準filter説明を確認目的で反復しない。
