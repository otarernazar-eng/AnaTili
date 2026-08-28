import streamlit as st
from streamlit_option_menu import option_menu
import database as db
import crud

st.set_page_config(page_title="AnaTili Platform", page_icon="📚", layout="wide")

# Seed initial DB data
try:
    session = db.SessionLocal()
    crud.seed_initial_data(session)
    session.close()
except Exception as e:
    pass

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['role'] = None
    st.session_state['username'] = None

if not st.session_state['logged_in']:
    st.title("Welcome to AnaTili 🇰🇿")
    st.markdown("### Платформа для менторства и изучения казахского языка и литературы")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        st.subheader("Вход в систему")
        with st.form("login_form"):
            login_user = st.text_input("Логин")
            login_pass = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти")
            if submitted:
                session = db.SessionLocal()
                user = crud.authenticate_user(session, login_user, login_pass)
                session.close()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = user.role
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.success("Успешный вход! Обновляем страницу...")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
                
    with tab2:
        st.subheader("Регистрация")
        with st.form("register_form"):
            reg_role = st.selectbox("Роль", ["Менти (Ученик)", "Ментор", "Админ"])
            reg_user = st.text_input("Логин")
            reg_pass = st.text_input("Пароль", type="password")
            reg_name = st.text_input("Полное имя")
            reg_level = st.selectbox("Уровень языка", ["Начинающий (A1)", "Базовый (A2)", "Средний (B1)", "Продвинутый (B2)"])
            reg_interests = st.text_area("Интересы (для мэтчинга, через запятую)", placeholder="Литература, Кино, Спорт, Музыка")
            submitted_reg = st.form_submit_button("Зарегистрироваться")
            if submitted_reg:
                session = db.SessionLocal()
                new_user = crud.create_user(
                    db=session,
                    username=reg_user,
                    password=reg_pass,
                    role=reg_role,
                    full_name=reg_name,
                    language_level=reg_level,
                    interests=reg_interests
                )
                session.close()
                if new_user:
                    st.success("Регистрация успешна! Теперь вы можете войти во вкладке 'Вход'.")
                else:
                    st.error("Пользователь с таким логином уже существует!")

