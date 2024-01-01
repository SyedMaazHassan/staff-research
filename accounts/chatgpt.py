

import os, json, requests
import traceback
from tqdm import tqdm
from django.conf import settings

class OpenAICall:
    CHATGPT_API_KEY = settings.CHATGPT_API_KEY

    def __init__(self, text):
        self.text = text
        self.prompt = None
        self.raw_content = None
        self.staff_list = []
        self.set_prompt()

    def get_ai_response(self):
        api_key = self.CHATGPT_API_KEY
        api_url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        prompt = self.prompt

        # Define the payload (data) for the API request
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful plain text to json converter.'},
                {'role': 'user', 'content': prompt}
            ]
        }

        try:
            print('- Fetching AI response')
            # Make the API request
            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Access the response data
            response_data = response.json()
            print('- AI response fetched successfully')
            result = response_data['choices'][0]['message']['content']
            print('- Saving raw AI output')
            self.raw_content = result
            print('- Converting into Python Dictionary')
            self.staff_list = json.loads(result)
            if not self.staff_list:
                print('- No staff found')
            print('- Staff list is ready')

        except requests.RequestException as req_exc:
            # Handle HTTP request-related errors
            print(f"Error making API request: {req_exc}")
            raise  # Re-raise the exception to propagate it further

        except json.JSONDecodeError as json_exc:
            # Handle JSON decoding errors
            print(self.raw_content)
            print(f"Error decoding JSON response: {json_exc}")
            raise  # Re-raise the exception to propagate it further

        except Exception as e:
            # Handle other unexpected errors
            print(f"Unexpected error: {e}")
            raise  # Re-raise the exception to propagate it further



    def set_prompt(self):
        print('- Setting up the prompt')
        tip = [
            {
                "name": "",
                "email": "",
                "job_title": ""
            },
            {
                "name": "",
                "email": "",
                "job_title": ""
            }
        ]
  

        # Construct the prompt with variables
        prompt = f'''
        Please convert the unstructured text from this /our-staff/ web page text into a structured JSON object that adheres to the following format. 
        It will be a list of staff members information. each staff member object has following:
            -name: only Full name of staff
            -email: only Email of staff
            -job_title: only Job title or designation of staff

            give /our-staff/ web page text:
            "{self.text}"

            Ensure that every staff member from raw text is captured accurately. Use proper quotes and maintain the structure provided.

            Sample Output:
            (format must be in valid json format, with proper quotes)
            {tip}

            Instructions:
            - Keep the name in 'name' key 
            - keep email in the 'email' key if exists
            - keep job title in the job_title key
            - if any field of staff member is not given, set empty string
            - Keep the Staff member object keys same as given in tip
            - Pick the name of staff member properly, avoid names of persons not included in staff list
            - Avoid adding irrelevant person information if not given in staff list
            - Avoid add text before or after json object. i just want json object, so it can be converted to python dictionary
            - If no Staff member found. Return only []
            Must do micro analysis of raw text to fill all fields of all staff members. 
            Fill as many staff objects as possible. 
        '''

        self.prompt = prompt



