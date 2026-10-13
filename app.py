import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Strict Expert Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Αυτόματος Αναλυτής με Σταθερά Όρια & Φίλτρο 0.5m")
st.markdown("""
* **Φίλτρο Επιφανείας KS-700:** Αυτόματη απόρριψη των πρώτων 0.50 μέτρων (αποφυγή θορύβου επαφής κεραίας).
* **Κανόνες Ταξινόμησης:** Κενά (Amplitude 0 - 40) | Μέταλλα (Amplitude > 200).
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
        
        # --- ΑΥΣΤΗΡΟ ΦΙΛΤΡΟ KS-700: Απόρριψη πρώτων 50 εκατοστών (Z < 0.50) ---
        df_filtered = df[df[z_col] >= 0.50].copy()
        
        if df_filtered.empty:
            st.warning("Προσοχή: Μετά την απόρριψη των πρώτων 50 εκατοστών (Z < 0.5m), δεν έμειναν δεδομένα στο αρχείο σου!")
        else:
            # --- ΑΥΣΤΗΡΗ ΤΑΞΙΝΟΜΗΣΗ ΒΑΣΕΙ ΤΩΝ ΟΡΙΩΝ ΠΟΥ ΖΗΤΗΣΑΤΕ ---
            def strict_classify(val):
                if val > 200:
                    return 'Μεταλλικός Στόχος'
                elif 0 <= val <= 40:
                    return 'Κενό / Τούνελ'
                else:
                    return 'Υπέδαφος / Βράχος'
                    
            df_filtered['Strict_Analysis'] = df_filtered[amp_col].apply(strict_classify)
            
            st.markdown("---")
            st.subheader("📋 Αναλυτική Έκθεση Εντοπισμού (Καθαρά Δεδομένα > 0.5m)")
            
            metals = df_filtered[df_filtered['Strict_Analysis'] == 'Μεταλλικός Στόχος']
            voids = df_filtered[df_filtered['Strict_Analysis'] == 'Κενό / Τούνελ']
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("### 🟥 Μεταλλικοί Στόχοι (Amplitude > 200)")
                if not metals.empty:
                    m_min_z = metals[z_col].min()
                    m_max_z = metals[z_col].max()
                    m_size_x = metals[x_col].max() - metals[x_col].min()
                    m_size_y = metals[y_col].max() - metals[y_col].min()
                    m_x_pos = (metals[x_col].min() + metals[x_col].max()) / 2
                    m_y_pos = (metals[y_col].min() + metals[y_col].max()) / 2
                    
                    st.error(f"""
                    * **Κατάσταση:** Εντοπίστηκε μέταλλο / υψηλή αντανάκλαση.
                    * **Βάθος Εντοπισμού:** Από **{m_min_z:.2f} m** έως **{m_max_z:.2f} m**.
                    * **Μέγεθος / Κάλυψη:** **{m_size_x:.2f} m** μήκος επί **{m_size_y:.2f} m** πλάτος.
                    * **Θέση στον Καννάβο (Κέντρο):** X = **{m_x_pos:.2f} m**, Y = **{m_y_pos:.2f} m**.
                    """)
                else:
                    st.info("Δεν βρέθηκαν σημεία με σήμα > 200 μετά τα 0.5m.")
                    
            with col_b:
                st.markdown("### 🟦 Κενά / Τούνελ (Amplitude 0 - 40)")
                if not voids.empty:
                    v_min_z = voids[z_col].min()
                    v_max_z = voids[z_col].max()
                    v_size_x = voids[x_col].max() - voids[x_col].min()
                    v_size_y = voids[y_col].max() - voids[y_col].min()
                    v_x_pos = (voids[x_col].min() + voids[x_col].max()) / 2
                    v_y_pos = (voids[y_col].min() + voids[y_col].max()) / 2
                    
                    st.info(f"""
                    * **Κατάσταση:** Εντοπίστηκε κενό / τούνελ.
                    * **Βάθος Εντοπισμού:** Από **{v_min_z:.2f} m** έως **{v_max_z:.2f} m**.
                    * **Μέγεθος / Κάλυψη:** **{v_size_x:.2f} m** μήκος επί **{v_size_y:.2f} m** πλάτος.
                    * **Θέση στον Καννάβο (Κέντρο):** X = **{v_x_pos:.2f} m**, Y = **{v_y_pos:.2f} m**.
                    """)
                else:
                    st.info("Δεν βρέθηκαν σημεία με σήμα 0-40 μετά τα 0.5m.")

            st.markdown("---")
            st.subheader("📊 Κατακόρυφη Τομή (Χωρίς Επιφανειακό Θόρυβο)")
            
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
                text=df_filtered['Strict_Analysis']
            ))
            slice_fig.update_layout(
                xaxis_title="Οριζόντια Θέση X (m)",
                yaxis_title="Βάθος Z (m)",
                yaxis=dict(autorange='reversed'),
                height=450,
                title="Τομογραφικό Προφίλ (Αποκοπή < 0.5m)"
            )
            st.plotly_chart(slice_fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας.")
