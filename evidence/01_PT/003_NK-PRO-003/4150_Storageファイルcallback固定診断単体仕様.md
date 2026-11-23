# Storageファイルcallback固定診断の単体仕様

NK-PRO-003／NK-SCN-001、RD FIL-001～009、UI237、SS333 §7.3、SSC-019・461。WBS-P003-05、F03、F02の構造証拠。対象は `OwnedTransferDirectory.atDirectory` から呼び出す既存FileOperation変換と外側の所有区間。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-STORAGE-CB001 | 合成ポートが借用値245を返す。callbackが既知のObjectを返す | 戻り値の同一性を保持。callback終了時のcloseは0、外側のcloseでのみ1 |
| PT-STORAGE-CB002 | FileAlreadyExistsException・NoSuchFileException・IOException・NoSuchAlgorithmExceptionをcallbackから別々に投げる | 順にCOLLISION・MISSING・UNAVAILABLE・UNAVAILABLE。固定診断、causeなし、抑制0。外側のcloseは1 |
| PT-STORAGE-CB003 | 四つの例外それぞれが合成AssertionErrorを抑制辺に持つ | 置換前に同じErrorを伝播。失敗後も外側の所有が有効で、外側のcloseは1 |

固定版の正規Storage JARから明示した純Javaの物理だけを使用する。合成ポートは実FDを開かず、全callbackは受け取るpathを使わない。実I/O・native・source全体とSSC-461の全移管は別工程。
