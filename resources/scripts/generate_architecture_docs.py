import os
import ast
import re

# Define paths to scan
PYTHON_AGENT_PATH = "Mobile-Agent-E/MobileAgentE/"
ANDROID_APP_PATH = "LuxoAI/app/src/main/"
OUTPUT_FILE = "resources/ARCHITECTURE.md"

def analyze_python_code(directory):
    """
    Analyzes Python code in the given directory using the AST module.
    Extracts class definitions, function definitions, and import statements.
    Attempts to identify basic relationships (calls, inheritance - basic version).
    """
    components = {"classes": {}, "functions": {}, "relationships": set()}
    print(f"Analyzing Python code in {directory}...")

    def get_call_context(stack):
        caller_name = None
        caller_class_name = None
        for p_node in reversed(stack):
            if isinstance(p_node, ast.FunctionDef):
                caller_name = p_node.name
                # Check if this function is a method of a class by looking further up stack
                for pp_node in reversed(stack[:stack.index(p_node)]): # Stack before current func def
                    if isinstance(pp_node, ast.ClassDef):
                        caller_class_name = pp_node.name
                        break
                break
            elif isinstance(p_node, ast.ClassDef): # Call directly in class scope
                caller_class_name = p_node.name
                break
        if caller_class_name and caller_name:
            return f"{caller_class_name}.{caller_name}"
        return caller_name or caller_class_name


    def find_calls_recursive(node, current_stack, components, current_module):
        """Recursively find calls within a node (e.g., function body, class body)."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name): # Simple direct calls like func_name()
                callee_name = node.func.id
                caller_context = get_call_context(current_stack)
                if caller_context:
                    components["relationships"].add((caller_context, callee_name, "calls"))
            elif isinstance(node.func, ast.Attribute): # e.g. self.method(), obj.method()
                # Could try to resolve self or obj type if needed, but for now just note the call name
                callee_name = node.func.attr
                caller_context = get_call_context(current_stack)
                # We might want to know what `node.func.value` (the object being called upon) is.
                # For now, just link context to the method name.
                if caller_context:
                     components["relationships"].add((caller_context, callee_name, "calls_attr"))


        for child_node in ast.iter_child_nodes(node):
            find_calls_recursive(child_node, current_stack + [node], components, current_module)


    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                print(f"  Processing Python file: {filepath}")
                try:
                    with open(filepath, "r", encoding="utf-8") as source_file:
                        source_code = source_file.read()
                    tree = ast.parse(source_code, filename=filepath)
                    current_module = os.path.splitext(file)[0]

                    for node in tree.body: # Iterate over top-level nodes in the module
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            base_classes = [base.id for base in node.bases if isinstance(base, ast.Name)]
                            components["classes"][class_name] = {"module": current_module, "bases": base_classes, "methods": []}
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef): # Method
                                    method_name = item.name
                                    components["classes"][class_name]["methods"].append(method_name)
                                    # Now find calls within this method's body (which is a list of nodes)
                                    for stmt in item.body:
                                        find_calls_recursive(stmt, [tree, node, item], components, current_module)
                            for base_class in base_classes:
                                components["relationships"].add((base_class, class_name, "inherits"))

                        elif isinstance(node, ast.FunctionDef): # Module-level function
                            func_name = node.name
                            components["functions"][func_name] = {"module": current_module, "calls": []}
                            # Now find calls within this function's body (which is a list of nodes)
                            for stmt in node.body:
                                find_calls_recursive(stmt, [tree, node], components, current_module)

                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                imported_name = alias.name
                                components["relationships"].add((current_module, imported_name.split('.')[0], "imports"))

                        # Find calls in module-level code if any (less common for complex logic)
                        find_calls_recursive(node, [tree], components, current_module)


                except Exception as e:
                    print(f"    Error parsing {filepath}: {e}")
    return components

def analyze_android_code(directory):
    """
    Analyzes Android (Kotlin/Java) code in the given directory using regex.
    Extracts class definitions, method definitions, and attempts to find calls.
    """
    components = {"classes": {}, "methods": {}, "relationships": set()}
    print(f"Analyzing Android code in {directory}...")

    class_pattern = re.compile(r"class\s+(\w+)\s*(?::\s*(\w+)\s*\(.*?\))?.*?\{", re.DOTALL) # Catches class Name and optional inheritance (simplified)
    method_pattern = re.compile(r"fun\s+(\w+)\s*\(.*?\)|void\s+(\w+)\s*\(.*?\)|@Composable\s*\n\s*fun\s+(\w+)\s*\(.*?\)", re.DOTALL) # Kotlin fun, Java void, Composable fun
    call_pattern = re.compile(r"\b(\w+)\s*\.\s*(\w+)\s*\(", re.DOTALL) # object.method() or Class.method()
    instantiation_pattern = re.compile(r"val\s+\w+\s*:\s*(\w+)|new\s+(\w+)\s*\(", re.DOTALL) # val foo: Type | new Type()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".kt", ".java")):
                filepath = os.path.join(root, file)
                current_module = os.path.splitext(file)[0]
                print(f"  Processing Android file: {filepath}")
                try:
                    with open(filepath, "r", encoding="utf-8") as source_file:
                        content = source_file.read()

                    # Find classes
                    for match in class_pattern.finditer(content):
                        class_name = match.group(1)
                        inherited_class = match.group(2) # Simplified, might not always be correct
                        if class_name not in components["classes"]:
                             components["classes"][class_name] = {"module": current_module, "methods": [], "super_class": inherited_class}
                        if inherited_class:
                            components["relationships"].add((inherited_class, class_name, "inherits"))

                        # Find methods within this class block (approximate)
                        # This is a simplification; proper parsing would be better.
                        # We assume methods are defined after "class ... {" and before the next class or EOF.
                        class_block_end = content.find("}", match.end())
                        class_block_end = class_block_end if class_block_end != -1 else len(content)
                        class_content = content[match.end():class_block_end]

                        for m_match in method_pattern.finditer(class_content):
                            method_name = m_match.group(1) or m_match.group(2) or m_match.group(3)
                            if method_name:
                                components["classes"][class_name]["methods"].append(method_name)
                                if class_name not in components["methods"]:
                                    components["methods"][f"{class_name}.{method_name}"] = {"module": current_module}

                                # Find calls within this method (approximate)
                                method_block_match = re.search(r"fun\s+" + re.escape(method_name) + r"\s*\(.*?\)\s*\{([\s\S]*?)\n\s*\}", class_content[m_match.start():], re.DOTALL)
                                if method_block_match:
                                    method_body = method_block_match.group(1)
                                    for call_match in call_pattern.finditer(method_body):
                                        obj_or_class_name = call_match.group(1)
                                        called_method_name = call_match.group(2)
                                        # If obj_or_class_name is a known class, or common (e.g. Log, Toast)
                                        if obj_or_class_name in components["classes"] or obj_or_class_name in ["Log", "Toast", "Intent", "Bundle", "Context"]:
                                            components["relationships"].add((f"{class_name}.{method_name}", f"{obj_or_class_name}.{called_method_name}", "calls"))
                                        # Could also check if obj_or_class_name is an instance of a known class
                                    for inst_match in instantiation_pattern.finditer(method_body):
                                        inst_class_name = inst_match.group(1) or inst_match.group(2)
                                        if inst_class_name and inst_class_name in components["classes"]:
                                            components["relationships"].add((f"{class_name}.{method_name}", inst_class_name, "instantiates"))


                except Exception as e:
                    print(f"    Error parsing {filepath}: {e}")
    return components

def generate_plantuml_diagram(python_components, android_components):
    """
    Generates PlantUML diagram syntax from extracted components.
    """
    print("Generating PlantUML diagram...")
    plantuml_syntax = "@startuml\n"
    plantuml_syntax += "skinparam componentStyle uml2\n"
    plantuml_syntax += "skinparam linetype ortho\n\n" # Orthogonal lines for better readability

    plantuml_syntax += 'package "Python Agent (Mobile-Agent-E)" <<Frame>> {\n'
    for class_name, details in python_components.get("classes", {}).items():
        plantuml_syntax += f'  component "{class_name}" as Py{class_name}\n'
    for func_name, details in python_components.get("functions", {}).items():
        plantuml_syntax += f'  component "{func_name}()" as PyFunc{func_name}\n' # Distinguish functions
    plantuml_syntax += '}\n\n'

    plantuml_syntax += 'package "Android Application (LuxoAI)" <<Frame>> {\n'
    for class_name, details in android_components.get("classes", {}).items():
        plantuml_syntax += f'  component "{class_name}" as Android{class_name}\n'
    # We might not want to list all methods as separate components unless they are very high-level
    plantuml_syntax += '}\n\n'

    # Add relationships
    # Python relationships
    for source, target, type in python_components.get("relationships", set()):
        # Normalize names to match diagram aliases
        source_alias = f"Py{source}" if source in python_components.get("classes", {}) else f"PyFunc{source}" if source in python_components.get("functions", {}) else f"Py{source}" # fallback for modules
        target_alias = f"Py{target}" if target in python_components.get("classes", {}) else f"PyFunc{target}" if target in python_components.get("functions", {}) else f"Py{target}"

        if type == "inherits":
            plantuml_syntax += f'  {source_alias} --|> {target_alias} : {type}\n'
        elif type == "calls":
            plantuml_syntax += f'  {source_alias} ..> {target_alias} : {type}\n' # Dotted for calls
        elif type == "imports":
             # For imports, we might want to represent it as a package dependency if target is a module
            if target_alias.startswith("Py") and not target_alias.startswith("PyFunc"): # Assuming target is a module/class here
                 plantuml_syntax += f'  {source_alias} ..> {target_alias} : {type}\n'


    # Android relationships
    for source, target, type in android_components.get("relationships", set()):
        source_alias = f"Android{source.split('.')[0]}" # Assume source is Class.method or Class
        target_alias = f"Android{target.split('.')[0]}" # Assume target is Class.method or Class

        # Ensure aliases exist if they are specific methods, otherwise use class alias
        if source in android_components.get("classes", {}): source_alias = f"Android{source}"
        if target in android_components.get("classes", {}): target_alias = f"Android{target}"

        # Avoid self-loops for simplicity in this diagram unless very specific
        if source_alias == target_alias and type != "calls_within_class": continue


        if type == "inherits":
            plantuml_syntax += f'  {source_alias} --|> {target_alias} : {type}\n'
        elif type == "calls" or type == "instantiates":
            plantuml_syntax += f'  {source_alias} ..> {target_alias} : {type}\n'

    # Placeholder for cross-system relationships (e.g., Python agent controlling Android UI)
    # This would require more semantic understanding or explicit annotations
    # For now, we can add a conceptual link.
    # Example: plantuml_syntax += 'PyController ..> AndroidMainActivity : controls via ADB\n'
    # Based on file reading, we know controller.py in Python and MainActivity.kt in Android are key.
    if "Operator" in python_components.get("classes", {}) and "MainActivity" in android_components.get("classes", {}):
        plantuml_syntax += '  PyOperator ..> AndroidMainActivity : (conceptual) interacts with via ADB commands\n'
    if "Chaquopy" not in python_components.get("classes", {}) and "Chaquopy" not in android_components.get("classes",{}): # Add a general Chaquopy node
        plantuml_syntax += 'package "Integration" <<Cloud>> {\n component "Chaquopy" as ChaquopyIntegration\n}\n'
        plantuml_syntax += 'PyOperator ..> ChaquopyIntegration : (conceptual) Python execution via\n'
        plantuml_syntax += 'ChaquopyIntegration ..> AndroidMainActivity : (conceptual) embedded in\n'


    plantuml_syntax += "\n@enduml\n"
    return plantuml_syntax

def generate_markdown_summary(python_components, android_components):
    """
    Generates a Markdown summary of the architecture from extracted components.
    """
    print("Generating Markdown summary...")
    summary = "## Architecture Overview\n\n"
    summary += "This document provides a high-level overview of the LuxoAI project architecture, generated by analyzing the codebase. It includes the Python agent and the Android application components.\n\n"

    summary += "### Python Agent (Mobile-Agent-E)\n"
    summary += "Key components found in `Mobile-Agent-E/MobileAgentE/`:\n"
    if python_components.get("classes"):
        summary += "#### Classes:\n"
        for name, details in python_components["classes"].items():
            summary += f"- **`{name}`**: (Module: `{details.get('module', 'N/A')}`)"
            if details.get("bases"):
                summary += f", Inherits: `{', '.join(details['bases'])}`"
            summary += "\n"
            # if details.get("methods"):
            #     summary += f"  - *Methods*: `{', '.join(details['methods'][:3])}`{', ...' if len(details['methods']) > 3 else ''}\n"
    if python_components.get("functions"):
        summary += "\n#### Standalone Functions:\n"
        for name, details in python_components["functions"].items():
            summary += f"- **`{name}()`**: (Module: `{details.get('module', 'N/A')}`)\n"
    summary += "\n"

    summary += "### Android Application (LuxoAI)\n"
    summary += "Key components found in `LuxoAI/app/src/main/`:\n"
    if android_components.get("classes"):
        summary += "#### Classes:\n"
        for name, details in android_components["classes"].items():
            summary += f"- **`{name}`**: (Module: `{details.get('module', 'N/A')}`)"
            if details.get("super_class"):
                summary += f", Inherits/Implements: `{details['super_class']}`"
            summary += "\n"
            # if details.get("methods"):
            #     summary += f"  - *Notable Methods*: `{', '.join(details['methods'][:3])}`{', ...' if len(details['methods']) > 3 else ''}\n"
    summary += "\n"

    summary += "### Identified Relationships & Interactions\n"
    summary += "The following is a simplified list of observed or inferred interactions:\n"

    py_rels = python_components.get("relationships", set())
    if py_rels:
        summary += "\n**Python Agent Internal:**\n"
        for src, tgt, type in sorted(list(py_rels)):
            summary += f"- `{src}` {type.replace('_', ' ')} `{tgt}`\n"

    android_rels = android_components.get("relationships", set())
    if android_rels:
        summary += "\n**Android App Internal:**\n"
        for src, tgt, type in sorted(list(android_rels)):
            if src.split('.')[0] == tgt.split('.')[0] and type != "inherits": # Avoid too much noise from intra-class calls for summary
                continue
            summary += f"- `{src}` {type.replace('_', ' ')} `{tgt}`\n"

    summary += "\n**Cross-System (Conceptual):**\n"
    summary += "- The Python agent (specifically components like `Operator`) is intended to interact with the Android application by sending ADB commands (e.g., tap, swipe, type).\n"
    summary += "- Chaquopy is the planned mechanism for embedding and running Python code within the LuxoAI Android app.\n"
    summary += "\n*Note: This is an automated analysis. Some relationships might be simplified or inferred.*\n"

    return summary

def main():
    # Add parent_stack attribute to AST nodes for easier traversal by analyze_python_code
    # This is a common pattern to augment AST nodes.
    def add_parent_stack(node):
        node.parent_stack = []
        for child in ast.iter_child_nodes(node):
            child.parent_stack = [node] + node.parent_stack
            add_parent_stack(child)

    original_walk = ast.walk
    def new_walk(node):
        # Before we start walking, ensure the root node has an empty parent_stack
        if not hasattr(node, 'parent_stack'):
            node.parent_stack = []

        # Now, populate parent_stack for all children before yielding them
        for child in ast.iter_child_nodes(node):
            child.parent_stack = [node] + node.parent_stack
            # Recursively ensure children's children also get parent_stack
            # This is a bit tricky with how ast.walk works.
            # A simpler way for analyze_python_code might be to manually recurse
            # and pass parent stack.
            # For now, this basic augmentation will be done before the main walk in analyze_python_code.
            # Let's adjust analyze_python_code to handle this.
        return original_walk(node)

    # The ast.walk augmentation is tricky. Instead, pass parent manually in analyze_python_code.
    # Reverting the ast.walk monkeypatch. analyze_python_code will be adjusted.

    print("Starting architecture documentation generation...")

    python_components = analyze_python_code(PYTHON_AGENT_PATH)
    android_components = analyze_android_code(ANDROID_APP_PATH)

    plantuml_diagram = generate_plantuml_diagram(python_components, android_components)
    markdown_summary = generate_markdown_summary(python_components, android_components)

    with open(OUTPUT_FILE, "w") as f:
        f.write("# LuxoAI Architecture\n\n")
        f.write("## Component Diagram (PlantUML)\n\n")
        f.write("```plantuml\n")
        f.write(plantuml_diagram)
        f.write("```\n\n")
        f.write(markdown_summary)

    print(f"Architecture documentation generated at {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
