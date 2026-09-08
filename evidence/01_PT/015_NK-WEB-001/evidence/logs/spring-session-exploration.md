# Spring Session接続探索・BUG-058/059・YKT-053/054

2026-09-08 JST、dev-web、NK-WEB-001/FUN-001/AUT-001～004、UI226、SS314 §7.2.5/331/352、SSC-042/PG-D-099、PT-WEB-044～049。JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0/JaCoCo0.8.15。Spring Session4.1.1/Web・Test7.0.9/Servlet6.1.0、全version/hash/依存収束再現は421 §5.7。

## 先行登録と横展開

SSC-042/判断8b8206f→SS/PT7416471→実装。BUG-058/YKT-053は3d01254、BUG-059/YKT-054は1e6b720で修正前起票。探索04で両方を再現後、Production修正。raw出力は/tmpだけ、実session/鍵/DB dumpなし。

| 対象 | 修正/非該当根拠・再発防止 |
|---|---|
| token削除delta | 旧snapshot UUIDだけで削除せず、現在token全valueを照合。別用途/時刻の再発行は固定障害/rollback。046のA取得→別request削除→同UUID用途B発行→古いA削除でB保持をassert |
| token追加delta | 既存putIfAbsent＋同UUID別value拒否は適合。046で同値重複追加、別用途衝突、最大10に別token追加拒否 |
| token保持/既削除 | immutable value containsは適合、古いsnapshotの未変更項目を再追加しない。046の並行10追加/削除・既に消えたtokenの削除冪等・他属性保持で確認 |
| SessionAttributes/lifecycle | 単一snapshotのUUID重複/null/10上限とpure mutationを既に検査。時系列delta所有者ではなく非修正、既存009～043回帰 |
| SavedRequestTarget | URI.normalizeが/../logsを残すため、raw pathの独立 . / .. segment patternを追加。006/045で先頭/末尾/連続/encodedを拒否、/file..txt・/.hidden・/.../file・query ../ は不変更 |
| SessionAttributeCodec保存read | 共通SavedRequest validatorへ委譲。014へ独立不正JSON path負例追加、実暗号/再起動回帰も実施 |
| Spring savedRequest setter | 共通validatorへ委譲。045で不正targetを拒否し、safe GET/除去/再読を対照確認 |
| RelativePath/DisplayPath/実file | RelativePathは全segmentの./..を拒否、DisplayPathはPathSyntax.containsParentSegmentで拒否しdisplay-onlyでresolverへ渡さない。保持file adapterは独立root/descriptor/segment検証、URI.normalize callerではない。既存Protocol/Storage/API/Web file PTを正式全reactorで再試験 |

## 探索履歴

| run末尾（prefix PT-WEB-spring-） | 終了JST | exit/結果 | raw log SHA256 |
|---|---|---|---|
| compile-01 | 21:05:32 | 1、未導入依存のversion収束失敗、Enforcerは維持 | 5e60860f9ac0a6a68597da02a448d3bb2dcd025e5af7698695ad39c4a1383c51 |
| compile-02 | 21:07:58 | 0、明示version固定後compile/NullAway | dae75b3e9aaae53f851aef9524c51af6c57e23111e14ab3fbce54c4522e67a30 |
| explore-01 | 21:12:12 | 1、新test fixture接続のfinal field初期化順compile error、未実行 | 87e3a173cf5c92fdc22f4e26dccfe4da9adaffac2f1505b3fa45c3081b584296 |
| explore-02 | 21:12:49 | 1、新test generic cast warning/Werror、明示型引数へ訂正し抑止なし、未実行 | 683206d0fb951b7d7b8e869ad0c819e2e551a81ebf570c60deece3702e3dc46a |
| explore-03 | 21:13:48 | 1、新6件中045がBUG-059 FAIL、既存lifecycle/store16 PASS | 92283051e2683f8247fb96cdf00613297828f4475ca2f4f37a6af7327eb895e4 |
| explore-04 | 21:15:47 | 1、新6件中045/046がBUG-059/058再現FAIL | 0eb35032cb532c953ddf58fddde030735864b03c112a0d66283560225d80af43 |
| explore-05 | 21:17:00 | 0、新6件＋既存27件PASS、残2分岐は次runで確認 | 290677ecc515c1eae4c3fb09b08275f89547c7016d0ab7c87ca0d10279a6a951 |
| explore-06 | 21:18:20 | 0、新6件＋既存27件PASS、対象line/method/class/branch100% | 040c9ab6258eac0dfe129e9353454c1ea800b19495cc0f4e9729d9ac4b3498e4 |

Fixture配線/初期依存の未成立はTDD接続準備であり実装済み外部挙動違反とは分類しない。実挙動違反058/059は別途先行登録した。Coverage用の無意味assert/除外/到達不能宣言なし。Spring Session generic getterのunchecked castだけは実API契約に必要な一箇所の抑止を隣接説明し、closed型と全unknown/type負例を045で確認。探索coverageは累積で正式clean verifyが最終gate。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SpringWebSessionTest,EncryptedWebSessionRepositoryTest,JdbcWebSessionStoreTest,SavedRequestTargetTest,SessionAttributeCodecTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

独立期待は固定attribute/UUID集合、µs日時/8h/SQL件数/hash、明示Cookie header属性。未発行CSRF fixtureは入力を実codecで暗号化してDBへ入れるが、expectedは独立のnull/名前集合でありproduction encode結果をexpectedに流用しない。SessionFilterFactoryは本番と同じCookie名/属性を固定し、Mock Servletでも実Spring wrapper/save/invalidate/response commitを通す。flush直前に別requestで削除されたsessionの保存は失敗し、Cookie再発行/DB再生成がないことをassertする。

## 正式gate・残件

正式PT-WEB-20260908-07、sourced6d9ff6c318f9bccb2df7d9716f742dda0573577、21:21:44～21:26:11 JST、exit0。全674件（Protocol80/Storage34/API394/Web125/CHR41）、新6件を含むWeb49件PASS。全5対象module line/method/class/branch各100%、NullAway/Enforcer/format PASS、SpotBugs0。SSC-042/BUG-058/059/YKT-053/054全対象再試験完了。002/manifest/checksumsで環境・実行・Test ID・hashへ追跡。Security chain、CSRF POST、API実認証/失効queue・監査、全画面/起動/実NK CHRは未完了。Program5/20とIT/ST未完了は変えない。
