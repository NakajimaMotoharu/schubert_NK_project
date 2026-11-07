# WebSecurity生成・輸送拒否guard単体仕様

NK-WEB-001/WBS-P015-02、FUN001/AUT/SYS006/UI221222226252/SS313314342351352/PG-D113114116。対象whole WebSecurityFilterFactory constructor/create。全Code coverageはfactoryの構築責務だけで、実normal business chainやCookie/session/roleの受入ではない。元DB/fullchain Testを抽出・迂回せず、新whole独立四methodで公開Filterのnull/identity/外側guardを検査する。

|Test ID|独立入力と期待値|
|---|---|
|PT-WEB-SECCONSTRUCT001|4依存それぞれnull→固定引数名NPE、request UUID supplier/監査/backend callback0|
|PT-WEB-SECCONSTRUCT002|同borrowed ownerでcreate二回→二つの別CompositeFilter、生成時UUID/監査0。SDKのprivate fieldを読まず設定を差替えない|
|PT-WEB-SECCONSTRUCT003|GET/POSTの非loopback TestNet peer→403・空body・Location/Cookie無し、SS352の固定七header各一、PROXY拒否監査一、request UUID一回。trusted internal context無し、session/form/JMS/business callbackはfixtureで常時禁止|
|PT-WEB-SECCONSTRUCT004|owned request UUID supplierが単純IllegalState→同一例外、監査/session/business/Location/Cookie0、外側headerは維持|

期待値はSS352手書七header/403/固定JSON reasonとidentity/countでProduction生成なし。構築graphはSS314の明示順（encoding/session/context/CSRF/login/cache/closedServlet/display/accessException/authorization、外側header/Caddy/infrastructure/internal-error）を元sourceと正常classbyteで別にレビューする。内部SDK設定の実business通過は未測定として残す。null/例外/有限二要求を網羅、並行DB/再送/認証は対象外。

同既SecurityContextOwnerPortFixtureはconstructor/zero-copy closeだけ、login-factory portで既に使うresource-free requester/registry/login/probe constructorを同public APIで構築しmessageID/sendを禁止する。空owned ThreadLocalをchild JVMで前後clear。SDKの既定constructor/provider初期化は生じ得るがtoken/nonce/鍵生成・Cipher/backendは呼ばない。request UUIDは公開固定値で必要な識別callback一回、session/Cookie ID/messageIDの発行ではない。JDK literal IP parserはDNS/socket接続なし、Product FFM/native/Root/VM/DB/crypto鍵・wireは実行しない。四guarded Mainは初期化・実method呼出0、normal class/Jar metadataのみ。

Main7aed正常22084/六静的22086を同byte再利用、新Test二sourceだけlint/Werror/PMD/CS/format。source固定後一Unit、元XML/exit/F-E-S-abort0/全factory Code L-M-C-B（自然零はN-A）/CRC/一exec/全実method/initを独立postで照合する。主張はconstruction/negative guard限定、全Security chain/実Caddy/DB/認証/CHR/native/451/正式1964-53/工数率を更新しない。開始.5/2/5cap6/原計画/全HOLD不変更。
