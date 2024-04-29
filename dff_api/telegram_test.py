import os

from dff.script import conditions as cnd
from dff.script import labels as lbl
from dff.script import TRANSITIONS, RESPONSE, Context, NodeLabel3Type, Message
from dff.messengers.telegram import PollingTelegramInterface
from dff.pipeline import Pipeline
from dff.utils.testing.common import is_interactive_mode

import re

from dff.script import GLOBAL, TRANSITIONS, RESPONSE, Message
import dff.script.conditions as cnd
import dff.script.labels as lbl
from dff.pipeline import Pipeline
from dff.utils.testing.common import (
    check_happy_path,
    is_interactive_mode,
    run_interactive_mode,
)


#import model

def func_response_classifier_request(ctx: Context, pipeline: Pipeline) -> bool:
    request = ctx.last_request.text
    from_model = None
    res = False
    if from_model in ['info', 'booking']:
        res = True
    return res
    

def func(ctx: Context, pipeline: Pipeline) -> bool:
    print('1:', ctx.last_request)
    print('2:', ctx.last_label)
    print('3:', ctx.last_response)
    if ctx.last_request.text == 'info':
        return True

def run_booking_hotels(_: Context, __: Pipeline) -> NodeLabel3Type:
    print ('booking has done.')
    return ("booking_flow", "booking_end", 1.0) 

def func_response(ctx: Context, pipeline: Pipeline) -> Message:
    print('1:', ctx.last_request)
    print('2:', ctx.last_label)
    print('3:', ctx.last_response)
    return Message('sample message')

script = { 
     "greeting_flow": {
         "start_node": {
             TRANSITIONS: {"greeting_node": cnd.exact_match(Message("/start"))},
         },
         "greeting_node": {
             RESPONSE: Message("Greeting node"),
             TRANSITIONS: {
                 ("get_info_flow", "info_node_start"): cnd.exact_match(Message('info')),
                 #("get_info_flow", "info_node_start"): func,
                 ("booking_flow", "booking_node_start"): cnd.exact_match(Message('book')),
                 #lbl.repeat(): cnd.true()
                 },
         },
         "fallback_node": {
             RESPONSE: Message("Please, repeat the request"),
             TRANSITIONS: {"greeting_node": cnd.exact_match(Message("/start"))},
         },
     },
     "booking_flow": {
         "booking_node_start": {
             RESPONSE: Message('Start booking'),
             TRANSITIONS: {
                 "booking_node_hotels": cnd.exact_match(Message("hotel")),
                 "booking_node_tickets": cnd.exact_match(Message("tickets"))
                 }
         },
         "booking_node_hotels": {
             RESPONSE: func_response,
             TRANSITIONS: {
                 "booking_node_hotels": cnd.exact_match(Message('repeat')),
                 "booking_node_start": cnd.exact_match(Message('ok'))
                 }
         },
         "booking_node_tickets": {
             RESPONSE: Message("Booking tickets"),
             TRANSITIONS: {}
         },
         "booking_end": {
             RESPONSE: Message("Thank you!"),
             TRANSITIONS: {("greeting_flow", "greeting_node"): cnd.true}
         }
     },
     "get_info_flow": {
         "info_node_start": {
             RESPONSE: Message("Get info node"),
             TRANSITIONS: {}
         }
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
