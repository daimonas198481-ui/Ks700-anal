import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - 3D Voxel & Isosurface Analyzer", layout="wide")

st.title("📡 KS-700 GPR - 3D Voxel & Isosurface Analyzer (Voxler Style)")
st.markdown("""
Επαγγελματική 3D ογκομετρική ανάλυση τύπου **Voxler**:
* 🟦 **Μπλε / Κενά / Φρέατα / Τούνελ:** Συνεχείς συμπαγείς όγκοι βάθους
* 🟥 **Κόκκινα / Στόχοι:** Σημεία υψηλής αντανάκλασης & μέταλλα
* 🟫 **Υπέδαφος:** Διαφανές πλέγμα αναφοράς
""")

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο CSV του KS-700 (π.χ. KS-700 data)", type=["csv", "txt"])

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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Isosurface & Voxel")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Στόχων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.92)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ / Φρεάτων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.20)))
        
        def classify_voxel(val):
            if val >= metal_th:
                return 'Μέταλλο / Στόχος'
            elif val <= void_th:
                return 'Κενό / Τούνελ / Φρέαρ'
            else:
                return 'Υπέδαφος'
                
        df['Voxel_Class'] = df[amp_col].apply(classify_voxel)
        
        # Metrics summary
        counts = df['Voxel_Class'].value_counts()
        col1, col2, col3 = st.columns(3)
        col1.metric("🟦 Κενά / Τούνελ", counts.get('Κενό / Τούνελ / Φρέαρ', 0))
        col2.metric("🟥 Μεταλλικοί Στόχοι", counts.get('Μέταλλο / Στόχος', 0))
        col3.metric("🟫 Σημεια Υπεδάφους", counts.get('Υπέδαφος', 0))
        
        st.subheader("🌐 3D Voxel & Isosurface Grid (Ογκομετρική Απεικόνιση)")
        
        fig = go.Figure()
        
        # 1. Subsoil background (Low opacity grid)
        subsoil = df[df['Voxel_Class'] == 'Υπέδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Υπέδαφος',
                marker=dict(size=2, color='tan', opacity=0.08, symbol='square')
            ))
            
        # 2. Voids / Tunnels / Shafts (Solid 3D Voxel cluster - Blue)
        voids = df[df['Voxel_Class'] == 'Κενό / Τούνελ / Φρέαρ']
        if not voids.empty:
            fig.add_trace(go.Scatter3d(
                x=voids[x_col], y=voids[y_col], z=voids[z_col],
                mode='markers', name='Κενό / Τούνελ / Φρέαρ (Συμπαγής Όγκος)',
                marker=dict(size=8, color='blue', opacity=0.92, symbol='square')
            ))
            
        # 3. Metals / High reflection targets (Red diamonds)
        metals = df[df['Voxel_Class'] == 'Μέταλλο / Στόχος']
        if not metals.empty:
            fig.add_trace(go.Scatter3d(
                x=metals[x_col], y=metals[y_col], z=metals[z_col],
                mode='markers', name='Μεταλλικός Στόχος',
                marker=dict(size=10, color='red', opacity=1.0, symbol='diamond')
            ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed') # Ensures depth goes downwards like GPR scans
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2D Depth Slice & Amplitude Profile
        st.subheader("📊 Κατακόρυφη Τομή & Κατανομή Σήματος (Depth Slice)")
        
        slice_fig = go.Figure()
        slice_fig.add_trace(go.Scatter(
            x=df[x_col], y=df[z_col],
            mode='markers',
            marker=dict(
                size=9,
                color=df[amp_col],
                colorscale='Jet',
                showscale=True,
                colorbar=dict(title="Amplitude")
            ),
            text=df['Voxel_Class']
        ))
        
        slice_fig.update_layout(
            xaxis_title="Οριζόντια Θέση X (m)",
            yaxis_title="Βάθος Z (m)",
            yaxis=dict(autorange='reversed'),
            height=500,
            title="Τομογραφικό Προφίλ Βάθους & Εντάσεων Σήματος"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας αρχείου: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να δείτε την 3D Voxel ανάλυση.")
