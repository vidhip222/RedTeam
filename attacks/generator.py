# attacks/generator.py
import json
import os
from attacks.templates import TEMPLATES
from attacks.perturbations import paraphrase_simple, whitespace_obfuscate, char_inject

OUT = os.path.join("data", "sample_attack_cases.json")

def generate_variants(base_templates, out_path=OUT):
    items = []
    for t in base_templates:
        items.append({
            "attack_id": t["id"],
            "prompt": t["prompt_template"],
            "tags": t["tags"],
            "metadata": {"severity": t["severity"], "source": "template"}
        })
        # add paraphrase variant
        items.append({
            "attack_id": t["id"] + "-paraphrase",
            "prompt": paraphrase_simple(t["prompt_template"]),
            "tags": t["tags"] + ["paraphrase"],
            "metadata": {"severity": t["severity"], "source": "paraphrase"}
        })
        items.append({
            "attack_id": t["id"] + "-obf",
            "prompt": whitespace_obfuscate(t["prompt_template"]),
            "tags": t["tags"] + ["obfuscation"],
            "metadata": {"severity": t["severity"], "source": "obfuscation"}
        })
    # dedupe by attack_id
    unique = {}
    for it in items:
        unique[it["attack_id"]] = it
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(list(unique.values()), f, indent=2)
    print(f"Wrote {len(unique)} attack cases to {out_path}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_variants(TEMPLATES)
