
import streamlit as st
import pandas as pd

# Data for the GCS table
data = {
    "Toiminto": [
        "Silmien avaaminen", "", "", "", 
        "Puhevaste", "", "", "", "", 
        "Paras liikevaste", "", "", "", "", "", ""
    ],
    "Reagointi": [
        "Spontaanisti", "Puheelle", "Kivulle", "Ei mitään", 
        "Orientoitunut", "Sekava", "Irrallisia sanoja", "Ääntelyä", "Ei mitään", 
        "Noudattaa kehotuksia", "Paikallistaa kivun", "Väistää kipua", "Fleksoi kivulle", "Ekstensoi kivulle", "Ei vastetta", ""
    ],
    "Pisteet": [
        4, 3, 2, 1, 
        5, 4, 3, 2, 1, 
        6, 5, 4, 3, 2, 1, "3–15"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Main title
st.title("Pään TT indikaatiosovellus")

# Intro text
st.write("Vastaa seuraaviin kysymyksiin arvioidaksesi pään TT-tarpeen päänvamman jälkeen")

# Initial questions using header for questions, subheader for replies, and title for outputs
st.header("GCS < 13 ensiavussa ensimmäistä kertaa arvioitaessa")
question_1 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_1")
with st.expander("Lisätietoa"):
    st.write("Explanation of terms and definitions for GCS < 13 ensiavussa")
    st.table(df)

if question_1 == "Kyllä":
    st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
elif question_1 == "Ei":
    st.header("GCS < 15 ensiavussa 2 tuntia vamman jälkeen")
    question_2 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_2")
    with st.expander("Lisätietoa"):
        st.write("Additional definitions or clarifications for GCS < 15 ensiavussa 2 tuntia vamman jälkeen")
        st.table(df)

    if question_2 == "Kyllä":
        st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
    elif question_2 == "Ei":
        st.header("Epäily avoimesta tai kasaan painuneesta kallonmurtumasta")
        question_3 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_3")

        if question_3 == "Kyllä":
            st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
        elif question_3 == "Ei":
            st.header("Merkki kallonpohjan murtumasta")
            question_4 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_4")
            with st.expander("Lisätietoa"):
                st.write("Hemotympanum, periorbitaalinen hematooma (brillen-hematooma), Subkutaaninen hematooma mastoideuslokeroston päällä (Battle's sign), Likvorivuoto nenästä tai korvasta")

            if question_4 == "Kyllä":
                st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
            elif question_4 == "Ei":
                st.header("Vamman jälkeinen kouristuskohtaus")
                question_5 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_5")

                if question_5 == "Kyllä":
                    st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
                elif question_5 == "Ei":
                    st.header("Paikallinen neurologinen puutosoire")
                    question_6 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_6")
                    with st.expander("Lisätietoa"):
                        st.write("Esim. hemipareesi, dysfasia, näkökenttäpuutos")

                    if question_6 == "Kyllä":
                        st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
                    elif question_6 == "Ei":
                        st.header("Useampi kuin yksi oksennusepisodi vamman jälkeen")
                        question_7 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_7")

                        if question_7 == "Kyllä":
                            st.markdown("<h1 style='color:red;'>Tee pään TT 1 tunnin sisään arvioinnista</h1>", unsafe_allow_html=True)
                        elif question_7 == "Ei":
                            # If all initial seven questions are answered "Ei", proceed to the next question
                            st.header("Onko vamman jälkeen ollut tajuttomuutta tai amnesiaa?")
                            question_8 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_8")

                            if question_8 == "Kyllä":
                                # Next question if question_8 is "Kyllä"
                                st.header("Ikä ≥ 65 v?")
                                question_10 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_10")

                                if question_10 == "Kyllä":
                                    st.markdown("<h1 style='color:orange;'>Tee pään TT 8 tunnin sisään vammasta</h1>", unsafe_allow_html=True)
                                elif question_10 == "Ei":
                                    # Proceed to question 11 if question_10 is "Ei"
                                    st.header("Tiedossa verenhyytymishäiriö?")
                                    question_11 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_11")
                                    with st.expander("Lisätietoa"):
                                        st.write("Maksan vajaatoiminta, hemofilia, antikoagulanttilääkitys, verihiutaleiden estäjälääkitys")

                                    if question_11 == "Kyllä":
                                        st.markdown("<h1 style='color:orange;'>Tee pään TT 8 tunnin sisään vammasta</h1>", unsafe_allow_html=True)
                                    elif question_11 == "Ei":
                                        # Proceed to question 12 if question_11 is "Ei"
                                        st.header("Vaarallinen vammamekanismi?")
                                        question_12 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_12")
                                        with st.expander("Lisätietoa"):
                                            st.write("Jalankulkija tai pyöräilijä joutunut moottoroidun ajoneuvon töytäisemäksi, henkilö lentänyt ulos ajoneuvosta, putoaminen yli 1 metrin tai yli 5 portaan korkeudesta")

                                        if question_12 == "Kyllä":
                                            st.markdown("<h1 style='color:orange;'>Tee pään TT 8 tunnin sisään vammasta</h1>", unsafe_allow_html=True)
                                        elif question_12 == "Ei":
                                            # Proceed to question 13 if question_12 is "Ei"
                                            st.header("Yli 30 minuutin retrogradinen amnesia?")
                                            question_13 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_13")
                                            with st.expander("Lisätietoa"):
                                                st.write("Muistamattomuus vammaa edeltäneistä tapahtumista")

                                            if question_13 == "Kyllä":
                                                st.markdown("<h1 style='color:orange;'>Tee pään TT 8 tunnin sisään vammasta</h1>", unsafe_allow_html=True)
                                            elif question_13 == "Ei":
                                                st.markdown("<h1 style='color:green;'>Ei tarvetta pään TT-kuvaukselle</h1>", unsafe_allow_html=True)
                            elif question_8 == "Ei":
                                # Proceed to question 9 if question_8 is "Ei"
                                st.header("Onko antikoagulaatiolääkitystä tai verihiutaleiden estäjälääkitystä (pois lukien aspiriinia)?")
                                question_9 = st.radio("", ["Valitse vaihtoehto", "Ei", "Kyllä"], key="question_9")
                                with st.expander("Lisätietoa"):
                                    st.write("Varfariini, DOAC, hepariini, LMWH, klopidogreeli, tikagreloori, prasugreeli")

                                if question_9 == "Kyllä":
                                    st.markdown("<h1 style='color:#DAA520;'>Harkinnan mukaan pään TT-kuvaus</h1>", unsafe_allow_html=True)
                                elif question_9 == "Ei":
                                    st.markdown("<h1 style='color:green;'>Ei tarvetta pään TT-kuvaukselle</h1>", unsafe_allow_html=True)

# Reference link
st.write("Viitteet: [Käypähoito – Aivovammat (2023)](https://www.kaypahoito.fi/hoi18020) | [NICE 2023 guidelines](https://www.nice.org.uk/guidance/ng232/chapter/recommendations#criteria-for-doing-a-ct-head-scan)")
