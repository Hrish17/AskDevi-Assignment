# AskDevi-Assignment

## Installation :

### 1. Clone the repo

```bash
git clone https://github.com/Hrish17/AskDevi-Assignment.git
cd AskDevi-Assignment
```

### 2. Backend Setup :

```bash
python3 -m venv venv
source venv/bin/activate


cd backend
pip install -r requirements.txt


python manage.py migrate
python manage.py runserver
```

- backend folder should have .env file with ASTROLOGYAPI_USERID, ASTROLOGYAPI_KEY, HUGGINGFACE_API_KEY, DJANGO_SECRET_KEY

### 3. Frontend Setup :

In another terminal,

```bash
cd frontend
npm install

npm start
```

## API Endpoints :

1. POST /api/register/ - Registers a user and returns a sessionId.
2. PUT /api/update-birth-details/<sessionId>/ - Updates the user's birth details.
3. POST /api/chat/<sessionId>/ - Accepts a message and returns a generated response.
4. GET /api/chat-history/<sessionId>/ - Returns full chat history.

## Models used :

1. Hugging face - deepseek-ai/DeepSeek-V3-0324
2. Sentence Transformer - all-MiniLM-L6-v2

## Example LLM Prompt Template :

```
You are Devi, a wise astrologer. Here is the user's birth chart:
{birth_info}

The user asks: {user_question}

Refer to the following classical astrology text excerpts for guidance:
{chunks_text}

Based on these excerpts and the user's chart, provide an insightful response in clear language.Just give the answer without any additional information or data. Don't say birth chart or chart or anything else. The answer shouldn't look like you're analysing the charts or planets. Don't use planets name. Limit your answer to 50-70 words.

Give general answers. Don't use astrological terms. Speak in humane way.

```
