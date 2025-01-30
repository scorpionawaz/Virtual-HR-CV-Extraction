#!/usr/bin/env python
# coding: utf-8

# # Document to Structured Data

# In[1]:


# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')

# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"

# ## Set Up Azure OpenAI

# In[2]:

import openai
# from dotenv import load_dotenv



# Set up Azure OpenAI
# load_dotenv()
# openai.api_type = "azure"
# openai.api_base = "https://cog-z6b6grosjkvfy.openai.azure.com/"
# openai.api_version = "2023-03-15"
# openai.api_key = "cdce6e9e7c774c44a42677efcdec8f38"

openai.api_type = "azure"
openai.api_base = "https://doamin.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "paste your API key here"
# ## Deploy a Model

# In[3]:


# id of desired_model
desired_model = 'gpt-4-32k' 
desired_capability = 'chat_completion' # apply as completion, since gpt-4 is only released as chat in Azure OpenAI

# list models deployed with
deployment_id = None
result = openai.Deployment.list()

for deployment in result.data:
    if deployment["status"] != "succeeded":
        continue
    
    model = openai.Model.retrieve(deployment["model"])
    print(model)
    # check if desired_model is deployed, and if it has 'completion' capability
    if model["id"] == desired_model and model['capabilities'][desired_capability]:
        deployment_id = deployment["id"]
        
# # if no model deployed, deploy one
# if not deployment_id:
#     print('No deployment with status: succeeded found.')

#     # Deploy the model
#     print(f'Creating a new deployment with model: {desired_model}')
#     result = openai.Deployment.create(model=desired_model, scale_settings={"scale_type":"standard"})
#     deployment_id = result["id"]
#     print(f'Successfully created {desired_model} that supports text {desired_capability} with id: {deployment_id}.')
# else:
#     print(f'Found a succeeded deployment of "{desired_model}" that supports text {desired_capability} with id: {deployment_id}.')


# ## Request API

# In[4]:


# this is for just testing , this code is just sends an simple query

# response = openai.ChatCompletion.create(
#   engine = deployment_id,
#   messages = [{"role":"user","content":"who are you?"},],
#   temperature=0.5,
#   max_tokens=2600,
#   top_p=0.95,
#   frequency_penalty=0,
#   presence_penalty=0, 
#   stop=None)

# response['choices'][0]['message']['role']
# response['choices'][0]['message']['content']


# In[6]:


def request_api(messages):
    response = openai.ChatCompletion.create(
        engine = "deployment-7e421a38499b4a798796e17358482e23",
        messages = messages,
        temperature=0,
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop='###')
    return response


# ## Get Structured Data

# In[7]:


def get_structured_data(document, prompt_postfix,):
    content = prompt_postfix.replace('<document>', document)
    messages = [{"role":"user","content":content},]; #print(messages)
    structured_data = request_api(messages)
    return structured_data


# ### Document Type: Resume
# ===========================================================================
# In[17]:

# reads the txt /////  you can uncomment this if you want to read txt
fname = "data/resume.txt"
encodings = ['utf-8', 'latin-1', 'utf-16']

for encoding in encodings:
    try:
        with open(fname, 'r', encoding=encoding) as f:
            document = f.readlines()
        
        # convert list to str
        document = ' '.join(document)
        print(document)
        break  # Stop looping if the file is successfully read
    except UnicodeError:
        continue  # Move to the next encoding if there is a Unicode error

# =============================================================================

# # read the word ////you can uncomment this if you want to read word
# import docx

# fname = "data/resume.docx"

# document = ""
# doc = docx.Document(fname)

# for paragraph in doc.paragraphs:
#     document += paragraph.text

# print(document)
# =============================================================================

# # read the pdf
# import PyPDF2

# fname = "data/resume.pdf"

# with open(fname, 'rb') as f:
#     reader = PyPDF2.PdfReader(f)
#     num_pages = len(reader.pages)
#     document = ""
#     for page_num in range(num_pages):
#         page = reader.pages[page_num]
#         text = page.extract_text()
#         document += text

# print(document)

# ===========================================================================
# In[18]:

# prompt is modified by nawaz

# prompt
prompt_postfix = """ <document>
  \n###
  \nExtract the key sections from the resume above into json . 
  it should not look like this , 
  "Skills": [
    "Python",
    "Java",
    "C++",
    "Django",
    "Ruby on Rails",
    "MySQL",
    "MongoDB",
    "Problem-solving",
    "Analytical abilities",
    "Communication",
    "Teamwork"
  ],
  
  define like skill 1 , skill2 etc , also do this with experiences and projects .dont use square braces.extracted data should not be lenghty . is should be so short , put multiple items in other attribute.
  .
"""
structured_data = get_structured_data(document, prompt_postfix)


# In[19]:


print(structured_data['choices'][0]['message']['content'])


# In[20]:


import json

output_string = structured_data['choices'][0]['message']['content']

# here the type casting has been done 
output_dict = json.loads(output_string)

# In[21]:


type(output_dict)

# In[ ]:

# In[22]:
with open('data.json', 'w') as file:
    # Write the dictionary to the JSON file
    json.dump(output_dict, file)


# In[23]: 

from flask import Flask, render_template, send_from_directory
import csv
import pandas as pd
import json

with open('data.json') as file:
    data = json.load(file)

# creating an csv file
df = pd.json_normalize(data)
df.to_csv('data.csv', index=False)



# In[ ]:

app = Flask(__name__)

@app.route('/')
def index():
    data = []
    with open('data.csv', 'r') as file:
        csv_data = csv.DictReader(file)
        for row in csv_data:
            data.append(row)
    return render_template('index.html', data=data)

@app.route('/open-file')
def open_file():
    return send_from_directory('.', 'data/resume.txt')

if __name__ == '__main__':
    app.run(port=5001)


# In[ ]:



# In[ ]:




