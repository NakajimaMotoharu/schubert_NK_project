# TransferIO 内部契約・独立試験計画（準備、未着手）

1472訂正/1477原counterに基づく後続候補、WBS-P017-09（実着手時は484の実leafを確認して費用二重化0）。現6748のMain/Testは変更せず、群開始予算・新PG/PT・受入はまだ0。元4189/原6750/当品質/traceを完了してから着手する。以後actual source/counterに変化があれば再照合する。

SS333§12/341・SSC118の外部契約は不変：固定保持FD/NOFOLLOW/正規実在日付とUUID、strict mtime-before、同device/uid/gid/mode/nlink/ACL/localRW、各前後再観測、個別file失敗はWARNING継続、parent gate不明は全体非成功、空の正規日付だけ削除、root/再帰削除0。現Mainに合成失敗を投じるため実原本/VM/Rootを触らず、fresh TempDirのpublic entryだけに限る。

## PG候補と責務

残gapは104の冗長upper-year、inspectのdirectory nlink/size/device/filesystem、sameDirectoryの各identity差、absent false、namesのiterator IOException/invalid entry。既year0/1/9999は3048002で済みなので重複新規試験を作らない。private reflection/不安定race/coverage除外で解消しない。

内部testabilityを整備する場合、既package-private constructorは同じProduction NIO実装へ委譲し、追加package-private constructorで限定Ioを借用する。Io候補はmetadata(Path)、filesystem(Path)、openNames(Path)、absent(Path)の読取だけ。実装は従来と同じFiles.readAttributes/Files.getFileStore/newDirectoryStream/NOFOLLOW存在確認に一対一委譲し、削除/開くentry/Path選択は引き続き既OwnedTransferDirectory/DirectoryCallsだけが所有する。Ioへdeleteやcaller指定root、権限操作を追加しない。追加型が必要なら物理Main増分を明記し、旧1667guardを曖昧化せず新sourceの正確な個数/追加class名で全原Jarを照合する。

mapの欠落/nullは既EnvironmentInodePolicy.metadataのfail-closed、filesystem/null streamも固定IOException/StorageIoExceptionで拒否しNPEを正常化しない。TWRでstreamを正規close、DirectoryIteratorExceptionは固定catalogへ、既親guardとfile個別warningの区別・同device比較を保つ。内部詳細分類5の範囲を超えるならSSC/QAを先行、外部期待値はコード都合で変更しない。

日付upper整理は8ASCII桁→year桁0000～9999→strict parse→year0だけ保全という受理集合の数学的同値を独立に記録する。単に到達不能として除外しない。削除するならguardはyear<1を残し、既0/1/9999に加えて9桁/符号/全角/無効閏日をpublic directory literalで保全確認する。上限検査を外部から入力できる別経路へ移して抜けを作らない。PG必要性/障害/横展開は実際の着手時に先行記録する。

## 独立PT候補

- 新metadata入力は実TempDirの公開attrsを複写して単一fieldだけ異常化。size<0、directory nlink<2、child device差、unsupported/null filesystemで対象保全又は親拒否をSSの責務ごとに確認する。
- root admission後のuid/gid/mode/dev/ino差を一つずつ入力、全五predicateの拒否とfile/parent byte・inode・ownedFD後条件を確認する。実root交換/UID変更/別deviceへmountしない。
- 削除要求の後に読み取り側からentry存在を返す故障は、既DirectoryCallsのself-owned unlink failure/nonremoval fixtureと読取口を組合せ、falseを成功へ数えない。外部元fileへ触れない。
- 自己所有のDirectoryStream faultでiterator/close例外・null entry名を確認。stream/FD全解放、固定診断のみ、失敗時0件成功・UNKNOWNをemptyへ補完0。path/getFileNameのnullは読取口から明示した不正provider入力で、private methodを直接呼ばない。
- 既TransferCleanupTest/FailureTestのmtime/size/link/symlink/深さ/親guard/null/既year境界を全byte固定で関連回帰。Test ID・独立期待値/入力/観点/commandは着手仕様で固定し、実行未済を合格にしない。

この段階は計画詳細化で、追加費/消化率/完成率を推定計上しない。PGPTの正式1964/53・17/190・工数null・全実環境HOLD/PTALT代替0/QA051finalを維持し、通常小群完了だけでは停止しない。
