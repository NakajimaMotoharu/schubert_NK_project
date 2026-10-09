"""New currentPG750 ordinary noargs once; completed55ac is never resumed."""
from pathlib import Path
from pg722_fresh_parent import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(),(
        ('pg722','pg758'),('pg723','pg759'),('pg721','pg757'),('PG715','PG750'),
        ('pg717-completed-activate-v1','pg752-completed-activate-v1'),
        ('3849806f2d462004c9135ed29b914388bf17d903219a2dc65a73bf23764eed7a','301fd4e8c2801c5b6c2356ae789a19a7b474ed49559852667a428eaac80cf263'),
        ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'),
        ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'),
        ('==524','==534'),("'originalBatchRows':524","'originalBatchRows':534"),
        ("'priorBatchRows':524","'priorBatchRows':534"),("'priorTodayRuns':42","'priorTodayRuns':52"),
        ("'priorToday42HistoryVerified':True","'priorToday52HistoryVerified':True"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new source8d ordinary once>','exec'),{'__file__':str(R/'pg758_fresh_parent.py'),'__name__':'__main__'})
