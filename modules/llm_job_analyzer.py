import json
import os
from typing import Dict, List
# from openai import OpenAI
import streamlit as st
from pychomsky.chchat import GCPVertexAnthropicChatWrapper

import warnings
warnings.filterwarnings("ignore")
# import os
import sys


from langchain import PromptTemplate
from langchain.chains import LLMChain
from pychomsky.chchat import AzureOpenAIChatWrapper

class LLMJobAnalyzer:
    def __init__(self):
        
        """Initialize pychomsky client with OpenAI-compatible API calls"""

        # Default model name
        
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make API call to LLM"""
        try:
            model_name="azure-chat-completions-gpt35-turbo-0125-sandbox"

            # Adjusted parameters for better analysis
            temperature=0.1  # Lower temperature for consistent analysis
            max_tokens=2000  # Increased for complex JSON responses
            
            llm = AzureOpenAIChatWrapper(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
            
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            response = llm.invoke(messages)
            print(f"{messages}")

            return response
        except Exception as e:
            st.error(f"Error calling Pychomsky API: {str(e)}")
            raise e
    
    def analyze_job_description(self, job_text: str) -> Dict:
        """Use LLM to comprehensively analyze job description"""
        
        system_prompt = """You are an expert HR analyst and resume writer. Analyze job descriptions and extract structured information to help tailor resumes effectively."""
        
        analysis_prompt = f"""
        Analyze this job description and extract the following information in JSON format:

        {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...],
            "experience_level": "entry|mid|senior|executive",
            "required_years": "number or range",
            "requirements": ["requirement1", "requirement2", ...],
            "responsibilities": ["responsibility1", "responsibility2", ...],
            "priority_skills": [
                {{"skill": "skill_name", "importance": "high|medium|low", "category": "technical|soft"}}
            ],
            "keywords": ["keyword1", "keyword2", ...],
            "company_values": ["value1", "value2", ...],
            "industry": "industry_name"
        }}

        Focus on:
        1. Technical skills (programming languages, tools, frameworks, technologies)
        2. Soft skills (leadership, communication, problem-solving, etc.)
        3. Experience level based on job title and requirements
        4. Must-have vs nice-to-have requirements
        5. Key responsibilities that show what the role involves
        6. Industry-specific terminology and buzzwords
        7. Company culture indicators

        Job Description:
        {job_text}

        Return only valid JSON, no additional text.
        """
        
        try:
            response = self._call_llm(analysis_prompt, system_prompt)
            
            # Clean response and parse JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            analysis = json.loads(response)
            
            # Add computed fields for compatibility with existing code
            analysis['skills'] = {
                'technical': analysis.get('technical_skills', []),
                'soft': analysis.get('soft_skills', []),
                'all_categories': {
                    'technical': analysis.get('technical_skills', []),
                    'soft': analysis.get('soft_skills', [])
                }
            }
            
            return analysis
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing LLM response as JSON: {str(e)}")
            # Fallback to basic analysis
            return self._fallback_analysis(job_text)
        except Exception as e:
            st.error(f"Error in job analysis: {str(e)}")
            return self._fallback_analysis(job_text)
    
    def calculate_match_score(self, profile_skills: List[str], job_analysis: Dict) -> float:
        """Use LLM to calculate intelligent match score between profile and job"""
        
        if not profile_skills:
            return 0.0
        
        system_prompt = """You are an expert resume matcher. Calculate how well a candidate's skills match a job's requirements, considering skill relevance, transferability, and industry context."""
        
        match_prompt = f"""
        Calculate a match score (0-100) between these profile skills and job requirements:

        Profile Skills: {', '.join(profile_skills)}

        Job Analysis: {json.dumps(job_analysis, indent=2)}

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
        
        try:
            response = self._call_llm(match_prompt, system_prompt)
            
            # Clean and parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            match_data = json.loads(response)
            return match_data.get('match_score', 0.0)
            
        except Exception as e:
            st.warning(f"Error calculating LLM match score, using fallback: {str(e)}")
            return self._fallback_match_score(profile_skills, job_analysis)
    
    def generate_tailoring_recommendations(self, profile: Dict, job_analysis: Dict) -> Dict:
        """Generate specific recommendations for tailoring resume to job"""
        
        system_prompt = """You are an expert resume writer. Provide specific, actionable recommendations for tailoring a resume to a specific job."""
        
        recommendations_prompt = f"""
        Given this profile and job analysis, provide tailoring recommendations:

        Profile Summary:
        - Name: {profile.get('name', 'N/A')}
        - Skills: {profile.get('programming_skills', '')}, {profile.get('technologies', '')}, {profile.get('language_skills', '')}, {profile.get('certifications', '')}
        - Experience: {len(profile.get('experiences', []))} positions
        - Education: {len(profile.get('education', []))} entries

        Job Analysis: {json.dumps(job_analysis, indent=2)}

        Provide recommendations in JSON format:
        {{
            "skills_reordering": ["skill1", "skill2", ...],
            "experience_prioritization": [
                {{"title": "Job Title", "company": "Company", "priority_score": 9}}
            ],
            "keywords_to_emphasize": ["keyword1", "keyword2"],
            "achievements_to_highlight": ["achievement1", "achievement2"],
            "summary_focus": "What to emphasize in professional summary",
            "cover_letter_points": ["point1", "point2"]
        }}

        Focus on:
        1. Which skills should appear first
        2. How to reorder work experience by relevance
        3. Keywords to naturally incorporate
        4. Specific achievements that align with job requirements

        Return only valid JSON.
        """
        
        try:
            response = self._call_llm(recommendations_prompt, system_prompt)
            
            # Clean and parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            return json.loads(response)
            
        except Exception as e:
            st.warning(f"Error generating tailoring recommendations: {str(e)}")
            return {}
    
    def _fallback_analysis(self, job_text: str) -> Dict:
        """Basic fallback analysis if LLM fails"""
        return {
            'technical_skills': [],
            'soft_skills': [],
            'experience_level': 'unknown',
            'requirements': [],
            'responsibilities': [],
            'priority_skills': [],
            'keywords': [],
            'skills': {
                'technical': [],
                'soft': [],
                'all_categories': {}
            }
        }
    
    def _fallback_match_score(self, profile_skills: List[str], job_analysis: Dict) -> float:
        """Simple fallback match calculation"""
        if not profile_skills:
            return 0.0
        
        job_skills = job_analysis.get('technical_skills', []) + job_analysis.get('soft_skills', [])
        if not job_skills:
            return 0.0
        
        profile_skills_lower = [skill.lower().strip() for skill in profile_skills]
        job_skills_lower = [skill.lower().strip() for skill in job_skills]
        
        matching = len(set(profile_skills_lower) & set(job_skills_lower))
        return (matching / len(job_skills_lower)) * 100