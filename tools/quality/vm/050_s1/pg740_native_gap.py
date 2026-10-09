"""Offline exact current9 plus3502 host6 XML; no source9bd import or VM operation."""
from pathlib import Path
from pg705_native_gap import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg705-current-native-gap-v1','pg740-current-native-gap-v1'),
        ('pg698-current-eight-native-v1','pg730-current-eight-native-v1'),
        ('e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045','2f575a4bbd2dd3ae83eb493c12aef0899c3702b6f9bf04bdf5bd46449facb500'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),
        ('pg704-current-nine-native-v1','pg739-current-nine-native-v1'),
        ('f5c612e6a3445c4ead6c103da1a8d77e4d323aca9ad02a525c1f426c6da9ae11','c638c89363f43431993dfc66028da722193adbff56c2cf7291929c94aa1923e1'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<current15exec XML coordinates>', 'exec'),
         {'__file__':str(R/'pg740_native_gap.py'),'__name__':'__main__'})
