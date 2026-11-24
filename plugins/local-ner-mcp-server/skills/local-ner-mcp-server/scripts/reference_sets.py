"""Validate, store, review, and search local NER reference sets."""

import argparse
import csv
import json
import os
import re
import tempfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

DEFAULT_DATA_DIR = Path.home() / ".codex" / "local-ner-mcp-server" / "reference_sets"
REFERENCE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")


def reference_path(directory, reference_id):
    if not isinstance(reference_id, str) or not REFERENCE_ID.fullmatch(reference_id):
        raise ValueError("參照表 ID 須為 1–80 個小寫英數或連字號，並以英數起首")
    return directory / f"{reference_id}.json"


def string_field(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 須為非空字串")
    return value


def records(document, field):
    entries = document.get(field)
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise ValueError(f"{field} 須為物件陣列")
    return entries


def load_json(path):
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if (
        not isinstance(document, dict)
        or type(document.get("schema_version")) is not int
        or document["schema_version"] != 1
    ):
        raise ValueError(f"{path.name} 的 schema_version 須為 1")
    reference_path(path.parent, document.get("id"))
    string_field(document, "name")

    entity_ids = set()
    for entity in records(document, "entities"):
        entity_id = string_field(entity, "id")
        if entity_id in entity_ids:
            raise ValueError(f"重複的實體 ID：{entity_id}")
        entity_ids.add(entity_id)
        string_field(entity, "name")
        entity_type = string_field(entity, "type")
        aliases = entity.get("aliases")
        if not isinstance(aliases, list) or any(
            not isinstance(alias, str) or not alias.strip() for alias in aliases
        ):
            raise ValueError(f"實體 {entity_id} 的 aliases 須為非空字串的陣列")
        if "location" in entity:
            location = entity["location"]
            if entity_type != "place" or not isinstance(location, dict):
                raise ValueError(f"實體 {entity_id} 的 location 須為地名座標物件")
            for key, bound in (("longitude", 180), ("latitude", 90)):
                value = location.get(key)
                if type(value) not in (int, float) or not -bound <= value <= bound:
                    raise ValueError(f"實體 {entity_id} 的 {key} 超出經緯度範圍")

    for relation in records(document, "relations"):
        string_field(relation, "type")
        for key in ("subject_id", "object_id"):
            entity_id = string_field(relation, key)
            if entity_id not in entity_ids:
                raise ValueError(f"關係的 {key} 指向未知實體：{entity_id}")

    rules = document.get("rules")
    if not isinstance(rules, dict) or rules.keys() - {"match_aliases"}:
        raise ValueError("rules 須為物件，目前支援 match_aliases")
    if "match_aliases" in rules and type(rules["match_aliases"]) is not bool:
        raise ValueError("match_aliases 須為布林值")
    return document


def save_reference(directory, source, replace=False):
    document = load_json(source)
    destination = reference_path(directory, document["id"])
    data = json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=directory, delete=False
    ) as pending:
        temporary = Path(pending.name)
        try:
            pending.write(data)
            pending.close()
            if replace:
                if not destination.is_file():
                    raise FileNotFoundError(f"找不到可更新的參照表：{document['id']}")
                os.replace(temporary, destination)
            else:
                os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
    return destination


@lru_cache(maxsize=8)
def indexed_document(path, signature):
    document = load_json(path)
    if document["id"] != path.stem:
        raise ValueError(f"參照表 ID 與檔名不一致：{path.name}")
    by_initial = defaultdict(lambda: defaultdict(dict))
    match_aliases = document["rules"].get("match_aliases", True)
    for entity in document["entities"]:
        names = [entity["name"]]
        if match_aliases:
            names.extend(entity["aliases"])
        for name in dict.fromkeys(names):
            by_initial[name[0]][len(name)].setdefault(name, []).append(entity)
    return document, by_initial


def read_reference(path):
    stat = path.stat()
    return indexed_document(path, (stat.st_ino, stat.st_mtime_ns, stat.st_size))


def list_reference_sets(directory):
    sets, errors = [], []
    for path in sorted(directory.glob("*.json")):
        try:
            document, _ = read_reference(path)
        except (ValueError, OSError) as error:
            errors.append({"file": path.name, "error": str(error)})
            continue
        sets.append({"id": document["id"], "name": document["name"]})
    return {"reference_sets": sorted(sets, key=lambda item: (item["name"], item["id"])),
            "errors": errors}


