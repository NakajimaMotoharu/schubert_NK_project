"""Fixed typed-guard candidate artifact/source inputs, not old Product qualification."""
import g07_host_class_provenance_inputs as data

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREFIX='typed-marker-guard'
NORMAL_NUMBER=14216
STATIC_NUMBER=14222
NORMAL_PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'

def out(config,number):
    return data.BASE/('PG14216-typed-marker-guard-six-compile-v1' if number==NORMAL_NUMBER else 'PG'+str(number)+'-'+config.PREFIX+'-v1')

def normal():
    value=data.read_checked(out(None,NORMAL_NUMBER)/'manifest.json',NORMAL_PIN)
    assert value['source']==SOURCE and value['actualExit']==value['testsExecuted']==0
    return value,NORMAL_PIN
