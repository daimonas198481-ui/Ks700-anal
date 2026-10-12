import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR Expert System", layout="wide")

st.title("📡 KS-700 GPR Expert System & Knowledge Engine")
st.markdown("""
Ολοκληρωμένη εφαρμογή ανάλυσης, 3D τομογραφίας και αυτόματης ταξινόμησης στόχων για το **KS-700 / KS-750 GPR**, 
ενσωματώνοντας όλη τη βιβλιοθήκη δοκιμών, μεθοδολογιών κανάβου, βιβλιογραφίας και εμπειρικών δεδομένων.
""")

st.sidebar.title("🧭 Πλοήγηση")
page = st.sidebar.radio("Επιλέξτε Ενότητα:", [
    "📊 3D Ανάλυση & Ταξινόμηση", 
    "📚 Βιβλιοθήκη & Γνωσιακή Βάση", 
    "🎯 Μεθοδολογία Κανάβου & Calibration",
    "⚙️ Παράμετροι Εδάφους & Διηλεκτρικά"
])

if page == "📊 3D Ανάλυση & Ταξινόμηση":
    st.header("🌐 3D Τομογραφία & Αυτόματος Εντοπισμός Στόχων")
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
            
            st.sidebar.subheader("🎛️ Κατώφλια Ταξινόμησης Στόχων")
            metal_th = st.sidebar.slider("Κατώφλι Μετάλλων (High Amplitude)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.95)))
            void_th = st.sidebar.slider("Κατώφλι Κενών / Δωματίων (Low/Negative Amp)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.15)))
            
            def classify(val):
                if val >= metal_th:
                    return 'Μέταλλο / Υψηλή Αντανάκλαση'
                elif val <= void_th:
                    return 'Κενό / Τούνελ / Δωμάτιο'
                else:
                    return 'Φυσικό Έδαφος / Υπόβαθρο'
            
            df['Target_Type'] = df[amp_col].apply(classify)
            
            color_map = {
                'Μέταλλο / Υψηλή Αντανάκλαση': 'red',
                'Κενό / Τούνελ / Δωμάτιο': 'blue',
                'Φυσικό Έδαφος / Υπόβαθρο': 'rgba(200, 200, 200, 0.1)'
            }
            
            fig = go.Figure(data=[go.Scatter3d(
                x=df[x_col],
                y=df[y_col],
                z=df[z_col],
                mode='markers',
                marker=dict(
                    size=4,
                    color=df['Target_Type'].map(color_map),
                    opacity=0.8
                ),
                text=df['Target_Type'] + "<br>Amp: " + df[amp_col].astype(str)
            )])
            
            fig.update_layout(
                scene=dict(
                    xaxis_title='X (m)',
                    yaxis_title='Y (m)',
                    zaxis_title='Βάθος Z (m)',
                    zaxis=dict(autorange='reversed')
                ),
                height=650,
                margin=dict(r=0, b=0, l=0, t=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Εντοπισμένοι Στόχοι")
            filtered_df = df[df['Target_Type'] != 'Φυσικό Έδαφος / Υπόβαθρο']
            st.dataframe(filtered_df)
            
        except Exception as e:
            st.error(f"Σφάλμα επεξεργασίας: {e}")

elif page == "📚 Βιβλιοθήκη & Γνωσιακή Βάση":
    st.header("📚 Βιβλιοθήκη & Θεωρητικό Υπόβαθρο KS-700")
    
    st.subheader("📖 Ακαδημαϊκή & Τεχνική Βιβλιογραφία")
    st.markdown("""
    * **Γεωλογία & Περιβάλλον** (Ευθύμιος Λ. Λέκκας): Αρχές στρωματογραφίας, γεωμορφολογίας και δομικής γεωλογίας για ερμηνεία σχισμών και ρηγμάτων.
    * **Εισαγωγή στη Μεταλλευτική Έρευνα** (Κωνσταντίνος Μόδης, Σοφία Σταματάκη): Τεχνικές εντοπισμού μεταλλοφορίας και διαχωρισμού ορυκτών σωμάτων.
    * **Εισαγωγή στη Μηχανική των Πετρωμάτων** (Παύλος Π. Νομικός): Συμπεριφορά βραχωδών σχηματισμών, αστοχίες και ανάλυση υπόγειων void/caverns.
    * **Γεωφυσικές Μεθοδολογίες & GPR** (Ανδρέας Τζάνης): Θεωρία ηλεκτρομαγνητικών κυμάτων, διηλεκτρική σταθερά ($\epsilon_r$) και διάδοση σήματος στο έδαφος.
    """)
    
    st.subheader("🎥 Οδηγίες & Βίντεο KS-700 / KS-750")
    st.markdown("""
    * **Time-Zero Correction & Surface Gain:** Ρύθμιση της αρχικής μηδενικής στάθμης του σήματος για αποφυγή κορεσμού από την επιφάνεια.
    * **Background Removal Filter:** Αφαίρεση του οριζόντιου θορύβου εδάφους για την ανάδειξη κατακόρυφων και τοπικών ανωμαλιών.
    * **FMCW Radar Principles:** Κατανόηση της λειτουργίας συνεχούς κύματος ρυθμιζόμενης συχνότητας (FMCW) του KS-700.
    """)

elif page == "🎯 Μεθοδολογία Κανάβου & Calibration":
    st.header("🎯 Μεθοδολογία Σάρωσης & Calibration (Field Experience)")
    
    st.markdown("""
    ### 📏 Κανόνες Κανάβου & Βηματισμού KS-700
    1. **Μονόδρομη Σάρωση (No Zig-Zag):** Οι επιστροφές γίνονται πάντα στη γραμμή βάσης. Η κίνηση εκτελείται από τον άξονα X προς τον Y.
    2. **Ειδικό Πρωτόκολλο Βηματισμού σε Κενά:** Επιστροφή στην αρχική θέση στο σταθερό έδαφος ανά 3 μέτρα. Εκτέλεση 1 πατήματος στο συμπαγές έδαφος και 3 πατημάτων πάνω από την περιοχή του κενού.
    3. **Grid Step:** Τυπικό πλέγμα 0.5m ή 1.0m ανάλογα με το μέγεθος του επιζητούμενου στόχου (π.χ. πλέγμα 99 σημείων).

    ### 🧪 Βαθμονόμηση (Calibration) από Πραγματικά Test
    * **Θολωτός Λίθινος Χώρος (Tholotos Room):** Σάρωση σε κόκκινο κοκκινόχωμα με χαλίκι (διάμετρος 3-3.5m, ύψος θόλου 4m).
    * **Δοκιμαστικό Κενό (Test Void):** Κατασκευασμένο κενό 1m (πλάτος) x 2m (μήκος) x 1.5m (ύψος) κάτω από 50cm κάλυψη εδάφους.
    * **Διπλοί Μεταλλικοί Στόχοι:** Θαμμένοι στόχοι στα 2 μέτρα βάθος με απόσταση 1 μέτρου σε στεγνό αργιλόχωμα για έλεγχο διακριτικής ικανότητας.
    * **Υπόγειο Οικίας:** Σάρωση πάνω από πλακάκι και σκυρόδεμα 25cm πάνω από κοιλότητα στεγανής δεξαμενής/βόθρου.
    * **Άσφαλτος:** Διαφορετική διηλεκτρική συμπεριφορά και ταχύτητα διάδοσης σε σχέση με το οργωμένο έδαφος ή το βουνό.
    """)

elif page == "⚙️ Παράμετροι Εδάφους & Διηλεκτρικά":
    st.header("⚙️ Υπολογιστής Ταχύτητας & Διηλεκτρικής Σταθεράς ($\epsilon_r$)")
    
    st.markdown("Υπολογισμός βάθους στόχου βάσει της διηλεκτρικής σταθεράς του εδάφους:")
    
    er_dict = {
        "Στεγνός Αέρας / Κενό": 1.0,
        "Στεγνή Άμμος": 4.0,
        "Στεγνό Αργιλόχωμα / Κοκκινόχωμα": 6.0,
        "Άσφαλτος": 5.0,
        "Ασβεστόλιθος / Βουνό": 8.0,
        "Υγρό Αργιλόχωμα": 15.0,
        "Νερό": 81.0
    }
    
    soil_type = st.selectbox("Επιλέξτε Τύπο Εδάφους / Στρώματος", list(er_dict.keys()))
    er = er_dict[soil_type]
    
    time_ns = st.number_input("Χρόνος Επιστροφής Σήματος Two-Way Travel Time (ns)", value=20.0, step=1.0)
    
    c = 0.3
    v = c / np.sqrt(er)
    depth = (v * time_ns) / 2
    
    st.info(f"""
    * **Διηλεκτρική Σταθερά ($\epsilon_r$):** {er}
    * **Ταχύτητα Διάδοσης Σήματος ($v$):** {v:.4f} m/ns ({v*1000:.0f} km/s)
    * **Υπολογισμένο Βάθος Στόχου:** **{depth:.2f} μέτρα**
    """)
