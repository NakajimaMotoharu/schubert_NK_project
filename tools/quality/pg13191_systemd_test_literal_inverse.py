"""Exact independent Test strings; inverse proves all pre-existing Java tokens preserved."""
import json
from public_java_digest_provenance import LEX

CONSTANTS = {
    'BUS_NEW': 'sd_bus_new',
    'MESSAGE_NEW_METHOD_CALL': 'sd_bus_message_new_method_call',
    'BUS_CALL': 'sd_bus_call',
    'GET_PROPERTY_STRING': 'sd_bus_get_property_string',
    'GET_PROPERTY': 'sd_bus_get_property',
    'LIBC_FREE': 'free',
    'BUS_RELEASE_EVENT': 'bus',
    'REQUEST_RELEASE_EVENT': 'request',
    'REPLY_RELEASE_EVENT': 'reply',
    'SYNTHETIC_FAILURE_MESSAGE': 'synthetic',
    'MESSAGE_UNREF': 'sd_bus_message_unref',
    'BUS_CLOSE_UNREF': 'sd_bus_close_unref',
    'LOADED_STATE': 'loaded',
    'BUS_PROCESS': 'sd_bus_process',
    'UNIQUE_BUS_NAME': ':1.7',
    'MESSAGE_READ_BASIC': 'sd_bus_message_read_basic',
    'GET_PROPERTY_TRIVIAL': 'sd_bus_get_property_trivial',
    'AMD64_ARCH': 'amd64',
    'LINUX_OS': 'Linux',
    'UID_KEY': 'uid',
    'MODE_KEY': 'mode',
}

def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(old,new):
    restored = new;references = {}
    for name,value in CONSTANTS.items():
        literal = json.dumps(value);declaration = 'private static final String '+name+' = '+literal+';'
        assert restored.count(declaration) == 1 and name not in tokens(old)
        restored = restored.replace(declaration,'',1)
        references[name] = tokens(restored).count(name)
        assert references[name] == tokens(old).count(literal) >= 4
    assert len(CONSTANTS) == 21
    expanded = [json.dumps(CONSTANTS[t]) if t in CONSTANTS else t for t in tokens(restored)]
    assert expanded == tokens(old)
    return dict(privateConstants=21,originalTokens=len(expanded),referenceCounts=references,wholeSourceTokensRecovered=True)

def negative(old,new):
    variants = [new.replace('String '+name+' = '+json.dumps(value),'String '+name+' = '+json.dumps(value+'-WRONG'),1) for name,value in CONSTANTS.items()]
    variants += [new.replace('assertEquals(1, out.size());','assertEquals(0, out.size());',1),
        new.replace('remaining < 1','remaining <= 1',1),new.rstrip()[:-1]]
    for value in variants:
        assert value != new
        try:inverse(old,value)
        except AssertionError:pass
        else:raise AssertionError('non-equivalent Test mutation accepted')
    return len(variants)
