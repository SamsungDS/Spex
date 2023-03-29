#!/usr/bin/env python3
"""
quick'n'dirty stab at converting json-spec to yace

This is simplified by the following assumptions:

* The given json-inputfile is a stage2 representation of an NVMe Command-set Spec.
  ==> Input-file contains commands, statuscodes, identify-structures, logpages, etc.

It constructs a dictionary containing "only"/"just":

* Commands
* Status Codes
* Opcodes?

"""
from pathlib import Path
from pprint import pprint
import json
import yaml
import re

REGEX_COMMAND = r"figure\s+\d+:\s+(?P<brief>[a-z0-9\s]+)(?P<dwords>.*)"
REGEX_DWORD = r"(?:dword\s(\d+))"

REGEX_STATUS_CODE = r"figure\s+\d+:\s+status\scode\s.\s(?P<descr>.*)"


def load():
    """Load command-set from file"""

    path = Path(__file__).parent.parent / "builddir" / "nvm.json"
    with path.open() as jspec:
        content = json.load(jspec)

    return content


def find_command_entities(entities):
    """
    Produces a dict, where key is the "brief" of the command, the command
    itself is a combination of multipe table-figures into a single
    command-entity

    * Brief description of the command
    * The dwords described
    * The entitites describing them
    """

    found = {}
    for entity in entities:
        if "title" not in entity:
            continue

        title = entity["title"].lower()
        if "command" not in title:
            continue
        if "dword" not in title:
            continue

        match = re.match(REGEX_COMMAND, title)
        if not match:
            continue

        brief = match.group("brief").strip()
        dwords = [
            int(m) for m in re.findall(REGEX_DWORD, match.group("dwords").strip())
        ]

        if brief not in found:
            found[brief] = {
                "doc": brief,
                "dwords": [],
                "entities": [],
            }

        found[brief]["dwords"] += dwords
        found[brief]["dwords"] = list(set(found[brief]["dwords"]))
        found[brief]["entities"].append((dwords, entity))

    return found


def invalid_u32(inv):
    return {
        "cls": "field",
        "sym": f"invalid{inv}",
        "doc": f"Bitfield with invalid repr.",
        "typ": "u32",
        "fmt": f'0x%"PRIx32"',
    }


