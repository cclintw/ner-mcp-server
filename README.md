# Local NER MCP Server

Local NER MCP Server is a desktop Codex plugin for building and using named-entity reference sets. Its Skill converts source files into a single named JSON reference set. Its read-only MCP server lists saved sets and finds exact mentions in text.

[Traditional Chinese guide (Markdown)](README_zh-TW.md) · [Traditional Chinese guide (HTML)](README_zh-TW.html)

## Installation

Use Codex CLI and Python 3.10 or later, available as `python3`. The first MCP server launch downloads its Python dependencies into a reusable environment in the user directory.

### From GitHub

With read access to `cclintw/textoria-ner-mcp-server`, run:

```sh
codex plugin marketplace add cclintw/textoria-ner-mcp-server && codex plugin add local-ner-mcp-server@local-ner
```

### From a local checkout

Run from the repository root:

```sh
codex plugin marketplace add . && codex plugin add local-ner-mcp-server@local-ner
```

In the desktop app, you can also open the project and install **Local NER MCP Server** from **Plugins → Browse directory → Local NER**.

## Usage

1. Open a new local Codex chat and attach a source file, such as CSV, TSV, JSON, GeoJSON, or SQLite.
2. Type `$` and select **Local NER MCP Server**, or use `$local-ner-mcp-server:local-ner-mcp-server`. Give the reference set a name, such as “Taiwan Place Names.”
3. Open the resulting JSON file. The Skill maps source fields, validates the extracted entities and relationships, and reports any source records it could not map.

Each reference set is saved as a JSON file in `~/.codex/local-ner-mcp-server/reference_sets/` by default. The same MCP server can read newly saved sets. See the [reference format](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/references/reference-format.md) for field definitions.

## MCP tools

| Tool | Behavior |
| --- | --- |
| `list_reference_sets` | List available reference set IDs and display names. |
| `match_mentions` | Accept a `reference_set_id` and the original `text`. Return exact matching spans, candidate entities, coordinates when available, and related records. |

Matching retains overlapping spans and candidates with identical names. Offsets count Unicode code points, with an inclusive start and exclusive end. Set the reference set's `match_aliases` rule to control alias matching. It defaults to enabled.

In the desktop app, check the server under **Plugins → MCP → From plugins**.

## Project layout and runtime

- [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json) declares the local marketplace entry.
- [plugin.json](plugins/local-ner-mcp-server/plugin.json) and [mcp.json](plugins/local-ner-mcp-server/mcp.json) define the plugin and its STDIO launcher.
- [SKILL.md](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/SKILL.md) defines the file-to-JSON workflow.
- [launch.py](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/scripts/launch.py) prepares the runtime and starts the server.

If the first launch times out while downloading dependencies, prepare the environment from the repository root, then open a new local Codex chat:

```sh
python3 -B plugins/local-ner-mcp-server/skills/local-ner-mcp-server/scripts/launch.py --setup
```

Keep generated or user-provided reference sets in the local reference set directory. The repository excludes `reference_sets/` and known local dataset filenames.
