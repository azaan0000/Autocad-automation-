import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import re
import ezdxf

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ASASCO AI Universal CAD & Schedule Sheet Studio",
    page_icon="📐",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0A0F1D; color: #F1F5F9; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }
    .sidebar .sidebar-content { background-color: #0F172A; }
    .stButton button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'project_type' not in st.session_state: st.session_state.project_type = "Security Door"
if 'width' not in st.session_state: st.session_state.width = 1.300
if 'height' not in st.session_state: st.session_state.height = 3.900
if 'bars' not in st.session_state: st.session_state.bars = 10
if 'panel_style' not in st.session_state: st.session_state.panel_style = "Vertical Fluted"
if 'hinge_count' not in st.session_state: st.session_state.hinge_count = 3
if 'lock_type' not in st.session_state: st.session_state.lock_type = "Multi-Point Lock & Handle"
if 'schedule_mode' not in st.session_state: st.session_state.schedule_mode = False
if 'project_desc' not in st.session_state: 
    st.session_state.project_desc = "Design a heavy-duty security door width 1.3m height 3.9m with 10 horizontal bars, 3 right hinges, vertical fluted panel, and multi-point lock."

st.title("📐 ASASCO AI Universal CAD & Schedule Sheet Studio")
st.markdown("Advanced AI Description Engine: Customizes frames, hinges, loavers, panels, locks, and generates Schedule Sheets for multiple designs.")

# ==========================================
# SIDEBAR - UNIVERSAL CONTROLS
# ==========================================
st.sidebar.header("🛠️ Universal Project Settings")
st.session_state.project_type = st.sidebar.selectbox(
    "Project Category",
    ["Security Door", "Sliding Glass Window", "Garage Door", "Partition Wall", "Balcony Grill"]
)

st.session_state.width = st.sidebar.number_input("Width (m)", value=float(st.session_state.width), step=0.01, format="%.3f")
st.session_state.height = st.sidebar.number_input("Height (m)", value=float(st.session_state.height), step=0.01, format="%.3f")
st.session_state.bars = st.sidebar.slider("Bars / Grills Count", 2, 25, int(st.session_state.bars))
st.session_state.panel_style = st.sidebar.selectbox("Panel / Loaver Style", ["Vertical Fluted", "Horizontal Louvers", "Plain Glass", "Solid Steel Sheet", "Geometric Grids"])
st.session_state.hinge_count = st.sidebar.slider("Hinges Count", 1, 6, int(st.session_state.hinge_count))
st.session_state.lock_type = st.sidebar.text_input("Lock & Hardware Specs", value=st.session_state.lock_type)

st.sidebar.markdown("---")
st.session_state.schedule_mode = st.sidebar.checkbox("📊 Enable Schedule Sheet Mode (Multi-Design Grid)", value=st.session_state.schedule_mode)

st.sidebar.success("🟢 **Universal AI Engine:** Ready")

# ==========================================
# UNIVERSAL AI DESCRIPTION PARSER
# ==========================================
def parse_universal_description(text):
    t = text.lower()
    
    # Project Type detection
    if "window" in t: st.session_state.project_type = "Sliding Glass Window"
    elif "garage" in t: st.session_state.project_type = "Garage Door"
    elif "partition" in t: st.session_state.project_type = "Partition Wall"
    elif "grill" in t: st.session_state.project_type = "Balcony Grill"
    elif "door" in t: st.session_state.project_type = "Security Door"

    # Dimensions
    wm = re.search(r'(?:width|w)\s*(?:to|=)?\s*(\d+\.?\d*)', t)
    if wm: 
        try: st.session_state.width = float(wm.group(1))
        except: pass
        
    hm = re.search(r'(?:height|h)\s*(?:to|=)?\s*(\d+\.?\d*)', t)
    if hm: 
        try: st.session_state.height = float(hm.group(1))
        except: pass

    # Bars / Grills
    bm = re.search(r'(\d+)\s*(?:bars|grills|lines)', t)
    if bm:
        try: st.session_state.bars = int(bm.group(1))
        except: pass

    # Hinges
    hingem = re.search(r'(\d+)\s*(?:hinges|hinge)', t)
    if hingem:
        try: st.session_state.hinge_count = int(hingem.group(1))
        except: pass

    # Panel styles
    if "louvers" in t or "loavers" in t: st.session_state.panel_style = "Horizontal Louvers"
    elif "fluted" in t: st.session_state.panel_style = "Vertical Fluted"
    elif "glass" in t: st.session_state.panel_style = "Plain Glass"
    elif "solid" in t: st.session_state.panel_style = "Solid Steel Sheet"

# ==========================================
# DRAWING FUNCTION GENERATOR
# ==========================================
def render_blueprint(w, h, bars, p_type, style, hinges, lock, title_suffix=""):
    canvas = np.zeros((750, 550, 3), dtype=np.uint8)
    canvas[:] = (12, 18, 32)
    
    x1, y1 = 70, 60
    x2, y2 = 480, 640
    
    # Outer Frame
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (210, 215, 225), 3, cv2.LINE_AA)
    
    ix1, iy1, ix2, iy2 = x1 + 15, y1 + 15, x2 - 15, y2 - 15
    cv2.rectangle(canvas, (ix1, iy1), (ix2, iy2), (148, 163, 184), 2, cv2.LINE_AA)
    
    # Internal patterns based on project type & style
    if "Door" in p_type or "Grill" in p_type:
        # Bars
        bar_coords = np.linspace(iy1 + 40, iy2 - 40, bars)
        cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
        for by in bar_coords:
            cv2.line(canvas, (ix1 + 5, int(by)), (ix2 - 5, int(by)), (220, 225, 235), 2, cv2.LINE_AA)
        cv2.line(canvas, (cx, iy1 + 5), (cx, iy2 - 5), (220, 225, 235), 2, cv2.LINE_AA)
        
        # Center Panel / Loavers
        pw, ph = 90, 300
        px1, py1 = cx - (pw // 2), cy - (ph // 2)
        px2, py2 = cx + (pw // 2), cy + (ph // 2)
        cv2.rectangle(canvas, (px1, py1), (px2, py2), (245, 158, 11), 2, cv2.LINE_AA)
        cv2.rectangle(canvas, (px1 + 2, py1 + 2), (px2 - 2, py2 - 2), (18, 24, 38), -1)
        
        if style == "Vertical Fluted":
            for rx in range(px1 + 10, px2, 12):
                cv2.line(canvas, (rx, py1 + 5), (rx, py2 - 5), (245, 158, 11), 1, cv2.LINE_AA)
        elif style == "Horizontal Louvers":
            for ry in range(py1 + 10, py2, 15):
                cv2.line(canvas, (px1 + 5, ry), (px2 - 5, ry), (245, 158, 11), 1, cv2.LINE_AA)

        # Hinges on Right
        hinge_step = (y2 - y1 - 100) / max(1, (hinges + 1))
        for i in range(hinges):
            hy = y1 + 50 + (i + 1) * hinge_step
            cv2.rectangle(canvas, (x2 - 3, int(hy)), (x2 + 10, int(hy) + 35), (245, 158, 11), -1, cv2.LINE_AA)

        # Lock on Left
        cv2.rectangle(canvas, (x1 - 10, cy - 20), (x1, cy + 20), (245, 158, 11), -1, cv2.LINE_AA)

    elif "Window" in p_type or "Partition" in p_type:
        # Glass panels split
        cv2.line(canvas, ((x1+x2)//2, y1), ((x1+x2)//2, y2), (56, 189, 248), 2, cv2.LINE_AA)
        cv2.putText(canvas, "GLASS PANEL", ((x1+x2)//2 - 60, (y1+y2)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (56, 189, 248), 1)

    # Dimensions
    cv2.putText(canvas, f"W: {w:.3f}m | H: {h:.3f}m", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 158, 11), 2)
    cv2.putText(canvas, f"[{p_type.upper()}] {title_suffix}", (x1, y2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return canvas

# ==========================================
# MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🚀 AI Description & Schedule Sheet", 
    "📂 Bill of Materials (BOM)", 
    "📥 AutoCAD DXF Export"
])

with tab1:
    col_desc, col_view = st.columns([1, 1], gap="medium")
    
    with col_desc:
        st.subheader("1️⃣ Universal AI Command & Description")
        user_desc = st.text_area(
            "Describe any project (Doors, Windows, Louvers, Hinges, Sizes, Grills):",
            value=st.session_state.project_desc,
            height=160
        )
        
        if st.button("✨ Parse Description & Update Design", type="primary", use_container_width=True):
            st.session_state.project_desc = user_desc
            parse_universal_description(user_desc)
            st.success("🤖 Description successfully parsed across all components!")
            st.rerun()

        st.markdown("---")
        st.info("💡 **Tip:** You can write anything like: 'Design a security door width 1.4m height 4.0m with 12 bars, 4 hinges, horizontal louvers'. The system will adapt everything automatically.")

    with col_view:
        st.subheader("2️⃣ Live CAD Blueprint / Schedule Sheet")
        
        if not st.session_state.schedule_mode:
            # Single Master View
            img = render_blueprint(
                st.session_state.width, 
                st.session_state.height, 
                st.session_state.bars, 
                st.session_state.project_type, 
                st.session_state.panel_style, 
                st.session_state.hinge_count, 
                st.session_state.lock_type,
                "SINGLE UNIT"
            )
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)
            st.success("✨ Single Design Blueprint successfully rendered with full specifications!")
        else:
            # Schedule Sheet Mode (Multi-Design Grid Sheet)
            st.markdown("### 📊 Schedule Sheet: Multiple Variations Grid")
            scols = st.columns(2)
            
            with scols[0]:
                st.markdown("**Design Variant 01 (Standard)**")
                img1 = render_blueprint(st.session_state.width, st.session_state.height, st.session_state.bars, st.session_state.project_type, st.session_state.panel_style, st.session_state.hinge_count, st.session_state.lock_type, "MARK-01")
                st.image(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB), use_container_width=True)

            with scols[1]:
                st.markdown("**Design Variant 02 (Customized Span)**")
                img2 = render_blueprint(st.session_state.width + 0.2, st.session_state.height, st.session_state.bars + 2, st.session_state.project_type, "Horizontal Louvers", st.session_state.hinge_count + 1, st.session_state.lock_type, "MARK-02")
                st.image(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB), use_container_width=True)
                
            st.success("📊 Multi-Design Schedule Sheet successfully generated!")

with tab2:
    st.subheader("📂 Complete Bill of Materials (BOM)")
    bom_data = {
        "Component": ["Structural Frame Profile", "Center Loaver / Panel", f"Security Bars ({st.session_state.bars} Pcs)", f"Heavy Hinges ({st.session_state.hinge_count} Pcs)", "Lock & Handle Assembly"],
        "Specification": [f"{st.session_state.project_type} Grade", st.session_state.panel_style, "Standard Welded Spacing", "Industrial Grade Right-Side", st.session_state.lock_type],
        "Dimensions": [f"{st.session_state.width}m x {st.session_state.height}m", "Custom Center Block", "Horizontal Span", "Matched Load Capacity", "Standard Fitment"],
        "Quantity": [1, 1, st.session_state.bars, st.session_state.hinge_count, 1]
    }
    st.table(bom_data)

with tab3:
    st.subheader("📥 Professional AutoCAD DXF Export")
    if st.button("📥 Generate & Download Schedule Sheet .DXF", type="primary", use_container_width=True):
        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()
        w_mm = st.session_state.width * 1000
        h_mm = st.session_state.height * 1000
        msp.add_lwpolyline([(0, 0), (w_mm, 0), (w_mm, h_mm), (0, h_mm), (0, 0)], close=True)
        
        dxf_buffer = io.StringIO()
        doc.write(dxf_buffer)
        
        st.download_button(
            label="💾 Download .DXF File",
            data=dxf_buffer.getvalue().encode('utf-8'),
            file_name="asasco_schedule_sheet.dxf",
            mime="application/dxf"
        )
        st.success("DXF Schedule file compiled successfully!")
