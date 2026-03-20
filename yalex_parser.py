import re


def remove_comments(text: str) -> str:
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


def split_rule_line(line: str):
    brace_start = line.find("{")
    brace_end = line.rfind("}")

    if brace_start == -1 or brace_end == -1 or brace_end < brace_start:
        return line.strip(), "{}"

    regex_part = line[:brace_start].strip()
    action_part = line[brace_start:brace_end + 1].strip()
    return regex_part, action_part


def parse_yalex(text: str) -> dict:
    text = remove_comments(text)
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]

    lets = {}
    rules = []
    rule_name = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("let "):
            left, right = line.split("=", 1)
            name = left[len("let "):].strip()
            regex = right.strip()
            lets[name] = regex
            i += 1
            continue

        if line.startswith("rule "):
            left, right = line.split("=", 1)
            rule_name = left[len("rule "):].strip()

            first_rule = right.strip()
            if first_rule:
                regex_part, action_part = split_rule_line(first_rule)
                rules.append({
                    "regex": regex_part,
                    "action": action_part
                })

            i += 1

            # Leer líneas siguientes del bloque rule
            while i < len(lines):
                current_raw = lines[i]
                current = current_raw.strip()

                if not current:
                    i += 1
                    continue

                if current.startswith("let ") or current.startswith("rule "):
                    break

                if current.startswith("|"):
                    current = current[1:].strip()

                regex_part, action_part = split_rule_line(current)
                rules.append({
                    "regex": regex_part,
                    "action": action_part
                })
                i += 1

            continue

        i += 1

    return {
        "lets": lets,
        "rule_name": rule_name,
        "rules": rules
    }


def parse_yalex_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return parse_yalex(f.read())