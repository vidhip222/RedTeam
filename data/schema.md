# JSON schemas

## attack_case
{
  "attack_id": "jb-001",
  "prompt": "string",
  "tags": ["jailbreak","instruction"],
  "metadata": {"severity":"high","source":"template"}
}

## result_item (one per model call)
{
  "attack_id": "jb-001",
  "prompt": "original prompt",
  "response": "model text response",
  "model_meta": {"mock":true},
  "timestamp": "ISO8601"
}

## score_item
{
  "attack_id": "jb-001",
  "vuln_bool": true,
  "vulnerability_reasons": ["contains_secret","instruction_followed"],
  "severity_score": 1.0,
  "notes": "string"
}
