import os
from graph.builder import graph

try:
    png_graph_bytes = graph.get_graph().draw_mermaid_png()
    file_name = "lms_agent_workflow.png"
    with open(file_name, "wb") as f:
        f.write(png_graph_bytes)

    print(f"Graph saved as '{file_name}' in your current directory.")

except Exception as e:
    print("Error: Could not generate Mermaid graph.")
    print(f"Details: {e}")