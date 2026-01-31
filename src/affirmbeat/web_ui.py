import json
import uuid
from pathlib import Path
import streamlit as st
import pandas as pd

from affirmbeat.core.project import Project, Affirmation, VoiceTrack
from affirmbeat.render.renderer import render_project

st.set_page_config(
    page_title="AffirmBeat Studio",
    page_icon="🎧",
    layout="wide",
)

def load_project(path: Path) -> Project:
    if not path.exists():
        st.error(f"Project not found: {path}")
        return None
    try:
        data = json.loads(path.read_text())
        return Project.model_validate(data)
    except Exception as e:
        st.error(f"Failed to load project: {e}")
        return None

def save_project(project: Project, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project.model_dump(), indent=2))
    st.toast(f"Project saved to {path}")

def get_project_files():
    projects_dir = Path("projects")
    projects_dir.mkdir(exist_ok=True)
    return list(projects_dir.glob("*.json"))

# --- Sidebar ---
with st.sidebar:
    st.title("🎧 AffirmBeat")
    
    project_files = get_project_files()
    selected_file = st.selectbox(
        "Select Project", 
        options=project_files, 
        format_func=lambda x: x.name
    )
    
    new_project_name = st.text_input("New Project Name", placeholder="my_new_project")
    if st.button("Create New Project"):
        if new_project_name:
            path = Path(f"projects/{new_project_name}.json")
            if path.exists():
                st.error("File already exists!")
            else:
                p = Project(project_id=str(uuid.uuid4()))
                save_project(p, path)
                st.rerun()

    if selected_file:
        project = load_project(selected_file)
    else:
        project = None

if not project:
    st.info("Please select or create a project to begin.")
    st.stop()

# --- Main Content ---
st.header(f"Project: {selected_file.stem}")

tabs = st.tabs(["📝 Affirmations", "🎤 Voice & Script", "🎹 Music", "🧠 Binaural Beats", "🎚️ Mix & Render"])

# --- Tab 1: Affirmations ---
with tabs[0]:
    st.subheader("Affirmations")
    st.write("List the affirmations you want to be spoken.")
    
    # Simple list editor
    # Converting to dataframe for easier editing in Streamlit
    data = [{"text": a.text, "tags": ", ".join(a.tags)} for a in project.affirmations]
    edited_df = st.data_editor(
        data, 
        num_rows="dynamic", 
        column_config={
            "text": st.column_config.TextColumn("Affirmation Text", width="large", required=True),
            "tags": st.column_config.TextColumn("Tags (comma separated)"),
        },
        use_container_width=True
    )
    
    # Update project from editor
    new_affirmations = []
    for idx, row in enumerate(edited_df):
        text = row.get("text")
        if text:
            tags = [t.strip() for t in row.get("tags", "").split(",") if t.strip()]
            # Preserve ID if possible, else generate new
            aid = project.affirmations[idx].id if idx < len(project.affirmations) else f"a{idx+1}"
            new_affirmations.append(Affirmation(id=aid, text=text, tags=tags))
    
    if new_affirmations != project.affirmations:
        project.affirmations = new_affirmations
        save_project(project, selected_file)


# --- Tab 2: Voice & Script ---
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("TTS Settings")
        provider = st.selectbox(
            "TTS Provider", 
            ["dummy", "espeak", "piper1"], 
            index=["dummy", "espeak", "piper1"].index(project.tts.provider)
        )
        project.tts.provider = provider
        
        if provider == "piper1":
            project.tts.model_path = st.text_input("Model Path", value=project.tts.model_path or "")
        
        project.tts.voice = st.text_input("Default Voice", value=project.tts.voice or "")
        project.tts.rate = st.slider("Speech Rate", 0.5, 2.0, float(project.tts.rate))

    with col2:
        st.subheader("Scripting Mode")
        mode = st.selectbox(
            "Overlap Mode",
            ["single", "triple_stack", "lead_whisper", "call_response"],
            index=["single", "triple_stack", "lead_whisper", "call_response"].index(project.script.mode),
            help="Single: One voice. Triple Stack: Three voices (Center, L, R) with offset. Lead Whisper: Center lead + whispers. Call Response: L then R."
        )
        project.script.mode = mode
        project.script.repeat_each = st.number_input("Repeat Each Line", min_value=1, value=project.script.repeat_each)
        project.script.gap_ms = st.number_input("Gap Between Lines (ms)", min_value=0, value=project.script.gap_ms)
        project.script.shuffle = st.checkbox("Shuffle Lines", value=project.script.shuffle)


