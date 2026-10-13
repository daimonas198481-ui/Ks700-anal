import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Target & Volume Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Ανάλυση Στόχων & 3D Όγκων Υπεδάφους")
st.markdown("""
Επαγγελματικό σύστημα εντοπισμού και αυτόματης μέτρησης βάθους και μεγέθους στόχων/κενών.
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
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Υψηλού Σήματος", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.80)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.35)))
        
        def classify_target(val):
            if val >= metal_th:
                return 'Μεταλλικός Στόχος'
            elif val <= void_th:
                return 'Κενό / Τούνελ'
            else:
                return 'Υπέδαφος'
                
        df['Target_Type'] = df[amp_col].apply(classify_target)
        
        # Υπολογισμός περιγραφών και μεγεθών αυτόματα
        st.subheader("📋 Αυτόματη Αναφορά Εντοπισμένων Στόχων & Κενών")
        
        metals_df = df[df['Target_Type'] == 'Μεταλλικός Στόχος']
        voids_df = df[df['Target_Type'] == 'Κενό / Τούνελ']
        
        col_rep1, col_rep2 = st.columns(2)
        
        with col_rep1:
            st.markdown("### 🟥 Μεταλλικοί Στόχοι")
            if not metals_df.empty:
                min_depth = metals_df[z_col].min()
                max_depth = metals_df[z_col].max()
                count_m = len(metals_df)
                st.info("""
                * **Κατάσταση:** Εντοπίστηκε ενεργός στόχος/μέταλλο.
                * **Εύρος Βάθους:** Από **{:.2f} m** έως **{:.2f} m**.
                * **Αριθμός Σημείων Καταγραφής:** {} σημεία.
                """.format(min_depth, max_depth, count_m))
            else:
                st.warning("Δεν βρέθηκαν μεταλλικοί στόχοι με το τρέχον κατώφλι. Χαμηλώστε το κατώφλι στη μπάρα.")
                
        with col_rep2:
            st.markdown("### 🟦 Κενά / Τούνελ")
            if not voids_df.empty:
                min_depth_v = voids_df[z_col].min()
                max_depth_v = voids_df[z_col].max()
                count_v = len(voids_df)
                st.info("""
                * **Κατάσταση:** Εντοπίστηκε πιθανό κενό / ανωμαλία.
                * **Εύρος Βάθους:** Από **{:.2f} m** έως **{:.2f} m**.
                * **Αριθμός Σημείων Καταγραφής:** {} σημεία.
                """.format(min_depth_v, max_depth_v, count_v))
            else:
                st.warning("Δεν βρέθηκαν κενά με το τρέχον κατώφλι.")

        # 3D Model
        st.subheader("🌐 3D Απεικόνιση Όγκων Υπεδάφους")
        fig = go.Figure()
        
        subsoil = df[df['Target_Type'] == 'Υπέδαφος']
        if not subsoil.empty:
            fig.add_trace(go.Scatter3d(
                x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                mode='markers', name='Υπέδαφος',
                marker=dict(size=2, color='tan', opacity=0.1, symbol='square')
            ))
            
        if not voids_df.empty:
            fig.add_trace(go.Scatter3d(
                x=voids_df[x_col], y=voids_df[y_col], z=voids_df[z_col],
                mode='markers', name='Κενό / Τούνελ',
                marker=dict(size=7, color='blue', opacity=0.95, symbol='square')
            ))
            
        if not metals_df.empty:
            fig.add_trace(go.Scatter3d(
                x=metals_df[x_col], y=metals_df[y_col], z=metals_df[z_col],
                mode='markers', name='Μεταλλικός Στόχος',
                marker=dict(size=9, color='red', opacity=1.0, symbol='diamond')
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
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας.")
