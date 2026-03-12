import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import io
import tomllib

# --- 1. CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Parafin: Brand Converter", layout="wide")

# Assets Directory (Dynamic Relative Path)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# --- MAIN TITLE WITH LOGO ---
# The [1, 8] ratio makes the logo column small and the title column large.
# vertical_alignment="center" ensures the image and text line up perfectly.
title_col1, title_col2 = st.columns([1, 8], vertical_alignment="center")

with title_col1:
    # Make sure this filename perfectly matches the logo you put in your assets folder
    logo_path = os.path.join(ASSETS_DIR, "city_express_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

with title_col2:
    st.title("Hotel Brand Converter")

if "render_history" not in st.session_state: st.session_state.render_history = []
if "render_img" not in st.session_state: st.session_state.render_img = None
if "last_base_file" not in st.session_state: st.session_state.last_base_file = None

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    
    # --- SILENT API KEY LOAD (HIDDEN FROM UI) ---
    api_key = ""
    # 1. Try to load from Streamlit Cloud Secrets
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    # 2. Fallback to local file for desktop testing
    else:
        secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "rb") as f:
                    secrets_data = tomllib.load(f)
                    if "GOOGLE_API_KEY" in secrets_data:
                        api_key = secrets_data["GOOGLE_API_KEY"]
            except Exception: pass 
    
    # --- BRAND SELECTOR (VISIBLE) ---
    st.subheader("🎯 Brand Template")
    brand_choice = st.selectbox("Select Target Brand", ["City Express by Marriott", "Spark by Hilton"])
    
    # Logic to find files based on brand string
    search_string = "city_express" if "City Express" in brand_choice else "spark"
    
    auto_refs = []
    if os.path.exists(ASSETS_DIR):
        all_files = os.listdir(ASSETS_DIR)
        auto_refs = [os.path.join(ASSETS_DIR, f) for f in all_files if search_string in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
    st.divider()
    
    # --- BRAND CUSTOMIZATION (SILENT VARIABLES) ---
    # The slider is removed, but the variable remains so the engine logic doesn't break
    blue_inset_pct = 30 

    # --- UPLOAD STRUCTURE (VISIBLE) ---
    st.subheader("📁 Upload Structure")
    base_file = st.file_uploader("Original Hotel (Structure)", type=['png', 'jpg', 'jpeg'])

# --- 3. CLIENT INITIALIZATION ---
if not api_key:
    st.warning("Please configure your Google API Key in the Streamlit Cloud Secrets dashboard.")
    st.stop()

client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version='v1alpha'))

# --- 4. DISPLAY COLUMNS ---
col1, col2 = st.columns(2)

if base_file:
    with col1:
        current_display_base = Image.open(base_file)
        # CHANGED: Replaced hardcoded width with use_container_width=True
        st.image(current_display_base, caption="Original Structure", use_container_width=True)

# --- 5. THE PRECISION ENGINE ---
st.divider() 

