"""Exact original-token recovery permits only two exception imports/classes, not weakened rejection."""
from public_java_digest_provenance import LEX

def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(old,new):
    assert old.count('MessageEncodingException') == old.count('PermanentProtocolException') == 2
    assert new.count('FieldEncodingException') == new.count('LayoutValidationException') == 2
    declaration = 'import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;'
    assert new.count(declaration) == 1
    restored = new.replace(declaration,'import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;')
    restored = restored.replace('FieldEncodingException','MessageEncodingException').replace('LayoutValidationException','PermanentProtocolException')
    assert tokens(restored) == tokens(old)
    return dict(originalTokens=len(tokens(old)),changedExceptionClasses=2,changedImports=2,mainChanged=False,inputAndAssertionShapeChanged=False)

def negative(old,new):
    values = [new.replace('LayoutValidationException.class','RuntimeException.class',1),new.replace('FieldEncodingException.class','IllegalArgumentException.class',1),new.replace('4097','4096',1),new.replace('10_000','9_999',1),new.replace('"row-10000"','"row-9999"',1),new.replace('assertThrows(','assertDoesNotThrow(',1),new.rstrip()[:-1]]
    for value in values:
        assert value != new
        try: inverse(old,value)
        except AssertionError: pass
        else: raise AssertionError('changed input/assertion or weaker exception accepted')
    return len(values)
