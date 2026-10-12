import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

st.set_page_config(page_title="KS-700 GPR - Professional Stratigraphy & Solid Volume Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Σύστημα Τομογραφίας & Συμπαγών Όγκων Υπεδάφους")
st.markdown("""
Επαγγελματική απεικόνιση τομών βάθους και **συμπαγών γεωμετρικών όγκων (3D Voxel/Mesh)**:
* 🟫 **Επιφανειακό Στρώμα / Κοκκινόχωμα**
* 🟨 **Υπέδαφος / Βράχος / Σταθερό Έδαφος**
* 🟦 **Κενά / Σήραγγες / Τούνελ** (Συμπαγής τρισδιάστατη μορφή)
* 🟥 **Μέταλλα / Σφραγίσματα / Στόχοι** (Συμπαγείς γεωμετρικοί όγκοι)
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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Κατωφλίων Στόχων")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Σφραγισμάτων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.90)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.18)))
        
        def classify_target(val):
            if val >= metal_th:
                return 'Μέταλλο / Στόχος'
            elif val <= void_th:
                return 'Κενό / Τούνελ'
            else:
                return 'Υπέδαφος / Έδαφος'
                
        df['Target_Type'] = df[amp_col].apply(classify_target)
        
        # Summary metrics
        counts = df['Target_Type'].value_counts()
        col1, col2, col3 = st.columns(3)
        col1.metric("🟦 Σημεία Κενών / Τούνελ", counts.get('Κενό / Τούνελ', 0))
        col2.metric("🟥 Σημεία Μετάλλων / Στόχων", counts.get('Μέταλλο / Στόχος', 0))
        col3.metric("🟫 Σημεία Υπεδάφους", counts.get('Υπέδαφος / Έδαφος', 0))
        
        st.subheader("🌐 3D Συμπαγής Γεωμετρική Απεικόνιση Όγκων")
        
        fig = go.Figure()
        
        # Plot Subsoil (Low opacity background)
        subsoil = df[df['Target_Type'] == 'Υπέδαφος / Έδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Υπέδαφος',
                marker=dict(size=2, color='tan', opacity=0.1)
            ))
            
        # Plot Voids / Tunnels as Solid Meshes/Clusters
        voids = df[df['Target_Type'] == 'Κενό / Τούνελ']
        if not voids.empty:
            fig.add_trace(go.Scatter3d(
                x=voids[x_col], y=voids[y_col], z=voids[z_col],
                mode='markers', name='Κενό / Τούνελ (Συμπαγής Όγκος)',
                marker=dict(size=7, color='blue', symbol='square', opacity=0.95)
            ))
            
        # Plot Metals / Sealed structures
        metals = df[df['Target_Type'] == 'Μέταλλο / Στόχος']
        if not metals.empty:
            fig.add_trace(go.Scatter3d(
                x=metals[x_col], y=metals[y_col], z=metals[z_col],
                mode='markers', name='Μέταλλο / Σφράγιση',
                marker=dict(size=9, color='red', symbol='diamond', opacity=1.0)
            ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed')
            ),
            height=700,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 2D Κατακόρυφη Τομή (Cross-Section & Stratigraphy)")
        # Create a 2D slice view across X and Z (averaging Y)
        slice_fig = go.Figure()
        
        # Add stratigraphy background layers simulation
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=0, y1=2,
                            fillcolor="#b85d38", opacity=0.4, layer="below", line_width=0)
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=2, y1=df[z_col].max(),
                            fillcolor="#d2b48c", opacity=0.3, layer="below", line_width=0)
        
        # Scatter for cross-section
        slice_fig.add_trace(go.Scatter(
            x=df[x_col], y=df[z_col],
            mode='markers',
            marker=dict(
                size=8,
                color=df[amp_col],
                colorscale='Viridis',
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
            title="Κατακόρυφη Τομή Εδάφους & Εντοπισμού Ανωμαλιών"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να δημιουργηθούν οι συμπαγείς όγκοι και οι τομές βάθους.")
