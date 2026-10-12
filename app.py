import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="KS-700 GPR Voxel & Isosurface 3D Analyzer", layout="wide")

st.title("📡 KS-700 GPR - Voxel / Isosurface 3D Expert Analyzer")
st.markdown("""
Προηγμένη 3D απεικόνιση τύπου **Voxel / Isosurface** με χρωματική κωδικοποίηση:
* 🟫 **Γκρι / Ανοιχτό:** Σταθερό/Φυσικό Έδαφος
* 🟩 **Πράσινο:** Αναμοχλευμένο έδαφος / Επιχώσεις (Disturbed Soil)
* 🟥 **Κόκκινο:** Μέταλλα / Στόχοι υψηλής αντανάκλασης (με προσέγγιση σχήματος)
* 🟦 **Μπλε:** Κενά / Σήραγγες / Τούνελ (με αυτόματη συνένωση/ογκομετρική σύνδεση)
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
        
        st.sidebar.subheader("🎛️ Ρυθμίσεις Ταξινόμησης Voxel")
        metal_th = st.sidebar.slider("Κατώφλι Μετάλλων (Κόκκινο)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.92)))
        void_th = st.sidebar.slider("Κατώφλι Κενών / Τούνελ (Μπλε)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.20)))
        disturbed_th_low = void_th
        disturbed_th_high = st.sidebar.slider("Όριο Αναμοχλευμένου Εδάφους (Πράσινο)", float(df[amp_col].min()), float(df[amp_col].max()), float(df[amp_col].quantile(0.50)))
        
        def classify_voxel(val):
            if val >= metal_th:
                return 'Μέταλλο'
            elif val <= void_th:
                return 'Κενό / Τούνελ'
            elif void_th < val <= disturbed_th_high:
                return 'Αναμοχλευμένο Έδαφος'
            else:
                return 'Φυσικό Έδαφος'
                
        df['Voxel_Type'] = df[amp_col].apply(classify_voxel)
        
        counts = df['Voxel_Type'].value_counts()
        st.subheader("📊 Στατιστικά Όγκου Voxel")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟦 Κενά / Τούνελ", counts.get('Κενό / Τούνελ', 0))
        col2.metric("🟥 Μέταλλα", counts.get('Μέταλλο', 0))
        col3.metric("🟩 Αναμοχλευμένο", counts.get('Αναμοχλευμένο Έδαφος', 0))
        col4.metric("🟫 Φυσικό Έδαφος", counts.get('Φυσικό Έδαφος', 0))
        
        st.subheader("🌐 Τρισδιάστατη Ογκομετρική Απεικόνιση (Voxel Grid)")
        
        color_map = {
            'Μέταλλο': 'red',
            'Κενό / Τούνελ': 'blue',
            'Αναμοχλευμένο Έδαφος': 'green',
            'Φυσικό Έδαφος': 'lightgray'
        }
        
        size_map = {
            'Μέταλλο': 8,
            'Κενό / Τούνελ': 7,
            'Αναμοχλευμένο Έδαφος': 4,
            'Φυσικό Έδαφος': 2
        }
        
        opacity_map = {
            'Μέταλλο': 1.0,
            'Κενό / Τούνελ': 0.9,
            'Αναμοχλευμένο Έδαφος': 0.4,
            'Φυσικό Έδαφος': 0.05
        }
        
        fig = go.Figure()
        
        for vtype, color in color_map.items():
            subset = df[df['Voxel_Type'] == vtype]
            if not subset.empty:
                fig.add_trace(go.Scatter3d(
                    x=subset[x_col],
                    y=subset[y_col],
                    z=subset[z_col],
                    mode='markers',
                    name=vtype,
                    marker=dict(
                        size=size_map[vtype],
                        color=color,
                        opacity=opacity_map[vtype],
                        symbol='square' if vtype in ['Κενό / Τούνελ', 'Μέταλλο'] else 'circle'
                    ),
                    text=vtype + "<br>Amp: " + subset[amp_col].astype(str)
                ))
                
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Βάθος Z (m)',
                zaxis=dict(autorange='reversed')
            ),
            height=700,
            margin=dict(r=0, b=0, l=0, t=0),
            legend=dict(itemsizing='constant')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🔍 Συνδεδεμένοι Στόχοι (Σήραγγες & Μεταλλικοί Σχηματισμοί)")
        tunnel_df = df[df['Voxel_Type'].isin(['Κενό / Τούνελ', 'Μέταλλο'])]
        st.dataframe(tunnel_df)
        
        csv_export = tunnel_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Λήψη Αναφοράς Στόχων & Τούνελ (CSV)",
            data=csv_export,
            file_name="ks700_voxel_tunnels_metals.csv",
            mime="text/csv",
        )
        
    except Exception as e:
        st.error(f"Σφάλμα επεξεργασίας: {e}")
else:
    st.info("Παρακαλώ ανεβάστε το αρχείο CSV σας για να δημιουργηθεί η 3D Voxel απεικόνιση.")
