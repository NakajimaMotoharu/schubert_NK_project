# Web custom metric payloadの有限並行

F03/2-2、P018-09、SS351/354、UI252、BUG-3284、YKT-2387/2691。元WEBPAY001～013、WEBFULL001～013の26件。固定TYPE、ready 0/1、HTTP route・件数・順序、custom と standard の既literalを保持する。負値はSS351に従い、同hashの二異値でも固定「invalid monitoring mode」と供給回数0を独立に確認する。

WEBPAY013の4worker/64 jobsを維持し、旧Future10秒内に加え、finallyにshutdownNowと10秒の終了を確認する。WEBFULL011の4worker/64、WEBFULL012の一workerと二つのLatchを維持し、provider、standardとBundleの寿命を各終了確認まで保つ。既30秒の結果・終了境界を維持する。FULL012では元どおりstandardを途中で閉じ、部分文字列を返さず、standardのscrape0、元例外の型を照合する。

試験は既Micrometer/Prometheusのin-memory所有物だけを使う。実HTTP、DB、JMS、配備、保護型は対象外。四静的と元26の単一run、生coverage、rawの支援不足、source／依存SHAをPG39500へ記録する。
