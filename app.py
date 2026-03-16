import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import io
import tomllib
import base64


# --- HELPER FUNCTION FOR IMAGE CSS ---
@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""


# --- 1. CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Parafin: Brand Converter", layout="wide")

# Parafin Platform Colors
parafin_blue = "#666B8B"
grayed_out_bg = "#F5F5F5"
grayed_out_text = "#888888"

st.markdown(f"""
    <style>
    /* 1. Hide the footer and hamburger menu */
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* 2. Target the "Manage app" button and its container specifically */
    .stAppDeployButton {{ display: none !important; }}
    div[data-testid="stStatusWidget"] {{ display: none !important; }}
    [id^="manage-app"], [class*="viewerBadge"] {{ display: none !important; }}

    /* 3. Clean up the top spacing */
    .block-container {{ padding-top: 2rem; }}

    /* 4. ROCK-SOLID BUTTON STYLING (Mobile-Proof) */
    /* Primary (Active/Selected) State */
    button[kind="primary"] {{
        background-color: {parafin_blue} !important;
        color: white !important;
        border-color: {parafin_blue} !important;
        border-radius: 5px !important;
        height: 3em !important;
        -webkit-appearance: none !important; /* Strips mobile browser default styling */
        appearance: none !important;
        opacity: 1 !important; /* Prevents mobile browsers from washing out the color */
    }}
    button[kind="primary"] * {{
        color: white !important;
    }}
    button[kind="primary"]:hover, button[kind="primary"]:focus, button[kind="primary"]:active {{
        background-color: {parafin_blue} !important;
        border-color: {parafin_blue} !important;
        color: white !important;
    }}

    /* Secondary (Inactive) & Disabled State */
    button[kind="secondary"], button:disabled {{
        background-color: {grayed_out_bg} !important;
        color: {grayed_out_text} !important;
        border-color: #E0E0E0 !important;
        border-radius: 5px !important;
        height: 3em !important;
        -webkit-appearance: none !important;
        appearance: none !important;
        opacity: 1 !important;
    }}
    button[kind="secondary"] * {{
        color: {grayed_out_text} !important;
    }}
    button[kind="secondary"]:hover:not(:disabled), button[kind="secondary"]:focus:not(:disabled), button[kind="secondary"]:active:not(:disabled) {{
        background-color: {grayed_out_bg} !important;
        color: {grayed_out_text} !important;
        border-color: #E0E0E0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Assets Directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


# --- STATE MANAGEMENT INIT ---
if "render_history" not in st.session_state: st.session_state.render_history = []
if "render_img" not in st.session_state: st.session_state.render_img = None
if "last_base_file" not in st.session_state: st.session_state.last_base_file = None

if "active_step" not in st.session_state: st.session_state.active_step = 'upload'
if "base_file" not in st.session_state: st.session_state.base_file = None
if "brand_choice" not in st.session_state: st.session_state.brand_choice = None


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
    st.header("Brand Converter")


# --- 2. HORIZONTAL BUTTON WORKFLOW ---
# Dynamic target brand logo rendering directly ABOVE the Brand Select button
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


# The 3 Main Workflow Buttons
b_col1, b_col2, b_col3 = st.columns(3)

# Button 1: Image Upload
type_btn1 = "primary" if st.session_state.active_step == 'upload' else "secondary"
if b_col1.button("Image Upload", type=type_btn1, use_container_width=True):
    st.session_state.active_step = 'upload'
    st.rerun()
b_col1.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 1</div>", unsafe_allow_html=True)

# Button 2: Brand Select
brand_disabled = st.session_state.base_file is None
type_btn2 = "primary" if st.session_state.active_step == 'brand' else "secondary"
if b_col2.button("Brand Select", type=type_btn2, disabled=brand_disabled, use_container_width=True):
    st.session_state.active_step = 'brand'
    st.rerun()
b_col2.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 2</div>", unsafe_allow_html=True)

# Button 3: Convert!
convert_disabled = (st.session_state.base_file is None) or (st.session_state.brand_choice is None)
type_btn3 = "primary" if st.session_state.active_step == 'convert' else "secondary"
convert_pressed = b_col3.button("Convert!", type=type_btn3, disabled=convert_disabled, use_container_width=True)
b_col3.markdown("<div style='text-align: center; font-size: 12px; color: #888888; margin-top: -12px;'>Step 3</div>", unsafe_allow_html=True)


st.divider()


# --- CALLBACK FUNCTIONS ---
def process_upload():
    """Fires after file is 100% uploaded — updates state before render cycle"""
    if st.session_state.upload_widget is not None:
        st.session_state.base_file = st.session_state.upload_widget
        if st.session_state.brand_choice is None:
            st.session_state.active_step = 'brand'
        else:
            st.session_state.active_step = 'convert'

def process_brand_change():
    """Fires on selectbox change — updates state before render cycle, no st.rerun() needed"""
    new_choice = st.session_state.brand_select_widget
    if new_choice is not None:
        st.session_state.brand_choice = new_choice
        st.session_state.active_step = 'brand'


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
if brand_choice:
    search_string = "city_express" if "City Express" in brand_choice else "spark" if "Spark" in brand_choice else "garner"
    if os.path.exists(ASSETS_DIR):
        all_files = os.listdir(ASSETS_DIR)
        auto_refs = [os.path.join(ASSETS_DIR, f) for f in all_files if search_string in f.lower() and "signage" not in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg'))]

blue_inset_pct = 30


# --- 4. CLIENT INITIALIZATION ---
client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version='v1alpha'))

# --- 5. DISPLAY COLUMNS ---
# FIX: Single declaration of spinner_placeholder — removed the duplicate that appeared after columns
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

            # FIX: All logic is now correctly inside a single try block so all errors are caught
            try:
                process_base = Image.open(base_file)
                orig_width, orig_height = process_base.size

                ratio_val = orig_width / orig_height
                chosen_ratio = "16:9" if ratio_val > 1.5 else "4:3" if ratio_val > 1.2 else "1:1"

                # --- PHOTOREALISTIC RENDERING PROTOCOL ---
                rendering_logic = (
                    "\nULTRA-PHOTOREALISTIC RENDERING PROTOCOL: \n"
                    "1. GLOBAL ILLUMINATION & BOUNCED LIGHT: Every new material must react to the scene's light source. "
                    "Calculated bounced light from the ground/pavement must reflect on the lower facade. \n"
                    "2. AMBIENT OCCLUSION: Generate high-fidelity contact shadows (AO) in all corners, window reveals, "
                    "and where the canopy meets the wall to ensure physical depth and prevent a flat look. \n"
                    "3. MATERIAL PHYSICS: New paint must have a 'Satin Stucco' finish. It must catch specular highlights "
                    "on sun-facing edges and show subtle texture variations. No flat or matte fills. \n"
                    "4. LOGO ILLUMINATION: If signage is placed, render subtle drop shadows and physical mounting depth."
                )

                # BRAND STANDARDS
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
                        "8. PHYSICAL SIGNAGE PLAQUE & PLACEMENT: \n"
                        "   - FINALLY, identify all primary signage areas on the building. \n"
                        "   - CRITICAL PLACEMENT RULE: You MUST place the physical sign plaque ONLY on the Warm Off-White stucco walls. \n"
                        "   - DO NOT place the sign on the Deep Navy Blue architectural elements. If the original hotel had a sign on a wall that is now Navy Blue, you must relocate the new sign to a Warm Off-White surface. \n"
                        "   - DO NOT just paint text on the wall. You MUST mount the entire physical sign panel shown in the provided asset. \n"
                        "   - Render the complete blue rectangular background and the yellow border ring exactly as it appears in the asset. \n"
                        "   - The text 'CITY EXPRESS BY MARRIOTT' must be inside this physical blue and yellow sign plaque. \n"
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
                        "5. SIGNAGE PLACEMENT RULE: The primary 'Spark' logo MUST ONLY appear on the solid, lightest gray exterior paint (PT-20). Do NOT place the logo over the busy geometric mural or dark accents. \n"
                        "6. ROOF PRESERVATION (PT-23): The exact pitched roof or skyline must remain completely unaltered in geometry, but you may update the roof color to match the PT-23 spec if applicable. \n"
                        "7. TRIM (PT-22): Keep architectural trim and details painted in the designated PT-22 color. \n"
                        "8. LOGO & SIGNAGE STENCILING: \n"
                        "   - FINALLY, identify all signage areas on the building (entrance canopies, ground-floor plaques). \n"
                        "   - APPLY the complete logo lockup 'spark by Hilton' from the provided asset as a precise visual stencil over all identified signage areas. \n"
                        "   - CRITICAL: You must include the 'by Hilton' sub-text. Render all letters with the *exact* lowercase formatting for 'spark', font, proportions, and color seen in the 'spark_signage.png' asset. \n"
                        "   - DO NOT invent your own font. You are tracing the provided asset. \n"
                        f"{rendering_logic}"
                    )
                elif "Garner" in brand_choice:
                    brand_instr = (
                        "MATERIAL AUDIT & SPECIFIC OVERRIDE (GARNER BY IHG): \n"
                        "1. THE NEUTRAL FIELD: Identify the primary building massing. Apply a clean, "
                        "warm greige neutral stucco finish. Use a fine sand-aggregate texture. \n"
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
                        "5. SIGNAGE PLACEMENT: Place the 'Garner by IHG' logo on the largest flat, "
                        "painted (non-masonry) wall surface available — preferably near the top of the "
                        "building or above the entrance. DO NOT place signage on a tower or raised element "
                        "that you have invented. Only use geometry that exists in the original photo. \n"
                        "6. LANDSCAPING & BASE: All existing stone, brick, or masonry base walls and columns are IMMUTABLE — preserve their exact color and texture. Apply a 'Digital Pressure Wash' only: remove dirt, mold, and weathering so they look freshly cleaned. Do NOT paint or recolor any masonry surface. Enhance entrance areas with crisp, focal landscaping. \n"
                        "7. LOGO & SIGNAGE STENCILING: \n"
                        "   - FINALLY, identify all signage areas on the building. \n"
                        "   - APPLY the complete logo lockup 'Garner by IHG' from the provided asset as a precise visual stencil over all identified signage areas. \n"
                        "   - CRITICAL: You must include the 'by IHG' sub-text. Render the letters with the *exact* capitalization, font, proportions, and styling seen in the 'garner_signage.PNG' asset. \n"
                        "   - DO NOT invent your own font. You are tracing the provided asset. \n"
                        f"{rendering_logic}"
                    )

                # 3. CONTEXTUAL SIGNAGE ANCHOR (ZERO-TOLERANCE 1:1 REPLACEMENT)
                signage_logic = (
                    "STRICT SIGNAGE ANCHORING (1:1 ONLY): \n"
                    "1. THE 'EXISTING SIGN' MASK: Identify every physical logo and sign in the original photo. \n"
                    "2. 1:1 REPLACEMENT ONLY: Replace existing signage with the brand specified ONLY in the existing signage locations. \n"
                    "3. NO NEW PLACEMENTS: If a wall is blank in the original photo, it MUST remain 100% blank in the render. Do not invent or add new signs. \n"
                    "4. MAJOR PROTRUSIONS: Major protrusions or large elements on the facade must be painted the Deep Navy Blue (PTW-004-SW) color palette, but they MUST REMAIN BLANK with no signage unless a sign was already there in the input image."
                )

                # GLOBAL OVERRIDE SYSTEM INSTRUCTIONS
                system_instruction = (
                    "### GLOBAL ARCHITECTURAL LOCKDOWN (ZERO GEOMETRY ALTERATION) ### \n"
                    "1. YOU ARE A PAINTER AND TEXTURE APPLICATOR, NOT AN ARCHITECT. \n"
                    "2. ABSOLUTE GEOMETRY & HEIGHT LOCK: The structural silhouette, massing, and every architectural edge of the input photo are 100% IMMUTABLE. You MUST NOT add extra floors, stories, or change the vertical height of the building. The exact number of floors in the original image must be preserved. Do not add new structures (e.g., do not build a porte-cochere or canopy if one is not in the original photo). \n"
                    "3. NO MIRRORING OR FLIPPING: You are strictly forbidden from mirroring, reversing, or horizontally flipping the input image. The left-to-right orientation of the building, parking lot, background, and environment must remain exactly as it appears in the original photo. \n"
                    "4. REFERENCE IMAGE USAGE: The attached reference images are STRICTLY for extracting the exact paint colors, material textures, and signage. DO NOT copy the architectural shape, height, or number of floors from the reference images. \n"
                    "5. SILHOUETTE & SKYLINE PRESERVATION: The exact silhouette of the building against the sky is completely locked. DO NOT add any new roof structures, geometry, or materials behind the existing parapets or walls. \n"
                    "6. SIGNAGE LOCK: DO NOT add new signage. ONLY replace existing signs in their exact original locations. \n"
                    "7. ZERO-TOLERANCE CONTENT LOCKED: \n"
                    "   - IDENTIFY the exact text from the provided signage asset. \n"
                    "   - DO NOT change the capitalization of any letters. \n"
                    "   - DO NOT change the font, color, or spelling of the logo. \n"
                    "   - DO NOT make any text lowercase if it is uppercase in the reference image, and vice versa. \n"
                    "8. REFERENCE IMAGE IS A MANDATORY VISUAL TEMPLATE: Treat the attached logo reference image as an immutable visual stencil for any text rendering. \n"
                    "9. MATERIAL PRESERVATION & RESTORATION (BRICK & STONE) — ZERO TOLERANCE: \n"
                    "   - IDENTIFY every surface in the input photo that is exposed brick, natural stone, stacked stone, or raw masonry (including columns, base walls, accent panels, and pilasters). \n"
                    "   - These surfaces are 100% IMMUTABLE in color, texture, and material. You are ABSOLUTELY FORBIDDEN from painting, tinting, recoloring, or obscuring them with any brand color whatsoever. \n"
                    "   - This rule overrides ALL brand paint instructions. If a brand instruction says to paint a surface Navy Blue, Light Gray, or any other color, but that surface is brick or stone in the original photo, the brick/stone WINS. Do not paint it. \n"
                    "   - Columns clad in stone remain stone. Base walls in brick remain brick. Accent stone panels remain stone. No exceptions. \n"
                    "   - The ONLY modification permitted on these masonry surfaces is a photorealistic 'Digital Pressure Wash': remove all visible dirt, mold, efflorescence, water stains, and weathering so the natural material looks freshly cleaned and fully restored — as if a professional pressure washing crew just finished. Bring out the full vibrancy and natural color depth of the original stone or brick. \n"
                    "   - Brand paint colors may ONLY be applied to stucco, EIFS, siding, fiber cement, metal panels, or previously painted flat surfaces. \n"
                    "ACT AS A PRECISION SURFACE-LEVEL VISUALIZER. \n"
                    f"BRAND STANDARDS: {brand_instr} \n"
                    f"SIGNAGE LOGIC: {signage_logic} \n"
                    "QUALITY: Photorealistic 8k architectural render."
                )

                contents = [system_instruction, process_base]

                if "Spark" not in brand_choice:
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
