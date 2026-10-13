import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

st.set_page_config(page_title="KS-700 GPR - True Voxel Grid Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Πραγματική 3D Ογκομετρική Ανάλυση (Voxler Grid)")
st.markdown("""
Επαγγελματικό σύστημα τρισδιάστατης παρεμβολής υπεδάφους:
* 🟦 **Συμπαγή Κενά / Τούνελ / Φρέατα** (Ενιαίοι όγκοι)
* 🟥 **Μεταλλικοί Στόχοι / Σφραγίσματα** (Υψηλές εντάσεις)
""")

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο CSV του KS-700", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success("Το αρχείο φορτώθηκε επιτυχώς!")
        
        cols = df.columns.tolist()
        c1, c2, c3, c4 = st.columns(4)
        x_col = c1.selectbox("Άξονας X (m)", cols, index=0 if len(cols)>0 else 0)
        y_col = c2.selectbox("Άξονας Y (m)", cols, index=1 if len(cols)>1 else 1 if len(cols)>1 else 0)
        z_col = c3.selectbox("Άξονας Z / Βάθος (m)", cols, index=2 if len(cols)>2 else 0)
        amp_col = c4.selectbox("Amplitude / Σήμα", cols, index=3 if len(cols)>3 else 0)
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Παρεμβολής & Όγκων")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.88)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.25)))
        
        # Δημιουργία πυκνού τρισδιάστατου πλέγματος (Interpolation Grid)
        res = st.sidebar.slider("Ανάλυση Πλέγματος (Grid Resolution)", 15, 45, 25)
        
        xi = np.linspace(df[x_col].min(), df[x_col].max(), res)
        yi = np.linspace(df[y_col].min(), df[y_col].max(), res)
        zi = np.linspace(df[z_col].min(), df[z_col].max(), res)
        XI, YI, ZI = np.meshgrid(xi, yi, zi, indexing='ij')
        
        points = df[[x_col, y_col, z_col]].values
        values = df[amp_col].values
        
        # Υπολογισμός τιμών στον ενδιάμεσο τρισδιάστατο χώρο
        VI = griddata(points, values, (XI, YI, ZI), method='linear', fill_value=np.nan)
        
        st.subheader("🌐 3D Ενιαίος Ογκομετρικός Σχηματισμός")
        
        fig = go.Figure()
        
        # 1. Κενά / Τούνελ ως συμπαγείς Isosurface όγκοι (Μπλε)
        void_mask = (VI <= void_th) & (~np.isnan(VI))
        if np.any(void_mask):
            fig.add_trace(go.Isosurface(
                x=XI[void_mask], y=YI[void_mask], z=ZI[void_mask],
                value=VI[void_mask],
                isomin=float(df[amp_col].min()),
                isomax=float(void_th),
                surface_count=2,
                colorscale='Blues',
                opacity=0.85,
                name='Συμπαγές Κενό / Τούνελ'
            ))
            
        # 2. Μεταλλικοί στόχοι ως συμπαγείς Isosurface όγκοι (Κόκκινοι)
        metal_mask = (VI >= metal_th) & (~np.isnan(VI))
        if np.any(metal_mask):
            fig.add_trace(go.Isosurface(
                x=XI[metal_mask], y=YI[metal_mask], z=ZI[metal_mask],
                value=VI[metal_mask],
                isomin=float(metal_th),
                isomax=float(df[amp_col].max()),
                surface_count=2,
                colorscale='Reds',
                opacity=0.9,
                name='Μεταλλικός Στόχος'
            ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed') # Σωστή φορά βάθους GPR
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2D Τομή
        st.subheader("📊 Κατακόρυφη Τομή & Στρωματογραφία")
        slice_fig = go.Figure()
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=0, y1=1.5,
                            fillcolor="#b85d38", opacity=0.4, layer="below", line_width=0)
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=1.5, y1=df[z_col].max(),
                            fillcolor="#d2b48c", opacity=0.3, layer="below", line_width=0)
        
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
