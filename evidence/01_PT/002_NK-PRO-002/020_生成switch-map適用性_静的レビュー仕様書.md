# 生成switch-map適用性・静的レビュー仕様

2026-10-26、主WBS-G01/群2240、開始.5/2/5pp cap10。review source8ba82083、既動的sourcefd3d04/PG9722は別のまま。017/018/PG-D671と、旧1222の「17非実行class」という表現を横断し、Codeのあるcompiler helper4とCodeなし13を区別する。後続索引で未完の適用性レビューと確認し、元102件・9726を再実行しない。

対象四classはPayloadCodec$1、MediaDescriptorValidator$1、FieldDefinition$1、LayoutFieldCatalog$1。原9726（sha c5e2b600dfadfca7c1a8a889fec5d605e775b7e75e36955bc4a70cf5298290b5）のactual CRC・raw hit25/miss16、counter0/0、固定JaCoCo0.8.15の標準filterを保持する。current9812の同class byteと全enum定義を先に束縛し、旧execの観測を現sourceの新PT/coverageへ移植しない。

許可範囲は既公開source/class/Jar/execの静的読取。独立Java工具だけをcompileしてASM/JDK parser/JaCoCoの既exec readerとメモリ内instrumentationを使い、probe番号と原bytecode handler/命令の位置を対応付ける。変換byteは解析用の一時byte arrayだけ、jar/Production classfileへ書き戻さず、生成/原classのdefine/load/init/実行・新agent attach・target method呼出しを行わない。実Root/VM/DB/HTTP/JMS/鍵/permit/intent/署名・配備操作0。不整合enum/classpathを作る製品fixture・coverage用の無意味なassertを追加しない。

静的期待は次のとおり。違う構造や対応不能があればUNKNOWNとして残し、対象を広げたり到達不能へ読み替えない。

1. 全4がACC_SYNTHETIC、switch-map配列fieldだけ、原methodはclinitだけ。Code有無はflag/属性と別に確認する。
2. 全missed probe IDを実execから読取り、bytecodeのcatch型/handler本体/合流点と比較する。NoSuchFieldError対応が確認できてもraw miss16を0へ変えない。
3. referenced enum field/values/ordinalの型・field名・descriptorを同固定Jarのenum定義へ照合する。artifactでfieldが実在することと、実環境のBOM/classloader/世代認証は別条件とする。
4. 標準filterの固定実装をローカルJaCoCo jarのmetadataから確認する。標準出力が0/0である理由を説明し、個別100や無Codeとして加算しない。

成果は完全4classの分類/根拠、未証明のruntime条件、451/SS354との適用性レビュー記録。line/method/class/branchの既159実測と13無Code/4生成Codeを混ぜず、除外設定・baseline/test oracleの変更0。レビューだけで自動除外承認、strict generated全命令資格、全G01/451/正式受入を与えない。原/v3/v4/v5・元event/費用を保持、工具検証は製品PTに数えない。新事実が得られれば残条件を具体化して他の許可済みPG/PTへ継続する。
