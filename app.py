import streamlit as st
import os
import random
from google import genai
from google.genai import types
from PIL import Image
import io
import tomllib
import base64
# from supabase import create_client

# --- PAGE CONFIG (must be first, called once only) ---
st.set_page_config(
    page_title="Parafin: Brand Converter",
    page_icon="https://imgur.com/OFMZh1F.png",
    layout="wide"
)

# --- GLOBAL COLORS ---
parafin_blue = "#666B8B"
grayed_out_bg = "#F5F5F5"
grayed_out_text = "#888888"

# --- AUTH GATE ---
# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def show_auth_page():
    st.markdown(f"""
        <style>
        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stAppDeployButton {{ display: none !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        [id^="manage-app"], [class*="viewerBadge"] {{ display: none !important; }}
        .block-container {{ padding-top: 2rem; }}
        button[kind="primary"] {{
            background-color: {parafin_blue} !important;
            color: white !important;
            border-color: {parafin_blue} !important;
            border-radius: 5px !important;
            height: 3em !important;
            -webkit-appearance: none !important;
            appearance: none !important;
            opacity: 1 !important;
            cursor: pointer !important;
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
        }}
        button[kind="primary"] * {{
            color: white !important;
        }}
        button[kind="primary"]:hover {{
            background-color: #7A7FA0 !important;
            border-color: #7A7FA0 !important;
            color: white !important;
        }}
        button[kind="primary"]:focus, button[kind="primary"]:active {{
            background-color: {parafin_blue} !important;
            border-color: {parafin_blue} !important;
            color: white !important;
        }}
        @media (max-width: 768px) {{
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
            [data-testid="stImage"] img {{
                width: 100% !important;
                height: auto !important;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
    parafin_logo_path = os.path.join(ASSETS_DIR, "PF_Logo_2023.png")
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        if os.path.exists(parafin_logo_path):
            st.image(parafin_logo_path, width=120)
        st.title("Hotel Brand Converter")
        st.caption("Access the tool — it's free!")
        st.divider()
        
        gif_path = os.path.join(os.path.dirname(__file__), "assets", "demo", "demo.gif")
        if os.path.exists(gif_path):
            st.image(gif_path, use_container_width=True)
            st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
            
        # THE NEW BYPASS BUTTON 
        if st.button("Click here to start Converting", type="primary", use_container_width=True):
            st.session_state["user"] = "guest_user_bypass"
            st.rerun()

if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# --- HELPER FUNCTION FOR IMAGE CSS ---
@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 1. CONFIGURATION & UI SETUP ---
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

st.markdown(f"""
    <style>
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stAppDeployButton {{ display: none !important; }}
    div[data-testid="stStatusWidget"] {{ display: none !important; }}
    [id^="manage-app"], [class*="viewerBadge"] {{ display: none !important; }}
    .block-container {{ padding-top: 2rem; }}
    button[kind="primary"] {{
        background-color: {parafin_blue} !important;
        color: white !important;
        border-color: {parafin_blue} !important;
        border-radius: 5px !important;
        height: 3em !important;
        -webkit-appearance: none !important;
        appearance: none !important;
        opacity: 1 !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
    }}
    button[kind="primary"] * {{
        color: white !important;
    }}
    button[kind="primary"]:hover {{
        background-color: #7A7FA0 !important;
        border-color: #7A7FA0 !important;
        color: white !important;
    }}
    button[kind="primary"]:focus, button[kind="primary"]:active {{
        background-color: {parafin_blue} !important;
        border-color: {parafin_blue} !important;
        color: white !important;
    }}
    button[kind="secondary"] {{
        background-color: {grayed_out_bg} !important;
        color: {grayed_out_text} !important;
        border-color: #E0E0E0 !important;
        border-radius: 5px !important;
        height: 3em !important;
        -webkit-appearance: none !important;
        appearance: none !important;
        opacity: 1 !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
    }}
    button[kind="secondary"] * {{
        color: {grayed_out_text} !important;
        transition: color 0.15s ease !important;
    }}
    button[kind="secondary"]:hover:not(:disabled) {{
        background-color: #8A8FAA !important;
        color: white !important;
        border-color: #8A8FAA !important;
    }}
    button[kind="secondary"]:hover:not(:disabled) * {{
        color: white !important;
    }}
    button[kind="secondary"]:active:not(:disabled) {{
        background-color: {parafin_blue} !important;
        color: white !important;
        border-color: {parafin_blue} !important;
    }}
    button[kind="secondary"]:active:not(:disabled) * {{
        color: white !important;
    }}
    button:disabled {{
        background-color: {grayed_out_bg} !important;
        color: {grayed_out_text} !important;
        border-color: #E0E0E0 !important;
        border-radius: 5px !important;
        height: 3em !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }}
    @media (max-width: 768px) {{
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }}
        [data-testid="stImage"] img {{
            width: 100% !important;
            height: auto !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


# --- STATE MANAGEMENT INIT ---
if "render_history" not in st.session_state: st.session_state.render_history = []
if "render_img" not in st.session_state: st.session_state.render_img = None
if "last_base_file" not in st.session_state: st.session_state.last_base_file = None

if "active_step" not in st.session_state: st.session_state.active_step = 'upload'
if "base_file" not in st.session_state: st.session_state.base_file = None
if "brand_choice" not in st.session_state: st.session_state.brand_choice = None
if "is_example" not in st.session_state: st.session_state.is_example = False


# --- SILENT API KEY LOAD ---
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except:
        api_key = None

if not api_key:
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "rb") as f:
                secrets_data = tomllib.load(f)
                api_key = secrets_data.get("GOOGLE_API_KEY")
        except:
            pass

if not api_key:
    st.error("API Key not found. Please add GOOGLE_API_KEY to Railway Variables.")
    st.stop()


# --- MAIN TITLE & PARAFIN LOGO ---
title_col1, title_col2 = st.columns([1, 6], vertical_alignment="center")

with title_col1:
    parafin_logo_path = os.path.join(ASSETS_DIR, "PF_Logo_2023.png")
    if os.path.exists(parafin_logo_path):
        st.image(parafin_logo_path, width=150)
    else:
        st.error("PF_Logo_2023.png not found in assets!")

with title_col2:
    st.header("Hotel Brand Converter")
    if st.button("Sign out", key="signout"):
        st.session_state.clear()
        st.rerun()

# --- BUTTON CLICK CALLBACKS ---
def go_to_upload():
    st.session_state.active_step = 'upload'

def go_to_brand():
    st.session_state.active_step = 'brand'


# --- 2. HORIZONTAL BUTTON WORKFLOW ---
logo_col1, logo_col2, logo_col3 = st.columns(3)

with logo_col2:
    if st.session_state.brand_choice is not None and st.session_state.base_file is not None:
        if "City Express" in st.session_state.brand_choice:
            logo_filename = "city_express_signage.PNG"
        elif "Spark" in st.session_state.brand_choice:
            logo_filename = "spark_signage.png"
        else:
            logo_filename = "garner_signage.PNG"

        logo_path = os.path.join(ASSETS_DIR, logo_filename)
        if os.path.exists(logo_path):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(logo_path, use_container_width=True)
        else:
            st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)


b_col1, b_col2, b_col3 = st.columns(3)

type_btn1 = "primary" if st.session_state.active_step == 'upload' else "secondary"
b_col1.button("Image Upload", type=type_btn1, use_container_width=True, on_click=go_to_upload)
b_col1.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 1</div>", unsafe_allow_html=True)

brand_disabled = st.session_state.base_file is None
type_btn2 = "primary" if st.session_state.active_step == 'brand' else "secondary"
b_col2.button("Brand Select", type=type_btn2, disabled=brand_disabled, use_container_width=True, on_click=go_to_brand)
b_col2.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 2</div>", unsafe_allow_html=True)

convert_disabled = (st.session_state.base_file is None) or (st.session_state.brand_choice is None)
type_btn3 = "primary" if st.session_state.active_step == 'convert' else "secondary"
convert_pressed = b_col3.button("Convert!", type=type_btn3, disabled=convert_disabled, use_container_width=True)
b_col3.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 3</div>", unsafe_allow_html=True)


st.divider()


# --- CALLBACK FUNCTIONS ---
def process_upload():
    if st.session_state.upload_widget is not None:
        st.session_state.base_file = st.session_state.upload_widget
        st.session_state.is_example = False
        if st.session_state.brand_choice is None:
            st.session_state.active_step = 'brand'
        else:
            st.session_state.active_step = 'convert'

def use_example():
    candidates = []
    if os.path.exists(ASSETS_DIR):
        for f in os.listdir(ASSETS_DIR):
            name, ext = os.path.splitext(f)
            if name.lower().startswith("example_") and ext.lower() in ('.png', '.jpg', '.jpeg'):
                candidates.append(os.path.join(ASSETS_DIR, f))
    if candidates:
        chosen = random.choice(candidates)
        st.session_state.base_file = chosen
        st.session_state.is_example = True
        if st.session_state.brand_choice is None:
            st.session_state.active_step = 'brand'
        else:
            st.session_state.active_step = 'convert'

def process_brand_change():
    new_choice = st.session_state.brand_select_widget
    if new_choice is not None:
        st.session_state.brand_choice = new_choice
        st.session_state.active_step = 'convert'


# --- 3. DYNAMIC UI PANELS ---
if st.session_state.active_step == 'upload':
    st.subheader("📁 Image Upload")
    st.caption("📱 **Mobile Users:** If your upload fails, tap your screen's menu (••• or compass) and select **Open in Safari/Chrome**.")

    st.file_uploader(
        "Existing Hotel Image",
        type=['png', 'jpg', 'jpeg'],
        key="upload_widget",
        on_change=process_upload
    )

    example_exists = os.path.exists(ASSETS_DIR) and any(
        os.path.splitext(f)[0].lower().startswith("example_") and
        os.path.splitext(f)[1].lower() in ('.png', '.jpg', '.jpeg')
        for f in os.listdir(ASSETS_DIR)
    )

    if example_exists:
        st.markdown("<div style='text-align: center; color: #888888; font-size: 13px; margin: 4px 0'>— or —</div>", unsafe_allow_html=True)
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.button(
                "✨ Use an Example Hotel Image",
                use_container_width=True,
                on_click=use_example
            )

elif st.session_state.active_step == 'brand':
    st.subheader("🎯 Select Target Brand")

    options = ["City Express by Marriott", "Spark by Hilton", "Garner by IHG"]
    current_idx = options.index(st.session_state.brand_choice) if st.session_state.brand_choice in options else None

    st.selectbox(
        "Select Target Brand",
        options,
        index=current_idx,
        placeholder="Choose a brand...",
        key="brand_select_widget",
        on_change=process_brand_change
    )

elif st.session_state.active_step == 'convert':
    st.success(f"✅ Ready! Click the **Convert!** button above to apply the {st.session_state.brand_choice} brand standards.")


# --- RESTORE VARIABLES FOR THE ENGINE ---
base_file = st.session_state.base_file
brand_choice = st.session_state.brand_choice

auto_refs = []
signage_ref = None
if brand_choice:
    search_string = "city_express" if "City Express" in brand_choice else "spark" if "Spark" in brand_choice else "garner"
    if os.path.exists(ASSETS_DIR):
        all_files = os.listdir(ASSETS_DIR)

        seen_basenames = set()
        for f in sorted(all_files):
            name, ext = os.path.splitext(f)
            if (search_string in f.lower()
                    and "signage" not in f.lower()
                    and "example" not in f.lower()
                    and ext.lower() in ('.png', '.jpg', '.jpeg')
                    and name.lower() not in seen_basenames):
                auto_refs.append(os.path.join(ASSETS_DIR, f))
                seen_basenames.add(name.lower())

        for f in sorted(all_files):
            name, ext = os.path.splitext(f)
            if (search_string in f.lower()
                    and "signage" in f.lower()
                    and ext.lower() in ('.png', '.jpg', '.jpeg')):
                signage_ref = os.path.join(ASSETS_DIR, f)
                break

blue_inset_pct = 30


# --- 4. CLIENT INITIALIZATION ---
client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version='v1alpha'))

