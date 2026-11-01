# Root ELF digest原8・現source単体テスト仕様

群PG17310、事前event3633、見積低1.5/標準4/高8共有pp・cap10。source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、正式1964PT/53scope・工数nullは不変。Program RootServiceExecutableAdmission.digest、Test RootElfDigestPortTest全8。関連RD/UIは既1045のNK-OPS-001追跡、SS343/354/SSC137/143/306。既1045の全8 ID/method・literal oracleを継承し、旧source成功は転用しない。

PT_DEFAULT：全Test253行とMain全体、digest/require/StorageIoExceptionのcalleeを読取照合。入力は64byte/8MiBの公開synthetic ELF、SeekableByteChannelはTestのmemory Inputのみ。JCA SHA256を利用する（crypto=true）、provider/global設定を変更しない。任意ファイル/秘密key/DB/VM/Root/サービス操作はしない。Testは元wholeを変更/抽出せず、実OS admission/admit/withSetpriv/RootDescriptorは呼ばない。全Main Source五physical（Code二、SAM NoCode三）を分母へ残す。

001固定SHA・factory一回・借用close0/zeroize、002NoSuchAlgorithmのredaction、003Runtime/Error同一性、004null fail-fast/read0、0058193誤申告拒否、006chunk1/7/64/8192、007read失敗三型identity/zeroize、0088MiB固定SHA。期待値は1045のliteralと独立hashlib算出、Productionから生成しない。nullによるNPEは境界fail-fastをassertする既契約でありcatch正常化ではない。

command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17310_root_elf_digest_eight_pt.py
新規専用slotで原8だけを実行し、真正終了/XML/FES0・同source/session/CRCと全Source coverageを独立postで照合する。部分coverage/未実行を100扱いしない。四held/六native/Root回収等不実行を受動exec読取で照合する。実行前なので結果/coverageは未確定。全体正式品質/CHR/OS admission/native受入は未達のまま。
