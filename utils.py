import streamlit as st


def display_results(prediction):
    st.header("Results")
    if prediction[0] == 1:
        st.warning("Subject may have Autism Spectrum Disorder")
    else:
        st.success("Subject does not have Autism Spectrum Disorder")
