import pandas as pd
from database import SessionLocal, Vocabulary
import sys

def import_vocab_from_csv(csv_path):
    session = SessionLocal()
    try:
        # Expecting CSV with columns: word, translation, example, pronunciation, level
        df = pd.read_csv(csv_path)
        
        words_added = 0
        for index, row in df.iterrows():
            # Check if word already exists to avoid duplicates
            if not session.query(Vocabulary).filter(Vocabulary.word == str(row.get('word', ''))).first():
                vocab = Vocabulary(
                    word=str(row.get('word', '')),
                    translation=str(row.get('translation', '')),
                    example=str(row.get('example', '')),
                    pronunciation=str(row.get('pronunciation', '')),
                    level=str(row.get('level', 'A1'))
                )
                session.add(vocab)
                words_added += 1
                
                # Commit in batches of 1000 to save memory
                if words_added % 1000 == 0:
                    session.commit()
                    print(f"Добавлено {words_added} слов...")
                    
        session.commit()
        print(f"Готово! Всего добавлено новых слов: {words_added}")
    except Exception as e:
        print(f"Ошибка при импорте: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python import_data.py path_to_file.csv")
    else:
        import_vocab_from_csv(sys.argv[1])
