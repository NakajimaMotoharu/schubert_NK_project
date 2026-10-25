"""BUG1747/1748 remedies, prior source/failures retained, new-only third output."""
import pg9386_composite_reference_graph as graph

if __name__=='__main__':
    graph.OUT=graph.BASE/'PG9386-composite-reference-graph-v3'
    graph.main()
