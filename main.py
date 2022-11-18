import streamlit as st

import questions

st.title("Autism Spectrum Disorder Screening")

st.write(
    "This is a screening tool for Autism Spectrum Disorder. Please answer the "
    "following questions as honestly as possible."
)
st.write(
    "Please note that this is not a diagnostic tool. If you suspect that you "
    "or someone you know may have ASD, please consult a medical professional."
)
st.header("Please answer the following questions:")

answers = ["" for _ in range(len(questions.data))]


def clean_answer(answer):
    final = answer
    if answer == "Yes":
        final = 1
    elif answer == "No":
        final = 0
    return final


with st.form("questions", True):
    for idx, question in enumerate(questions.data):
        question_type = question.get("type", "boolean")
        if question_type == "boolean":
            answers[idx] = st.radio(question["text"], ("Yes", "No"))
        elif question_type == "number":
            answers[idx] = st.number_input(
                question["text"], **question.get("input", {})
            )
        elif question_type == "select":
            answers[idx] = st.selectbox(question["text"], question["options"])
    submitted = st.form_submit_button("Submit")
    if submitted:
        cleaned_answers = map(clean_answer, answers)
        print(list(cleaned_answers))