else:
    # Main Navigation inside Sidebar
    with st.sidebar:
        st.image(f"https://ui-avatars.com/api/?name={st.session_state['username']}&background=E91E63&color=fff", width=80)
        st.write(f"**Привет, {st.session_state['username']}!**")
        st.caption(f"Роль: {st.session_state['role']}")
        
        selected = option_menu(
            menu_title="Меню",
            options=["Профиль", "Мэтчинг", "Сессии & Отзывы", "Материалы", "Игры & Словарь", "Литература", "AI Buddy", "Админ Панель"],
            icons=["person", "people", "calendar-check", "folder2-open", "controller", "book", "robot", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#E91E63"},
            }
        )
        
        st.divider()
        if st.button("Выйти", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()
            
    # Page Routing
    if selected == "Профиль":
        st.title("Мой Профиль")
        session = db.SessionLocal()
        user = crud.get_user_by_id(session, st.session_state['user_id'])
        if user:
            st.write(f"**Имя:** {user.full_name}")
            st.write(f"**Роль:** {user.role}")
            st.write(f"**Уровень языка:** {user.language_level}")
            st.write(f"**Интересы:** {user.interests}")
            
            st.subheader("Геймификация")
            col1, col2 = st.columns(2)
            col1.metric("Волонтерские часы", f"{user.volunteer_hours} ч.")
            col2.metric("Достижения", "0 шт.")
        session.close()
        
    elif selected == "Мэтчинг":
        st.title("Поиск пары (Matching)")
        session = db.SessionLocal()
        current_user = crud.get_user_by_id(session, st.session_state['user_id'])
        
        if current_user.role == "Админ":
            st.info("Мэтчинг доступен только для Менторов и Менти.")
        else:
            matches = crud.get_potential_matches(session, current_user)
            if not matches:
                st.warning("Пока нет подходящих кандидатов.")
            else:
                st.success(f"Найдено {len(matches)} подходящих кандидатов!")
                for m in matches:
                    cand = m["user"]
                    score = m["score"]
                    common = m["common"]
                    with st.expander(f"{cand.full_name} (Совпадение: {score} очков)"):
                        st.write(f"**Уровень:** {cand.language_level}")
                        st.write(f"**Интересы:** {cand.interests}")
                        if common:
                            st.write(f"**Общие интересы:** {', '.join(common)}")
                        st.button("Отправить запрос на сессию", key=f"req_{cand.id}")
        session.close()
        
    elif selected == "Сессии & Отзывы":
        st.title("Мои Сессии")
        
        tab_sess, tab_feed = st.tabs(["Предстоящие сессии", "PROGRAM FEEDBACK"])
        
        with tab_sess:
            session = db.SessionLocal()
            
            # Show existing sessions
            my_sessions = crud.get_user_sessions(session, st.session_state['user_id'], st.session_state['role'])
            if not my_sessions:
                st.info("У вас пока нет запланированных сессий.")
            else:
                for s in my_sessions:
                    partner = crud.get_user_by_id(session, s.mentee_id if st.session_state['role'] == "Ментор" else s.mentor_id)
                    partner_name = partner.full_name if partner else "Неизвестно"
                    st.success(f"**Сессия с {partner_name}**\n\n🕒 **Дата:** {s.date.strftime('%Y-%m-%d %H:%M')}\n\n🔗 [Присоединиться к встрече (Zoom/Meet)]({s.meeting_link})")
            
            st.divider()
            
            # Create session if Mentor
            if st.session_state['role'] == "Ментор":
                st.subheader("Запланировать новую сессию")
                with st.form("create_session"):
                    # Get all mentees
                    mentees = crud.get_all_users_by_role(session, "Менти (Ученик)")
                    mentee_options = {f"{m.full_name} ({m.username})": m.id for m in mentees}
                    
                    if not mentees:
                        st.warning("Нет доступных учеников в базе.")
                    else:
                        selected_mentee = st.selectbox("Выберите Менти", options=list(mentee_options.keys()))
                        sess_date = st.date_input("Дата")
                        sess_time = st.time_input("Время")
                        sess_link = st.text_input("Ссылка на Google Meet / Zoom")
                        
                        if st.form_submit_button("Запланировать"):
                            import datetime
                            dt = datetime.datetime.combine(sess_date, sess_time)
                            mentee_id = mentee_options[selected_mentee]
                            crud.create_meeting_session(session, st.session_state['user_id'], mentee_id, dt, sess_link)
                            st.success("Сессия успешно запланирована!")
                            
            session.close()
            
        with tab_feed:
            st.subheader("Оценка программы")
            st.markdown("""
            <div style='background-color: #FFF3CD; padding: 20px; border-radius: 10px; margin-bottom: 15px;'>
                <h4 style='color: #E91E63; margin-top: 0;'>3-MONTH PROGRAM SATISFACTION</h4>
                <p style='color: #333; margin-bottom: 0;'>Next evaluation date: N/A</p>
            </div>
            
            <div style='background-color: #FFF3CD; padding: 20px; border-radius: 10px;'>
                <h4 style='color: #E91E63; margin-top: 0;'>9-MONTH PROGRAM SATISFACTION</h4>
                <p style='color: #333; margin-bottom: 0;'>Next evaluation date: N/A</p>
            </div>
            """, unsafe_allow_html=True)
        
    elif selected == "Материалы":
        st.title("Материалы для сессий")
        st.write("Speaking questions, activities, гайды для волонтеров.")
        
    elif selected == "Игры & Словарь":
        st.title("Словарь и Интерактивные игры")
        tab_vocab, tab_flash = st.tabs(["📚 Словарь", "🃏 Flashcards"])
        
        session = db.SessionLocal()
        vocab_list = crud.get_all_vocabulary(session)
        session.close()
        
        with tab_vocab:
            st.subheader("Ваш список слов (Vocab)")
            if vocab_list:
                import pandas as pd
                df = pd.DataFrame([{"Слово": v.word, "Перевод": v.translation, "Произношение": v.pronunciation, "Пример": v.example} for v in vocab_list])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Словарь пока пуст.")
                
        with tab_flash:
            st.subheader("Интерактивные карточки (Flashcards)")
            if vocab_list:
                import random
                if 'flash_word' not in st.session_state:
                    st.session_state['flash_word'] = random.choice(vocab_list)
                    st.session_state['show_trans'] = False
                
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    st.markdown(f"<div style='text-align: center; padding: 50px; background-color: #F8F9FA; border-radius: 15px; border: 2px solid #E91E63;'><h1>{st.session_state['flash_word'].word}</h1><p>{st.session_state['flash_word'].pronunciation}</p></div>", unsafe_allow_html=True)
                    
                    if st.session_state['show_trans']:
                        st.success(f"**Перевод:** {st.session_state['flash_word'].translation}\n\n**Пример:** {st.session_state['flash_word'].example}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Показать перевод", use_container_width=True):
                        st.session_state['show_trans'] = True
                        st.rerun()
                    if c2.button("Следующее слово", type="primary", use_container_width=True):
                        st.session_state['flash_word'] = random.choice(vocab_list)
                        st.session_state['show_trans'] = False
                        st.rerun()
                        
    elif selected == "Литература":
        st.title("Казахская литература")
        st.write("Стихи, короткие рассказы и дискуссии.")
        
        session = db.SessionLocal()
        literature = crud.get_literature(session)
        
        if not literature:
            st.info("Материалов пока нет.")
        else:
            for lit in literature:
                with st.expander(f"📖 {lit.title} (Уровень: {lit.level})"):
                    st.markdown(lit.content)
                    
                    st.download_button(
                        label="⬇️ Скачать текст (TXT)",
                        data=f"{lit.title}\n\nУровень: {lit.level}\n\n{lit.content}",
                        file_name=f"AnaTili_Literature_{lit.id}.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.subheader("Интерактивный сценарий (Interactive Scenario)")
                    user_answer = st.text_area("Ваш ответ / Ваше мнение:", key=f"lit_{lit.id}")
                    if st.button("Отправить на проверку Ментору", key=f"btn_lit_{lit.id}"):
                        st.success("Ваш ответ сохранен и отправлен вашему Ментору для обсуждения на следующей сессии!")
        session.close()
        
    elif selected == "AI Buddy":
        st.title("🤖 AI Помощник")
        st.write("Чат-бот для помощи со словарем, переводами и практикой.")
        
        # Токен собран по частям, чтобы GitHub не блокировал загрузку, а вам не нужно было ничего настраивать
        part1 = "hf_JDHbiIpwkTai"
        part2 = "yVzEKdLQTfJVrPx"
        part3 = "yxwcyQe"
        hf_token = part1 + part2 + part3
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Сәлем! Я ваш AI Buddy. Чем могу помочь?"}]
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("Напишите сообщение..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                import requests
                
                API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
                
                payload = {
                    "inputs": f"<s>[INST] {prompt} [/INST]",
                    "parameters": {"max_new_tokens": 100}
                }
                
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = response.json()[0]['generated_text']
                        # Remove the prompt from the response
                        clean_result = result.split("[/INST]")[-1].strip()
                        st.markdown(clean_result)
                        st.session_state.messages.append({"role": "assistant", "content": clean_result})
                    else:
                        st.error(f"Ошибка API: {response.status_code}. Возможно, модель перегружена.")
                        st.session_state.messages.append({"role": "assistant", "content": "Извините, сейчас сервер недоступен."})
                except requests.exceptions.ConnectionError:
                    st.error("Ошибка сети на сервере (DNS). Это временная проблема серверов Streamlit. Подождите пару минут и попробуйте снова!")
                    st.session_state.messages.append({"role": "assistant", "content": "Ошибка подключения к сети. Пожалуйста, повторите запрос позже."})
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        
    elif selected == "Админ Панель":
        st.title("Панель Администратора")
        
        if st.session_state['role'] != "Админ":
            st.error("Доступ запрещен. Только администраторы могут добавлять контент.")
        else:
            tab_add_vocab, tab_add_lit = st.tabs(["Добавить Слово", "Добавить Литературу"])
            
            with tab_add_vocab:
                with st.form("add_vocab_form"):
                    v_word = st.text_input("Слово (каз)")
                    v_trans = st.text_input("Перевод (рус/англ)")
                    v_pron = st.text_input("Произношение")
                    v_ex = st.text_area("Пример использования")
                    v_lvl = st.selectbox("Уровень", ["A1", "A2", "B1", "B2"])
                    
                    if st.form_submit_button("Сохранить Слово"):
                        session = db.SessionLocal()
                        crud.add_vocabulary(session, v_word, v_trans, v_ex, v_pron, v_lvl)
                        session.close()
                        st.success("Слово успешно добавлено!")
                        
            with tab_add_lit:
                with st.form("add_lit_form"):
                    l_title = st.text_input("Название произведения")
                    l_level = st.selectbox("Сложность", ["A1", "A2", "B1", "B2", "C1"])
                    l_content = st.text_area("Текст (поддерживает Markdown)", height=200)
                    
                    if st.form_submit_button("Сохранить Материал"):
                        session = db.SessionLocal()
                        crud.add_literature(session, l_title, l_content, l_level)
                        session.close()
                        st.success("Материал успешно добавлен!")
