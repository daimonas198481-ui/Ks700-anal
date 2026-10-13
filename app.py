import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Voxler Style 3D Solid Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Σύστημα 3D Ογκομετρικής Ανάλυσης (Voxler Style)")
st.markdown("""
Επαγγελματικό εργαλείο 3D απεικόνισης υπεδάφους τύπου **Voxler**:
* 🟦 **Συμπαγή Κενά / Τούνελ / Φρέατα:** Ογκομετρικοί σχηματισμοί βάθους
* 🟥 **Μεταλλικοί Στόχοι & Σφραγίσματα:** Υψηλή ενεργειακή αντανάκλαση
* 🟫 **Υπέδαφος & Στρώματα:** Πλέγμα αναφοράς βάθους
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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Κατωφλίων Voxler")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Υψηλού Σήματος", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.90)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ / Φρεάτων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.22)))
        
        def classify_voxel(val):
            if val >= metal_th:
                return 'Μέταλλο / Στόχος'
            elif val <= void_th:
                return 'Κενό / Τούνελ / Φρέαρ'
            else:
                return 'Υπέδαφος'
                
        df['Voxel_Type'] = df[amp_col].apply(classify_voxel)
        
        # Μετρήσεις
        counts = df['Voxel_Type'].value_counts()
        col1, col2, col3 = st.columns(3)
        col1.metric("🟦 Σημεία Κενών / Τούνελ", counts.get('Κενό / Τούνελ / Φρέαρ', 0))
        col2.metric("🟥 Σημεία Μετάλλων", counts.get('Μέταλλο / Στόχος', 0))
        col3.metric("🟫 Σημεία Υπεδάφους", counts.get('Υπέδαφος', 0))
        
        st.subheader("🌐 3D Ογκομετρικό Μοντέλο (Voxler Style Isosurface)")
        
        fig = go.Figure()
        
        # 1. Υπέδαφος (Background grid)
        subsoil = df[df['Voxel_Type'] == 'Υπέδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Υπέδαφος',
                marker=dict(size=2, color='tan', opacity=0.06, symbol='square')
            ))
            
        # 2. Κενά / Τούνελ / Φρέατα (Συμπαγείς μπλε όγκοι)
        voids = df[df['Voxel_Type'] == 'Κενό / Τούνελ / Φρέαρ']
        if not voids.empty:
            fig.add_trace(go.Scatter3d(
                x=voids[x_col], y=voids[y_col], z=voids[z_col],
                mode='markers', name='Κενό / Τούνελ / Φρέαρ (Συμπαγής Όγκος)',
                marker=dict(size=8, color='blue', opacity=0.95, symbol='square')
            ))
            
        # 3. Μεταλλικοί στόχοι (Κόκκινα διαμάντια)
        metals = df[df['Voxel_Type'] == 'Μέταλλο / Στόχος']
        if not metals.empty:
            fig.add_trace(go.Scatter3d(
                x=metals[x_col], y=metals[y_col], z=metals[z_col],
                mode='markers', name='Μεταλλικός Στόχος / Σφράγιση',
                marker=dict(size=10, color='red', opacity=1.0, symbol='diamond')
            ))
            
            # Γραμμή σύνδεσης μεταξύ στόχου και κενού (εφόσον υπάρχουν και τα δύο)
            if not voids.empty:
                m_x, m_y, m_z = metals[x_col].iloc[0], metals[y_col].iloc[0], metals[z_col].iloc[0]
                v_x, v_y, v_z = voids[x_col].iloc[0], voids[y_col].iloc[0], voids[z_col].iloc[0]
                fig.add_trace(go.Scatter3d(
                    x=[m_x, v_x], y=[m_y, v_y], z=[m_z, v_z],
                    mode='lines', name='Απόσταση Στόχου - Κενού',
                    line=dict(color='black', width=5, dash='dash')
                ))
            
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed') # Αντιστροφή βάθους για σωστή απεικόνιση GPR προς τα κάτω
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Κατακόρυφη Τομή Εδάφους & Προφίλ Βάθους")
        
        slice_fig = go.Figure()
        # Στρώματα background
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=0, y1=1.5,
                            fillcolor="#b85d38", opacity=0.4, layer="below", line_width=0)
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=1.5, y1=df[z_col].max(),
                            fillcolor="#d2b48c", opacity=0.3, layer="below", line_width=0)
        
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
            text=df['Voxel_Type']
        ))
        
        slice_fig.update_layout(
            xaxis_title="Οριζόντια Θέση X (m)",
            yaxis_title="Βάθος Z (m)",
            yaxis=dict(autorange='reversed'),
            height=500,
            title="Τομογραφικό Προφίλ & Στρωματογραφία Εδάφους"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να ενεργοποιηθεί το 3D ογκομετρικό μοντέλο.")
