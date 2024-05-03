import os

from dff.script import conditions as cnd
from dff.script import labels as lbl
from dff.script import GLOBAL, TRANSITIONS, RESPONSE, MISC, Context, NodeLabel3Type, Message
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
from dff.script.core.message import Image, Attachments

def extract_data(ctx: Context, _: Pipeline):  # A function to extract data with
    message = ctx.last_request
    text = ''
    if message is None:
        return text, None
    update = getattr(message, "update", None)
    if message.text is not None:
        text = message.text
    elif message.update.caption is not None:
        text = message.update.caption
    
    if update.photo is None:
        return text, None
    #if not isinstance(update, Message):
    #    return
    #if (
        # check attachments in update properties
    #    not update.photo
    #    and not (update.document and update.document.mime_type == "image/jpeg")
    #):
    #    return
    photo = update.document or update.photo[-1]
    file = interface.messenger.get_file(photo.file_id)
    result = interface.messenger.download_file(file.file_path)
    with open("001.jpg", "wb+") as new_file:
        new_file.write(result)
    return text, result


#import model

MODES = {
    'INFO_MODE': {'flow': 'get_info_flow',
                  'node': 'info_node_start'
                  },
    'BOOKING_MODE': {'flow': 'booking_flow',
                     'node': 'booking_node_start'},
    'CHAT_MODE': {'flow': 'chat_flow',
                  'node': 'chat_node_start'}
    }


#processor, model = model.get_model()

def chat(ctx: Context, pipeline: Pipeline) -> Message:
    if ctx.last_response == "Let's chat!":
        text = ''
#    else:
#        prompt = '[INST]' + ctx.last_request.text + '[/INST]'
#        inputs = processor(prompt, None, return_tensors="pt").to("cuda:0")
#        output = model.generate(**inputs, max_new_tokens=100)
#        text = processor.decode(output[0], skip_special_tokens=True)
#        print (text)
    return Message(text)

def func1(ctx: Context, pipeline: Pipeline):
    ctx.misc['var0'] = '111222333'
    print (ctx.misc['var0'])
    return ctx.misc['var0']


def func(ctx: Context, pipeline: Pipeline) -> bool:
    ctx.misc['class'] = ctx.last_request.text
#    print('1:', ctx.last_request)
#    print('2:', ctx.last_label)
#    print('3:', ctx.last_response)
    return True


def get_answer_from_llm(str, img=None, **kwargs):
    return {'transit': str, 'country': 'USA'}

def get_node_by_request_type(ctx: Context, _: Pipeline) -> NodeLabel3Type:
    request_text, request_image = extract_data(ctx, pipeline)
    print (request_text)
    res_llm = get_answer_from_llm(request_text, request_image)
    request_class = res_llm['transit']
    ctx.misc = {'country': res_llm['country']}
    print (res_llm)
    if request_class in list(MODES.keys()):
        res = (MODES[request_class]['flow'], MODES[request_class]['node'], 1.0)
    else:
        res = ("greeting_flow", "fallback_node", 1.0)
    return res


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
             ),
             TRANSITIONS: {
                 get_node_by_request_type: cnd.true(),
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