def grab_commands(entities):
    """Return commands from the given 'entities'"""

    found = find_command_entities(entities)

    commands = {}
    for brief, attrs in found.items():
        processed = []

        struct_sym = "nvme_nvm_" + brief.lower().replace(" ", "_")
        command = {
            "cls": "struct",
            "sym": struct_sym,
            "doc": brief,
            "ant": {"opc": 0xFF},
            "members": [],
        }

        nbitfields = 0

        # Describing cdw0 + cdw1 the same way, always, with opcode etc.
        command["members"].append({
            "cls": "field",
            "sym": "opc",
            "typ": "u8",
            "fmt": '0x%"PRIx8"',
            "doc": "command OPCode",
        })
        command["members"].append({
            "cls": "field",
            "sym": "cdw0_misc",
            "typ": "u8",
            "fmt": '0x%"PRIx8"',
            "doc": f"CDW0 fuse, psdt, etc.",
        })
        command["members"].append({
            "cls": "field",
            "sym": "cid",
            "typ": "u16",
            "fmt": '0x%"PRIx16"',
            "doc": "Command IDentifier",
        })
        command["members"].append({
            "cls": "field",
            "sym": "nsid",
            "typ": "u32",
            "fmt": '0x%"PRIx32"',
            "doc": "NameSpace IDentifier",
        })

        for cdw in range(2, 15 + 1):
            if cdw in processed:
                continue

            if cdw not in attrs["dwords"]:  # Emit a default command-dword field
                member = {
                    "cls": "field",
                    "sym": "cdw%0d" % cdw,
                    "typ": "u32",
                    "fmt": '0x%"PRIx32"',
                    "doc": f"Command Dword {cdw}",
                }
                command["members"].append(member)

                processed.append(cdw)
                continue

            for dwords, entity in attrs["entities"]:
                if cdw not in dwords:
                    continue

                processed += dwords

                fields = entity["fields"]

                if len(fields) == 1:  # Entity with a single field
                    field = fields[0]

                    width = field["range"]["high"] - field["range"]["low"] + 1
                    if width not in [32, 64]:
                        print(f"Bad width: {width}")
                        return {}

                    member = {
                        "cls": "field",
                        "sym": field["label"],
                        "doc": f"Single field for cdw({cdw}) dwords({dwords})",
                        "typ": f"u{width}",
                        "fmt": f'0x%"PRIx{width}"',
                        "typ": f"u{width}",
                    }
                    command["members"].append(member)
                    break

                nbitfields += 1
                bitfield = {
                    "cls": "bitfield",
                    "sym": f"bits{nbitfields}",
                    "doc": f"Bitfield for cdw({cdw}) dwords({dwords})",
                    "width": 0,
                    "members": [],
                }

                reserved = 0
                invalid = 0
                for field in fields:  # Emit bitfield
                    sym = field["label"]
                    if sym == "RESERVED":
                        reserved += 1
                        sym = f"rsvd{reserved}"

                    if re.findall("[^a-z0-9_]+", sym):
                        invalid += 1
                        sym = f"invalid{invalid}"

                    width = field["range"]["high"] - field["range"]["low"] + 1
                    bits = {
                        "cls": "bits",
                        "sym": sym,
                        "width": width,
                        "doc": f"Bits for cdw({cdw}) dwords({dwords})",
                    }
                    bitfield["members"].append(bits)
                    bitfield["width"] += width

                if bitfield["width"] in [8, 16, 24, 32, 64]:
                    command["members"].append(bitfield)
                else:
                    invalid += 1
                    command["members"].append(invalid_u32(invalid))

                break

        commands[brief] = command

    return list(commands.values())


def grab_opcodes(entities):
    """Return opcodes found in the given 'entities'"""

    return {}


def grab_sc(entities):
    """Return status-codes found in the given 'entities'"""

    found = {}
    for entity in entities:
        if "title" not in entity:
            continue

        match = re.match(REGEX_STATUS_CODE, entity["title"].lower())
        if not match:
            continue

        descr = match.group("descr")
        if descr not in found:
            found[descr] = []
        found[descr] += entity["fields"]

    enums = []
    for descr, fields in found.items():
        words = descr.lower().split()
        enum = {
            "cls": "enum",
            "sym": "sc_" + ("specific" if "specific" in words else words[0]),
            "doc": descr,
            "members": [],
        }
        for field in fields:
            if " " in field["val"]:
                continue

            sym = field["label"].lower()
            if re.match("[^a-z90-9_]+", sym):
                print(f"Invalid sym({sym})")

            enum["members"].append(
                {
                    "cls": "enum_value",
                    "sym": sym,
                    "val": {
                        "cls": "hex",
                        "lit": int(field["val"].replace("h", ""), 16),
                    },
                    "doc": field["brief"] if "brief" in field else "",
                }
            )
        enums.append(enum)

    return enums


def stage2_to_yace():
    stage2 = load()["entities"]

    data = {}
    data["meta"] = {
        "project": "NVMe",
        "version": "0.0.1",
        "brief": "Its a kind of magic, magic, magic!",
        "full": "...",
        "prefix": "nvme",
        "author": "Simon A. F. Lund <os@safl.dk>",
        "lic": "BSD-3-Clause",
    }

    data["opcodes"] = grab_opcodes(stage2)
    data["status_codes"] = grab_sc(stage2)
    data["commands"] = grab_commands(stage2)

    with (Path(__file__).parent.parent / "builddir" / "foo.yaml").open("w") as yfd:
        yaml.safe_dump(data, yfd, sort_keys=False)


def main():
    stage2_to_yace()


if __name__ == "__main__":
    main()
