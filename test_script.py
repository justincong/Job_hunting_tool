# Import necessary libraries
import json
from pychomsky.chchat import AzureOpenAIChatWrapper
from langchain.prompts import (
    PromptTemplate,
)
from pydantic import BaseModel
from typing import Optional


# very simple test
# model names are ebay pseudonyms listed on wiki
# https://pages.github.corp.ebay.com/jarvis/docs/Application%20developer%20SDK/#models-supported

model_name="azure-chat-completions-gpt35-turbo-0125-sandbox"
#Modify the values below to see different outputs
temperature=1.0
max_tokens=200

llm = AzureOpenAIChatWrapper( model_name=model_name, temperature=temperature, max_tokens=max_tokens)

#Be concise

#Not recommended. The prompt below is unnecessarily verbose.


context = """You are an expert resume matcher. Calculate how well a candidate's skills match a job's requirements, considering skill relevance, transferability, and industry context."""
        
prompt = f"""
        Calculate a match score (0-100) between these profile skills and job requirements:

        Profile Skills: {', '.join('hello world')}

        Job Analysis: {json.dumps("cool", indent=2)}

        Consider:
        1. Direct skill matches (exact or similar technologies)
        2. Transferable skills (related technologies, frameworks)
        3. Soft skills alignment
        4. Experience level compatibility
        5. Industry relevance

        Provide your analysis in this JSON format:
        {{
            "match_score": 85.5,
            "matching_skills": ["skill1", "skill2"],
            "missing_critical_skills": ["skill1", "skill2"],
            "transferable_skills": ["skill1", "skill2"],
            "skill_gaps": ["gap1", "gap2"],
            "recommendations": ["rec1", "rec2"]
        }}

        Return only valid JSON.
        """

from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content=context),
    HumanMessage(content=prompt),
]

###########################################
# Invoke LLM
###########################################

response=llm.invoke(messages)

print(response)
     
# #Recommended. The prompt below is to the point and concise.
# prompt = "Suggest a name for a flower shop that sells bouquets of dried flowers"

# messages = [
#     SystemMessage(content=context),
#     HumanMessage(content=prompt),
# ]
# response=llm.invoke(messages)
# print(response)
     