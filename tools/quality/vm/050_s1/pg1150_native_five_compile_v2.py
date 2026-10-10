"""BUG1039/YKT808: separate immutable helper input from fresh fixture outputs."""
import ast
from pg1149_native_five_compile import source as previous

FIXTURES={'BackupPublicationFixture','BackupArtifactFixture','BackupManifestFixture'}


def helper_input(name):
    base=name.rsplit('/',1)[-1]
    return base.endswith('.class')and base[:-6].split('$',1)[0]not in FIXTURES


def source():
    text=previous().replace('pg1148-native-five-tools-v1','pg1148-native-five-tools-v2').replace('pg1149-native-five-frozen-v1','pg1150-native-five-frozen-v2').replace('PG1149-native-five-compile-v1','PG1150-native-five-compile-v2')
    marker="if name.endswith('.class'):\n            p=W/'pg1144-terminal-tools-v1'/name"
    if text.count(marker)!=1:raise ValueError('fixed immutable input/output separation refused')
    text=text.replace(marker,"if name.endswith('.class')and name.rsplit('/',1)[-1][:-6].split('$',1)[0]not in {'BackupPublicationFixture','BackupArtifactFixture','BackupManifestFixture'}:\n            p=W/'pg1144-terminal-tools-v1'/name")
    text=text.replace("text.replace('pg1134-issued-api-tools-v1','pg1148-native-five-tools-v2')", "text.replace('pg1148-native-five-tools-v1','pg1148-native-five-tools-v2')")
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<new-only separated native compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
