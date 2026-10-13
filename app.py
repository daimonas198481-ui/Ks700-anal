import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

st.set_page_config(page_title="KS-700 GPR - Voxler True 3D Solid Volume", layout="wide")

st.title("📡 KS-700 GPR - 3D True Voxel & Isosurface Grid (Voxler Engine)")
st.markdown("""
Πραγματική ογκομετρική απεικόνιση υπεδάφους με ενιαία σύνδεση δεδομένων (Voxler Style):
* 🟦 **Συμπαγή Κενά / Τούνελ:** Ενιαίοι τρισδιάστατοι όγκοι βάθους
* 🟥 **Μεταλλικοί Στόχοι:** Σημεία υψηλής αντανάκλασης
* 🟫 **Υπέδαφος:** Πλέγμα αναφοράς
""")

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο CSV του KS-700", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success("Το αρχείο CSV φορτώθηκε επιτυχώς!")
        
        cols = df.columns.tolist()
        c1, c2, c3, c4 = st.columns(4)
        x_col = c1.selectbox("Άξονας X (m)", cols, index=0 if len(cols)>0 else 0)
        y_col = c2.selectbox("Άξονας Y (m)", cols, index=1 if len(cols)>1 else 1 if len(cols)>1 else 0)
        z_col = c3.selectbox("Άξονας Z / Βάθος (m)", cols, index=2 if len(cols)>2 else 0)
        amp_col = c4.selectbox("Amplitude / Σήμα", cols, index=3 if len(cols)>3 else 0)
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις 3D Voxel Grid")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Στόχων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.88)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.25)))
        
        # Δημιουργία πυκνού 3D πλέγματος (Interpolation για ενιαίους όγκους)
        grid_res = st.sidebar.slider("Ανάλυση Πλέγματος (Grid Resolution)", 15, 40, 25)
        
        xi = np.linspace(df[x_col].min(), df[x_col].max(), grid_res)
        yi = np.linspace(df[y_col].min(), df[y_col].max(), grid_res)
        zi = np.linspace(df[z_col].min(), df[z_col].max(), grid_res)
        XI, YI, ZI = np.meshgrid(xi, yi, zi, indexing='ij')
        
        points = df[[x_col, y_col, z_col]].values
        values = df[amp_col].values
        
        # Παρεμβολή τιμών στον ενδιάμεσο χώρο
        VI = griddata(points, values, (XI, YI, ZI), method='linear', fill_value=np.nan)
        
        st.subheader("🌐 3D Ενιαίος Ογκομετρικός Σχηματισμός (Voxler Isosurface)")
        
        fig = go.Figure()
        
        # 1. Εμφάνιση Κενών/Τούνελ ως συμπαγή ισοεπιφάνεια (Isosurface)
        # Δημιουργούμε μάσκα για τα κενά
        void_mask = (VI <= void_th) & (~np.isnan(VI))
        if np.any(void_mask):
            fig.add_trace(go.Isosurface(
                x=XI[void_mask],
                y=YI[void_mask],
                z=ZI[void_mask],
                value=VI[void_mask],
                isomin=float(df[amp_col].min()),
                isomax=float(void_th),
                surface_count=3,
                colorscale='Blues',
                opacity=0.85,
                name='Συμπαγές Κενό / Τούνελ'
            ))
            
        # 2. Εμφάνιση Μετάλλων / Υψηλού σήματος
        metal_mask = (VI >= metal_th) & (~np.isnan(VI))
        if np.any(metal_mask):
            fig.add_trace(go.Isosurface(
                x=XI[metal_mask],
                y=YI[metal_mask],
                z=ZI[metal_mask],
                value=VI[metal_mask],
                isomin=float(metal_th),
                isomax=float(df[amp_col].max()),
                surface_count=2,
                colorscale='Reds',
                opacity=0.95,
                name='Μεταλλικός Στόχος / Σφράγιση'
            ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed') # Σωστή φορά βάθους GPR προς τα κάτω
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Κατακόρυφη Τομή & Στρωματογραφία")
        slice_fig = go.Figure()
        slice_fig.add_trace(go.Scatter(
            x=df[x_col], y=df[z_col],
            mode='markers',
            marker=dict(
                size=8,
                color=df[amp_col],
                colorscale='Jet',
                showscale=True,
                colorbar=dict(title="Amplitude")
            ),
            text=df[amp_col]
        ))
        slice_fig.update_layout(
            xaxis_title="Οριζόντια Θέση X (m)",
            yaxis_title="Βάθος Z (m)",
            yaxis=dict(autorange='reversed'),
            height=500,
            title="Τομογραφικό Προφίλ Βάθους"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας.")
