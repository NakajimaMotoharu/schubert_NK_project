# private field命名の意味保存

NK-OPS-001/F03、PT-F03-FIELD-3714、SS311/354・411/451、BUG1317/YKT1083。base候補5224、PG3712 actual0（2026-10-15T22:25:25.489073～22:25:41.653760Z）、253findingを正確field tokenへ結合、private/non-record/non-serialized190候補・serialized63保留。全六compiler各0、原Main/SAST/VM変更0。manifestcf783e8046d5050eb5bcd7f129d60af46153b5e779d0d1dfcc4506ef18444e57、matrixb3d6c06aeaa78911271d33712e25aa34381b66a52e957a282a1e1cb8f2d0de13。

## 自動候補の境界

実symbolでprivate field宣言と参照のみを置換し、public/protected/package member・record component・Serializable state・reflection annotation・anonymous owner・未知tokenは変更しない。同名method/constructor引数/他owner field、認証identity、literal/JSON/電文/SQL・schemaやinitializer順は不変更。新名は既source identifierと衝突しない説明的private名、同field複数指摘は一symbolとして扱う。任意文字列置換やfieldへのprivate reflectionを用いない。

PT-3714-001：独立literal小classでconstructor shadow、this.fieldとfield()、nested owner、static field、lambda、array/null、literal内の同名を区別する。正当部分のexpected source/field mappingを独立literalで比較。未知/foreign/非private/record/Serializable/collision/位置・型違いは拒否。

PT-3714-002：元全849source/253target原本・classpath hashを固定、190候補の範囲だけをnew-only候補へ反映。全field visibility/型/annotation・公開method/constructor ABIと、旧field名への正規化を明示した全resolved binding/木構造/literalを実compilerで前後一致させる。GJFはfixed skip-reflowing-long-strings。異なるprivate名を同一とするのは当明示mappingだけ、他の不一致を正規化で隠さない。

PT-3714-003：固定Checkstyle/PMDでraw全件を保存し、実差分と残serialized63/他未分類を確認。Mainへ反映前に全candidate SHA/old SHAを照合。新sourceは既Root/native/coverageへ無断再bindingせず必要一全体と正規当source資格へ進む。metadata純試験はProduction PT件数へ加算しない。

群残subset1/3/8共有ppをdiscovery .2/.6/1.5、symbol candidate .5/1.5/4、independent binding/static .3/.9/2.5へ分割。親子併算0、共有K01/native・実費配賦は別、N/Tnullを維持。最初のfield probe純1は前群内作業で再課金せず、今回見積は残作業のみ。F03/四100/正式/工数率/QA051finalは不変更。
