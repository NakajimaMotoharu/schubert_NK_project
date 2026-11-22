# Animationメニュー・一覧表示実行結果

PG204/PT-WEB230～237、仕様016。正式21/sourcee4eb018d817bf234d646246f8a5166c21868b3b4、2026-09-20 08:05:26～08:17:17 JST、clean verify 11:49/exit0で認定。全1625PT/Web366、failed/error/skipped0、6Java4coverage100%・Production5静的解析未解決0、41scope/70負canary成功。新4class28method91line52branch全missed0。PG205と合わせ2部分成果16PTを追加し88部分成果835PT。HTTP/MQ/動画stream/実NKgate・PGPT/IT/ST完成ではない。実行command/環境/対象commit/各hashはevidence/manifest.json、raw log SHA256=d841d9b16cbea9b2e76a4e0b36955941206cc151689dabebb8accfdc31a5a2f3。以下は選択試験記録。

`/tmp/pgpt-pg204-green.log`、2026-09-20 08:01:36 JST終了、35.968秒、exit0、SHA256 `b0c7fa2dddbb28d604ae0d0bb9298eb94eb51620fe57970aff3df55e74a8ba45`。新8PTと依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新4classのline/method/class/branch全missed0、除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,AnimationViewModelTest
```

source803e02ef＋PG204作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12、tool変更なし。入力/独立期待は016のmenu15/4/1/20、3main/2sub（sub先行も含む）、OVA0/4/50/51、各不整合/null・不変所有・閉bean・固定percent URL・HTML逃避・64並行。実際は全assert成功。015 collectorへ230～237/source3hash/016017を追加、019独立inventory含む68canary成功。017の1と計69は次正式gateで確認する。正式command/対象commit/時刻/環境/exit/coverage/source・証跡hashはmanifestへ記録する。

## 2026-11-22 現候補の例外宣言再試験

PG42382／a55900c5087c8ba9e2562d8fe1493a04aadbb9b6／Core 1e4e9e64830b552727043f3cb8b9435b28cba472。PT-WEB-235/237の2件成功、F/E/skip 0。独立の表示・Bean・並行期待を維持し、型付きSpotBugs 0。有限workerのPMD生指摘を保持。残りの元試験は同じ理由で再演していない。BUG-3581／YKT-2816、evidence/01_PT/018_NK-OPS-001/evidence/PG42382-f03-two-views-four-current-v1/manifest.json SHA256 2b645964726a54149e518e23159bc1386e043ce55b1e778d239820f638c8edfc。
