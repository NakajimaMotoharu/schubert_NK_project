# 音楽ペア移行の既定locale互換試験結果

PG44054 の PT-MIG-MUSICPAIR027 は 2026-11-24 23:24 JST に成功。実行1、失敗0、エラー0、skip0。製品Core `4d3a0f69c8241f6dd3dbe67e5fdf7b067cd98349`、試験source `07d1b62c80c892bead6f38167204fe83bf1a9843`。正規Bootstrap JARから抽出した三物理を使用した。

- en-USでは `SHINE` と大文字 `(INSTRUMENTAL)` が本編・伴奏の一組になる。期待値どおり。
- tr-TRでは大文字Iの小文字化により二ファイルが本編として扱われ、後のものが同じ表示タイトルを採用し、先のものをshadow記録に載せる。期待値どおり。
- JDK 25.0.4の隔離したJVMで実行。既定localeとカテゴリの元値を復元する。業務DB・音声・実ファイル・nativeを使用しない。
- 同一execの四指標は行77/103、メソッド16/22、クラス3/3、分岐35/62。既存26件とは別のexec。全451は未成立。
- 試験1ファイルの書式・Checkstyle・PMDは指摘0。全Bootstrap検査への加算は対象を限定する。

[単体仕様](175_音楽ペアの既定locale互換単体仕様.md) [証跡](evidence/PG44054-current-music-pairing-locale-compat/manifest.json)
