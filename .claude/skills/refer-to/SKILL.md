---
name: refer-to
description: Load a bibliography paper text file by name/author and answer questions about it.
allowed-tools: Read, Glob, Grep, Bash
---

The user wants to consult a paper from the bibliography. Their request: "$ARGUMENTS"

## Steps

1. **List available files**: Run `ls "research/bibliography/"` to see what `.txt` files are available.

2. **Match to the paper**: From "$ARGUMENTS", identify which file best matches the paper the user wants to reference. Files are named by citation (e.g., `Dreher et al. (2019) (African Leaders).txt`). Match on author name, year, or keyword. If genuinely ambiguous, list the options and ask.

3. **Read efficiently** — these files can be large. Do NOT attempt a full read first. Instead:
   - **Grep first**: Use Grep with keywords relevant to the question to find line numbers and context. Include synonyms and related terms to maximize recall.
   - **Read targeted sections**: Use `offset` + `limit` on the Read tool to pull only the relevant portions.
   - **Iterate if needed**: Run additional Greps if the first doesn't surface enough.

## Answer Format

- **Be direct**: Lead with a clear answer, then support it.
- **Quote verbatim**: Include short exact quotes with line numbers, e.g. *"...exact phrase..." (line 204)*.
- **Cite page numbers** when visible in the text (look for page headers/footers or PDF markers). Use line numbers as fallback.
- Distinguish what the paper **claims** from what it **demonstrates**.
