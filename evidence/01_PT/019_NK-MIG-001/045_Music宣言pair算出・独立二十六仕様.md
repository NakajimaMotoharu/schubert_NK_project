# Music宣言pair算出・独立26仕様

NK-MIG-001/MIG-DAT-003/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC360、WBS-P01903.02。

UI223§7の「曲」一group内の現行pair規則とCurrent公開MusicService.java trackPairs/displayTitle/pairKey/isInstrumental/removeClosestInstrumental/levenshteinDistanceを、純値bootstrap.migration.MusicMigrationPairingへ具体化する。RD MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/FUN-008/DAT-004、UI223/242/243/254、SS311/331/34310.1.3/4。実129file/カテゴリsection分割/Current inventory/hash/安定ID/DB保存/全移行の受入は別。これは一つの「曲」groupの宣言displayPath→title mapだけを受ける算出部品で、別groupを混ぜず呼ぶのは上位assembly責務。

plan(Nullable Map<Nullable String,Nullable String>)はsnapshotし、null map/key/value、空/不正UTF8/nonNFC/ISO control、path512byte超/title256byte超を固定IAE。pathは相対POSIXで先頭末尾slash/backslash/空segment/dot/dotdotを拒否し、trim/補完/FS照合をしない。正UTF8byteのunsigned辞書順でpathを固定し、Unicode codepoint昇順と同じ順序にする。正UTF8/NFCは既移行境界の不変条件で、値を勝手に正規化しない。

Currentの正確なliteral規則を維持する。Instrumentalはtitle.toLowerCase(Locale.getDefault())にinstまたはinstrumentを含む（instinct等も現行どおり）。LocaleはCurrent同様既定を参照し変更しない。displayTitleは先頭^数字-数字\\s+、半全角括弧inst/instrument注記以降、空白＋inst/instrument以降を現行正規表現のまま除去しtrim。pair keyはdisplayTitleを同じ既定localeで小文字化し、Current literal文字集合だけを除去する（一般Unicode punctuation除去へ拡張しない、日本語、。を勝手に除去しない）。Java regex/UTF16 charAtのLevenshteinを維持し、空の導出keyも現在の算出値として保持する。空keyをDBのM/Iに保存できるとはしない。

path昇順の各trackをMain/InstrumentalのLinkedHashMapへputする。正規化key衝突時はCurrentどおり後の値で置換し最初のkey挿入位置を維持する。置換で画面pairから隠れる元pathは別immutable shadowedPathsへ記録し、データを黙って消失させない（公開画面や保存roleを新設しない）。Main mapの値順で同一keyInstrumentalを一回remove、無ければ残Instrumentalのkeyに対しUTF16 Levenshteinの最小2以内・最初の候補を一回remove、最後に未使用Instrumental値順。最小距離初期値3で候補nullのみを判定すればCurrentの<=2と同じで、到達不能なbestDistance<=2かつbestKey=nullの追加枝を作らない。距離は二int配列入替え、グローバル状態なし。

手書きprivate constructorのimmutable nested Pairはtitle/key/Optional mainDisplayPath/Optional instrumentalDisplayPathを返す。Resultはimmutable pairs/shadowedPathsを返す。Main/Pair/Result toStringは固定redacted。public input値のrecord生成filterや手抜きcoverage除外を追加しない。Map入力を保持せず返却list/optional値は他呼出と独立。両side欠落Pairは生成しない。shadowed/空導出keyを自動修復・別pairroleで保存しない。実データで保存表現に問題があれば、その範囲の既設計/必要QAを先行し、当算出成功を保存合格へ読み替えない。

PT-MIG-MUSICPAIR001..026: 空、一対exact、Mainのみ、Instのみ、case/instinct役割、prefixと必要空白、半全角/閉じ無し注記とsuffix、正確な記号集合と残る日本語句読点、距離1（insert/delete/replace/空両側）、距離2、距離3拒否、exact優先、最小距離優先、同距離path先頭、再使用無し、Main後未対応Inst順、宣言map順逆転/Unicode codepoint順、両roleのduplicatekey上書き/最初key順/全shadowed列挙、空導出key、null境界、危険path、UTF8/NFC/control/不正surrogate、path512/513-title256/257境界、immutable/alias/三redaction、拒否後独立正常/任意pathと導出title、finite8workers64/Future5/finallyshutdownNow-await10。期待pairとshadowed値は手書きliteral、距離の独立表は別Python matrixで検算しproduction methodでexpectedを作らない。実Current code/source hashとregex literal対応を証跡化し実masterは読まない。

新Pairing26のwhole一Main三physical、同source/一exec/通常Root静的/NullAway/lintWerror/独立CRC-init/XML/四100/実Codeを検証する。追加不足1.75/5.25/10.5未較正を詳細+PG26 1.25/3.75/7.5cap8、normal26 .5/1.5/3cap4に分離。元費用/SV上限保持、token/専有費null。実Current129/DB/全ETL/Root/native/CHR/451全体/ITSTとHOLDは未受入。
