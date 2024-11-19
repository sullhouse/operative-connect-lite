from openai import OpenAI
import json
import requests

# Load the OpenAI API key from the JSON file
with open('OpenAI_Operative_Connect_Lite_API_Key.json') as f:
    api_key_data = json.load(f)
    client = OpenAI(
        api_key=api_key_data['key'],  # this is also the default, it can be omitted
    )

# Define the intents dictionary
with open('intents.json') as f:
    intents_dict = json.load(f)

def determine_intent(user_query):
    # Define the intent options
    intents = list(intents_dict.keys())
    
    # Use GPT to classify the intent
    intents_list = ", ".join(intents)
    messages = [
        {"role": "system", "content": f"You are an assistant that classifies user queries into predefined intents. "
                                      f"The possible intents are: {intents_list}. If the query doesn't match any intent, "
                                      f"or the intent is ambiguous, ask a brief clarifying question. "
                                      "Respond in the format 'Intent: <intent>' or 'Clarification: <question>'."},
        {"role": "user", "content": f"Query: {user_query}. What is the intent?"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=50
    )
    
    intent = response.choices[0].message.content.strip()
    
    if intent.startswith("Intent:"):
        intent = intent.replace("Intent:", "").strip()
        intent = intent.replace(".", "").strip()
        required_params = intents_dict[intent]["required_params"]
        optional_params = intents_dict[intent]["optional_params"]
        parameters_dict = {}
        if len(required_params) > 0 or len(optional_params) > 0:
            parameters_dict = determine_parameters(user_query, intent, ", ".join(intents_dict[intent]["required_params"] + intents_dict[intent]["optional_params"]))
            if missing_params(parameters_dict, required_params):
                intent = f"Clarification: Please provide the following parameters: {', '.join(missing_params(parameters_dict, required_params))}"
                return intent, False
        execute_intent(intent, parameters_dict)
        return intent, True
    elif intent.startswith("Clarification:"):
        intent = intent.replace("Clarification:", "").strip()
        intent = intent.replace(".", "").strip()
        return intent, False
    else:
        intent = "unknown"

    return intent, False

def determine_parameters(user_query, intent, parameters_list):
    # Use GPT to determine the parameters
    messages = [
        {"role": "system", "content": f"You are an assistant that extracts parameters for the '{intent}' intent. "
                                      f"You are looking for the following parameters: {parameters_list}. "
                                      f"Respond with the parameters in the format '<parameter_name>: <parameter_value>' with each on a new line."
                                      "If a parameter is not present, respond with '<parameter_name>: none'."},
        {"role": "user", "content": f"Query: {user_query}. What are the parameters?"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=50
    )
    
    parameters = response.choices[0].message.content.strip()
    parameters_list = parameters.split("\n")
    parameters_dict = {}
    for parameter in parameters_list:
        key, value = parameter.split(":")
        parameters_dict[key.strip()] = value.strip()
    
    return parameters_dict

def missing_params(parameters_dict, required_params):
    missing_params = [param for param in required_params if param not in parameters_dict or parameters_dict[param] == "none"]
    return missing_params

def execute_intent(intent, parameters_dict):
    # Execute the intent by calling the API
    api_url = intents_dict[intent]["api_url"]
    api_method = intents_dict[intent]["api_method"]
    
    if api_method == "GET":
        headers = {
            'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImRhbi5icm93bkBleGFtcGxlcGV0c3RvcmUuY29tIiwiZXhwIjoxNzMxOTkyMDI5fQ.57OCqP7JRjiYEKXtpHhemxwfCCXnxOmNp1vbvNU0zIw'
        }
        response = requests.get(api_url, headers=headers, params=parameters_dict)
    else:
        headers = {
            'Content-Type': 'application/json',
            'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImRhbi5icm93bkBleGFtcGxlcGV0c3RvcmUuY29tIiwiZXhwIjoxNzMxOTkyMDI5fQ.57OCqP7JRjiYEKXtpHhemxwfCCXnxOmNp1vbvNU0zIw'
        }
        response = requests.post(api_url, headers=headers, json=parameters_dict)
    print(beautify_response(response.text))

def beautify_response(response_text):
    # Use GPT to beautify the response
    messages = [
        {"role": "system", "content": "You are an assistant that takes data in json format and turns it into human readable lists and tables so that it is easy to read for a human. "
                                      "Respond with the well formatted response."},
        {"role": "user", "content": f"Response text: {response_text}. Format the response text."}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=1000
    )
    
    return response.choices[0].message.content.strip()
# Test the function
if __name__ == "__main__":
    user_inputs = [
        "list my organizations",
        "create a new organization called OpenAI",
        "what are the partnerships?",
        "map juan@hello.com to OpenAI",
        "what partnerships exist?"
    ]

    for user_input in user_inputs:
        print(f"User Input: {user_input}")
        intent, is_intent = determine_intent(user_input)
        if is_intent:
            print(f"Detected Intent: {intent}")
        else:
            print(f"Clarification Question: {intent}")
