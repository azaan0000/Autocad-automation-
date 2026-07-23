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
    page_title="ASASCO AI Smart CAD Studio - AI Command Engine",
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
if 'door_width' not in st.session_state: st.session_state.door_width = 1.300
if 'door_height' not in st.session_state: st.session_state.door_height = 3.900
if 'bar_count' not in st.session_state: st.session_state.bar_count = 10
if 'element_title' not in st.session_state: st.session_state.element_title = "DOOR (STEEL ON THE STREET)"
if 'active_layer' not in st.session_state: st.session_state.active_layer = "All Layers (Master View)"
if 'project_desc' not in st.session_state: 
    st.session_state.project_desc = "Design a heavy-duty modern security door with width 1.300m and height 3.900m, 10 horizontal security bars, vertical fluted center panel, 3 right-side hinges, and left-side handle."

st.title("📐 ASASCO AI Smart CAD Studio [AI Command Enabled]")
st.markdown("AI Natural Language Command Parser integrated: Type any instruction to instantly control the drawing.")

# ==========================================
# SIDEBAR - ADVANCED CONTROLS & LAYERS
# ==========================================
st.sidebar.header("🛠️ Modular Layer & Component Control")
st.session_state.active_layer = st.sidebar.selectbox(
    "Active Design Layer",
    [
        "All Layers (Master View)",
        "A-DOOR-FRAME-EXT",
        "A-DOOR-FRAME-INT",
        "A-SECURITY-MESH-HATCH",
        "A-HORIZONTAL-SECURITY-BARS",
        "A-CENTER-FLUTED-PANEL",
        "A-HARDWARE-HINGES-LOCKS",
        "A-DIMENSION-CALLOUTS"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Manual Fine-Tuning")
st.session_state.door_width = st.sidebar.number_input("Width (m)", value=float(st.session_state.door_width), step=0.01, format="%.3f")
st.session_state.door_height = st.sidebar.number_input("Height (m)", value=float(st.session_state.door_height), step=0.01, format="%.3f")
st.session_state.bar_count = st.sidebar.slider("Horizontal Security Bars", 4, 20, int(st.session_state.bar_count))
st.session_state.element_title = st.sidebar.text_input("Element Title", value=st.session_state.element_title)

st.sidebar.success("🟢 **Engine Status:** AI Command Processor Active.")

# ==========================================
# AI COMMAND PARSER FUNCTION
# ==========================================
def process_ai_command(command_text):
    text = command_text.lower()
    updated = False
    
    # 1. Width Extraction (e.g., width 1.5m, 1.45 meters)
    w_match = re.search(r'(?:width|w)\s*(?:to|=)?\s*(\d+\.?\d*)', text)
    if w_match:
        try:
            val = float(w_match.group(1))
            if 0.5 <= val <= 10.0:
                st.session_state.door_width = val
                updated = True
        except: pass

    # 2. Height Extraction (e.g., height 4.1m, 3.8 meters)
    h_match = re.search(r'(?:height|h)\s*(?:to|=)?\s*(\d+\.?\d*)', text)
    if h_match:
        try:
            val = float(h_match.group(1))
            if 0.5 <= val <= 10.0:
                st.session_state.door_height = val
                updated = True
        except: pass

    # 3. Bar Count Extraction (e.g., 12 bars, horizontal bars 14)
    bars_match = re.search(r'(\d+)\s*(?:bars|horizontal bars)', text)
    if bars_match:
        try:
            val = int(bars_match.group(1))
            if 4 <= val <= 20:
                st.session_state.bar_count = val
                updated = True
        except: pass
        
    return updated

# ==========================================
# MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🚀 AI Command & Live Blueprint", 
    "📂 Bill of Materials (BOM)", 
    "📥 Professional AutoCAD DXF Export"
])

