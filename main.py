import pickle

import pandas as pd
import streamlit as st
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split

from questions import data

screening = pd.read_csv("./DataSet/Screening/data.csv")
screening.drop("Unnamed: 0", axis=1, inplace=True)
x = screening.iloc[:, :-1]
y = screening.iloc[:, -1]
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42
)

estimators = [
    ("lr", pickle.load(open("Screening/logistic_regression_screening.sav", "rb"))),
    ("svc", pickle.load(open("Screening/svc_screening.sav", "rb"))),
    ("knn", pickle.load(open("Screening/knn_screening.sav", "rb"))),
    ("naive", pickle.load(open("Screening/naive_screening.sav", "rb"))),
]
screening_voting = VotingClassifier(estimators=estimators, voting="hard")
screening_voting.fit(x_train, y_train)

st.title("Autism Spectrum Disorder Screening")

st.write(
    "This is a screening tool for Autism Spectrum Disorder. Please answer the "
    "following questions as honestly as possible."
)
st.write(
    "Please note that this is not a diagnostic tool. If you suspect that you "
    "or someone you know may have ASD, please consult a medical professional."
)

answers = ["" for _ in range(len(data))]
prediction = None


def get_clean_answer(answer):
    final = answer
    if answer == "Yes":
        final = 1
    elif answer == "No":
        final = 0
    return final


def to_category(options, chosen):
    """Returns the index of `chosen` in `options`"""
    return options.index(chosen)


with st.form("questions", True):
    for idx, question in enumerate(data):
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
        cleaned_answers = list(map(get_clean_answer, answers))
        final_input = {
            "result": sum(cleaned_answers[:10]),
            "age": cleaned_answers[10],
            "gender": to_category(data[11]["options"], cleaned_answers[11]),
            "ethnicity": to_category(data[12]["options"], cleaned_answers[12]),
            "jaundice": cleaned_answers[13],
            "relation": to_category(data[14]["options"], cleaned_answers[14]),
            "autism": cleaned_answers[15],
            "age_desc": to_category(data[16]["options"], cleaned_answers[16]),
        }
        inputs = cleaned_answers[:10] + list(final_input.values())
        prediction = screening_voting.predict([inputs])

if prediction:
    st.header("Results")
    if prediction[0] == 1:
        st.warning("Subject may have Autism Spectrum Disorder")
    else:
        st.success("Subject does not have Autism Spectrum Disorder")
