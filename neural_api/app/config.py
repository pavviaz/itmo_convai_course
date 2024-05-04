HEALTHCHECK_TIMEOUT = 30
HEALTHCHECK_SLEEP = 5

RAG_PATH = "rag_data/rag.csv"

MAX_NEW_TOKENS = 1024
TIMEOUT = 60

WORKER_URL = "worker"
LLM_EP = "worker"
AVAIL_INTENTS = ["s_info", "c_descr", "visiting"]

HELPER_PROMPT = \
"""
[INST] The user's current request is 'UUU'. Previous message: 'CTX'.
Using this request and previous message, generate JSON with one required field 'transit', that denotes user's request type.
Use previous message only to understand the country user is asking about!
You can choose one of the following:
1) s_info: choose this if user asks something about picture given (for example 'What is this?' or 'Describe the photo'). if you choose this, do not make ANY additional keys, 'transit' is THE ONLY ONE.
2) c_descr: choose this if user asks exact question about general understand, ways to get in, in-country transport, tourist attractions, shopping, food and hotels of the country (for example 'What is the best food there?', 'What currency do they use?', etc). ONLY if you choose this, make an additional field in JSON called 'country', which value can be one of the following: RRR. If you don't have enough context to understand the country, set it to 'NA'
3) visiting: choose this if user want to fly a country and book a hotel (for example 'Can you plan a trip from Moscow to this country from 04.05.2024 to 11.05.2024?', 'Please, make a tour there from London'). If you choose this, additionaly generate keys 'c_from' and 'c_to' denoting the cities and keys 'date_from' and 'date_to' (in 'YYYY-MM-DD' format) ONLY if it possible to extract them. 
[/INST]
"""

S_INFO_PROMPT = \
"""
[INST] <image> UUU [/INST]
"""

C_DESCR_PROMPT = \
"""
[INST] The user's request is 'UUU'. Use your own knowladge and this info to give final short (couple paragraphs) answer (if following info empty, look at previous context): RRR [/INST]
"""
C_DESCR_NO_RAG = "**NOTE**\nWe couldn't find info about requested country in our database, so the following text is only LLM-generated\n"