"""Source canaries for confirmed close and explicit fault provenance; no Production PT."""
from pg5940_private_lock_compile import ROOT
from pg6542_jdbc_catch_inventory import LEX
from pg6760_transfer_io_selected import TEST


def words(text):return [m.group()for m in LEX.finditer(text)if not m.group().startswith(('//','/*'))]


def count(seq,pattern):return sum(seq[i:i+len(pattern)]==pattern for i in range(len(seq)))


def verify(text):
    seq=words(text)
    contracts=((1,'delegate.close(); closedStreams++; if (injecting("close"))'),
      (2,'assertEquals(1, f.faultsInjected, "the intended fixture fault was reached");'),
      (1,'boolean heldDirectory = f.root.atDirectory(Files::isDirectory); assertTrue(heldDirectory);'),
      (1,'if (!fault.equals(name)) return false; faultsInjected++; return true;'))
    for expected,pattern in contracts:
        if count(seq,words(pattern))!=expected:raise ValueError('explicit fixture confirmation/provenance contract: '+pattern)


if __name__=='__main__':verify((ROOT/TEST).read_text());print('fixture source confirmation/provenance0; Production PT0')
