# OutboxDlqMetadata 単体テスト仕様

SS312/321/324/331、SSC155、SS351、451。WBS-P006-02/P018-10.03 CATALOG-021/F03、元PT-QST-DLQ-MODELのwhole2は不変。追加PT-QST-DLQ-VALUESは公開合成UUID・固定時刻・識別文字列から値を構成し、origin、transport、count、timestampを変更する独立期待を使う。正規エラー値はSS固定で、未知エラーの拒否は元試験を使う。要素同一性、null/異型、固定秘匿診断を確認する。製品・電文・送信を変更しない。BUG-3217・YKT-2431。実JMS/DB/権限の試験は含めない。証跡PG38260以降を参照。
