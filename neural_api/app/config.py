HEALTHCHECK_TIMEOUT = 30
HEALTHCHECK_SLEEP = 5

RAG_PATH = "rag_data/rag.csv"

MAX_NEW_TOKENS = 1024
TIMEOUT = 60

WORKER_URL = "worker"
LLM_EP = "worker"
AVAIL_INTENTS = ["s_info", "c_descr", "ticket_ord"]

HELPER_PROMPT = \
"""
[INST] <image> The user's request is 'UUU'. Generate JSON with one required field 'transit', that denotes user's request type.
You can choose one of the following depending of what user asks something about:
1) s_info: sightseen on the photo (for example 'What is this?' or 'Describe the photo'). if you choose this, do not make ANY additional keys, 'transit' is THE ONLY ONE.
2) c_descr: country in general, that is on the photo (for example 'What are the best landmarks in \{country_name\}' (image-aware request) or 'Is there nice food?' (image-dependent request)). ONLY if you choose this, make an additional field in JSON called 'country', which value can be one of RRR if the country on photo presented here, NA otherwise. 
3) ticket_ord: how to get into the country or want to buy tickets to fly a country (for example 'What are the tickets price?', or 'How can I get there?', or 'What is the easiest way to get into...?'). if you choose this, do not make ANY additional keys, 'transit' is THE ONLY ONE.
Do exactly what I said
[/INST]
"""

S_INFO_PROMPT = \
"""
[INST] <image> UUU [/INST]
"""

C_DESCR_PROMPT = \
"""
[INST] The user's request is 'UUU'. Use your own knowladge and this info to give final short (couple paragraphs) answer: RRR [/INST]
"""
C_DESCR_NO_RAG = "**NOTE**\nWe couldn't find info about requested country in our database, so the following text is only LLM-generated\n"