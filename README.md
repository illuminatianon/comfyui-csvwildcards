# CSV Wildcard Node for ComfyUI

A ComfyUI custom node that provides dynamic text substitution using wildcards and CSV files. Perfect for creating varied prompts with consistent relationships between terms.

## Installation

1. Navigate to your ComfyUI's custom_nodes directory
2. Clone this repository: `git clone https://github.com/illuminatianon/comfyui-csvwildcards.git`
3. Restart ComfyUI

## Usage

### Basic Structure

The node system provides two main ways to substitute text:

1. Simple wildcards: `{filename}` or `{directory/filename}`
2. CSV-based wildcards: `{csv:filename:column}` or `{csv:directory/filename:column}`

### Simple Wildcards

For simple wildcards, create text files in the `data` directory. You can organize them in subdirectories:

```
data/
  animal.txt
  appendage.txt
  texture.txt
  pokemon/
    types.txt
    moves.txt
  monsters/
    abilities.txt
    features.txt
```

Each text file should contain one option per line. For example, `animal.txt`:
```
wolf
dragon
bear
tiger
```

Use these in your template with either direct filename or directory path:
```
A {animal} with {texture} fur                     # Direct file reference
A {pokemon/types} Pokemon with {monsters/abilities} ability  # Using directory paths
```

### CSV Wildcards

CSV wildcards allow you to maintain relationships between related terms. Create CSV files in the `data` directory, optionally organizing them in subdirectories:

```
data/
  monster.csv
  pokemon/
    moves.csv
    abilities.csv
```

Example `monster.csv`:
```csv
color,size,texture
red,large,scaly
blue,small,furry
green,medium,slimy
purple,tiny,rough
```

Use these in your template with either direct filename or directory path:
```
The {csv:monster:color} creature was {csv:monster:size}                    # Direct file reference
A Pokemon with {csv:pokemon/moves:name} that causes {csv:pokemon/moves:effect}  # Using directory path
```

Important: When using CSV wildcards, all references to the same CSV file in a single prompt will use values from the same row, maintaining consistency in your descriptions.

### Node Setup

1. Add a `CSVWildcardNode` to your workflow
2. Enter your prompt template in the text area
3. Connect the output to any node that accepts a string input (like a CLIP Text Encode node)

### Example Templates

Basic example:
```
A {animal} with {texture} skin and {appendage} appendages
```

CSV example with consistent attributes:
```
The {csv:monster:color} {animal}-like monster has {csv:monster:size} {appendage} with a {csv:monster:texture} texture
```

Directory structure example:
```
A {pokemon/types} Pokemon that knows {csv:pokemon/moves:name} which has {csv:pokemon/moves:power} power
```

## Tips

1. CSV files must have a header row
2. Column names in CSV files are case-insensitive
3. Spaces and special characters in column names are stripped
4. Missing wildcards will remain unchanged in the output (useful for debugging)
5. When using directories, use forward slashes (`/`) for path separation
6. Directory references require explicit path (e.g., `{pokemon/types}` not just `{pokemon}`)

## File Organization

Put your wildcard files in the `data` directory:
- Text files (`.txt`) for simple wildcards
- CSV files (`.csv`) for related term groups
- Organize files in subdirectories for better structure
- Use forward slashes (`/`) for directory paths in templates

## Error Handling

- Missing files: The system will silently skip missing wildcard files
- Malformed CSV references: Invalid CSV placeholders will be left unchanged
- Empty files: Empty files will be treated as having no valid options
- Directory references: Must include explicit file path with forward slash