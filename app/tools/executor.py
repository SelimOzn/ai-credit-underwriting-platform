from app.tools.registry import TOOL_REGISTRY

def execute_tool(name: str, args: dict):
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Tool {name} not registered")
    tool = TOOL_REGISTRY[name]

    return tool.invoke(args)