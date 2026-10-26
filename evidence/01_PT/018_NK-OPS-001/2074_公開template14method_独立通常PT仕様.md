# 公開template14methodの独立通常PT仕様

群2408（着手前1/3/7pp、cap10）。sourcea82c44a678cce0ded7fda59cf84a2276ded51e30。2073の二template Testに対する同値定数変更後の必要再試験であり、旧成功確認だけの再演ではない。Main/Test変更・旧全回帰反復・追加fixture0。正常10480/原source全token10482/静的10478を参照し、compile/staticを繰り返さない。

## Program・契約・独立oracle

NK-WEB-002、関連WBS-P01608/09/11/12。原Program仕様011_Animation一覧template単体テスト仕様書及び015_Music階層template単体テスト仕様書の全表を正本として、そのfixture/操作・入力・独立期待値・正常/境界/異常/例外/並行・非該当null/再送を継承する。Test IDは**PT-SCR-046～053、PT-SCR-066～071**の14件。class#methodは原表から抽出し、現sourceの全@Test methodと完全一致で束縛する。USER/ADMIN/公開合成actor、0/最大件数、固定文言/順序/URL/locale/MB丸め、独立Current CSS宣言/selector、escape・合成CSRFの分離を明示期待へ照合する。Production projection/formatterからexpectedを生成しない。

## 着手前の具体独立性と操作境界

AnimationTemplateTest八/MusicHierarchyTemplateTest六の全method/helper/field、WebMvcConfiguration全文と限定bean constructorを読取確認。両Testはlifecycle/@BeforeAll/@AfterAll/@TempDir/static blockなし。WebMvcConfigurationはproxyBeanMethods=false/@EnableWebMvcだけ、component scan/boot/noargsなし、beanはProblemViewFactory/ErrorController/MenuController/LoginController/template resolver/engine/view resolver/CSRF value processor。bean constructorは純粋生成/nonnullだけ、業務endpointを呼ばない。新contextはtry-resourceで閉じる。

MockServletContext/MockHttpServletRequest/Responseと公開合成SessionPrincipal/CsrfTokenを用い、ポート/外部HTTP/Login/認証・権限変更/DB/JMS/Root/VM/key/nativeを起動しない。resolverは固定classpath:/templates/と閉じたview名、未知/traversal/redirect名はnull期待であり外部URL接続を試みない。合成escape文字列はDOM内の無害な表示入力であり実Browser/JavaScript実行なし。既workerはtry-resource所有8thread/64task、Future10秒、共有contextを閉じる。元DB依存Controller/API Testや八enum sourceの再試行・fixture迂回へ使わない。

入力resourceはnormal10480の凍結snapshot内 `src/schubert-nk-web/src/main/resources` の公開template/CSSだけ。classpath jar内resourceと各元source hashを照合する。CSS境界Testはmodule-relative src/main/resourcesを読むため、JVM cwdをその**正常snapshotのweb module**へ固定する。Testが作成する `target/scenario-screen-traces` は着手前に存在しないことを確認し、今回owned outputsとしてPT-SCR-053.txt/071.txtの固定公開count二fileだけを許可する。古いimage/log/原本/Backup/private/raw・元repo targetを上書きしない。source/compiled Test/Main jar bytesは実行前後不変を確認する。

## 実行・後条件・未受入

PG10486で当source/normal/static/source proof・原仕様14case/二suite・public resource・14完全Main class・出力不在・launcher hashを固定。PG10488を新slot/sessionで一回実行し、F/E/S/flaky/aborted/container失敗0以外は合格にしない。PG10490で元XML/summary/終了code/当source/session/CRC/全MainとTest不変・公開count二file/禁止probe-classload0を独立照合する。新規Test ID0、旧73の28件/15class成功・execを転用/合成しない。

counter対象はAnimation/Menu/List/Video/Row、Music category/section/Card、TopBarの九完全classとWebMvcConfiguration・限定bean四classの計14。全line/method/class/branchの測定値をそのまま保存し、部品/beanの未実行分岐を除外しない。これはtemplateの14methodのscopeであり全Java/全画面/全451 coverageではない。

原仕様どおりraw HTML/context/session/CSRF/credentialをGitや公開artifactへ保存せず、元XML（値のないmethod/status）・公開count・hash・counterだけ保存。command/OS/JDK/tool/branch/source/時刻/input/expected/actual/exit/coverage/path/hashはmanifest/後続2075へ。独立postや原定数化のmetadata反例を製品PT件数へ加えない。元static26/volatile十pending/原八enum・実環境全HOLD/QA051 final/正式1964PT-53scope/17-190/工数nullは維持。HTTP/server/Browser/CHR/native/IT/STの完了に換算しない。
