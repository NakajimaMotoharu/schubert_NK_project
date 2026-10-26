"""New-only plan for formatted source; pre-format evidence remains immutable."""
import pg10710_graph_diagnostic_constants_plan as stage

if __name__ == '__main__':
    stage.OUT = stage.data.BASE/'PG10711-graph-diagnostic-formatted-plan-v1'
    stage.main()
