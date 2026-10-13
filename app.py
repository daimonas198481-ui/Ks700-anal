import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Voxler Solid 3D Analyzer", layout="wide")

st.title("📡 KS-700 GPR - 3D Ογκομετρική Ανάλυση Υπεδάφους")
st.markdown("""
Επαγγελματική απεικόνιση 3D όγκων τύπου **Voxler**:
* 🟦 **Συμπαγή Κενά / Τούνελ / Φρέατα**
* 🟥 **Μεταλλικοί Στόχοι / Σφραγίσματα**
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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Κατωφλίων")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων (High Amplitude)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.85)))
        void_th = st.sidebar.slider("Κατώφλι Κενών (Low Amplitude)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.30)))
        
        def classify_target(val):
            if val >= metal_th:
                return 'Μέταλλο / Στόχος'
            elif val <= void_th:
                return 'Κενό / Τούνελ'
            else:
                return 'Υπέδαφος'
                
        df['Target_Type'] = df[amp_col].apply(classify_target)
        
        # 3D Solid Voxel Model
        st.subheader("🌐 3D Ογκομετρικό Μοντέλο (Voxler Style)")
        
        fig = go.Figure()
        
        # 1. Υπέδαφος (διαφανές πλέγμα)
        subsoil = df[df['Target_Type'] == 'Υπέδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Υπέδαφος',
                marker=dict(size=2, color='tan', opacity=0.1, symbol='square')
            ))
            
        # 2. Κενά / Τούνελ (Συμπαγείς μπλε όγκοι)
        voids = df[df['Target_Type'] == 'Κενό / Τούνελ']
        if not voids.empty:
            fig.add_trace(go.Scatter3d(
                x=voids[x_col], y=voids[y_col], z=voids[z_col],
                mode='markers', name='Κενό / Τούνελ (Συμπαγής Όγκος)',
                marker=dict(size=7, color='blue', opacity=0.95, symbol='square')
            ))
            
        # 3. Μεταλλικοί στόχοι (Κόκκινα διαμάντια)
        metals = df[df['Target_Type'] == 'Μέταλλο / Στόχος']
        if not metals.empty:
            fig.add_trace(go.Scatter3d(
                x=metals[x_col], y=metals[y_col], z=metals[z_col],
                mode='markers', name='Μεταλλικός Στόχος',
                marker=dict(size=9, color='red', opacity=1.0, symbol='diamond')
            ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed') # Σωστή φορά βάθους προς τα κάτω
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2D Depth Slice
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
            text=df['Target_Type']
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
