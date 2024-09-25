import json
import random
import time
from datetime import datetime, timedelta
import sys
import os
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add parent directory to sys.path for importing settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import QOTD_ENABLED

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(SCRIPT_DIR, 'qotd/qotd_200.json')
BACKUP_FILE = os.path.join(SCRIPT_DIR, 'qotd/qotd_backup.json')
LAST_QOTD_FILE = os.path.join(SCRIPT_DIR, 'qotd/last_qotd.json')

def load_json(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return {"questions": []}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {filename}")
        return {"questions": []}

def save_json(filename: str, data: Dict[str, Any]) -> None:
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def load_questions(filename: str) -> List[str]:
    data = load_json(filename)
    return data.get('questions', [])

def save_questions(filename: str, questions: List[str]) -> None:
    save_json(filename, {'questions': questions})

def load_last_qotd_date() -> datetime:
    data = load_json(LAST_QOTD_FILE)
    last_qotd = data.get('last_qotd')
    return datetime.fromisoformat(last_qotd) if last_qotd else None

def save_last_qotd_date(date: datetime) -> None:
    save_json(LAST_QOTD_FILE, {'last_qotd': date.isoformat()})

def pick_random_question(questions: List[str]) -> str:
    if not questions:
        logging.warning("No questions available")
        return "No question available"
    return random.choice(questions)

def is_new_day(last_date: datetime) -> bool:
    return last_date is None or datetime.now().date() > last_date.date()

def reset_questions() -> None:
    questions = load_questions(BACKUP_FILE)
    save_questions(QUESTIONS_FILE, questions)
    logging.info("Questions reset from backup")

def run_qotd() -> None:
    logging.info("Starting QOTD process")
    questions = load_questions(QUESTIONS_FILE)
    last_qotd = load_last_qotd_date()

    if QOTD_ENABLED and is_new_day(last_qotd):
        if not questions:
            reset_questions()
            questions = load_questions(QUESTIONS_FILE)

        random_question = pick_random_question(questions)
        logging.info(f"Question of the Day: {random_question}")

        questions.remove(random_question)
        save_questions(QUESTIONS_FILE, questions)
        save_last_qotd_date(datetime.now())
    else:
        logging.info("QOTD is not enabled or it's not a new day yet")

def regenerate_choice() -> None:
    questions = load_questions(QUESTIONS_FILE)
    random_question = pick_random_question(questions)
    logging.info(f"Regenerated QOTD question: {random_question}")

def main() -> None:
    while True:
        try:
            now = datetime.now()
            last_qotd = load_last_qotd_date()

            if is_new_day(last_qotd):
                run_qotd()
            else:
                logging.info("Waiting for the next day to run QOTD.")

            # Sleep for an hour and check again
            time.sleep(3600)  
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            time.sleep(3600)  # Wait 1 hour before retrying on error


if __name__ == "__main__":
    main()
