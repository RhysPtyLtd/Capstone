
## AST Visualizer

### Introduction

The AST Visualizer is a tool that generates visual abstract syntax trees (ASTs) from Python source code. This tool can help developers understand the structure of their code, the relationships between different code elements, and the dependencies their code has on external modules.

### Features

- Generate a graphical representation of the AST.
- Identify and color-code imports, function calls, class definitions, and function definitions.
- Report on functions used from imported modules and their respective paths.

### Requirements

- Python 3.x
- Graphviz
- PIL (Pillow)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/RhysPtyLtd/Capstone.git
   cd [repository-directory]
   ```

2. Install the required libraries:

   ```
   pip install graphviz Pillow
   ```

### Usage

   ```python
   python3 deps.py
   ```