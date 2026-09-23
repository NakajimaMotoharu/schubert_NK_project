# NK-WEB-002 共有session依存実行結果

PG230/PT-SCR124～126は選択`WebApplicationTest`実行成功、追加3件のfailure/error/skipped0。隔離PostgreSQL/Artemis・実Tomcatを用い、Log MVC bean解決、Login HTTP200/承認済みタイトル、factoryへ渡したrepositoryから発行cookieのsession取得、null/誤型dependencyのbind前拒否を確認。追加後の正式全reactor・証跡収集は未実施のため、**まだ限定認定しない**。`WebApplication`選択coverage instruction132/132・line24/24・method6/6・class1/1、branchなし。実NK CHR-L01とWeb親は未完了。
