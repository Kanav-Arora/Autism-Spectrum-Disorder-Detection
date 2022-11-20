import glob
import pickle

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

from questions import data
from utils import display_results

asdd = "Autism Spectrum Disorder Detection"

st.set_page_config(page_title=asdd, page_icon=':brain:')

st.title(asdd)

st.write(
    "This is a screening tool for Autism Spectrum Disorder. Please answer the "
    "following questions as honestly as possible."
)
st.write(
    "Please note that this is not a diagnostic tool. If you suspect that you "
    "or someone you know may have ASD, please consult a medical professional."
)


@st.cache
def screen_load():
    screening = pd.read_csv("DataSet/Screening/data.csv")
    screening.drop("Unnamed: 0", axis=1, inplace=True)
    x = screening.iloc[:, :-1]
    y = screening.iloc[:, -1]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    estimators = [
        (
            "lr",
            pickle.load(
                open("Screening/logistic_regression_screening.sav", "rb")
            ),
        ),
        ("svc", pickle.load(open("Screening/svc_screening.sav", "rb"))),
        ("knn", pickle.load(open("Screening/knn_screening.sav", "rb"))),
        ("naive", pickle.load(open("Screening/naive_screening.sav", "rb"))),
    ]
    screening_voting = VotingClassifier(estimators=estimators, voting="hard")
    screening_voting.fit(x_train, y_train)
    return screening_voting


screening_voting = screen_load()

answers = ["" for _ in range(len(data))]


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


# -------------------- Image ---------------------#


@st.cache
def load_image():
    dir = "./DataSet/Images/Autistic/train/"
    ori_label = []
    ori_imgs = []

    for images in glob.iglob(f"{dir}/*"):
        ori_label.append(1)
        new_img = Image.open(images)
        ori_imgs.append(
            ImageOps.fit(new_img, (64, 64), Image.ANTIALIAS).convert("RGB")
        )

    dir = "./DataSet/Images/Non_Autistic/train/"

    for images in glob.iglob(f"{dir}/*"):
        ori_label.append(0)
        new_img = Image.open(images)
        ori_imgs.append(
            ImageOps.fit(new_img, (64, 64), Image.ANTIALIAS).convert("RGB")
        )

    imgs = np.array([np.array(im) for im in ori_imgs])
    imgs = np.array([cv2.resize(im, (32, 32)).flatten() for im in imgs])
    lb = LabelBinarizer().fit(ori_label)
    label = lb.transform(ori_label)

    dir = "./DataSet/Images/Autistic/test/"
    ti = []
    output = []

    for images in glob.iglob(f"{dir}/*"):
        output.append(1)
        new_img = Image.open(images)
        ti.append(
            ImageOps.fit(new_img, (64, 64), Image.ANTIALIAS).convert("RGB")
        )

    dir = "./DataSet/Images/Non_Autistic/test/"

    for images in glob.iglob(f"{dir}/*"):
        output.append(0)
        new_img = Image.open(images)
        ti.append(
            ImageOps.fit(new_img, (64, 64), Image.ANTIALIAS).convert("RGB")
        )

    ti = np.array([np.array(im) for im in ti])
    ti = np.array([cv2.resize(im, (32, 32)).flatten() for im in ti])

    estimators = [
        (
            "lr",
            pickle.load(
                open("Image Classification/logistic_regression.sav", "rb")
            ),
        ),
        ("knn", pickle.load(open("Image Classification/knn.sav", "rb"))),
        (
            "naive",
            pickle.load(open("Image Classification/naive_bayes.sav", "rb")),
        ),
        ("svc", pickle.load(open("Image Classification/svc.sav", "rb"))),
    ]

    image_voting = VotingClassifier(estimators=estimators, voting="hard")
    image_voting.fit(imgs, np.array(label))
    return image_voting


image_voting = load_image()


with st.form("survey"):

    st.subheader("Screening method")
    st.text("Please answer the following questions as honestly as possible:")

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

    st.subheader("Image method")
    st.text("Please upload an image of the subject:")

    picture = st.file_uploader("Image of subject")

    submitted = st.form_submit_button("Submit")
    if submitted and picture is not None:
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
        screening_prediction = screening_voting.predict([inputs])
        ri = []
        new_img = Image.open(picture)
        ri.append(
            ImageOps.fit(new_img, (64, 64), Image.ANTIALIAS).convert("RGB")
        )
        ri = np.array([np.array(im) for im in ri])
        ri = np.array([cv2.resize(im, (32, 32)).flatten() for im in ri])
        image_prediction = image_voting.predict(ri)
        display_results(screening_prediction)
        print(image_prediction)