def match_mentions(directory, reference_id, text):
    path = reference_path(directory, reference_id)
    document, index = read_reference(path)
    matches = []
    matched_ids = set()
    for start, first in enumerate(text):
        for length, names in index.get(first, {}).items():
            end = start + length
            name = text[start:end]
            candidates = names.get(name) if end <= len(text) else None
            if candidates:
                matches.append({
                    "start": start, "end": end, "text": name,
                    "candidates": candidates,
                })
                matched_ids.update(entity["id"] for entity in candidates)
    matches.sort(key=lambda match: (match["start"], -match["end"]))
    names = {entity["id"]: entity["name"] for entity in document["entities"]}
    relations = [
        dict(relation, subject_name=names[relation["subject_id"]],
             object_name=names[relation["object_id"]])
        for relation in document["relations"]
        if relation["subject_id"] in matched_ids or relation["object_id"] in matched_ids
    ]
    return {"reference_set_id": reference_id, "name": document["name"],
            "matches": matches, "relations": relations}


def review_tables(document):
    names = {entity["id"]: entity["name"] for entity in document["entities"]}
    entities, places = [], []
    for entity in document["entities"]:
        aliases = "、".join(entity["aliases"])
        if entity["type"] == "place":
            location = entity.get("location", {})
            places.append((entity["id"], entity["name"], aliases,
                           location.get("longitude", ""), location.get("latitude", "")))
        else:
            entities.append((entity["id"], entity["name"], entity["type"], aliases))
    relations = [
        (relation["subject_id"], names[relation["subject_id"]], relation["type"],
         relation["object_id"], names[relation["object_id"]])
        for relation in document["relations"]
    ]
    rules = [(key, json.dumps(value, ensure_ascii=False)) for key, value in document["rules"].items()]
    return (
        ("entities", "實體表", ("實體 ID", "名稱", "類型", "別名"), entities),
        ("places", "地名表", ("實體 ID", "地名", "別名", "經度", "緯度"), places),
        ("relations", "關係表", ("起點 ID", "起點實體", "關係", "終點 ID", "終點實體"), relations),
        ("rules", "規則表", ("規則", "設定值"), rules),
    )


def markdown_row(values):
    cells = (str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")
             for value in values)
    return "| " + " | ".join(cells) + " |"


def preview(document, limit):
    for _, title, headings, rows in review_tables(document):
        print(f"## {title}（{len(rows)} 筆）\n")
        print(markdown_row(headings))
        print(markdown_row(["---"] * len(headings)))
        for row in rows[:limit]:
            print(markdown_row(row))
        print()
        if len(rows) > limit:
            print(f"顯示前 {limit} 筆。\n")


def export_csv(document, destination):
    tables = review_tables(document)
    destination.mkdir(parents=True, exist_ok=True)
    for filename, _, _, _ in tables:
        path = destination / f"{filename}.csv"
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"匯出檔已存在：{path}")
    for filename, _, headings, rows in tables:
        path = destination / f"{filename}.csv"
        with path.open("x", encoding="utf-8-sig", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(headings)
            writer.writerows(rows)
        print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    commands = parser.add_subparsers(dest="command", required=True)
    save = commands.add_parser("save")
    save.add_argument("json", type=Path)
    save.add_argument("--replace", action="store_true")
    review = commands.add_parser("preview")
    review.add_argument("json", type=Path)
    review.add_argument("--limit", type=int, default=15)
    export = commands.add_parser("export")
    export.add_argument("json", type=Path)
    export.add_argument("directory", type=Path)
    commands.add_parser("list")
    match = commands.add_parser("match")
    match.add_argument("id")
    match.add_argument("text_file", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "save":
            print(save_reference(args.data_dir, args.json, args.replace))
        elif args.command == "preview":
            if args.limit < 0:
                raise ValueError("--limit 須為非負整數")
            preview(load_json(args.json), args.limit)
        elif args.command == "export":
            export_csv(load_json(args.json), args.directory)
        elif args.command == "list":
            print(json.dumps(list_reference_sets(args.data_dir), ensure_ascii=False))
        elif args.command == "match":
            original = args.text_file.read_bytes().decode("utf-8-sig")
            print(json.dumps(match_mentions(args.data_dir, args.id, original), ensure_ascii=False))
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
