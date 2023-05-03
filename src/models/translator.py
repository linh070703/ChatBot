from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from langdetect import detect
from utils.model_api import generate_general_call_chatgpt_api
from utils.logger import logging, print

def translate(text: str, src="vi", dest="en") -> str:
    """
    Translate text to English.

    Args:
        text (str): text to translate
        
    Returns:
        str: translated text
    """
    text = " ".join(text.split())
    model_input = f"""Translate from {src} into {dest}:
{text}

{dest}:"""
    logging.info(f"Model input: \n{model_input}")
    output = generate_general_call_chatgpt_api(
        inputs=model_input,
        top_p=0.92,
        max_tokens=4096,
    )
    logging.info(f"Model output: \n{output}")
    return output
    

def convert_answer_language_to_same_as_question(question: str, answer: str) -> str:
    """
    Convert language of answer to same as question's language.
    If answer language is already matched with question language, return answer unchanged.

    Args:
        question (str): question
        answer (str): answer
        
    Returns:
        str: answer
    """
    question_lang = detect(question)
    answer_lang = detect(answer)
    if question_lang == answer_lang:
        print("Question and answer language are the same. No need to translate.")
        return answer
    else:
        logging.info(f"Question language: {question_lang}")
        logging.info(f"Answer language: {answer_lang}")
        logging.info(f"Translating answer to {question_lang}...")
        return translate(answer, src=answer_lang, dest=question_lang)