# --- 5. DISPLAY COLUMNS ---
spinner_placeholder = st.empty()

col1, col2 = st.columns(2)

if base_file:
    with col1:
        current_display_base = Image.open(base_file)
        st.image(current_display_base, caption="Existing Hotel", use_container_width=True)


# --- 6. THE PRECISION ENGINE ---
if convert_pressed and base_file and brand_choice and auto_refs:
    st.session_state.active_step = 'convert'

    with spinner_placeholder:
        with st.spinner(f"Applying {brand_choice} Standards..."):

            try:
                process_base = Image.open(base_file)
                orig_width, orig_height = process_base.size

                rendering_logic = (
                    "\nRENDERING QUALITY: \n"
                    "- New paint must have a satin stucco finish with specular highlights on sun-facing edges. \n"
                    "- Generate contact shadows (ambient occlusion) in all corners and window reveals. \n"
                    "- Bounced light from the ground must reflect on the lower facade. \n"
                    "- If signage is placed, render subtle drop shadows and physical mounting depth. \n"
                )

                if "City Express" in brand_choice:
                    brand_instr = (
                        "MATERIAL AUDIT & SPECIFIC OVERRIDE (CITY EXPRESS): \n"
                        "1. BASE MATERIAL AUDIT: Carefully scan every surface in the input photo for exposed brick, stacked stone, natural stone, or raw masonry. \n"
                        "   - IF ANY SURFACE IS STONE OR BRICK (columns, base walls, accent panels, pilasters, etc.): You MUST preserve that material exactly — same color, same texture, same pattern. Apply a 'Digital Pressure Wash' only: remove all dirt, mold, efflorescence, and weathering so it looks freshly cleaned and fully restored. DO NOT paint, tint, or recolor these surfaces under any circumstance. \n"
                        "   - IF A SURFACE IS STUCCO OR EIFS (smooth, flat, painted): Replace with 'Warm Greige Plaster' (Finish B) — a medium-tone sandy greige with heavy sand-aggregate texture. \n"
                        "   - RULE PRIORITY: Stone/brick preservation overrides all brand paint instructions below. If uncertain whether a surface is masonry or stucco, treat it as masonry and preserve it. \n"
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
                        "   - CRITICAL: Do NOT paint canopy support columns blue; they must follow the Base Material Audit (masonry/stucco). \n"
                        "8. PHYSICAL SIGNAGE: Handled by the signage rules below. \n"
                        f"{rendering_logic}"
                    )
                elif "Spark" in brand_choice:
                    brand_instr = (
                        "MATERIAL AUDIT & SPECIFIC OVERRIDE (SPARK BY HILTON): \n"
                        "1. THE BASE CANVAS (PT-20): Analyze the primary body of the building facade (brick, stucco, EIFS). "
                        "Paint the vast majority of the main building massing a clean, Light Gray (PT-20). "
                        "Apply a 'Digital Power Wash' to remove all weathering, making it look refreshed and modern. \n"
                        "2. DARK ACCENTS (PT-21): Identify structural insets, recessed window bays, or secondary architectural volumes. "
                        "Paint these areas a Dark Accent Gray/Slate (PT-21) to create depth. \n"
                        "3. THE SPARK GEOMETRIC MURAL (PT-24 FOCAL): This must be a FULL-HEIGHT vertical intervention. \n"
                        "   A. VERTICAL DOMINANCE: Identify the most prominent architectural 'bump out' or vertical bay. "
                        "Apply the geometric mural starting from the top of the ground-floor base all the way to "
                        "the uppermost roofline parapet of that specific section. It must cover the entire "
                        "vertical height of the identified massing. \n"
                        "   B. COLOR HIERARCHY: Strictly use percentages from the Implementation Guide: "
                        "Violet (35%), Lavender (25%), Slate (20%), Lime (15%), and Grays (15%). "
                        "Ensure Violet and Lavender are the dominant visual weights. \n"
                        "   C. GEOMETRIC DENSITY & CONTINUITY: Maintain the floor-height triangle scale, ensuring they "
                        "stack vertically without gaps. The pattern must be applied as a continuous canvas—render "
                        "pattern colors over or behind windows/mullions without creating boundaries or 'cut-outs' around glass. \n"
                        "   D. PLACEMENT GUARDRAIL: Do NOT cover the whole building in this pattern; it is a localized, asymmetrical focal mural. \n"
                        "4. PORTE COCHERE (CANOPY) LOGIC: If a projecting drive-under canopy exists, you may apply the geometric triangle mural to the UNDERSIDE (ceiling) of the canopy, or paint the canopy fascia PT-20 Light Gray. Keep columns clean. \n"
                        "5. SIGNAGE PLACEMENT RULE: The 'spark by Hilton' logo must only appear on solid PT-20 Light Gray wall surface. Do NOT place over the geometric mural. Signage placement count and locations are governed by the signage rules below. \n"
                        "6. ROOF: Governed by the global roof rule — do not change roof color or material. \n"
                        "7. TRIM (PT-22): Keep architectural trim and details painted in the designated PT-22 color. \n"
                        "8. LOGO APPEARANCE: The 'spark by Hilton' logo has a single 4-pointed star at the TOP-LEFT above the 's', 'spark' in bold lowercase purple (#6B3FA0), and 'by Hilton' smaller below. The star is lime yellow-green (#C8D400). No other decorative elements. \n"
                        f"{rendering_logic}"
                    )
                elif "Garner" in brand_choice:
                    brand_instr = (
                        "MATERIAL AUDIT & SPECIFIC OVERRIDE (GARNER BY IHG): \n"
                        "0. MATERIAL INVENTORY (DO THIS FIRST): Before applying any treatment, scan every surface "
                        "of the input photo and categorize each as either: (A) existing masonry — brick, stone, "
                        "stacked stone, raw concrete block — or (B) painted/smooth surface — stucco, EIFS, siding, "
                        "fiber cement, or previously painted walls. This inventory governs everything below. \n"
                        "1. THE NEUTRAL FIELD: For all Category B (painted/smooth) surfaces identified above, "
                        "apply a clean warm greige neutral paint finish. DO NOT change the surface material — "
                        "stucco stays stucco, just repainted. DO NOT add, invent, or simulate any stone, brick, "
                        "or masonry texture on surfaces that are smooth in the original photo. \n"
                        "2. DARK CONTRAST SECTIONS (PAINT ONLY — DO NOT BUILD): Scan the existing facade for "
                        "architectural elements that already project, recess, or read as focal volumes — such as "
                        "an existing entrance bay, recessed window columns, or a raised parapet section. "
                        "If such elements exist in the original photo, paint ONLY those existing surfaces in "
                        "Deep Charcoal Gray (Iron Ore) to create contrast. "
                        "CRITICAL: DO NOT construct, invent, or add any new vertical tower, raised parapet, rooftop element, "
                        "or massing that does not already exist in the input image. You are a painter, not an architect. "
                        "If no strong focal volume exists, apply the Deep Charcoal Gray sparingly to the entrance "
                        "surround or upper fascia band only. \n"
                        "3. THE SEAFOAM SOFFIT (ONLY IF CANOPY EXISTS): Analyze the original photo for a "
                        "projecting drive-under canopy or porte-cochere. IF one already exists, paint its "
                        "UNDERSIDE (ceiling/soffit) in a signature Seafoam Teal accent color. "
                        "IF NO canopy exists in the original photo, skip this step entirely. DO NOT build one. \n"
                        "4. CANOPY FASCIA (ONLY IF CANOPY EXISTS): IF a canopy already exists, paint its "
                        "vertical fascia edges in Deep Charcoal Gray. IF no canopy exists, skip this step. \n"
                        "5. SIGNAGE: Handled by the signage rules below. \n"
                        "6. MASONRY ZERO-TOLERANCE RULE: \n"
                        "   - Category A surfaces (existing brick/stone/masonry) from your inventory: IMMUTABLE. "
                        "Preserve exact color and texture. Apply a Digital Pressure Wash only — remove dirt, "
                        "mold, and weathering so they look freshly cleaned. Do NOT paint or recolor them. \n"
                        "   - Category B surfaces (smooth/painted): STRICTLY FORBIDDEN from receiving any "
                        "stone, brick, or masonry treatment. Do NOT add stone cladding, brick veneer, stacked "
                        "stone, or any masonry-like texture to surfaces that are smooth in the original photo. "
                        "If it was stucco in the input, it must remain stucco in the output — just repainted. \n"
                        f"{rendering_logic}"
                    )

                signage_logic = (
                    "SIGNAGE RULES — READ CAREFULLY BEFORE PLACING ANY LOGO:\n"
                    "STEP A: Count every existing hotel brand sign visible in the input photo. "
                    "Include ALL of the following: wall-mounted signs, illuminated sign boxes, channel letters, "
                    "canopy fascia signs, AND freestanding road/pylon signs on poles. Count every sign of every type.\n"
                    "STEP B: Replace ONLY those signs, one for one, in their exact locations. "
                    "If you counted 1 sign, place exactly 1 new brand sign. "
                    "If you counted 2 signs, place exactly 2 new brand signs. "
                    "If you counted 3 signs, place exactly 3. "
                    "Each new sign goes in the exact same position, same size, and same surface/structure as the original it replaces.\n"
                    "STEP C: If you counted ZERO existing signs anywhere in the photo, place exactly 1 new brand sign "
                    "on the single most prominent flat wall surface near the top of the building.\n"
                    "STEP D: Do not place any additional signs beyond the count from Step A (or the 1 sign from Step C). "
                    "Every blank wall that was blank in the input must remain blank. No exceptions.\n"
                    "STEP E: For freestanding road/pylon signs — replace the brand panel on the sign structure "
                    "with the new brand logo. Keep the pole, base, and sign cabinet structure exactly as it is. "
                    "Only the brand artwork on the face of the sign changes."
                )

                system_instruction = (
                    "TASK: Retouch the surfaces of the exact photo provided. Do not generate a new image.\n\n"
                    "PERSPECTIVE & COMPOSITION LOCK — highest priority, overrides everything:\n"
                    "- The camera position, angle, focal length, and perspective in the output must be identical to the input photo.\n"
                    "- The horizon line, vanishing points, and spatial relationships between all elements must be preserved exactly.\n"
                    "- Every window, door, floor band, and architectural feature must appear at the same position and size relative to the frame as in the input.\n"
                    "- The parking lot, sky, trees, and surroundings are completely frozen — do not alter them.\n\n"
                    "GEOMETRY LOCK — nothing may be added, removed, or reshaped:\n"
                    "- Walls, roofline, canopies, overhangs, and floor count are all frozen as they appear in the photo.\n"
                    "- Do not add new floors, wings, towers, canopies, or any structure not visible in the input.\n"
                    "- The reference brand images are color and signage samples only — do not use their building shapes.\n\n"
                    "ROOF LOCK — overrides all brand instructions below:\n"
                    "- The roof color, material, and texture are completely frozen exactly as they appear in the input photo.\n"
                    "- Do NOT repaint, recolor, re-tile, re-shingle, or alter the roof in any way.\n"
                    "- If the input has a red metal roof, the output must have a red metal roof.\n"
                    "- If the input has a gray shingle roof, the output must have a gray shingle roof.\n"
                    "- If the input has a tan/beige roof, the output must have a tan/beige roof.\n"
                    "- This rule cannot be overridden by any brand color standard below.\n\n"
                    "MASONRY LOCK — overrides all brand instructions below:\n"
                    "- Brick, stone, or raw masonry surfaces stay that exact material and color — pressure wash clean but do not paint or replace.\n"
                    "- Smooth/stucco/painted surfaces may be repainted but must stay smooth — do not add stone or brick texture.\n\n"
                    "WHAT YOU MAY CHANGE — painted wall surfaces and signage only:\n"
                    f"{brand_instr}\n\n"
                    "SIGNAGE:\n"
                    f"{signage_logic}\n\n"
                    f"{rendering_logic}"
                )

                user_parts = [process_base]

                if signage_ref:
                    user_parts.append("This is the EXACT SIGNAGE LOGO to reproduce. Same layout, proportions, colors, and icon position — do not modify it.")
                    user_parts.append(Image.open(signage_ref))

                for ref_path in auto_refs:
                    user_parts.append("COLOR/MATERIAL REFERENCE ONLY — do not copy this building shape or perspective:")
                    user_parts.append(Image.open(ref_path))

                user_parts.append(
                    f"Edit the first photo above by applying these paint and signage changes only. "
                    f"The input photo is {orig_width}x{orig_height} pixels. "
                    f"The output must be the same photo at the same {orig_width}x{orig_height} dimensions with only surface colors and signs changed. "
                    f"The camera angle, perspective, framing, horizon line, and every structural element must be "
                    f"identical to the input. Do not zoom, crop, rotate, or reframe.\n\n"
                    f"{system_instruction}"
                )

                response = client.models.generate_content(
                    model='gemini-3.1-flash-image-preview',
                    contents=user_parts,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        temperature=0.1
                    )
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        raw_img = Image.open(io.BytesIO(part.inline_data.data))
                        final_img = raw_img.resize((orig_width, orig_height), Image.Resampling.LANCZOS)
                        st.session_state.render_history.append(final_img)
                        st.session_state.render_img = final_img
                        st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error: {e}")


# --- 7. RENDER DISPLAY & CAROUSEL ---
if st.session_state.render_img:
    with col2:
        st.image(st.session_state.render_img, caption=f"{st.session_state.brand_choice} Concept", use_container_width=True)
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
