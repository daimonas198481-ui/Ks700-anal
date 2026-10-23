import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Strict Rules Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Αυτόματος Αναλυτής Υπεδάφους (Αυστηρά Κριτήρια)")
st.markdown("""
* **Φίλτρο Επιφανείας KS-700:** Αυτόματη απόρριψη των πρώτων **50 εκατοστών ($Z < 0.50\text{m}$)** για εξάλειψη του θορύβου επαφής της κεραίας.
* **Κανόνες Ταξινόμησης:** 
  * 🟦 **Κενά / Τούνελ:** Amplitude από **0 έως 40**.
  * 🟥 **Μεταλλικοί Στόχοι:** Amplitude **> 200**.
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
        
        # 1. Αυστηρό φίλτρο: Απόρριψη πρώτων 50 εκατοστών (Z < 0.50)
        df_filtered = df[df[z_col] >= 0.50].copy()
        
        if df_filtered.empty:
            st.warning("Προσοχή: Μετά την απόρριψη των πρώτων 50 εκατοστών (Z < 0.5m), δεν έμειναν δεδομένα στο αρχείο!")
        else:
            # 2. Ταξινόμηση βάσει των ακριβών ορίων
            def strict_classification(val):
                if val > 200:
                    return 'Μεταλλικός Στόχος'
                elif 0 <= val <= 40:
                    return 'Κενό / Τούνελ'
                else:
                    return 'Υπέδαφος / Βράχος'
                    
            df_filtered['Target_Type'] = df_filtered[amp_col].apply(strict_classification)
            
            st.markdown("---")
            st.subheader("📋 Αυτόματη Έκθεση Εντοπισμού & Θέσης στον Καννάβο")
            
            metals = df_filtered[df_filtered['Target_Type'] == 'Μεταλλικός Στόχος']
            voids = df_filtered[df_filtered['Target_Type'] == 'Κενό / Τούνελ']
            
            col_rep1, col_rep2 = st.columns(2)
            
            with col_rep1:
                st.markdown("### 🟥 Μεταλλικοί Στόχοι (Amplitude > 200)")
                if not metals.empty:
                    m_min_z = metals[z_col].min()
                    m_max_z = metals[z_col].max()
                    m_size_x = metals[x_col].max() - metals[x_col].min()
                    m_size_y = metals[y_col].max() - metals[y_col].min()
                    m_cx = (metals[x_col].min() + metals[x_col].max()) / 2
                    m_cy = (metals[y_col].min() + metals[y_col].max()) / 2
                    
                    st.error(f"""
                    * **Κατάσταση:** Εντοπίστηκε ισχυρή μεταλλική αντανάκλαση.
                    * **Εύρος Βάθους (Z):** Από **{m_min_z:.2f} m** έως **{m_max_z:.2f} m**.
                    * **Διαστάσεις (Μέγεθος):** **{m_size_x:.2f} m** (μήκος X) × **{m_size_y:.2f} m** (πλάτος Y).
                    * **Θέση στον Καννάβο (Κέντρο):** X = **{m_cx:.2f} m**, Y = **{m_cy:.2f} m**.
                    * **Συνολικά σημεία:** {len(metals)}
                    """)
                else:
                    st.info("Δεν εντοπίστηκαν μεταλλικοί στόχοι με τιμή > 200 στα καθαρά δεδομένα (> 0.5m).")
                    
            with col_rep2:
                st.markdown("### 🟦 Κενά / Τούνελ (Amplitude 0 - 40)")
                if not voids.empty:
                    v_min_z = voids[z_col].min()
                    v_max_z = voids[z_col].max()
                    v_size_x = voids[x_col].max() - voids[x_col].min()
                    v_size_y = voids[y_col].max() - voids[y_col].min()
                    v_cx = (voids[x_col].min() + voids[x_col].max()) / 2
                    v_cy = (voids[y_col].min() + voids[y_col].max()) / 2
                    
                    st.info(f"""
                    * **Κατάσταση:** Εντοπίστηκε ζώνη κενότητας / τούνελ.
                    * **Εύρος Βάθους (Z):** Από **{v_min_z:.2f} m** έως **{v_max_z:.2f} m**.
                    * **Διαστάσεις (Μέγεθος):** **{v_size_x:.2f} m** (μήκος X) × **{v_size_y:.2f} m** (πλάτος Y).
                    * **Θέση στον Καννάβο (Κέντρο):** X = **{v_cx:.2f} m**, Y = **{v_cy:.2f} m**.
                    * **Συνολικά σημεία:** {len(voids)}
                    """)
                else:
                    st.info("Δεν εντοπίστηκαν κενά με τιμή 0-40 στα καθαρά δεδομένα (> 0.5m).")

            st.markdown("---")
            st.subheader("🌐 Τρισδιάστατη Οπτικοποίηση Στόχων & Κενών")
            
            fig = go.Figure()
            
            # Subsoil background
            subsoil = df_filtered[df_filtered['Target_Type'] == 'Υπέδαφος / Βράχος']
            if not subsoil.empty:
                fig.add_trace(go.Scatter3d(
                    x=subsoil[x_col], y=subsoil[y_col], z=subsoil[z_col],
                    mode='markers', name='Υπέδαφος',
                    marker=dict(size=2, color='lightgray', opacity=0.15, symbol='square')
                ))
                
            # Voids
            if not voids.empty:
                fig.add_trace(go.Scatter3d(
                    x=voids[x_col], y=voids[y_col], z=voids[z_col],
                    mode='markers', name='Κενό / Τούνελ (0-40)',
                    marker=dict(size=6, color='blue', opacity=0.9, symbol='square')
                ))
                
            # Metals
            if not metals.empty:
                fig.add_trace(go.Scatter3d(
                    x=metals[x_col], y=metals[y_col], z=metals[z_col],
                    mode='markers', name='Μεταλλικός Στόχος (>200)',
                    marker=dict(size=8, color='red', opacity=1.0, symbol='diamond')
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

            st.subheader("📊 Κατακόρυφη Τομή (Βάθος vs Θέση X)")
            slice_fig = go.Figure()
            slice_fig.add_trace(go.Scatter(
                x=df_filtered[x_col], y=df_filtered[z_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df_filtered[amp_col],
                    colorscale='Jet',
                    showscale=True,
                    colorbar=dict(title="Amplitude")
                ),
                text=df_filtered['Target_Type']
            ))
            slice_fig.update_layout(
                xaxis_title="Οριζόντια Θέση X (m)",
                yaxis_title="Βάθος Z (m)",
                yaxis=dict(autorange='reversed'),
                height=450,
                title="Τομογραφία (Αποκοπή < 0.5m)"
            )
            st.plotly_chart(slice_fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας αρχείου: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να ξεκινήσει η αυτόματη ανάλυση.")
