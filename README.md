# Local NER MCP Server

Local NER MCP Server is a Codex plugin for creating and reusing named-entity reference sets. Use the bundled Skill to turn source files into a named JSON reference set. Use the MCP server to find terms from a saved set when annotating text in any local project where the plugin is available.

## Installation

### 1. In a Codex project chat

Open a chat in any local Codex project, paste this line, and send it.

```text
Please install the Local NER MCP Server plugin by running `codex plugin marketplace add cclintw/ner-mcp-server && codex plugin add local-ner-mcp-server@local-ner`.
```

### 2. In a terminal

If you use Codex CLI, run this command from any folder.

```sh
codex plugin marketplace add cclintw/ner-mcp-server && codex plugin add local-ner-mcp-server@local-ner
```

### 3. With a local copy of the plugin source

The source repository is [cclintw/ner-mcp-server](https://github.com/cclintw/ner-mcp-server). If you already have a local copy, open its `ner-mcp-server` folder in a terminal. The correct folder contains `.agents/plugins/marketplace.json`.

```sh
codex plugin marketplace add . && codex plugin add local-ner-mcp-server@local-ner
```

The dot refers to this local copy. In the desktop app, you can also open that folder as a project and select **Local NER MCP Server** under **Plugins → Browse directory → Local NER**.

The installation commands require access to `codex`. The plugin requires Python 3.10 or later available as `python3`. On first launch, it automatically downloads and installs its Python dependencies. This step requires an internet connection.

## Create an annotation reference set

1. Open a new local Codex chat and attach readable files that contain identifiable entities. Sources can include CSV, TSV, JSON, GeoJSON, SQLite, text documents, and JPG or PNG images such as character lists and family trees.
2. Type `$` and select **Local NER MCP Server**, or use `$local-ner-mcp-server:local-ner-mcp-server`. Give the reference set a name, such as “Taiwan Place Names.”
3. Open the resulting JSON file. The Skill extracts and validates the entities and relationships it can identify and reports any parts of the sources it could not interpret reliably.

Each reference set is saved as a JSON file in `~/.codex/local-ner-mcp-server/reference_sets/` by default. The same MCP server can read newly saved sets. See the [reference format](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/references/reference-format.md) for field definitions.

## Use a reference set in another project

Open the local Codex project where you want to annotate text and attach the original text in the chat. If **Local NER MCP Server** appears in the **+** menu next to the message box, select it there. You can also name the plugin directly in your message. Local projects share the saved reference sets without copying JSON files.

### Use a reference set by name

> Use the “紅樓夢” reference set from Local NER MCP Server to annotate character names in the attached text.

### List the reference sets before choosing

> List the annotation reference sets available from Local NER MCP Server and wait for me to choose one before annotating the text.

Once Codex shows the list, reply with the name of the set you want to use.

> Use the “Taiwan Place Names” reference set to annotate place names in the attached text.

## Project layout

- [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json) declares the local marketplace entry.
- [plugin.json](plugins/local-ner-mcp-server/plugin.json) and [mcp.json](plugins/local-ner-mcp-server/mcp.json) define the plugin and its STDIO launcher.
- [SKILL.md](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/SKILL.md) defines the file-to-JSON workflow.
- [launch.py](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/scripts/launch.py) prepares the runtime and starts the server.

Keep generated or user-provided reference sets in the local reference set directory. The repository excludes `reference_sets/` and known local dataset filenames.
