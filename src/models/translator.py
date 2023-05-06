from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from lingua import Language, LanguageDetectorBuilder
from functools import lru_cache
from src.utils.model_api import generate_general_call_chatgpt_api
from src.utils.logger import logging, print
import threading

# detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH,
    # Language.FRENCH, Language.GERMAN, Language.SPANISH,
    Language.VIETNAMESE, Language.CHINESE, Language.JAPANESE, Language.KOREAN,
    Language.INDONESIAN, Language.THAI, Language.HINDI, Language.ARABIC,
    # Language.RUSSIAN, Language.PORTUGUESE, Language.ITALIAN, Language.TURKISH,
    # Language.DUTCH, Language.POLISH, Language.SWEDISH, Language.DANISH,
).with_preloaded_language_models().build()

def detect_language_of(text: str) -> str:
    return detector.detect_language_of(text).name

@lru_cache(maxsize=256)
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
        temperature=0.5,
        top_p=0.92,
        max_tokens=3072,
    )
    logging.info(f"Model output: \n{output}")
    output = " ".join(output.split())
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
    question_lang = detector.detect_language_of(question).name
    answer_lang = detector.detect_language_of(answer).name

    answer = translate_currency(answer, src=answer_lang)
    if question_lang == answer_lang:
        logging.info(f"Question and answer language are the same ({question_lang}). No need to translate.")
        return answer
    else:
        logging.info(f"Question language: {question_lang}")
        logging.info(f"Answer language: {answer_lang}")
        logging.info(f"Translating answer to {question_lang}...")
        return translate(answer, src=answer_lang, dest=question_lang)

def batch_convert_answer_language_to_same_as_question(question: str, answers: List[str]) -> List[str]:
    """
    Convert language of answer to same as question's language.
    If answer language is already matched with question language, return answer unchanged.
    In parralel

    Args:
        question (str): question
        answers (List[str]): list of answers
        
    Returns:
        List[str]: list of answers
    """
    question_lang = detector.detect_language_of(question).name
    answer_langs = [detector.detect_language_of(answer).name for answer in answers]
    answers = [translate_currency(answer, src=answer_lang) for answer, answer_lang in zip(answers, answer_langs)]
    if any([question_lang == answer_lang for answer_lang in answer_langs]):
        logging.info(f"Question and answer language are the same ({question_lang}). No need to translate.")
        return answers
    else:
        logging.info(f"Question language: {question_lang}")
        logging.info(f"Answer languages: {answer_langs}")
        logging.info(f"Translating answers to {question_lang}...")
        results = []
        threads = []
        for answer, answer_lang in zip(answers, answer_langs):
            def _translate(answer, answer_lang, results):
                results.append(translate(answer, src=answer_lang, dest=question_lang))
            t = threading.Thread(target=_translate, args=(answer, answer_lang, results))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        
        return results

    
def translate_currency(currency: str, src="ENGLISH") -> str:
    """
    Translate currency to English.

    Args:
        currency (str): currency to translate
        
    Returns:
        str: translated currency
    """
    currency = " ".join(currency.split())
    if src != "VIETNAMESE":
        # replace all "nghìn", "triệu", "tỷ" with "thousand", "million", "billion"
        currency = currency.replace("nghìn", "thousand").replace("triệu", "million").replace("tỷ", "billion")
        # replace all "đồng" with "VND"
        currency = currency.replace("đồng", "VND")
    
    return currency
        
    
def answer_I_dont_know_multilingual(messages: List[Dict[str, str]]):
    """
    Answer "I don't know" in the same language as the question.
    
    Args:
        messages (List[Dict[str, str]]): list of messages
        
    Returns:
        str: answer
    """
    messages = [m for m in messages if m['user'].lower() != 'assistant'][-12:]
    raw_conversation = "\n".join([f"{m['user'].strip()}: {' '.join(m['content'].split())}" for m in messages])
    user_language = detector.detect_language_of(raw_conversation).name
    logging.info(f"User language: {user_language}")
    if user_language == Language.ENGLISH.name:
        return "I'm sorry, but I do not understand what you mean. Can you rephrase your question?"
    elif user_language == Language.VIETNAMESE.name:
        return "Xin lỗi, tôi không hiểu ý bạn. Bạn có thể nói rõ hơn được không?"
    elif user_language == Language.CHINESE.name:
        return "对不起，我不明白你的意思。你能再说一遍吗？"
    elif user_language == Language.JAPANESE.name:
        return "すみませんが、私はあなたの意味がわかりません。"
    else:
        logging.info(f"Translating answer to {user_language}...")
        return translate("I don't understand.", src=Language.ENGLISH.name, dest=user_language)