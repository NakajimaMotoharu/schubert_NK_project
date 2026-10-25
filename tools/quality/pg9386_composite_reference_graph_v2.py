"""BUG1747 remedy: original failed producer preserved; new-only v2 class metadata output."""
import pg9386_composite_reference_graph as graph

if __name__=='__main__':
    graph.OUT=graph.BASE/'PG9386-composite-reference-graph-v2'
    graph.main()
