import ast
from graphviz import Digraph
import pkgutil

SOURCE = "deps.py"

class ASTVisualizer(ast.NodeVisitor):
    def __init__(self):
        self.dot = Digraph()
        self._counter = 0

    def _id(self):
        """Generate a unique node id in the graph."""
        self._counter += 1
        return f'node{self._counter}'

    def visit_Import(self, node):
        node_id = self._id()
        names = ', '.join([n.name for n in node.names])
        self.dot.node(node_id, color='red', label=f"Import: {names}")
        return node_id

    def visit_ImportFrom(self, node):
        node_id = self._id()
        names = ', '.join([n.name for n in node.names])
        label = f"From: {node.module}\nImport: {names}"
        self.dot.node(node_id, color='red', label=label)
        return node_id
    
    # visit a class definition
    def visit_ClassDef(self, node):
        # Label the node with the class name
        node_id = self._id()
        self.dot.node(node_id, label=f"class def {node.name}")
        return node_id

    def visit_Call(self, node):
        """Visit a function call node and label it with the function's name and its module (if any)."""
        node_id = self._id()
        label = self.get_full_name(node.func)  # Use the get_full_name method here to get the full call name
        self.dot.node(node_id, color='red', label=label)

        # Link the current node with its children
        for field, value in ast.iter_fields(node):
            value = value if isinstance(value, list) else [value]
            for item in value:
                if isinstance(item, ast.AST):
                    child_id = self.visit(item)
                    self.dot.edge(node_id, child_id)

        return node_id

    def get_full_name(self, node):
        """Recursively get the full name (for attributes) from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_full_name(node.value)}.{node.attr}"
        else:
            return type(node).__name__  # Fallback

    def visit_FunctionDef(self, node):
        """Visit a function definition and label it with 'def {function name}'."""
        node_id = self._id()
        label = f"def {node.name}"
        self.dot.node(node_id, label=label)

        # Link the current node with its children
        for field, value in ast.iter_fields(node):
            value = value if isinstance(value, list) else [value]
            for item in value:
                if isinstance(item, ast.AST):
                    child_id = self.visit(item)
                    self.dot.edge(node_id, child_id)

        return node_id

    def generic_visit(self, node):
        """Visit a node."""
        node_id = self._id()
        self.dot.node(node_id, label=type(node).__name__)

        # Link the current node with its children
        for field, value in ast.iter_fields(node):
            value = value if isinstance(value, list) else [value]
            for item in value:
                if isinstance(item, ast.AST):
                    child_id = self.visit(item)
                    self.dot.edge(node_id, child_id)

        return node_id

    def visualize(self, source_code):
        tree = ast.parse(source_code)
        self.visit(tree)
        return self.dot

def get_imports(source_code):
    """Returns a list of modules imported in the given source code."""
    tree = ast.parse(source_code)
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                # Only add the main module name (before the first dot)
                main_module = n.name.split('.')[0]
                imports.append(main_module)
        elif isinstance(node, ast.ImportFrom):
            main_module = node.module.split('.')[0]  # Only add the main module name
            imports.append(main_module)
            
            for n in node.names:
                sub_module = n.name.split('.')[0]
                full_name = f"{node.module}.{sub_module}" if node.module else sub_module
                imports.append(full_name.split('.')[0])  # Only add the main module name

    return list(set(imports))  # Remove duplicates

class PackageFunctionCollector(ast.NodeVisitor):
    def __init__(self):
        self.imported_modules = set()  # All imported modules/packages
        self.functions_used = {}  # Mapping of module to its functions used and its path
        self.module_paths = {}  # Mapping of module to its path

    def visit_Import(self, node):
        for alias in node.names:
            module = alias.name.split('.')[0]  # Only consider the main module
            self.imported_modules.add(module)
            self.add_module_path(module)

    def visit_ImportFrom(self, node):
        module = node.module.split('.')[0]
        self.imported_modules.add(module)
        self.add_module_path(module)

        # Add imported functions from this module to functions_used
        for alias in node.names:
            if module not in self.functions_used:
                self.functions_used[module] = []
            self.functions_used[module].append(alias.name)

    def add_module_path(self, module_name):
        loader = pkgutil.get_loader(module_name)
        if loader is not None and hasattr(loader, 'path'):
            self.module_paths[module_name] = loader.path

    def visit_Call(self, node):
        # If the call is an attribute and is an imported module, add to functions_used
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self.imported_modules:
            module = node.func.value.id
            function_name = node.func.attr
            if module not in self.functions_used:
                self.functions_used[module] = []
            if function_name not in self.functions_used[module]:
                self.functions_used[module].append(function_name)
        self.generic_visit(node)  # Continue visiting child nodes

    def report(self):
        # Returns a dictionary with each imported module, its functions, and its path
        report = {}
        for module, functions in self.functions_used.items():
            report[module] = {
                "functions": functions,
                "path": self.module_paths.get(module, "Unknown")
            }
        return report

def extract_functions_from_code(source_code):
    tree = ast.parse(source_code)
    collector = PackageFunctionCollector()
    collector.visit(tree)
    return collector.report()

# Test
with open(SOURCE, 'r') as f:
    source_code = f.read()

result = extract_functions_from_code(source_code)
for module, data in result.items():
    print(f"Module: {module}")
    print(f"Path: {data['path']}")
    print(f"Functions: {', '.join(data['functions'])}")
    print("------")


visualizer = ASTVisualizer()
dot = visualizer.visualize(source_code)
dot.view()