with tab1:
    col_desc, col_view = st.columns([1, 1], gap="medium")
    
    with col_desc:
        st.subheader("1️⃣ AI Command & Description Box")
        user_command = st.text_area(
            "Type your command or specs (e.g. 'Change width to 1.4m and bars to 12'):",
            value=st.session_state.project_desc,
            height=160
        )
        
        if st.button("✨ Execute AI Command & Update Drawing", type="primary", use_container_width=True):
            st.session_state.project_desc = user_command
            success_flag = process_ai_command(user_command)
            
            if success_flag:
                st.success("🤖 AI Command successfully executed! Blueprint updated.")
            else:
                st.info("ℹ️ Command processed. No parameter value changes detected, current specs applied.")
            st.rerun()

        st.markdown("---")
        st.info("💡 **AI Command Tips:**\n- Type `width 1.4m` to change width.\n- Type `height 4.0m` to change height.\n- Type `12 bars` to adjust security bars.")

    with col_view:
        st.subheader("2️⃣ Live CAD Blueprint Rendering")
        
        # High-Precision OpenCV Rendering Engine with Layer Support
        canvas = np.zeros((850, 650, 3), dtype=np.uint8)
        canvas[:] = (12, 18, 32)
        
        x1, y1 = 100, 80
        x2, y2 = 550, 740
        
        show_all = "All Layers" in st.session_state.active_layer
        
        # Layer 1: Outer Frame
        if show_all or "FRAME-EXT" in st.session_state.active_layer:
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (210, 215, 225), 3, cv2.LINE_AA)
            cv2.line(canvas, (x1, y1), (x1 + 25, y1 + 25), (210, 215, 225), 2, cv2.LINE_AA)
            cv2.line(canvas, (x2, y1), (x2 - 25, y1 + 25), (210, 215, 225), 2, cv2.LINE_AA)
            cv2.line(canvas, (x1, y2), (x1 + 25, y2 - 25), (210, 215, 225), 2, cv2.LINE_AA)
            cv2.line(canvas, (x2, y2), (x2 - 25, y2 - 25), (210, 215, 225), 2, cv2.LINE_AA)

        # Layer 2: Inner Frame
        ix1, iy1, ix2, iy2 = x1 + 18, y1 + 18, x2 - 18, y2 - 18
        if show_all or "FRAME-INT" in st.session_state.active_layer:
            cv2.rectangle(canvas, (ix1, iy1), (ix2, iy2), (148, 163, 184), 2, cv2.LINE_AA)
            
        # Layer 3: Security Mesh Hatching
        if show_all or "MESH-HATCH" in st.session_state.active_layer:
            for mx in range(ix1 + 20, ix2 - 15, 30):
                cv2.line(canvas, (mx, iy1 + 5), (mx, iy2 - 5), (35, 45, 60), 1, cv2.LINE_AA)
            for my in range(iy1 + 25, iy2 - 15, 40):
                cv2.line(canvas, (ix1 + 5, my), (ix2 - 5, my), (35, 45, 60), 1, cv2.LINE_AA)

        # Layer 4: Horizontal Security Bars & Center Vertical Backbone
        if show_all or "SECURITY-BARS" in st.session_state.active_layer:
            bar_coords = np.linspace(iy1 + 45, iy2 - 45, st.session_state.bar_count)
            cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
            for by in bar_coords:
                cv2.line(canvas, (ix1 + 5, int(by)), (ix2 - 5, int(by)), (220, 225, 235), 2, cv2.LINE_AA)
            cv2.line(canvas, (cx, iy1 + 5), (cx, iy2 - 5), (220, 225, 235), 2, cv2.LINE_AA)

        # Layer 5: Center Fluted Panel
        if show_all or "FLUTED-PANEL" in st.session_state.active_layer:
            cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
            pw, ph = 100, 360
            px1, py1 = cx - (pw // 2), cy - (ph // 2)
            px2, py2 = cx + (pw // 2), cy + (ph // 2)
            cv2.rectangle(canvas, (px1, py1), (px2, py2), (245, 158, 11), 2, cv2.LINE_AA)
            cv2.rectangle(canvas, (px1 + 2, py1 + 2), (px2 - 2, py2 - 2), (18, 24, 38), -1)
            for rx in range(px1 + 12, px2, 14):
                cv2.line(canvas, (rx, py1 + 8), (rx, py2 - 8), (245, 158, 11), 1, cv2.LINE_AA)

        # Layer 6: Hardware Hinges & Locks
        if show_all or "HINGES-LOCKS" in st.session_state.active_layer:
            cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
            hinge_x = x2 - 3
            for hy in [y1 + 90, cy - 20, y2 - 130]:
                cv2.rectangle(canvas, (int(hinge_x), int(hy)), (int(hinge_x) + 12, int(hy) + 40), (245, 158, 11), -1, cv2.LINE_AA)
            handle_x = x1 - 3
            cv2.rectangle(canvas, (int(handle_x) - 15, cy - 15), (int(handle_x), cy + 25), (245, 158, 11), -1, cv2.LINE_AA)
            cv2.line(canvas, (int(handle_x) - 15, cy + 5), (int(handle_x) - 35, cy + 5), (245, 158, 11), 3, cv2.LINE_AA)

        # Layer 7: Dimension Callouts
        if show_all or "DIMENSION-CALLOUTS" in st.session_state.active_layer:
            cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
            cv2.line(canvas, (x1, y1 - 35), (x2, y1 - 35), (56, 189, 248), 2, cv2.LINE_AA)
            cv2.putText(canvas, f"{st.session_state.door_width:.3f} m", (cx - 45, y1 - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (56, 189, 248), 2, cv2.LINE_AA)
            
            cv2.line(canvas, (x1 - 40, y1), (x1 - 40, y2), (56, 189, 248), 2, cv2.LINE_AA)
            cv2.putText(canvas, f"{st.session_state.door_height:.3f} m", (x1 - 85, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (56, 189, 248), 2, cv2.LINE_AA)

        # Footer Title Tag
        cv2.putText(canvas, f"[{st.session_state.element_title}]", (x1 + 10, y2 + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2, cv2.LINE_AA)

        st.image(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB), use_container_width=True)
        st.success("✨ Blueprint rendered successfully via AI Command Processor!")

with tab2:
    st.subheader("📂 Bill of Materials (BOM)")
    bom_data = {
        "Item Code": ["ASASCO-FRM-101", "ASASCO-MSH-102", "ASASCO-BAR-103", "ASASCO-PNL-104", "ASASCO-HDW-105"],
        "Component Description": ["Outer Galvanized Frame (Mitered)", "Expanded Security Mesh", f"Horizontal Bars ({st.session_state.bar_count} Pcs) + Center Backbone", "Center Fluted Master Panel", "3 Right Hinges & Left Handle Set"],
        "Dimensions / Specs": [f"{st.session_state.door_width}m x {st.session_state.door_height}m", "16-Gauge", "Standard Spacing", "Vertical Ribbed", "Factory Matched"],
        "Quantity": [1, 1, st.session_state.bar_count + 1, 1, 1]
    }
    st.table(bom_data)

with tab3:
    st.subheader("📥 Professional AutoCAD DXF Export")
    if st.button("📥 Generate & Download .DXF File", type="primary", use_container_width=True):
        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()
        w_mm = st.session_state.door_width * 1000
        h_mm = st.session_state.door_height * 1000
        msp.add_lwpolyline([(0, 0), (w_mm, 0), (w_mm, h_mm), (0, h_mm), (0, 0)], close=True)
        
        dxf_buffer = io.StringIO()
        doc.write(dxf_buffer)
        
        st.download_button(
            label="💾 Download .DXF File",
            data=dxf_buffer.getvalue().encode('utf-8'),
            file_name="asasco_ai_command_door.dxf",
            mime="application/dxf"
        )
        st.success("DXF compiled successfully!")
        
