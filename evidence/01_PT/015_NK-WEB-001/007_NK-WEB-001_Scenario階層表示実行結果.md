# NK-WEB-001 Scenario階層表示実行結果

正式認定: PT-WEB-20260920-11/source50ebfa27026736b702d723f7e11a482495b6cc0d、04:47:50～04:59:36 JST/Maven11:44/exit0。全1528PT（Web269、うち本Program193）成功、failed/error/skipped0。6Java4coverage100%/Production5静的解析未解決0、40scope/58負canary成功。新12PTと6class42method82line10branch全missed0を限定認定。BUG212/YKT168の全3fieldを再試験し完了。raw log SHA256=0e49ecccc91cd044c055e37fea950dd209f7334fe2288ba4b9929ac94970b739。command/環境/source/hashはmanifest。controller/実template/HTTP/実NKgate/PGPT/IT/STは未完了。以下は選択試験履歴。

PG193/PT-WEB-182～193、仕様006。正式全回帰前。3一覧projectionを1部分成果として扱うが、現在の正式1516件/76部分成果へは未加算。

| run | 終了JST/時間/exit | 結果 | raw log SHA256 |
|---|---|---|---|
| /tmp/pgpt-pg193-green.log | 2026-09-20 04:45:04/32.016秒/1 | 新12PT成功だがSpotBugs EI_EXPOSE_REP3件。BUG212/YKT168起票 | 17aa4d4ce977eb00213127a4919d67ff7ab4368b65b5b0af5550e694b86f988b |
| /tmp/pgpt-pg193-green2.log | 2026-09-20 04:46:36/31.430秒/0 | 新12PT/Page8/依存選択成功、NullAway/Enforcer/Spotless/SpotBugs0 | af0dd474253e7983f2d7a36b6d1af46381a2fadf48642cb5916ed795f6d89e7e |

新6class/42method/82line/10branch全missed0。0branchの3Cardは分岐なしで除外設定ではない。各literal値/URL/0・最大・超過/全null/100並行/合成DOM escape/閉getter/診断/入力・出力list不変性を成功。既に検証済recordを受ける前提なので、wire semantic/認証/要求bindingの合格とはしない。Production template/controller/HTTP/実NKgateは未完了。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,PageViewModelTest,ScenarioHierarchyViewModelTest`。source c4f8aa1d＋PG193変更/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15、tool追加なし。

BUG212再現は3constructorの保持式をStream.toListの直接代入にした初稿。runtime WEB187は不変だがstatic EI_EXPOSE_REPがgetGames/getRoutes/getFilesで各1件出た。保持時List.copyOfへ統一し全3警告0、warning抑制/coverage除外なし。YKT168検索はweb/view全.toList/List.copyOf/List.of、新3fieldを修正、既存Menu.cardsはList.copyOfで非該当、他既存viewはlist非保持。WEB187/191とgetter全試験が再発確認。台帳は正式全回帰後まで再試験待ち。

入力/期待値は006と独立literal fixture、実際値はassertされたgetter/合成DOM。collector015が12ID・4source hash・006/007を収集し、019独立inventoryは欠落/余分/未知methodを拒否する。正式command/対象commit/OS/tool/時刻/exit/coverage/evidence hashはmanifestへ成功後固定する。

## 2026-11-22 現候補の例外宣言再試験

PG42382／a55900c5087c8ba9e2562d8fe1493a04aadbb9b6／Core 1e4e9e64830b552727043f3cb8b9435b28cba472。PT-WEB-188/190の2件成功、F/E/skip 0。独立の表示・Bean・並行期待を維持し、型付きSpotBugs 0。有限workerのPMD生指摘を保持。残りの元試験は同じ理由で再演していない。BUG-3581／YKT-2816、evidence/01_PT/018_NK-OPS-001/evidence/PG42382-f03-two-views-four-current-v1/manifest.json SHA256 2b645964726a54149e518e23159bc1386e043ce55b1e778d239820f638c8edfc。
