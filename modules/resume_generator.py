from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

class ResumeGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the resume"""
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1,  # Center alignment
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=3
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Contact info style
        self.contact_style = ParagraphStyle(
            'ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,  # Center alignment
            spaceAfter=12,
            fontName='Helvetica'
        )
    
    def prioritize_experiences(self, experiences: List[Dict], job_analysis: Dict) -> List[Dict]:
        """Prioritize and tailor experiences based on job requirements"""
        if not job_analysis:
            return experiences
        
        # Get job keywords and skills
        job_keywords = [kw[0].lower() for kw in job_analysis.get('keywords', [])]
        job_skills = [skill.lower() for skill in 
                     job_analysis.get('skills', {}).get('technical', []) + 
                     job_analysis.get('skills', {}).get('soft', [])]
        
        all_job_terms = set(job_keywords + job_skills)
        
        # Score each experience based on relevance
        scored_experiences = []
        for exp in experiences:
            score = 0
            exp_text = (exp.get('title', '') + ' ' + 
                       exp.get('company', '') + ' ' + 
                       exp.get('description', '')).lower()
            
            # Count matches with job terms
            for term in all_job_terms:
                if term in exp_text:
                    score += 1
            
            # Boost score for priority skills
            priority_skills = job_analysis.get('priority_skills', [])
            for priority in priority_skills[:5]:  # Top 5 priority skills
                if priority['skill'].lower() in exp_text:
                    score += 3 if priority['in_requirements'] else 2
            
            scored_experiences.append((score, exp))
        
        # Sort by score (descending) and return experiences
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for score, exp in scored_experiences]
    
    def tailor_experience_description(self, description: str, job_analysis: Dict) -> str:
        """Enhance experience description with job-relevant keywords"""
        if not job_analysis or not description:
            return description
        
        # Get priority skills and keywords
        priority_skills = job_analysis.get('priority_skills', [])
        top_keywords = [kw[0] for kw in job_analysis.get('keywords', [])[:10]]
        
        # For now, return original description
        # In a more advanced version, this could use NLP to enhance descriptions
        return description
    
    def get_all_skills_combined(self, profile: Dict) -> str:
        """Combine all skill categories into a single string"""
        all_skills = []
        
        # Collect skills from all categories
        categories = ['programming_skills', 'technologies', 'language_skills', 'certifications']
        for category in categories:
            skills_text = profile.get(category, '')
            if skills_text:
                skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                all_skills.extend(skills_list)
        
        return ', '.join(all_skills)
    
    def generate_tailored_skills(self, profile: Dict, job_analysis: Dict) -> str:
        """Generate a tailored skills section based on job requirements"""
        # Get all skills combined from categories
        all_skills_text = self.get_all_skills_combined(profile)
        
        if not all_skills_text:
            return ""
        
        profile_skill_list = [skill.strip() for skill in all_skills_text.split(',')]
        
        if not job_analysis:
            return all_skills_text
        
        # Get job skills
        job_technical = job_analysis.get('skills', {}).get('technical', [])
        job_soft = job_analysis.get('skills', {}).get('soft', [])
        priority_skills = [ps['skill'] for ps in job_analysis.get('priority_skills', [])]
        
        # Prioritize skills that match the job
        matched_skills = []
        unmatched_skills = []
        
        for skill in profile_skill_list:
            skill_lower = skill.lower()
            is_match = (skill_lower in [js.lower() for js in job_technical + job_soft] or
                       skill in priority_skills)
            
            if is_match:
                matched_skills.append(skill)
            else:
                unmatched_skills.append(skill)
        
        # Put matched skills first
        tailored_skills = matched_skills + unmatched_skills
        return ', '.join(tailored_skills)
    
    def generate_categorized_skills_text(self, profile: Dict) -> str:
        """Generate skills text organized by categories"""
        skills_sections = []
        
        categories = {
            'Programming': profile.get('programming_skills', ''),
            'Technologies': profile.get('technologies', ''),
            'Languages': profile.get('language_skills', ''),
            'Certifications': profile.get('certifications', '')
        }
        
        for category, skills_text in categories.items():
            if skills_text:
                skills_sections.append(f"{category}: {skills_text}")
        
        return ' | '.join(skills_sections)
    
    def generate_professional_summary(self, profile: Dict, job_analysis: Dict) -> str:
        """Generate a tailored professional summary"""
        base_summary = profile.get('summary', '')
        
        if not job_analysis:
            return base_summary or "Experienced professional with a strong background in technology and innovation."
        
        # Extract key elements from job analysis
        experience_level = job_analysis.get('experience_level', 'experienced')
        top_skills = job_analysis.get('priority_skills', [])[:3]
        
        if base_summary:
            return base_summary
        
        # Generate a basic summary if none exists
        skill_text = ""
        if top_skills:
            skills_list = [skill['skill'] for skill in top_skills]
            skill_text = f" with expertise in {', '.join(skills_list)}"
        
        level_text = {
            'entry': 'Motivated entry-level professional',
            'mid': 'Experienced professional',
            'senior': 'Senior professional with proven leadership',
            'executive': 'Executive-level professional'
        }.get(experience_level, 'Experienced professional')
        
        return f"{level_text}{skill_text}, ready to contribute to organizational success."
    
    def generate_pdf_resume(self, profile: Dict, job_analysis: Dict = None) -> io.BytesIO:
        """Generate a PDF resume"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        content = []
        
        # Header with name and contact info
        name = profile.get('name', 'Your Name')
        content.append(Paragraph(name, self.header_style))
        
        # Contact information
        contact_info = []
        if profile.get('email'):
            contact_info.append(profile['email'])
        if profile.get('phone'):
            contact_info.append(profile['phone'])
        if profile.get('location'):
            contact_info.append(profile['location'])
        if profile.get('linkedin'):
            contact_info.append(profile['linkedin'])
        
        if contact_info:
            contact_text = ' | '.join(contact_info)
            content.append(Paragraph(contact_text, self.contact_style))
        
        content.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        summary = self.generate_professional_summary(profile, job_analysis)
        if summary:
            content.append(Paragraph("PROFESSIONAL SUMMARY", self.section_style))
            content.append(Paragraph(summary, self.body_style))
            content.append(Spacer(1, 0.1*inch))
        
        # Skills
        if job_analysis:
            skills = self.generate_tailored_skills(profile, job_analysis)
        else:
            skills = self.generate_categorized_skills_text(profile)
        
        if skills:
            content.append(Paragraph("SKILLS", self.section_style))
            content.append(Paragraph(skills, self.body_style))
            content.append(Spacer(1, 0.1*inch))
        
        # Experience
        experiences = profile.get('experiences', [])
        if experiences:
            content.append(Paragraph("PROFESSIONAL EXPERIENCE", self.section_style))
            
            # Prioritize experiences based on job analysis
            prioritized_exp = self.prioritize_experiences(experiences, job_analysis)
            
            for exp in prioritized_exp:
                # Job title and company
                title_company = f"<b>{exp.get('title', 'Position')}</b>"
                if exp.get('company'):
                    title_company += f" - {exp.get('company')}"
                if exp.get('duration'):
                    title_company += f" ({exp.get('duration')})"
                
                content.append(Paragraph(title_company, self.body_style))
                
                # Description
                description = self.tailor_experience_description(
                    exp.get('description', ''), job_analysis
                )
                if description:
                    content.append(Paragraph(description, self.body_style))
                
                content.append(Spacer(1, 0.1*inch))
        
        # Education
        education = profile.get('education', [])
        if education:
            content.append(Paragraph("EDUCATION", self.section_style))
            
            for edu in education:
                # Degree and institution
                edu_line = f"<b>{edu.get('degree', 'Degree')}</b>"
                if edu.get('field'):
                    edu_line += f" in {edu.get('field')}"
                if edu.get('institution'):
                    edu_line += f" - {edu.get('institution')}"
                if edu.get('year'):
                    edu_line += f" ({edu.get('year')})"
                
                content.append(Paragraph(edu_line, self.body_style))
                
                # Additional details
                if edu.get('details'):
                    content.append(Paragraph(edu.get('details'), self.body_style))
                
                content.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer
    
    def generate_word_resume(self, profile: Dict, job_analysis: Dict = None) -> io.BytesIO:
        """Generate a Word document resume"""
        doc = Document()
        
        # Header with name
        name = profile.get('name', 'Your Name')
        header = doc.add_heading(name, level=1)
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Contact information
        contact_info = []
        if profile.get('email'):
            contact_info.append(profile['email'])
        if profile.get('phone'):
            contact_info.append(profile['phone'])
        if profile.get('location'):
            contact_info.append(profile['location'])
        if profile.get('linkedin'):
            contact_info.append(profile['linkedin'])
        
        if contact_info:
            contact_para = doc.add_paragraph(' | '.join(contact_info))
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Professional Summary
        summary = self.generate_professional_summary(profile, job_analysis)
        if summary:
            doc.add_heading('PROFESSIONAL SUMMARY', level=2)
            doc.add_paragraph(summary)
        
        # Skills
        if job_analysis:
            skills = self.generate_tailored_skills(profile, job_analysis)
        else:
            skills = self.generate_categorized_skills_text(profile)
        
        if skills:
            doc.add_heading('SKILLS', level=2)
            doc.add_paragraph(skills)
        
        # Experience
        experiences = profile.get('experiences', [])
        if experiences:
            doc.add_heading('PROFESSIONAL EXPERIENCE', level=2)
            
            # Prioritize experiences based on job analysis
            prioritized_exp = self.prioritize_experiences(experiences, job_analysis)
            
            for exp in prioritized_exp:
                # Job title and company
                title_text = exp.get('title', 'Position')
                if exp.get('company'):
                    title_text += f" - {exp.get('company')}"
                if exp.get('duration'):
                    title_text += f" ({exp.get('duration')})"
                
                title_para = doc.add_paragraph()
                title_run = title_para.add_run(title_text)
                title_run.bold = True
                
                # Description
                description = self.tailor_experience_description(
                    exp.get('description', ''), job_analysis
                )
                if description:
                    doc.add_paragraph(description)
        
        # Education
        education = profile.get('education', [])
        if education:
            doc.add_heading('EDUCATION', level=2)
            
            for edu in education:
                # Degree and institution
                edu_text = edu.get('degree', 'Degree')
                if edu.get('field'):
                    edu_text += f" in {edu.get('field')}"
                if edu.get('institution'):
                    edu_text += f" - {edu.get('institution')}"
                if edu.get('year'):
                    edu_text += f" ({edu.get('year')})"
                
                edu_para = doc.add_paragraph()
                edu_run = edu_para.add_run(edu_text)
                edu_run.bold = True
                
                # Additional details
                if edu.get('details'):
                    doc.add_paragraph(edu.get('details'))
        
        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer