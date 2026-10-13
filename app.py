import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Auto Expert Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Αυτόματος Επαγγελματικός Αναλυτής Υπεδάφους")
st.markdown("""
**Σύστημα Αυτόματης Ανίχνευσης & Ερμηνείας KS-700:** 
* *Ενσωματωμένο φίλτρο αποκοπής επιφανειακού θορύβου κεραίας (Ground-Contact Noise Filter).*
* *Αυτόματος υπολογισμός βάθους, γεωμετρικών διαστάσεων και θέσης στον κάνναβο.*
""")

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο CSV του KS-700", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success("Το αρχείο CSV φορτώθηκε και διαβάστηκε επιτυχώς!")
        
        cols = df.columns.tolist()
        c1, c2, c3, c4 = st.columns(4)
        x_col = c1.selectbox("Άξονας X (m)", cols, index=0 if len(cols)>0 else 0)
        y_col = c2.selectbox("Άξονας Y (m)", cols, index=1 if len(cols)>1 else 1 if len(cols)>1 else 0)
        z_col = c3.selectbox("Άξονας Z / Βάθος (m)", cols, index=2 if len(cols)>2 else 0)
        amp_col = c4.selectbox("Amplitude / Σήμα", cols, index=3 if len(cols)>3 else 0)
        
        # --- ΚΡΙΣΙΜΟ ΦΙΛΤΡΟ KS-700 ---
        # Λόγω της επαφής της κεραίας με το έδαφος στην αρχή (Z κοντά στο 0), 
        # οι μονάδες είναι υψηλές χωρίς να υπάρχει μέταλλο. 
        # Δίνουμε επιλογή αυτόματου φιλτραρίσματος επιφανειακού θορύβου (π.χ. κάτω από 0.15m).
        st.sidebar.subheader("⚙️ Ρυθμίσεις Φίλτρου KS-700")
        ignore_surface = st.sidebar.checkbox("Αυτόματη απόρριψη επιφανειακού θορύβου επαφής (Z < 0.15m)", value=True)
        
        df_filtered = df.copy()
        if ignore_surface:
            # Φιλτράρισμα θορύβου επαφής στην κορυφή
            df_filtered = df_filtered[df_filtered[z_col] >= 0.15]
            
        if df_filtered.empty:
            st.warning("Μετά την εφαρμογή του φίλτρου επιφανειακού θορύβου, δεν έμειναν δεδομένα. Απενεργοποιήστε το φίλτρο αν το βάθος ξεκινάει από 0.")
        else:
            # Αυτόματος υπολογισμός στατιστικών ορίων από τα καθαρά δεδομένα
            min_amp = float(df_filtered[amp_col].min())
            max_amp = float(df_filtered[amp_col].max())
            
            metal_th = st.sidebar.slider("Αυτόματο Κατώφλι Μετάλλων", min_amp, max_amp, float(df_filtered[amp_col].quantile(0.90)))
            void_th = st.sidebar.slider("Αυτόματο Κατώφλι Κενών", min_amp, max_amp, float(df_filtered[amp_col].quantile(0.15)))
            
            def expert_classify(val):
                if val >= metal_th:
                    return 'Μεταλλικός Στόχος'
                elif val <= void_th:
                    return 'Κενό / Τούνελ'
                else:
                    return 'Υπέδαφος / Βράχος'
                    
            df_filtered['Expert_Analysis'] = df_filtered[amp_col].apply(expert_classify)
            
            # --- ΑΝΑΛΥΤΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ & ΕΝΤΟΠΙΣΜΟΣ ΣΤΟΝ ΚΑΝΝΑΒΟ ---
            st.markdown("---")
            st.subheader("📋 Αυτόματη Τεχνική Έκθεση & Θέση στον Καννάβο")
            
            metals = df_filtered[df_filtered['Expert_Analysis'] == 'Μεταλλικός Στόχος']
            voids = df_filtered[df_filtered['Expert_Analysis'] == 'Κενό / Τούνελ']
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("### 🟥 Εντοπισμός Μεταλλικών Στόχων")
                if not metals.empty:
                    m_min_z = metals[z_col].min()
                    m_max_z = metals[z_col].max()
                    m_size_x = metals[x_col].max() - metals[x_col].min()
                    m_size_y = metals[y_col].max() - metals[y_col].min()
                    m_x_pos = (metals[x_col].min() + metals[x_col].max()) / 2
                    m_y_pos = (metals[y_col].min() + metals[y_col].max()) / 2
                    
                    st.error(f"""
                    * **Κατάσταση:** Εντοπίστηκε ισχυρή μεταλλική αντανάκλαση.
                    * **Βάθος Εντοπισμού:** Από **{m_min_z:.2f} m** έως **{m_max_z:.2f} m**.
                    * **Μέγεθος / Εύρος:** Περίπου **{m_size_x:.2f} m** (μήκος) επί **{m_size_y:.2f} m** (πλάτος).
                    * **Θέση στον Καννάβο (Κέντρο):** Σημείο X = **{m_x_pos:.2f} m**, Y = **{m_y_pos:.2f} m**.
                    * **Ερμηνεία KS-700:** Αποκλείστηκε ο επιφανειακός θόρυβος επαφής· ο στόχος βρίσκεται σε καθαρό υπόγειο στρώμα.
                    """)
                else:
                    st.success("Δεν εντοπίστηκε μεταλλικός στόχος με τα τρέχοντα όρια.")
                    
            with col_b:
                st.markdown("### 🟦 Εντοπισμός Κενών / Τούνελ")
                if not voids.empty:
                    v_min_z = voids[z_col].min()
                    v_max_z = voids[z_col].max()
                    v_size_x = voids[x_col].max() - voids[x_col].min()
                    v_size_y = voids[y_col].max() - voids[y_col].min()
                    v_x_pos = (voids[x_col].min() + voids[x_col].max()) / 2
                    v_y_pos = (voids[y_col].min() + voids[y_col].max()) / 2
                    
                    st.info(f"""
                    * **Κατάσταση:** Εντοπίστηκε ζώνη πτώσης σήματος (Κενό / Τούνελ).
                    * **Βάθος Εντοπισμού:** Αρχίζει στα **{v_min_z:.2f} m** και φτάνει έως τα **{v_max_z:.2f} m**.
                    * **Μέγεθος / Εύρος:** Εκτιμώμενη κάλυψη **{v_size_x:.2f} m** επί **{v_size_y:.2f} m**.
                    * **Θέση στον Καννάβο (Κέντρο):** Σημείο X = **{v_x_pos:.2f} m**, Y = **{v_y_pos:.2f} m**.
                    * **Ερμηνεία KS-700:** Χαρακτηριστική συμπεριφορά υπόγειας ασυνέχειας ή κενής δομής.
                    """)
                else:
                    st.success("Δεν εντοπίστηκε κενό με τα τρέχοντα όρια.")

            st.markdown("---")
            st.subheader("📊 Κατακόρυφη Τομή Ελέγχου")
            
            slice_fig = go.Figure()
            slice_fig.add_trace(go.Scatter(
                x=df_filtered[x_col], y=df_filtered[z_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df_filtered[amp_col],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Amplitude")
                ),
                text=df_filtered['Expert_Analysis']
            ))
            slice_fig.update_layout(
                xaxis_title="Οριζόντια Θέση X (m)",
                yaxis_title="Βάθος Z (m)",
                yaxis=dict(autorange='reversed'),
                height=450,
                title="Κατακόρυφη Τομή KS-700 (Με φίλτρο θορύβου επαφής)"
            )
            st.plotly_chart(slice_fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να ξεκινήσει η αυτόματη ανάλυση.")
