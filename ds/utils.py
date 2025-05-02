import os
import json
from deepseek import *
import openai
import random
from message_list import Message_list
model="deepseek"

def llm(message_list):
    try:
        ans=make_sure_execute_function(get_multi_round_response,messages=message_list)
    except openai.APITimeoutError:
        ans="请求超时"
    except Exception as e:
        ans="错误信息"+str(e)

    return ans


def get_response(message_list,content):
    message_list.append_message(role="user",content=content)
    response=llm(message_list.message_list)
    message_list.append_message(role="assistant",content=response)
    message_list.show_last_message()