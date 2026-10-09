"""Current730eight plus actual737 single bootstrap only; old9/17 never imported."""
from pathlib import Path
from pg704_native import source as previous
from pg737_sources import current
from pg738_final import actual_bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(actual_bind(current(previous())), (
        ('pg704','pg739'),('PG704','PG739'),('pg703-bootstrap-final-v4','pg738-bootstrap-final-v1'),
        ('pg698','pg730'),('PG698','PG730'),
        ('e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045','2f575a4bbd2dd3ae83eb493c12aef0899c3702b6f9bf04bdf5bd46449facb500'),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a'),
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg739_native.py'),'__name__':'current9only'}
    exec(compile(source(),'<current9 native samebyte>', 'exec'),env);env['main']()