# --- Tab 3: Music ---
with tabs[2]:
    st.subheader("Background Music")
    m_provider = st.selectbox(
        "Music Provider",
        ["placeholder", "stable_audio_open", "file"],
        index=["placeholder", "stable_audio_open", "file"].index(project.music.provider) if project.music.provider in ["placeholder", "stable_audio_open", "file"] else 0
    )
    project.music.provider = m_provider
    
    if m_provider == "stable_audio_open":
        st.warning("Requires 'stable-audio-tools' and a GPU is recommended.")
        project.music.prompt = st.text_area("Music Prompt", value=project.music.prompt)
        project.music.model_id = st.text_input("Model ID", value=project.music.model_id or "stabilityai/stable-audio-open-1.0")
        project.music.seed = st.number_input("Seed", value=project.music.seed)
    elif m_provider == "file":
        st.info("Uses a local audio file. Supports WAV, MP3, FLAC, OGG.")
        file_path_input = st.text_input("Path to Audio File", value=project.music.prompt, help="Absolute path to your music file")
        project.music.prompt = file_path_input
        if file_path_input and Path(file_path_input).exists():
            st.success("File found!")
        elif file_path_input:
            st.error("File not found.")
        # Auto-configure chunk size to avoid looping glitches
        if project.music.chunk_sec < project.duration_sec:
             project.music.chunk_sec = project.duration_sec
             st.caption(f"Chunk size auto-adjusted to {project.duration_sec}s to prevent restarting.")
    else:
        st.info("Uses a generated sine-tone placeholder track.")

    project.music.crossfade_ms = st.slider("Loop Crossfade (ms)", 0, 5000, project.music.crossfade_ms)
    
    # Gain control
    # Check if gain_db exists (added in recent update)
    current_gain = getattr(project.music, "gain_db", -16.0)
    music_gain = st.slider("Music Volume (dB)", -40.0, 0.0, float(current_gain))
    project.music.gain_db = music_gain


# --- Tab 4: Binaural Beats ---
with tabs[3]:
    st.subheader("Binaural Beats Generator")
    st.markdown("""
    **What are Binaural Beats?**
    
    When you hear two tones with slightly different frequencies in each ear, your brain processes a beat at the difference of the frequencies.
    This is called a *binaural beat* and is often used to entrain brainwaves to desired states.
    """)
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        enabled = st.checkbox("Enable Binaural Beats", value=project.binaural.enabled)
        project.binaural.enabled = enabled
        
        carrier = st.number_input(
            "Carrier Frequency (Hz)", 
            value=float(project.binaural.carrier_hz),
            help="The base tone pitch. Lower is deeper. 220Hz is standard 'A'."
        )
        project.binaural.carrier_hz = carrier
        
        beat = st.number_input(
            "Beat Frequency (Hz)", 
            value=float(project.binaural.beat_hz),
            step=0.5,
            help="The difference between L/R. This determines the brainwave state."
        )
        project.binaural.beat_hz = beat

    with col_b2:
        st.info(f"Current State: **{beat} Hz**")
        
        if beat >= 30:
            st.write("**Gamma (>30Hz):** Peak focus, cognitive enhancement.")
        elif beat >= 13:
            st.write("**Beta (13-30Hz):** Active thinking, focus, anxiety.")
        elif beat >= 8:
            st.write("**Alpha (8-13Hz):** Relaxed alertness, light meditation.")
        elif beat >= 4:
            st.write("**Theta (4-8Hz):** Deep meditation, creativity, dreaming.")
        else:
            st.write("**Delta (<4Hz):** Deep sleep, healing.")
            
    st.divider()
    gain = st.slider("Volume (dB)", -60.0, 0.0, float(project.binaural.gain_db), help="Should be barely audible behind the voice/music.")
    project.binaural.gain_db = gain


# --- Tab 5: Mix & Render ---
with tabs[4]:
    st.subheader("Final Output")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        duration_min = st.number_input("Total Duration (minutes)", value=project.duration_sec / 60.0, step=1.0)
        project.duration_sec = int(duration_min * 60)
        
    with col_m2:
        master_peak = st.slider("Master Peak (dB)", -10.0, 0.0, float(project.mix.master_peak_db))
        project.mix.master_peak_db = master_peak

    st.write("---")
    
    if st.button("Save & Render Project", type="primary"):
        save_project(project, selected_file)
        with st.spinner("Rendering audio... This may take a moment."):
            try:
                output_dir = render_project(selected_file)
                st.success(f"Render complete! Output saved to: {output_dir}")
                
                final_wav = output_dir / "final.wav"
                if final_wav.exists():
                    st.audio(str(final_wav))
                else:
                    st.warning("Render finished but 'final.wav' was not found.")
                    
            except Exception as e:
                st.error(f"Render failed: {e}")
                st.exception(e)

# Auto-save on widget change is not default in Streamlit, but we save explicitly or via callbacks above.
# To ensure changes persist if user switches tabs without explicit save, we can auto-save at the end.
if st.session_state.get("autosave", True):
    # This is a bit aggressive, maybe just a "Save" button is better, but let's try to keep it synced.
    # Actually, let's trust the "Save & Render" or explicit actions for now to avoid IO thrashing.
    pass

with st.sidebar:
    if st.button("Save Changes"):
        save_project(project, selected_file)