if st.button("🚀 Generate Precision Render", type="primary") and base_file and auto_refs:
    with st.spinner(f"Applying Marriott Standards (PG 17-25)..."):
        try:
            process_base = Image.open(base_file)
            orig_width, orig_height = process_base.size
            
            # Define chosen_ratio before the API call block
            ratio_val = orig_width / orig_height
            chosen_ratio = "16:9" if ratio_val > 1.5 else "4:3" if ratio_val > 1.2 else "1:1"

            # BRAND STANDARDS: PTW-003-SW COLOR SPEC + SINGLE LINE ENFORCEMENT
            if "City Express" in brand_choice:
                brand_instr = (
                    "MATERIAL AUDIT & SPECIFIC OVERRIDE (CITY EXPRESS): \n"
                    "1. BASE MATERIAL AUDIT: Analyze the ground floor masonry. \n"
                    "   - IF STONE OR BRICK: You MUST maintain the original base color (hue and tone). "
                    "Apply a 'Digital Power Wash': remove all dirt, mold, and weathering, but do not change the "
                    "natural color of the brick/stone. It should look like a freshly restored original wall. \n"
                    "   - IF STUCCO OR EIFS: Replace entirely with 'Warm Greige Plaster' (Finish B). "
                    "The color must be a medium-tone sandy greige with a heavy, professional sand-aggregate texture. \n"
                    f"2. VOLUMETRIC PAINT (PTW-004-SW): Identify structural protrusions or large elements on the facade. Paint the wall faces "
                    f"of these volumes in Deep Navy Blue. IF there are repetitive vertical insets "
                    f"or recessed window bays, asymmetrically apply this Deep Navy Blue to approximately {blue_inset_pct}% of those "
                    f"insets (scattered) to break up the massing and create an architectural rhythm. \n"
                    "3. TRIM PROTECTION: Keep architectural moulding and window cornices Warm Off-White. \n"
                    "4. THE YELLOW DATUM (PTW-003-SW): Render one crisp horizontal yellow line as a 'cap' "
                    "sitting exactly on the top edge of the ground floor masonry/plaster. \n"
                    "5. UPPER WALLS: All primary non-protruding surfaces must be Warm Off-White (Finish A) stucco. \n"
                    "6. BOUNDARY LOCK: No blue paint bleed below the yellow datum line. \n"
                    "7. CONDITIONAL CANOPY LOGIC (ONLY IF EXISTING): Analyze the main entrance in the original photo. \n"
                    "   - IF a projecting drive-under canopy (porte-cochere) already exists: Paint ONLY the uppermost horizontal trim line (highest parapet edge) in Deep Navy Blue. \n"
                    "   - IF NO projecting canopy exists in the original photo: DO NOT build or invent one. Keep the original entrance geometry exactly as it is. \n"
                    "   - CRITICAL: Do NOT paint canopy support columns blue; they must follow the Base Material Audit (masonry/stucco)."
                )
            else:
                brand_instr = "Apply Spark by Hilton brand colors and materials as shown in references."

            # 3. CONTEXTUAL SIGNAGE ANCHOR (ZERO-TOLERANCE 1:1 REPLACEMENT)
            signage_logic = (
                "STRICT SIGNAGE ANCHORING (1:1 ONLY): \n"
                "1. THE 'EXISTING SIGN' MASK: Identify every physical logo and sign in the original photo. \n"
                "2. 1:1 REPLACEMENT ONLY: Replace existing signage with the brand specified ONLY in the existing signage locations. \n"
                "3. NO NEW PLACEMENTS: If a wall is blank in the original photo, it MUST remain 100% blank in the render. Do not invent or add new signs. \n"
                "4. MAJOR PROTRUSIONS: Major protrusions or large elements on the facade must be painted the Deep Navy Blue (PTW-004-SW) color palette, but they MUST REMAIN BLANK with no signage unless a sign was already there in the input image."
            )

            system_instruction = (
                "### GLOBAL ARCHITECTURAL LOCKDOWN (ZERO GEOMETRY ALTERATION) ### \n"
                "1. YOU ARE A PAINTER AND TEXTURE APPLICATOR, NOT AN ARCHITECT. \n"
                "2. ABSOLUTE GEOMETRY LOCK: The structural silhouette, massing, and every architectural edge of the input photo are 100% IMMUTABLE. Do not add new structures (e.g., do not build a porte-cochere or canopy if one is not in the original photo). \n"
                "3. REFERENCE IMAGE USAGE: The attached reference images are STRICTLY for extracting the exact paint colors (Navy Blue, Off-White, Yellow) and material textures (stucco). \n"
                "4. SILHOUETTE & SKYLINE PRESERVATION: The exact silhouette of the building against the sky is completely locked. DO NOT add any new roof structures, geometry, or materials behind the existing parapets or walls. If a roof is not visible in the input photo, it must not be visible in the render. \n"
                "5. SIGNAGE LOCK: DO NOT add new signage. ONLY replace existing signs in their exact original locations. Navy blue protrusions must remain blank unless a sign exists there. \n"
                "ACT AS A PRECISION SURFACE-LEVEL VISUALIZER. \n"
                f"BRAND STANDARDS: {brand_instr} \n"
                f"SIGNAGE LOGIC: {signage_logic} \n"
                "QUALITY: Photorealistic 8k architectural render."
            )

            contents = [system_instruction, process_base]
            for ref_path in auto_refs:
                contents.append(Image.open(ref_path))

            response = client.models.generate_content(
                model='gemini-3.1-flash-image-preview',
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=chosen_ratio),
                    temperature=0.4  
                )
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    raw_img = Image.open(io.BytesIO(part.inline_data.data))
                    # FORCE PIXEL MATCH
                    final_img = raw_img.resize((orig_width, orig_height), Image.Resampling.LANCZOS)
                    st.session_state.render_history.append(final_img)
                    st.session_state.render_img = final_img
                    st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# --- 6. RENDER DISPLAY & CAROUSEL ---
if st.session_state.render_img:
    with col2:
        # CHANGED: Replaced hardcoded width with use_container_width=True
        st.image(st.session_state.render_img, caption=f"{brand_choice} Concept", use_container_width=True)
        buf = io.BytesIO()
        st.session_state.render_img.save(buf, format="PNG")
        st.download_button("💾 Save Render", buf.getvalue(), "parafin_render.png", "image/png")

if st.session_state.render_history:
    st.divider()
    st.subheader("🔄 Previous Renders")
    cols = st.columns(len(st.session_state.render_history))
    for idx, img in enumerate(st.session_state.render_history):
        with cols[idx]:
            st.image(img, use_container_width=True)
            if st.button(f"Recall #{idx+1}", key=f"recall_{idx}"):
                st.session_state.render_img = st.session_state.render_history[idx]
                st.rerun()



