Here is the review of the pending changes.

### 🔴 Must-Fix Bugs & Regressions

1.  **Memory OOM Risk (`src/affirmbeat/providers/music_file.py`)**
    *   `sf.read(file_path)` loads the **entire** audio file into RAM as a float32 numpy array. If a user provides a long set (e.g., 1 hour WAV), this will consume massive memory (approx. 1GB per hour at 48kHz stereo float32) and potentially crash the application.
    *   **Fix:** Use `sf.SoundFile` to read only the required duration or stream blocks, especially if the file is longer than the requested duration.

2.  **CI/Automation Blocker (`setup.sh`)**
    *   The `read -p "Do you want to install..."` block will hang indefinitely in non-interactive environments (CI pipelines, Docker builds) where `stdin` is closed or not a TTY.
    *   **Fix:** Check if running interactively (`[ -t 0 ]`) or allow an argument/env var (e.g., `INSTALL_AI=true ./setup.sh`) to bypass the prompt.

3.  **State Thrashing in UI (`src/affirmbeat/web_ui.py`)**
    *   `project.music.chunk_sec = project.duration_sec` inside the draw loop forces the config value every rerun. If the user tries to manually adjust the chunk size in the UI (if that control exists elsewhere) or via config, this line silently overwrites it immediately.
    *   **Fix:** Only apply this default if the provider *changed* in this run, or disable the chunk size control conditionally when "file" provider is selected.

### ⚠️ Risky Edge Cases

1.  **Semantic Overload of `prompt`**
    *   In `web_ui.py`, you reuse `project.music.prompt` to store the file path. If a user switches from "stable_audio_open" (where they typed a text prompt) to "file", that text prompt is treated as a file path (and fails). If they switch back, their file path is now their generation prompt.
    *   **Fix:** Add a dedicated `file_path` field to the `MusicConfig` or clear the field when switching providers.

2.  **Hard-Cut Looping**
    *   `FileMusicProvider` uses `np.tile` for looping. If the source file does not have a zero-crossing or perfect loop point at the end, this will introduce audible clicks/pops (discontinuities) at every repeat.
    *   **Fix:** Implement a crossfade at the loop boundary or rely on the upstream mixer to handle looping if it supports crossfading buffers.

### 🧪 Test Ideas

1.  **Large File Test:** Feed a 1GB+ audio file to `FileMusicProvider` and monitor RAM usage.
2.  **Non-Interactive Setup:** Run `setup.sh < /dev/null` to verify it defaults safely (probably to "No") instead of hanging.
3.  **Short Source Audio:** Test with a source file that is significantly shorter than the target duration (e.g., 5s file for 300s target) to verify the `np.tile` logic doesn't produce index errors.
