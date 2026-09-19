# shell診断混線の修正・横展開再試験

PG197/BUG217/YKT173、InspectorDeploymentTest.statusMapping/malformedReceipts、PT-OPS-INBOX-002/003。関連018001、UI251、SS343/SSC053/BUG137。Production wrapper・終了code・receipt grammar・全50tool呼出しは不変更。

## 正式13の失敗（非合格）

PT-WEB-20260920-13/source6187f7bd、2026-09-20 05:40:44～05:46:23 JST、Maven5:37/exit1。API689件中1failure、Web/Batchはskippedで合格算入しない。raw SHA256 `2bfb1c8056e3b3abd766c29193fb031829f0e6566df27d775c37e04ae4074502`。既存認定は正式12/1544PTのままで、PG195選択12PTを正式認定へ加算しない。

公開fixtureのmissing Javaは期待どおりexit50/stdout空/receipt hex21。共有stderrにpipeline左printfと右odのsh -xが並行出力され、`printf/usr/bin/od !`のように混線し、旧contains("printf !")が失敗した。証跡はevidence/logs/BUG-217-formal13-missing-java.json、SHA256 `94c28fc4b2077727d00501c35d7ebecb11054475144bc25909b2dfce64759eb2`。実credential/raw sessionはなく、pathをPT_ROOT/REPOSITORY/JDKへ置換済み。

## 修正と独立期待

修正前に915/916へ起票。子pipelineのxtrace連続性を期待せず、pipeline全完了後に親が出す唯一の`inspector_receipt=`へexact hexで照合する。期待byteは仕様の公開receipt文字列＋成功dot/失敗bangをUTF-8にし、標準HexFormatで独立算出する。Production shellのcase/od出力をexpected生成へ流用しない。正常0/10/50/70、JVM非zero1/70/143、missing Java、不正29receiptの全対象へ適用。

原混線パターンを持つ合成Resultを受入れ、誤marker・欠落・同一重複・異なる重複の4negativeを拒否するfixture canaryをPT002へ追加。正しい失敗コードであってもmarker誤りを通さない。src全testのprintf marker/err containsを検索し、直接marker条件はこのclassだけ。残るexit文字列は親の直列終端、placeholder/引数拒否時のlauncher不存在検査はpipeline起動前のため非該当。期待値削除・sleep・timeout延長・retry合格化はしていない。

## 選択再試験

同toolchain JDK25.0.4/Maven3.9.12/Ubuntu26.04.1、dev-foundation作業tree。commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am spotless:apply test -Dtest=FieldCodecTest,ResourceScopeTest,InspectorDeploymentTest`。反復はspotless:applyなしの同test。

| run | 終了JST/秒/exit | SHA256 |
|---|---|---|
| pgpt-bug217-green | 05:49:49/11.383/0 | ca928c92d0a41476487ed4ac25dbd8150b1818ee71298d4aa1617887a66e9719 |
| repeat1 | 05:50:36/6.117/0 | 41a4ec55dd187543ce25e291bdc6bef8b322e3f3cdc621e9fc35d777ad61767d |
| repeat2 | 05:50:42/5.559/0 | 92fbb916b3b0bad7eef69d65ae6fdcefea3fecf465f0f668a07df54729ff1e8f |
| repeat3 | 05:50:49/5.389/0 | 7424a72ca149ce26bac22b4cac8a4089665d706e5014d755c39d632af21d6a3e |

毎回deployment8PT/50tool呼出し成功、失敗/error/skipped0。これで正式13を合格へ書換えない。Java Production変更なしだが、次の正式clean verify/全coverage/static/同source収集後まで台帳完了を保留する。
