"""Remove only one exact javap constant declaration plus its adjacent descriptor."""

def remove_constant(text,declaration,descriptor):
    lines = text.splitlines(keepends=True)
    positions = [i for i,line in enumerate(lines) if line.strip() == declaration]
    if len(positions) != 1:
        raise ValueError('exactly one constant declaration required')
    i = positions[0]
    if i+1 >= len(lines) or lines[i+1].strip() != 'descriptor: '+descriptor:
        raise ValueError('exact adjacent constant type required')
    return ''.join(lines[:i]+lines[i+2:])

def selftest():
    negatives = 0
    for declaration,descriptor in [('private static final int YEAR = 1;','I'),('private static final java.lang.String FREE = "free";','Ljava/lang/String;')]:
        block = '  '+declaration+'\n    descriptor: '+descriptor+'\n'
        before = 'header\n  method();\n    descriptor: ()V\n';after = 'header\n'+block+before[7:]
        assert remove_constant(after,declaration,descriptor) == before
        for bad in [after.replace(declaration,declaration+' changed'),after.replace('descriptor: '+descriptor,'descriptor: J',1),after.replace(block,''),after.replace(block,block+block),after.replace(block,block.splitlines(keepends=True)[0])]:
            assert bad != after
            try:remove_constant(bad,declaration,descriptor)
            except ValueError:negatives += 1
            else:raise AssertionError('non-equivalent field block accepted')
    return dict(positive=2,negative=negatives)
