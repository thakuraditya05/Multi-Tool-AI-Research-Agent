from mcp.server.fastmcp import FastMCP

# Naya MCP server initialize kar rahe hain
mcp = FastMCP("MathServer")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers (a - b)"""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> str | float:
    """Divide two numbers (a / b)"""
    if b == 0:
        return "Error: Division by zero is not allowed"
    return a / b

if __name__ == "__main__":
    # Server ko stdio (Standard Input/Output) mode me run karein
    mcp.run(transport='stdio')
    
    
    
    
    # mcp-server/math.py