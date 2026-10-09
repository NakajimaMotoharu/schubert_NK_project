"""Offline exact current8 + host6 XML coordinates, no VM action."""
from pathlib import Path
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg615_current_native_gap.py').read_text(),(
        ('pg614-current-eight-native-v1','pg698-current-eight-native-v1'),
        ('4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1','e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045'),
        ('23b14a44b10504172e030bbd6625926bf049fb5c','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('pg615-current-native-gap-v1','pg700-current-native-gap-v1'),
        ('pg599-candidate-bootstrap-six-host-v1','pg680-owner-six-host-v1'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<same-source qualified gap coordinates>','exec'),
         {'__file__':str(R/'pg700_native_gap.py'),'__name__':'__main__'})
