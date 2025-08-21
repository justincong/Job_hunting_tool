import re
from collections import Counter
from typing import Dict, List, Set
import string

class JobAnalyzer:
    def __init__(self):
        # Basic English stopwords (no NLTK dependency)
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'will', 'can', 'could', 'should', 'would', 'may', 'might',
            'must', 'shall', 'to', 'from', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very'
        }
        
        # Common technical skills and keywords
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'data': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'tableau', 'powerbi'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'figma', 'photoshop']
        }
        
        # Soft skills keywords
        self.soft_skills = [
            'leadership', 'teamwork', 'communication', 'problem solving', 'analytical',
            'creative', 'innovative', 'collaborative', 'adaptable', 'organized',
            'detail-oriented', 'self-motivated', 'proactive', 'strategic', 'mentoring'
        ]
        
        # Experience level indicators
        self.experience_levels = {
            'entry': ['entry', 'junior', 'associate', 'graduate', 'trainee', '0-2 years'],
            'mid': ['mid', 'intermediate', 'experienced', '3-5 years', '2-4 years'],
            'senior': ['senior', 'lead', 'principal', 'staff', '5+ years', '6+ years'],
            'executive': ['director', 'manager', 'head', 'chief', 'vp', 'vice president']
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)
        
        return text.strip()
    
    def extract_skills(self, job_text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from job description"""
        processed_text = self.preprocess_text(job_text)
        
        found_skills = {
            'technical': [],
            'soft': [],
            'all_categories': {}
        }
        
        # Extract technical skills by category
        for category, skills in self.technical_skills.items():
            category_skills = []
            for skill in skills:
                if skill in processed_text:
                    category_skills.append(skill)
                    found_skills['technical'].append(skill)
            
            if category_skills:
                found_skills['all_categories'][category] = category_skills
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in processed_text:
                found_skills['soft'].append(skill)
        
        return found_skills
    
    def extract_requirements(self, job_text: str) -> List[str]:
        """Extract job requirements and qualifications"""
        requirements = []
        
        # Look for requirements sections
        req_patterns = [
            r'(?i)requirements?\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nresponsibilities|\nqualifications|$)',
            r'(?i)qualifications?\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nresponsibilities|\nrequirements|$)',
            r'(?i)must\s+have\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nnice\s+to\s+have|\npreferred|$)'
        ]
        
        for pattern in req_patterns:
            match = re.search(pattern, job_text, re.DOTALL)
            if match:
                req_text = match.group(1)
                # Split by bullet points or new lines
                items = re.split(r'[•\-\*\n]', req_text)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 10:  # Filter out very short items
                        requirements.append(item)
        
        return requirements
    
    def extract_responsibilities(self, job_text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        
        # Look for responsibilities sections
        resp_patterns = [
            r'(?i)responsibilities\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nrequirements|\nqualifications|$)',
            r'(?i)duties\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nrequirements|\nqualifications|$)',
            r'(?i)you\s+will\s*[:\-]?\s*(.+?)(?=\n\s*\n|\nrequirements|\nqualifications|$)'
        ]
        
        for pattern in resp_patterns:
            match = re.search(pattern, job_text, re.DOTALL)
            if match:
                resp_text = match.group(1)
                # Split by bullet points or new lines
                items = re.split(r'[•\-\*\n]', resp_text)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 10:
                        responsibilities.append(item)
        
        return responsibilities
    
    def extract_experience_level(self, job_text: str) -> str:
        """Determine required experience level"""
        processed_text = self.preprocess_text(job_text)
        
        # Check for experience level indicators
        for level, indicators in self.experience_levels.items():
            for indicator in indicators:
                if indicator in processed_text:
                    return level
        
        # Check for years of experience
        years_pattern = r'(\d+)[\+\-\s]*years?\s+(?:of\s+)?experience'
        years_match = re.search(years_pattern, processed_text)
        if years_match:
            years = int(years_match.group(1))
            if years <= 2:
                return 'entry'
            elif years <= 5:
                return 'mid'
            else:
                return 'senior'
        
        return 'unknown'
    
    def simple_tokenize(self, text: str) -> List[str]:
        """Simple tokenization without NLTK dependency"""
        # Split on whitespace and punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def extract_keywords(self, job_text: str, top_n: int = 20) -> List[tuple]:
        """Extract most important keywords from job description"""
        processed_text = self.preprocess_text(job_text)
        
        # Simple tokenization
        words = self.simple_tokenize(processed_text)
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Return top keywords
        return word_freq.most_common(top_n)
    
    def analyze_job_description(self, job_text: str) -> Dict:
        """Comprehensive analysis of job description"""
        if not job_text or not job_text.strip():
            raise ValueError("Job description cannot be empty")
        
        analysis = {
            'skills': self.extract_skills(job_text),
            'requirements': self.extract_requirements(job_text),
            'responsibilities': self.extract_responsibilities(job_text),
            'experience_level': self.extract_experience_level(job_text),
            'keywords': self.extract_keywords(job_text),
            'priority_skills': [],
            'matching_score': 0
        }
        
        # Determine priority skills (skills mentioned multiple times or in requirements)
        all_skills = analysis['skills']['technical'] + analysis['skills']['soft']
        req_text = ' '.join(analysis['requirements']).lower()
        
        priority_skills = []
        for skill in all_skills:
            skill_count = job_text.lower().count(skill.lower())
            if skill_count > 1 or skill.lower() in req_text:
                priority_skills.append({
                    'skill': skill,
                    'frequency': skill_count,
                    'in_requirements': skill.lower() in req_text
                })
        
        # Sort by frequency and requirement presence
        priority_skills.sort(key=lambda x: (x['in_requirements'], x['frequency']), reverse=True)
        analysis['priority_skills'] = priority_skills
        
        return analysis
    
    def calculate_match_score(self, profile_skills: List[str], job_analysis: Dict) -> float:
        """Calculate how well profile skills match job requirements"""
        if not profile_skills:
            return 0.0
        
        profile_skills_lower = [skill.lower().strip() for skill in profile_skills]
        job_skills = job_analysis['skills']['technical'] + job_analysis['skills']['soft']
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        if not job_skills_lower:
            return 0.0
        
        # Calculate intersection
        matching_skills = set(profile_skills_lower) & set(job_skills_lower)
        
        # Weight by priority skills
        priority_weight = 0
        for priority_skill in job_analysis.get('priority_skills', []):
            if priority_skill['skill'].lower() in profile_skills_lower:
                priority_weight += 2 if priority_skill['in_requirements'] else 1
        
        # Base score from skill overlap
        base_score = len(matching_skills) / len(job_skills_lower)
        
        # Adjusted score with priority weighting
        adjusted_score = min(1.0, base_score + (priority_weight * 0.1))
        
        return round(adjusted_score * 100, 1)  # Return as percentage