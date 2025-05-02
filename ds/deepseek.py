import openai
from openai import OpenAI
import traceback
import time
import json
import os
import requests

client = OpenAI(
    api_key="",
    base_url="https://api.deepseek.com"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Determine weather in my location",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state e.g. San Francisco, CA",
                    },
                    "day": {"type": "string", "enum": ["今天", "明天", "后天"]},
                },
                "additionalProperties": False,
                "required": ["location", "day"],
            },
        },
    },
]


def get_weather(location, day):
    """
    location:城市名
    day: "type": "string", "enum": ["今天", "明天", "后天"]
    """
    res=requests.get(f"http://v1.yiketianqi.com/api?unescape=1&version=v91&appid=85383488&appsecret=xHlN3MzY&city={location}")
    j=json.loads(res.text)

    if day == "今天":
        tq = j["data"][0]
    elif day == "明天":
        tq = j["data"][1]
    elif day == "后天":
        tq = j["data"][2]
    else:
        tq={}

    ans = f"""{location}{tq['date']}天气:{tq['tem2']}℃到{tq['tem1']}℃，{tq['wea_day']}转{tq['wea_night']}
空气质量{tq['air_level']} {tq['air_tips']}
"""
    if "alarm" in tq.keys():
        alarm=""
        for a in tq['alarm']:
            alarm=alarm+"< "+a['alarm_title']+" >\n"+a['alarm_content']+"\n"
        ans=ans+alarm

    return ans


def call_tool(message):
    # Extract the arguments for get_delivery_date
    # Note this code assumes we have already determined that the model generated a function call.
    # See below for a more production ready example that shows how to check if the model generated a function call
    tool_calls = message.tool_calls[0]
    arguments = json.loads(tool_calls.function.arguments)
    function_name = tool_calls.function.name

    if function_name == "get_weather":

        location = arguments.get("location")
        day = arguments.get("day")

        # Call the get_weather function
        weather = get_weather(location, day)
        return weather


def analyse_message(message):
    if message.tool_calls:
        return call_tool(message)
    else:
        return message.content


def get_single_round_response(
    model="deepseek-chat",
    system_prompt="You are a helpful assistant",
    prompt="hello",
    temperature=1.3,
):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        tools=tools,
        temperature=temperature,
        stream=False,
    )
    return analyse_message(response.choices[0].message)


def get_multi_round_response(messages, model="deepseek-chat", temperature=1.3):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        temperature=temperature,
        stream=False,
    )

    return analyse_message(response.choices[0].message)


def make_sure_execute_function(func_name, *args, **kwargs):
    if func_name and callable(func_name):
        while True:
            try:
                res = func_name(*args, **kwargs)
                return res
            except openai.APITimeoutError:
                pass
                # client = OpenAI(api_key="sk-30a8aa44c12147cf90996fc3dd5d01bb", base_url="https://api.deepseek.com")

            except:
                traceback.print_exc()
                time.sleep(6)
    else:
        raise ValueError(f"Function '{func_name}' not found")
