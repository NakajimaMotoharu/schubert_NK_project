# NK-MED-001 Rangeの終点に使う十進数の上限

WBS-P009-04/2、FUN-005～007、PER-004～006、UI223 §8／237 §9、DIF-012、SS333 §10.1、SSC-476、PT-MED-RANGE-BOUND-001。対象は `HttpByteRangeParser.parseFirst`。現行ControllerはSpring HttpHeadersからRangeを読み、Spring Boot 3.3.5のFramework 6.1.14は全数値を符号付きlongとして変換する。NKはその非負範囲を維持し、無効入力のHTTP 416は承認済みDIF-012に従う。 [Spring Bootのversion](https://github.com/spring-projects/spring-boot/blob/v3.3.5/gradle.properties#L21) [Springの数値解析](https://github.com/spring-projects/spring-framework/blob/v6.1.14/spring-web/src/main/java/org/springframework/http/HttpRange.java#L135-L150)

| fixture全長 | 終点 | 独立期待 |
| --- | --- | --- |
| 3 | 9,223,372,036,854,775,807 | 2^63 − 1。上限内。末尾2へ切り詰め、0～2／長さ3 |
| 3 | 9,223,372,036,854,775,808 | 2^63。上限外。切り詰め前にUnsatisfiable |

JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、Linux x86_64。実行は `python3 evidence/01_PT/018_NK-OPS-001/input/5638_range_decimal_limit.py --corrected`。PG41248は当Main `6c2e8b027818c8dac0ed0f895edb85658e9c4ff1` と確定正本 `ee27a308b6b7da7bd9744000ee490a8f91956ead`。成功1、失敗／エラー／skip／未実行各0、終了0。従前と同じMain物理5のhash、当execの2CRCを照合。全coverageはPG41206の当Main有限証跡を参照し、別execを合算しない。実HTTP、現行baseline、実media配信や451の判定は別。

PR442の当初Range番号は開発台帳のQA-060予約に重複した。既番号を保持し、PR443でRangeのみSSC-476を確定した。旧PG41246は履歴に保持し、PG41248の番号訂正後再試験を同じTest IDの再資格として扱う。

- [現行正本のPR443](https://github.com/NakajimaMotoharu/schubert_NK_project/pull/443)
- [履歴PG41246](../018_NK-OPS-001/evidence/PG41246-media-range-bounded-decimal-end-v1/manifest.json) SHA-256 ebd498ab88efcfb7a6822f206531ce088d8cd6b5c869703bfcae84cb42a551b7
- [確定番号PG41248](../018_NK-OPS-001/evidence/PG41248-media-range-decimal-corrected-catalog-v1/manifest.json) SHA-256 c4f8298602f254f6fd81272990dbb8b06aa0b63673f773b5986cd86cd521e297
