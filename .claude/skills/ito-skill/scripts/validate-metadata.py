import re
import sys
import argparse

def validate_metadata(name, description):
    errors = []

    if not (1 <= len(name) <= 64):
        errors.append(f"NAME ERROR: '{name}' is {len(name)} characters. Must be between 1-64.")

    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(
            f"NAME ERROR: '{name}' contains invalid characters. "
            "Use only lowercase letters, numbers, and single hyphens. "
            "No consecutive hyphens, and cannot start/end with a hyphen."
        )

    if len(description) > 250:
        errors.append(
            f"DESCRIPTION ERROR: Description is {len(description)} characters. "
            "Must be 250 characters or fewer."
        )

    en_first_person = {"i", "me", "my", "we", "our", "you", "your"}
    desc_words = set(re.findall(r'\b\w+\b', description.lower()))
    found_en = en_first_person.intersection(desc_words)

    zh_first_person = ["我", "我的", "我們", "我們的", "你", "你的", "您", "您的"]
    found_zh = [w for w in zh_first_person if w in description]

    found_forbidden = found_en | set(found_zh)
    if found_forbidden:
        errors.append(
            f"STYLE WARNING: Description contains first/second person terms: {found_forbidden}. "
            "Use third-person imperative (e.g., 'Creates...', 'Updates...')."
        )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    else:
        print("SUCCESS: Metadata is valid and optimized for discovery.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()
    validate_metadata(args.name, args.description)
