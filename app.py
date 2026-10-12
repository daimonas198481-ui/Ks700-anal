import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Professional 3D Solid Model Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Προηγμένο Μοντέλο Συμπαγών Όγκων & Στρωμάτων")
st.markdown("""
Επαγγελματική απεικόνιση τρισδιάστατου μοντέλου με:
* 🟫 **Στρώματα Εδάφους:** Κοκκινόχωμα & Σταθερό Υπέδαφος
* 🟦 **Συμπαγή Τούνελ / Κενά:** Ογκομετρική σύνδεση & κυλινδρική μορφή
* 🟥 **Στόχοι & Μέταλλα:** Γεωμετρικοί όγκοι με γραμμές σύνδεσης
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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Γεωμετρικών Όγκων")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Σφραγισμάτων", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.90)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.20)))
        
        def classify_target(val):
            if val >= metal_th:
                return 'Μέταλλο / Στόχος'
            elif val <= void_th:
                return 'Τούνελ / Κενό'
            else:
                return 'Υπέδαφος'
                
        df['Target_Type'] = df[amp_col].apply(classify_target)
        
        # 3D Solid Model Visualization
        st.subheader("🌐 Τρισδιάστατο Μοντέλο Υπεδάφους (Συμπαγείς Όγκοι & Στρώματα)")
        
        fig = go.Figure()
        
        # 1. Background Subsoil Layer
        subsoil = df[df['Target_Type'] == 'Υπέδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Σταθερό Υπέδαφος / Βράχος',
                marker=dict(size=3, color='tan', opacity=0.15, symbol='square')
            ))
            
        # 2. Solid Tunnels / Voids (Cylindrical / Block cluster representation)
        voids = df[df['Target_Type'] == 'Τούνελ / Κενό']
        if not voids.empty:
            fig.add_trace(go.Scatter3d(
                x=voids[x_col], y=voids[y_col], z=voids[z_col],
                mode='markers', name='Τούνελ / Κενό (Συμπαγής Όγκος)',
                marker=dict(size=8, color='blue', opacity=0.9, symbol='square')
            ))
            
        # 3. Metals / Sealed structures
        metals = df[df['Target_Type'] == 'Μέταλλο / Στόχος']
        if not metals.empty:
            fig.add_trace(go.Scatter3d(
                x=metals[x_col], y=metals[y_col], z=metals[z_col],
                mode='markers', name='Μεταλλικός Στόχος / Σφράγιση',
                marker=dict(size=10, color='red', opacity=1.0, symbol='diamond')
            ))
            
            # Add connecting dashed line between first metal and first void if both exist
            if not voids.empty:
                m_x, m_y, m_z = metals[x_col].iloc[0], metals[y_col].iloc[0], metals[z_col].iloc[0]
                v_x, v_y, v_z = voids[x_col].iloc[0], voids[y_col].iloc[0], voids[z_col].iloc[0]
                fig.add_trace(go.Scatter3d(
                    x=[m_x, v_x], y=[m_y, v_y], z=[m_z, v_z],
                    mode='lines', name='Απόσταση Στόχου - Κενού',
                    line=dict(color='black', width=4, dash='dash')
                ))

        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed')
            ),
            height=750,
            margin=dict(r=0, b=0, l=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2D Cross-Section Stratigraphy View
        st.subheader("📊 Κατακόρυφη Τομή Εδάφους & Στρατιγραφίας")
        slice_fig = go.Figure()
        
        # Stratigraphy Rectangles
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=0, y1=2,
                            fillcolor="#b85d38", opacity=0.5, layer="below", line_width=0, name="Κοκκινόχωμα")
        slice_fig.add_shape(type="rect", x0=df[x_col].min(), x1=df[x_col].max(), y0=2, y1=df[z_col].max(),
                            fillcolor="#d2b48c", opacity=0.4, layer="below", line_width=0, name="Υπέδαφος")
        
        slice_fig.add_trace(go.Scatter(
            x=df[x_col], y=df[z_col],
            mode='markers',
            marker=dict(
                size=8,
                color=df[amp_col],
                colorscale='Plasma',
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
            title="Τομή Στρατιγραφίας & Εντοπισμού"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να δημιουργηθεί το τρισδιάστατο μοντέλο.")
