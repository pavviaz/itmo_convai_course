import os

from dff.script import conditions as cnd
from dff.script import labels as lbl
from dff.script import GLOBAL, TRANSITIONS, RESPONSE, Context, NodeLabel3Type, Message
from dff.messengers.telegram import PollingTelegramInterface
from dff.pipeline import Pipeline

import re

from dff.utils.testing.common import (
    check_happy_path,
    is_interactive_mode,
    run_interactive_mode,
)

from dff.script.core.message import Button
from dff.messengers.telegram import (
    PollingTelegramInterface,
    TelegramUI,
    TelegramMessage,
    RemoveKeyboard,
)

import model

processor, model = model.get_model()

def chat(ctx: Context, pipeline: Pipeline) -> Message:
    if ctx.last_response == "Let's chat!":
        text = ''
    else:
        prompt = '[INST]' + ctx.last_request.text + '[/INST]'
        inputs = processor(prompt, None, return_tensors="pt").to("cuda:0")
        output = model.generate(**inputs, max_new_tokens=100)
        text = processor.decode(output[0], skip_special_tokens=True)
        print (text)
    return Message(text)

# def func(ctx: Context, pipeline: Pipeline) -> bool:
#     print('1:', ctx.last_request)
#     print('2:', ctx.last_label)
#     print('3:', ctx.last_response)
#     if ctx.last_request.text == 'info':
#         return True

# def run_booking_hotels(_: Context, __: Pipeline) -> NodeLabel3Type:
#     print ('booking has done.')
#     return ("booking_flow", "booking_end", 1.0) 

# def func_response(ctx: Context, pipeline: Pipeline) -> Message:
#     print('1:', ctx.last_request)
#     print('2:', ctx.last_label)
#     print('3:', ctx.last_response)
#     return Message('sample message')

script = {
     "greeting_flow": {
         "start_node": {
             TRANSITIONS: {"greeting_node": cnd.exact_match(Message("/start"))},
         },
         "greeting_node" : {
             RESPONSE: TelegramMessage(
                 text = "Hello! I can help you where you can go! Please, choose the correct option:",
                 ui=TelegramUI(
                     buttons=[
                         Button(text='Find wonderful place'),
                         Button(text='Book a hotel or tickets'),
                         Button(text="I want nothing, I just wanna chat")
                     ],
                     is_inline=False,
                     row_width=4,
                 )
             ),
             TRANSITIONS: {
                 ("get_info_flow", "info_node_start"): cnd.exact_match(
                     TelegramMessage(text='Find wonderful place')
                 ),
                 ("booking_flow", "booking_node_start"): cnd.exact_match(
                     TelegramMessage(text='Book a hotel or tickets')
                 ),
                 ("chat_flow", "chat_node_start"): cnd.exact_match(
                     TelegramMessage(text='I want nothing, I just wanna chat')
                 )
             }
         },
         "fallback_node": {
             RESPONSE: Message("Please, repeat the request"),
             TRANSITIONS: {"greeting_node": cnd.exact_match(Message("/start"))},
         },
     },
     "booking_flow": {
         "booking_node_start": {
             RESPONSE: TelegramMessage(
                 'What do you want to book? Please, choose the correct option:',
                 ui=TelegramUI(
                     buttons=[
                         Button(text='Hotel'),
                         Button(text='Tickets')
                     ],
                     is_inline=False,
                     row_width=4,
                 )
                 ),
             TRANSITIONS: {
                 "booking_node_hotels": cnd.exact_match(
                     TelegramMessage(text='Hotel')
                 ),
                 "booking_node_tickets": cnd.exact_match(
                     TelegramMessage(text='Tickets')
                 )
                 }
         },
         "booking_node_hotels": {
             RESPONSE: TelegramMessage(
                 **{
                     "text": "Please write a preffered dates and country/region/city", "ui": RemoveKeyboard()
                 }
             ),
             TRANSITIONS: {
                 "booking_node_hotels": cnd.exact_match(Message('repeat')),
                 "booking_node_start": cnd.exact_match(Message('ok'))
                 }
         },
         "booking_node_tickets": {
             RESPONSE: TelegramMessage(
                 **{
                     "text": "Please write a preffered dates and country/region/city", "ui": RemoveKeyboard()
                 }
             ),
             TRANSITIONS: {}
         },
         "booking_end": {
             RESPONSE: Message("Thank you!"),
             TRANSITIONS: {("greeting_flow", "greeting_node"): cnd.true()}
         }
     },
     "get_info_flow": {
         "info_node_start": {
             RESPONSE: Message("Get info node"),
             TRANSITIONS: {}
         }
     },
     "chat_flow": {
         "chat_node_start": {
             RESPONSE: TelegramMessage(
                 **{
                     "text": "Let's chat!", "ui": RemoveKeyboard()
                 }
             ),
             TRANSITIONS: {"chat_node": cnd.true()}
         },
         "chat_node": {
             RESPONSE: chat,
             TRANSITIONS: {"chat_node": cnd.true()},
         },
     }
 }





# this variable is only for testing
happy_path = (
    (Message("/start"), Message("Hi")),
    (Message("Hi"), Message("Hi")),
    (Message("Bye"), Message("Hi")),
)


interface = PollingTelegramInterface(token=os.environ["TG_BOT"])

pipeline = Pipeline.from_script( 
    script=script,
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
    messenger_interface=interface,
    # The interface can be passed as a pipeline argument.
)



def main():
    print ('ok')
    pipeline.run()


if __name__ == "__main__" and is_interactive_mode():
    main()
