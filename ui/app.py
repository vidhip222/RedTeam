# ui/app.py (robust: handles missing experimental_rerun)
import streamlit as st
import json
import os

st.set_page_config(page_title="RedTeam Proto", layout="wide")
st.title("NLP Red-Teaming Prototype — Results Viewer")

results_path = "data/results.jsonl"
scores_path = "data/score_report.json"

st.sidebar.header("Controls")

# safe lookup for experimental rerun (some Streamlit builds remove it)
_rerun_available = hasattr(st, "experimental_rerun")

if st.sidebar.button("Refresh"):
    if _rerun_available:
        st.experimental_rerun()
    else:
        st.sidebar.info("Auto-rerun not available in this Streamlit version. Please refresh the browser (F5).")

st.sidebar.markdown("Files read from `data/` directory.")

def load_results(path):
    if not os.path.exists(path):
        return []
    items = []
    with open(path, "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception as e:
                items.append({
                    "attack_id": f"bad-line-{i}",
                    "prompt": "",
                    "response": f"<could not parse line {i}: {e}>",
                    "model_meta": {},
                    "timestamp": ""
                })
    return items

def load_scores(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf8") as f:
            data = json.load(f)
            # Handle both direct array and nested structure
            if isinstance(data, dict) and "scores" in data:
                return data["scores"]
            return data if isinstance(data, list) else []
    except Exception:
        return []

results = load_results(results_path)
scores = load_scores(scores_path)
score_map = {s.get("attack_id"): s for s in scores}

st.header(f"Results ({len(results)})")

# Overview table: attack_id + short prompt + vulnerability if scored
if results:
    rows = []
    for r in results:
        aid = r.get("attack_id", "")
        prompt_snip = (r.get("prompt") or "")[:80].replace("\n", " ")
        score = score_map.get(aid)
        vuln = score.get("vulnerable") if score else None
        rows.append({"attack_id": aid, "prompt": prompt_snip, "vuln": vuln})
    st.table(rows)

st.markdown("---")

for idx, r in enumerate(results):
    aid = r.get("attack_id", f"attack-{idx}")
    prompt = r.get("prompt", "")
    response = r.get("response", "")
    model_meta = r.get("model_meta", {})
    ts = r.get("timestamp", "")
    with st.expander(f"{aid} — { (prompt[:60] + '...') if len(prompt)>60 else prompt }"):
        st.subheader("Prompt")
        st.code(prompt, language="text")
        st.subheader("Model response")
        key_for_textarea = f"response_{aid}_{idx}"
        # readonly text area (unique key avoids duplicate element ID)
        st.text_area("Model response (read-only)", value=response, height=180, key=key_for_textarea)
        st.write("Metadata / timestamp:")
        st.json({"model_meta": model_meta, "timestamp": ts})
        s = score_map.get(aid)
        if s:
            st.subheader("Score")
            # show a colored indicator for vuln_bool
            if s.get("vuln_bool"):
                st.error(f"VULNERABLE — severity {s.get('severity_score')}")
            else:
                st.success(f"Not vulnerable — severity {s.get('severity_score')}")
            st.json(s)
        else:
            st.info("Not scored yet. Run the scorer to populate `data/score_report.json`.")

st.markdown("---")
st.write("Tip: Run pipeline: attacks/generator.py → runner/cli.py --model=mock → eval/scorer.py")
