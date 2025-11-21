# attacks/advanced_generator.py
"""Advanced attack generator with all new attack types"""
import json
import os
from attacks.templates import TEMPLATES
from attacks.perturbations import paraphrase_simple, whitespace_obfuscate
from attacks.encoding_attacks import apply_encoding_attack
from attacks.token_smuggling import apply_token_smuggling
from attacks.context_attacks import apply_context_attack
from attacks.multiturn_attacks import apply_multiturn_attack
from attacks.fewshot_injection import apply_fewshot_attack
from attacks.multilingual_attacks import apply_multilingual_attack
from attacks.semantic_evasion import apply_semantic_evasion

def generate_advanced_attacks(base_templates=None, out_path="data/advanced_attack_cases.json"):
    """Generate attacks using all advanced techniques"""
    if base_templates is None:
        base_templates = TEMPLATES
    
    items = []
    
    for template in base_templates:
        base_prompt = template["prompt_template"]
        base_id = template["id"]
        base_tags = template.get("tags", [])
        base_severity = template.get("severity", "medium")
        
        # 1. Base template
        items.append({
            "attack_id": base_id,
            "prompt": base_prompt,
            "tags": base_tags,
            "metadata": {"severity": base_severity, "source": "template"}
        })
        
        # 2. Encoding attacks
        for encoding_type in ["base64", "rot13", "unicode_obfuscate", "hex"]:
            items.append({
                "attack_id": f"{base_id}-enc-{encoding_type}",
                "prompt": apply_encoding_attack(base_prompt, encoding_type),
                "tags": base_tags + ["encoding", encoding_type],
                "metadata": {"severity": base_severity, "source": "encoding", "type": encoding_type}
            })
        
        # 3. Token smuggling
        for smuggling_type in ["special_tokens", "whitespace", "boundary"]:
            items.append({
                "attack_id": f"{base_id}-smug-{smuggling_type}",
                "prompt": apply_token_smuggling(base_prompt, smuggling_type),
                "tags": base_tags + ["token_smuggling", smuggling_type],
                "metadata": {"severity": base_severity, "source": "token_smuggling", "type": smuggling_type}
            })
        
        # 4. Context attacks
        for context_type in ["long_context", "distraction", "buried"]:
            items.append({
                "attack_id": f"{base_id}-ctx-{context_type}",
                "prompt": apply_context_attack(base_prompt, context_type),
                "tags": base_tags + ["context_attack", context_type],
                "metadata": {"severity": base_severity, "source": "context", "type": context_type}
            })
        
        # 5. Multi-turn attacks
        for turn_strategy in ["gradual", "role", "poisoning"]:
            items.append({
                "attack_id": f"{base_id}-mt-{turn_strategy}",
                "prompt": apply_multiturn_attack(base_prompt, turn_strategy),
                "tags": base_tags + ["multiturn", turn_strategy],
                "metadata": {"severity": base_severity, "source": "multiturn", "type": turn_strategy}
            })
        
        # 6. Few-shot injection
        for fewshot_type in ["fewshot", "instruction", "demonstration"]:
            items.append({
                "attack_id": f"{base_id}-fs-{fewshot_type}",
                "prompt": apply_fewshot_attack(base_prompt, fewshot_type),
                "tags": base_tags + ["fewshot", fewshot_type],
                "metadata": {"severity": base_severity, "source": "fewshot", "type": fewshot_type}
            })
        
        # 7. Multilingual attacks
        for lang in ["es", "fr", "de", "zh"]:
            items.append({
                "attack_id": f"{base_id}-ml-{lang}",
                "prompt": apply_multilingual_attack(base_prompt, "translate", lang),
                "tags": base_tags + ["multilingual", lang],
                "metadata": {"severity": base_severity, "source": "multilingual", "lang": lang}
            })
        
        # 8. Semantic evasion
        for evasion_type in ["paraphrase", "academic", "euphemism", "question"]:
            items.append({
                "attack_id": f"{base_id}-sem-{evasion_type}",
                "prompt": apply_semantic_evasion(base_prompt, evasion_type),
                "tags": base_tags + ["semantic_evasion", evasion_type],
                "metadata": {"severity": base_severity, "source": "semantic_evasion", "type": evasion_type}
            })
        
        # 9. Simple variants (original)
        items.append({
            "attack_id": f"{base_id}-paraphrase",
            "prompt": paraphrase_simple(base_prompt),
            "tags": base_tags + ["paraphrase"],
            "metadata": {"severity": base_severity, "source": "paraphrase"}
        })
        
        items.append({
            "attack_id": f"{base_id}-obf",
            "prompt": whitespace_obfuscate(base_prompt),
            "tags": base_tags + ["obfuscation"],
            "metadata": {"severity": base_severity, "source": "obfuscation"}
        })
    
    # Dedupe by attack_id
    unique = {}
    for item in items:
        unique[item["attack_id"]] = item
    
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(list(unique.values()), f, indent=2)
    
    print(f"Wrote {len(unique)} advanced attack cases to {out_path}")
    return list(unique.values())

if __name__ == "__main__":
    generate_advanced_attacks()




