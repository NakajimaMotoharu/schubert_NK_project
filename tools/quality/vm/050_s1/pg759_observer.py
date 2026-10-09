"""Observer first, same freshRoot/source8d; no second start or old generation reuse."""
from pathlib import Path
from pg723_observer import source as previous, watch as previous_watch
from pg662_sources import replace

R=Path(__file__).resolve().parent


def watch():return replace(previous_watch(),(('PG715','PG750'),))


def source():
    return replace(previous(),(
        ('pg723','pg759'),('PG722','PG758'),('pg722','pg758'),('PG715','PG750'),
        ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'),
        ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<current750 same freshRoot observer>', 'exec'),{'__file__':str(R/'pg759_observer.py'),'__name__':'__main__','watch':watch})
