from graphviz import Digraph

def create_ai_pipeline_flowchart():
    # Create a directed graph
    dot = Digraph(comment='AI Pipeline Flowchart', format='png')

    # Add nodes
    dot.node('A', 'Data Ingestion')
    dot.node('B', 'Data Preprocessing')
    dot.node('C', 'Model Training')
    dot.node('D', 'Model Deployment')
    dot.node('E', 'Model Monitoring')

    # Add edges
    dot.edge('A', 'B', label='Data Collection')
    dot.edge('B', 'C', label='Data Preparation')
    dot.edge('C', 'D', label='Model Deployment')
    dot.edge('D', 'E', label='Model Monitoring')
    dot.edge('E', 'C', label='Model Retraining', style='dashed')

    # Render the graph
    dot.render('ai_pipeline_flowchart', view=True)

if __name__ == '__main__':
    create_ai_pipeline_flowchart()