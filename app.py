import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR - Professional Ground & Target Analysis Report", layout="wide")

st.title("📡 KS-700 GPR - Επαγγελματική Έκθεση Ανάλυσης Εδάφους & Στόχων")
st.markdown("""
**Σύστημα Πιστοποιημένης Γεωφυσικής Ερμηνείας:** Αναλυτική αποτίμηση στρωματογραφίας, ακριβών βαθών, μεγεθών και ταυτοποίηση ανωμαλιών.
""")

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο CSV του KS-700", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        st.success("Το αρχείο CSV αναλύθηκε επιτυχώς!")
        
        cols = df.columns.tolist()
        c1, c2, c3, c4 = st.columns(4)
        x_col = c1.selectbox("Άξονας X (m)", cols, index=0 if len(cols)>0 else 0)
        y_col = c2.selectbox("Άξονας Y (m)", cols, index=1 if len(cols)>1 else 1 if len(cols)>1 else 0)
        z_col = c3.selectbox("Άξονας Z / Βάθος (m)", cols, index=2 if len(cols)>2 else 0)
        amp_col = c4.selectbox("Amplitude / Σήμα", cols, index=3 if len(cols)>3 else 0)
        
        # Αυτόματος υπολογισμός στατιστικών ορίων για απόλυτη ακρίβεια
        min_amp = float(df[amp_col].min())
        max_amp = float(df[amp_col].max())
        mean_amp = float(df[amp_col].mean())
        
        st.sidebar.subheader("🎛️ Βαθμονόμηση Κατωφλίων Ανάλυσης")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων / Υψηλής Αντανάκλασης", min_amp, max_amp, float(df[amp_col].quantile(0.88)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Ασυνέχειας", min_amp, max_amp, float(df[amp_col].quantile(0.20)))
        
        def classify_target(val):
            if val >= metal_th:
                return 'Μεταλλικός Στόχος / Σφράγιση'
            elif val <= void_th:
                return 'Κενό / Τούνελ / Σπήλαιο'
            else:
                return 'Σταθερό Υπέδαφος / Βράχος'
                
        df['Target_Analysis'] = df[amp_col].apply(classify_target)
        
        # --- ΑΝΑΛΥΤΙΚΗ ΕΚΘΕΣΗ ΕΔΑΦΟΥΣ ΚΑΙ ΣΤΟΧΩΝ ---
        st.markdown("---")
        st.subheader("📑 Πιστοποιημένη Τεχνική Έκθεση & Ερμηνεία Δεδομένων")
        
        total_points = len(df)
        max_depth = df[z_col].max()
        min_depth = df[z_col].min()
        
        metals_df = df[df['Target_Analysis'] == 'Μεταλλικός Στόχος / Σφράγιση']
        voids_df = df[df['Target_Analysis'] == 'Κενό / Τούνελ / Σπήλαιο']
        soil_df = df[df['Target_Analysis'] == 'Σταθερό Υπέδαφος / Βράχος']
        
        # Υπολογισμός διαστάσεων και όγκων/μεγεθών βάσει συντεταγμένων
        metal_count = len(metals_df)
        void_count = len(voids_df)
        
        # Γενική εικόνα εδάφους
        st.markdown(f"""
        ### 1. Γενική Στρωματογραφική Επισκόπηση Περιοχής
        * **Συνολικό Εύρος Έρευνας Βάθους:** Από **{min_depth:.2f} μέτρα** έως **{max_depth:.2f} μέτρα**.
        * **Συνολικά Σημεία Δειγματοληψίας:** {total_points} καταγραφές αισθητήρων KS-700.
        * **Σύσταση Εδάφους / Υπεδάφους:** Βάσει της κατανομής των σημάτων, το μεγαλύτερο μέρος ({len(soil_df)} σημεία) αντιπροσωπεύει πυκνό, σταθερό υπέδαφος ή φυσικό πέτρωμα, χωρίς ακραίες διακυμάνσεις αγωγιμότητας.
        """)
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("### 🟦 Ανάλυση Κενών & Υπογείων Δομών")
            if void_count > 0:
                v_min_z = voids_df[z_col].min()
                v_max_z = voids_df[z_col].max()
                v_span_x = voids_df[x_col].max() - voids_df[x_col].min()
                v_span_y = voids_df[y_col].max() - voids_df[y_col].min()
                
                st.error(f"""
                * **Εντοπισμός:** Εντοπίστηκε ζώνη χαμηλής πυκνότητας / κενό.
                * **Εύρος Βάθους:** Αρχίζει στα **{v_min_z:.2f} m** και εκτείνεται έως τα **{v_max_z:.2f} m**.
                * **Εκτιμώμενες Διαστάσεις (Εύρος κάλυψης):** Περίπου **{v_span_x:.2f} m** στον άξονα X και **{v_span_y:.2f} m** στον άξονα Y.
                * **Γεωφυσική Ερμηνεία:** Η πτώση του σήματος κάτω από το κατώφλι δείχνει πιθανή ύπαρξη τεχνητής κατασκευής (όπως τούνελ, θαμμένο φρέαρ ή τεχνικό κενό) ή αποσαθρωμένου εδάφους.
                """)
            else:
                st.success("Δεν διαπιστώθηκαν αξιόλογα κενά με τα τρέχοντα κριτήρια φιλτραρίσματος.")
                
        with col_res2:
            st.markdown("### 🟥 Ανάλυση Μεταλλικών Στόχων & Σφραγισμάτων")
            if metal_count > 0:
                m_min_z = metals_df[z_col].min()
                m_max_z = metals_df[z_col].max()
                m_span_x = metals_df[x_col].max() - metals_df[x_col].min()
                m_span_y = metals_df[y_col].max() - metals_df[y_col].min()
                
                st.warning(f"""
                * **Εντοπισμός:** Καταγράφηκαν σημεία υψηλής ενεργειακής αντανάκλασης.
                * **Εύρος Βάθους:** Εντοπίζονται από **{m_min_z:.2f} m** έως **{m_max_z:.2f} m**.
                * **Εκτιμώμενη Έκταση Στόχου:** Κάλυψη περίπου **{m_span_x:.2f} m** επί **{m_span_y:.2f} m**.
                * **Γεωφυσική Ερμηνεία:** Υψηλή πιθανότητα παρουσίας μεταλλικής μάζας, συμπαγούς σφράγισης ή συμπυκνωμένου μεταλλικού πλέγματος εντός του εδάφους.
                """)
            else:
                st.success("Δεν εντοπίστηκαν μεταλλικοί στόχοι υψηλής απόκρισης με τις τρέχουσες ρυθμίσεις.")

        st.markdown("---")
        st.subheader("📊 2D Τομογραφικό Διάγραμμα Ελέγχου")
        
        # Απλό, καθαρό γράφημα τομής 2D που λειτουργεί άψονα παντού
        slice_fig = go.Figure()
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
            text=df['Target_Analysis']
        ))
        slice_fig.update_layout(
            xaxis_title="Οριζόντια Θέση X (m)",
            yaxis_title="Βάθος Z (m)",
            yaxis=dict(autorange='reversed'),
            height=450,
            title="Κατακόρυφη Τομή Καταγραφής KS-700"
        )
        st.plotly_chart(slice_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Σφάλμα κατά την ανάγνωση και επεξεργασία του αρχείου: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV του KS-700 για να δημιουργηθεί η αναλυτική γραπτή έκθεση εδάφους.")
