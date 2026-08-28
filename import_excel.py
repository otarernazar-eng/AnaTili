import pandas as pd
from database import SessionLocal, Vocabulary
import sys

def import_vocab_from_excel(file_path):
    session = SessionLocal()
    try:
        # Skip the first 2 rows which are title and messy headers
        df = pd.read_excel(file_path, skiprows=2)
        
        # The columns will likely be: Unnamed: 0, Қазақша, Русский, English
        # We need to rename them to access them easily if needed, or use them directly.
        # Let's check if 'Қазақша' exists. If not, fallback to column indices.
        col_kz = df.columns[1] if len(df.columns) > 1 else 'Қазақша'
        col_ru = df.columns[2] if len(df.columns) > 2 else 'Русский'
        col_en = df.columns[3] if len(df.columns) > 3 else 'English'
        
        words_added = 0
        for index, row in df.iterrows():
            kz_word = str(row.get(col_kz, '')).strip()
            ru_word = str(row.get(col_ru, '')).strip()
            en_word = str(row.get(col_en, '')).strip()
            
            # Skip if kz_word is NaN or empty (might be a category row)
            if kz_word == 'nan' or not kz_word:
                continue
                
            # Avoid duplicates
            if not session.query(Vocabulary).filter(Vocabulary.word == kz_word).first():
                vocab = Vocabulary(
                    word=kz_word,
                    translation=f"{ru_word} / {en_word}",
                    example="",
                    pronunciation="",
                    level="A1"
                )
                session.add(vocab)
                words_added += 1
                
        session.commit()
        print(f"Готово! Из файла Excel добавлено новых слов и фраз: {words_added}")
    except Exception as e:
        print(f"Ошибка при импорте Excel: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    import_vocab_from_excel("Kazakh_Russian_English_Dictionary (1).xlsx")
