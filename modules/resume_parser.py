import PyPDF2
import pdfplumber
from docx import Document
import re
from typing import Dict, List, Optional

class ResumeParser:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'machine learning', 'data analysis', 'project management', 'leadership',
            'communication', 'teamwork', 'problem solving', 'analytical', 'strategic'
        ]
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            # Try with pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e2:
                raise Exception(f"Could not extract text from PDF: {str(e2)}")
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Could not extract text from DOCX: {str(e)}")
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone regex (various formats)
        phone_pattern = r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn URL
        linkedin_pattern = r'(https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # Extract name (assumes first line or first few words)
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(char in line for char in ['@', 'http', '+1', '(']):
                # Simple heuristic: name is likely 2-4 words, all title case
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.istitle() for word in words):
                    contact_info['name'] = line
                    break
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text based on keyword matching"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Look for skills sections
        skills_section_pattern = r'(?i)skills?\s*[:\-]?\s*(.+?)(?=\n\s*\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text)
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            additional_skills = re.split(r'[,\n\|;]', skills_text)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from text"""
        experiences = []
        
        # Look for experience/work sections
        exp_pattern = r'(?i)(experience|work\s+history|employment|professional\s+experience)\s*[:\-]?\s*(.+?)(?=\n\s*\n[A-Z]|\neducation|\nskills|$)'
        exp_match = re.search(exp_pattern, text, re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(2)
            
            # Split by potential job entries (look for dates or company patterns)
            job_pattern = r'(\d{4}[-–]\d{4}|\d{4}[-–]present|\w+\s+\d{4}[-–]\w+\s+\d{4})'
            jobs = re.split(job_pattern, exp_text)
            
            for i in range(1, len(jobs), 2):  # Every other element after split
                if i+1 < len(jobs):
                    duration = jobs[i].strip()
                    job_text = jobs[i+1].strip()
                    
                    lines = [line.strip() for line in job_text.split('\n') if line.strip()]
                    if lines:
                        title_company = lines[0]
                        description = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                        
                        experiences.append({
                            'title': title_company,
                            'company': '',
                            'duration': duration,
                            'description': description
                        })
        
        return experiences
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from text"""
        education = []
        
        # Look for education section
        edu_pattern = r'(?i)education\s*[:\-]?\s*(.+?)(?=\n\s*\n[A-Z]|\nexperience|\nskills|$)'
        edu_match = re.search(edu_pattern, text, re.DOTALL)
        
        if edu_match:
            edu_text = edu_match.group(1)
            lines = [line.strip() for line in edu_text.split('\n') if line.strip()]
            
            for line in lines:
                if any(word in line.lower() for word in ['university', 'college', 'bachelor', 'master', 'phd', 'degree']):
                    education.append({
                        'institution': line,
                        'degree': '',
                        'year': ''
                    })
        
        return education
    
    def parse_resume(self, file) -> Dict:
        """Main method to parse resume and extract all information"""
        try:
            # Determine file type and extract text
            if file.type == "application/pdf":
                text = self.extract_text_from_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = self.extract_text_from_docx(file)
            else:
                raise ValueError("Unsupported file type. Please upload PDF or DOCX files.")
            
            # Extract different sections
            contact_info = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            experiences = self.extract_experience(text)
            education = self.extract_education(text)
            
            # Create structured data
            parsed_data = {
                'name': contact_info.get('name', ''),
                'email': contact_info.get('email', ''),
                'phone': contact_info.get('phone', ''),
                'linkedin': contact_info.get('linkedin', ''),
                'location': '',  # Hard to extract reliably
                'website': '',
                'summary': '',  # Will be extracted separately if needed
                'skills': ', '.join(skills),
                'experiences': experiences,
                'education': education,
                'raw_text': text
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")