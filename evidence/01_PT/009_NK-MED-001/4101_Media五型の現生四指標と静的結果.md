# NK-MED-001 現Media五型の生四指標と静的確認

WBS-P009-04/2、SS333／352／354、PG-D-1190、BUG-3475／3476。MediaRangeService.respondでは二つの本文型を明示し、残るUnsatisfiableを既416へ渡した。署名、借用channelとresponse、HEAD・attachment・Content-Lengthの既結果を維持する。PT-MED-FAILURE-NAME-001は公開Reason三名を固定入力とし、同じreason、503、BUSY時だけRetry-After 1を確認。未知、大小相違、nullを拒否する。

PG41260は11 Test class、製品27（新1／必要な再資格26）とfixture1の計28成功。失敗・エラー・skip・未実行各0、終了0。実環境を用いず、承認済みメモリ入力と自己所有TempDir（終了時空）を使用した。再現は入力5642／5643の `--fixed`。JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、Linux x86_64。

PG41262の同一元execと13物理で、生line 135/135、method 39/39、class 9/9、branch 74/74、instruction 722/722。4物理は自然なコードなしを保持する。手動除外・旧exec合算なし。既生M1/B1は是正済み。同一sourceの公的ABIは旧範囲と一致。

PG41264のRoot同一設定NullAwayは終了0、当13物理すべて同execのbyteと一致。SpotBugs2は元試験のnull拒否assertion、PMD1は呼出内だけのMap。PG41266で実行行・元source・所有と不変コピーを独立に確認し、当適用指摘・未分類各0。生警告は保存し、判定設定や抑制を変更していない。実HTTP／Native・実owner・全451とPGPT全体は未受入。

- [新28実行](../018_NK-OPS-001/evidence/PG41260-media-current-five-types-corrected-v1/manifest.json) SHA-256 26a4aa4ab0adf7826d73691d8dde64a53d77ba8565568ae2c525d51735841775
- [生coverage](../018_NK-OPS-001/evidence/PG41262-media-current-five-types-corrected-independent-v1/manifest.json) SHA-256 8d20a95c2f4e32f787a4db435ffbe502eda9db22d68eae291f1f1978af574824
- [元静的結果](../018_NK-OPS-001/evidence/PG41264-media-current-five-types-typed-static-v1/manifest.json)
- [適用性・ABI](../018_NK-OPS-001/evidence/PG41266-media-current-five-types-static-dispositions-v1/manifest.json) SHA-256 b497d0a39eb1fec82b6d51c619fe0d053e493edddfc24b8842983097a99cc0d7
