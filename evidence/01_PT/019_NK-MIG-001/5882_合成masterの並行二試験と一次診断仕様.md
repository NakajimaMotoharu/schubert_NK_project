# 合成masterの並行試験と一次診断

NK-MIG-001、SS343・354、WBS-P019-03.02/2、BUG-3930、YKT-2997。

- PT-MIG-FINGER016は、8 workerに64件を供給する。各結果が元fixtureの独立固定の件数・bytes・SHA-256の6行に一致し、同じ呼出先で値が混ざらないことを確認する。
- PT-MIG-MASTER020は、8 workerに64件を供給する。呼出しごとに別のmemory sinkで、6つの元固定UTF-8行列・順序が一致することを確認する。

Futureの上限は5秒、所有workerの停止は10秒。本体例外と停止例外が重なる場合、元失敗を主に保持する。既共通診断試験と仕上げ後の通常PTを別に参照する。正規Bootstrapと関連されるJDK SDK、source、selected XML、終了値、未加工coverageを同実行に保存する。接続DB・実資源・COPY SDKは使用しない。
