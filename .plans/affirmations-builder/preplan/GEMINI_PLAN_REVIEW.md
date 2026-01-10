# Gemini Plan Review

- model: `gemini-3-pro-preview`
- generated_at: `2026-01-10T20:36:03+00:00`

---

Here is a review of the proposed plan options for the `affirmations-builder` update.

# Summary
The current codebase relies on specific local binaries (`bin/piper`) and model files, making the rendering pipeline sensitive to environment configuration. The lack of an existing top-level `tests/` directory (based on the file listing) suggests the project is in early stages or lacks a formalized verification strategy. Introducing changes to the core renderer without automated verification (Option A) is high-risk for audio processing pipelines, where failures can be silent (e.g., empty files) or require time-consuming manual listening to detect.

# Option A Review
**Minimal renderer fix**
- **Strengths:** Lowest effort; immediately addresses the "broken" state of the renderer.
- **Gaps:** Completely ignores the lack of test infrastructure.
- **Risks:** "Works on my machine" syndrome is highly likely given the external binary dependencies (`piper`, `espeak-ng`). Future refactors will likely break the renderer again without a safety net.
- **Recommendation:** **Reject.** Too fragile for a core logic fix.

# Option B Review
**Renderer fix + smoke tests**
- **Strengths:** Introduces a much-needed testing harness (`tests/`). A "smoke test" that generates a small asset is crucial for CI/CD and ensuring dependencies (like `libsndfile` or `piper`) are correctly linked.
- **Gaps:** Needs to ensure the test environment can actually execute the `piper` binary (permissions, paths).
- **Risks:** Test setup might reveal environmental issues (missing shared libraries), slightly increasing initial scope, but this is "good" friction.
- **Recommendation:** **Approve.** This strikes the right balance between fixing the immediate issue and establishing a baseline for quality.

# Option C Review
**Fix + validation polish**
- **Strengths:** Prevents runtime errors by validating config early.
- **Gaps:** Combines logic fixes with UX improvements, potentially muddying the PR diff.
- **Risks:** Scope creep. Validation logic can get complex quickly (e.g., checking if paths exist, if binaries are executable).
- **Recommendation:** **Defer.** Implement Option B first to secure the renderer. Validation polish should be a follow-up task once the core pipeline is verified stable.

# Recommended verification contract

1.  **Static Analysis:**
    ```bash
    # Ensure no undefined names or syntax errors before running
    # (Assuming ruff or flake8 is available, otherwise relying on runtime)
    grep -r "import" src/affirmbeat/render/renderer.py
    ```

2.  **Automated Smoke Test (New):**
    ```bash
    # Option B verification
    python3 -m unittest discover tests -v
    ```

3.  **End-to-End Integration:**
    ```bash
    # clean previous output to ensure new generation
    rm -rf projects/output/stems/* 
    
    # Run the demo project (ensures binaries and paths are correct)
    python3 src/affirmbeat/cli/main.py render projects/demo_project.json
    
    # Verify output existence (simple check)
    ls -l projects/output/stems/
    ```
