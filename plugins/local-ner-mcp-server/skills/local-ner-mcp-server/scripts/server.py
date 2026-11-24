"""Serve local NER reference sets through MCP over stdio."""

import argparse
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from reference_sets import DEFAULT_DATA_DIR
from reference_sets import list_reference_sets as list_sets
from reference_sets import match_mentions as match_text


def build_server(data_dir):
    server = FastMCP("Local NER MCP Server")
    read_only = ToolAnnotations(readOnlyHint=True)

    @server.tool(annotations=read_only)
    def list_reference_sets() -> dict[str, Any]:
        """列出本機命名實體參照表的 ID 和顯示名稱。"""
        return list_sets(data_dir)

    @server.tool(annotations=read_only)
    def match_mentions(reference_set_id: str, text: str) -> dict[str, Any]:
        """依指定參照表比對原文，回傳命中範圍、候選實體、地名座標和相關關係。"""
        return match_text(data_dir, reference_set_id, text)

    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    args = parser.parse_args()
    build_server(args.data_dir).run(transport="stdio")
