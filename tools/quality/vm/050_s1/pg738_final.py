"""Independent full21/534 post of actual737; no start/stop/repair or old proof replay."""
from pathlib import Path
from pg703_final import source as previous
from pg737_sources import current
from pg662_sources import replace

R=Path(__file__).resolve().parent


def actual_bind(raw):
    return replace(raw,tuple((a,b)for a,b in (
        ('1d70b8f79fb1aa6c1da796b181948334e2a4a7ae962a0365fb5b0c6750c4fb53','82316ed36abbedd2f85f1e26ca35cd2f10e4c1ac5c7deabc4454bcc5203257d4'),
        ('dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562','25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e'),
        ('d420de6553ef48038a40332c37a8b12e','0d42d02df3a44b7bb036140f6cc076cf'),
        ('122580694582','130424890693'),('122582163571','130426534781'),('122610694582','130454890693'),
        ('2464638','2793207'),('12258069','13042489'),('128965','138755'),
        ('==524','==534'),("'batchRows':524","'batchRows':534"),('1.468989','1.644088'),
    )if a in raw))


def source():
    return replace(actual_bind(current(previous())), (
        ('pg703','pg738'),('PG703','PG738'),('pg738-bootstrap-final-v4','pg738-bootstrap-final-v1'),
        ('pg682-manifest.sig','pg715-manifest.sig'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<independent actual737 full21>', 'exec'),
         {'__file__':str(R/'pg738_final.py'),'__name__':'__main__'})
