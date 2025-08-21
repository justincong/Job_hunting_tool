import streamlit as st
from typing import Dict

class ResumePreview:
    def __init__(self):
        self.preview_style = """
        <style>
        .resume-preview {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-family: 'Times New Roman', serif;
            line-height: 1.4;
        }
        .resume-header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .resume-name {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .resume-contact {
            font-size: 12px;
            color: #666;
        }
        .resume-section {
            margin: 15px 0;
        }
        .resume-section-title {
            font-size: 14px;
            font-weight: bold;
            color: #333;
            text-transform: uppercase;
            border-bottom: 1px solid #666;
            padding-bottom: 2px;
            margin-bottom: 8px;
        }
        .resume-content {
            font-size: 12px;
            color: #333;
            margin-bottom: 8px;
        }
        .resume-job-title {
            font-weight: bold;
            font-size: 12px;
        }
        .resume-company {
            font-style: italic;
            color: #555;
        }
        .resume-duration {
            float: right;
            color: #666;
            font-size: 11px;
        }
        .resume-description {
            margin-top: 4px;
            font-size: 11px;
            text-align: justify;
        }
        .skills-tag {
            background-color: #f0f0f0;
            color: #333;
            padding: 2px 6px;
            margin: 1px 2px;
            border-radius: 3px;
            font-size: 10px;
            display: inline-block;
        }
        </style>
        """
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return text
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    
    def generate_html_preview(self, profile: Dict, job_analysis: Dict = None, generator=None) -> str:
        """Generate HTML preview of the resume"""
        
        # Use generator to get tailored content if available
        if generator and job_analysis:
            summary = generator.generate_professional_summary(profile, job_analysis)
            skills = generator.generate_tailored_skills(profile.get('skills', ''), job_analysis)
            experiences = generator.prioritize_experiences(profile.get('experiences', []), job_analysis)
        else:
            summary = profile.get('summary', '')
            skills = profile.get('skills', '')
            experiences = profile.get('experiences', [])
        
        # Start building HTML
        html = f"{self.preview_style}<div class='resume-preview'>"
        
        # Header
        html += "<div class='resume-header'>"
        html += f"<div class='resume-name'>{self.escape_html(profile.get('name', 'Your Name'))}</div>"
        
        # Contact info
        contact_parts = []
        if profile.get('email'):
            contact_parts.append(self.escape_html(profile['email']))
        if profile.get('phone'):
            contact_parts.append(self.escape_html(profile['phone']))
        if profile.get('location'):
            contact_parts.append(self.escape_html(profile['location']))
        if profile.get('linkedin'):
            contact_parts.append(self.escape_html(profile['linkedin']))
        
        if contact_parts:
            html += f"<div class='resume-contact'>{' | '.join(contact_parts)}</div>"
        
        html += "</div>"
        
        # Professional Summary
        if summary:
            html += "<div class='resume-section'>"
            html += "<div class='resume-section-title'>Professional Summary</div>"
            html += f"<div class='resume-content'>{self.escape_html(summary)}</div>"
            html += "</div>"
        
        # Skills
        if skills:
            html += "<div class='resume-section'>"
            html += "<div class='resume-section-title'>Skills</div>"
            html += "<div class='resume-content'>"
            
            # Convert skills to tags
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            for skill in skills_list:
                html += f"<span class='skills-tag'>{self.escape_html(skill)}</span>"
            
            html += "</div></div>"
        
        # Experience
        if experiences:
            html += "<div class='resume-section'>"
            html += "<div class='resume-section-title'>Professional Experience</div>"
            
            for exp in experiences:
                html += "<div class='resume-content'>"
                
                # Title and duration
                html += f"<div class='resume-job-title'>{self.escape_html(exp.get('title', 'Position'))}"
                if exp.get('duration'):
                    html += f"<span class='resume-duration'>{self.escape_html(exp.get('duration'))}</span>"
                html += "</div>"
                
                # Company
                if exp.get('company'):
                    html += f"<div class='resume-company'>{self.escape_html(exp.get('company'))}</div>"
                
                # Description
                if exp.get('description'):
                    # Limit description length for preview
                    desc = exp.get('description', '')
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    html += f"<div class='resume-description'>{self.escape_html(desc)}</div>"
                
                html += "</div>"
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def display_preview(self, profile: Dict, job_analysis: Dict = None, generator=None):
        """Display the resume preview in Streamlit"""
        
        # Use a simpler approach - display sections separately
        st.markdown("### 👁️ Resume Preview")
        
        # Create a container with styling
        with st.container():
            # Apply custom CSS
            st.markdown("""
            <style>
            .preview-container {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .preview-header {
                text-align: center;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }
            .preview-name {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
            .preview-contact {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            .preview-section {
                margin: 15px 0;
            }
            .preview-section-title {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                text-transform: uppercase;
                border-bottom: 1px solid #666;
                padding-bottom: 2px;
                margin-bottom: 8px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Header section
            name = self.escape_html(profile.get('name', 'Your Name'))
            contact_parts = []
            if profile.get('email'):
                contact_parts.append(self.escape_html(profile['email']))
            if profile.get('phone'):
                contact_parts.append(self.escape_html(profile['phone']))
            if profile.get('location'):
                contact_parts.append(self.escape_html(profile['location']))
            
            st.markdown(f"""
            <div class="preview-container">
                <div class="preview-header">
                    <div class="preview-name">{name}</div>
                    <div class="preview-contact">{' | '.join(contact_parts)}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Professional Summary
            if generator and job_analysis:
                summary = generator.generate_professional_summary(profile, job_analysis)
                skills = generator.generate_tailored_skills(profile.get('skills', ''), job_analysis)
                experiences = generator.prioritize_experiences(profile.get('experiences', []), job_analysis)
            else:
                summary = profile.get('summary', '')
                skills = profile.get('skills', '')
                experiences = profile.get('experiences', [])
            
            if summary:
                st.markdown('<div class="preview-section-title">Professional Summary</div>', unsafe_allow_html=True)
                st.write(summary)
            
            # Skills
            if skills:
                st.markdown('<div class="preview-section-title">Skills</div>', unsafe_allow_html=True)
                skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
                skills_cols = st.columns(3)
                for i, skill in enumerate(skills_list):
                    with skills_cols[i % 3]:
                        st.write(f"• {skill}")
            
            # Experience
            if experiences:
                st.markdown('<div class="preview-section-title">Professional Experience</div>', unsafe_allow_html=True)
                for exp in experiences:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{exp.get('title', 'Position')}** - *{exp.get('company', 'Company')}*")
                        with col2:
                            st.write(exp.get('duration', ''))
                        
                        if exp.get('description'):
                            desc = exp.get('description', '')
                            if len(desc) > 300:
                                desc = desc[:300] + "..."
                            st.write(desc)
                        st.write("")  # Add space between experiences
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add preview notes
        with st.expander("ℹ️ Preview Notes"):
            st.write("• This is a simplified preview of your resume")
            st.write("• The actual PDF/Word document will have better formatting")
            st.write("• Font sizes and spacing may differ in the exported version")
            if job_analysis:
                st.write("• ✅ This preview shows the tailored version based on job analysis")
            else:
                st.write("• This preview shows the standard version of your resume")
    
    def show_comparison(self, profile: Dict, job_analysis: Dict, generator):
        """Show side-by-side comparison of standard vs tailored resume"""
        
        st.markdown("### 🔄 Standard vs Tailored Comparison")
        
        # Show differences first (more reliable)
        st.markdown("#### 🔍 Key Differences")
        
        # Skills comparison
        original_skills = [s.strip() for s in profile.get('skills', '').split(',') if s.strip()]
        tailored_skills_str = generator.generate_tailored_skills(profile.get('skills', ''), job_analysis)
        tailored_skills = [s.strip() for s in tailored_skills_str.split(',') if s.strip()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📄 Standard Version:**")
            if original_skills:
                st.write("**Skills (Original Order):**")
                for skill in original_skills[:8]:  # Show top 8
                    st.write(f"• {skill}")
            
            # Standard experience order
            original_exp = profile.get('experiences', [])
            if original_exp:
                st.write("**Experience (Original Order):**")
                for i, exp in enumerate(original_exp[:3]):
                    st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
        
        with col2:
            st.markdown("**🎯 Tailored Version:**")
            if tailored_skills:
                st.write("**Skills (Prioritized for Job):**")
                for skill in tailored_skills[:8]:  # Show top 8
                    st.write(f"• {skill}")
            
            # Tailored experience order
            tailored_exp = generator.prioritize_experiences(original_exp, job_analysis)
            if tailored_exp:
                st.write("**Experience (Prioritized by Relevance):**")
                for i, exp in enumerate(tailored_exp[:3]):
                    st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
        
        # Summary comparison
        st.markdown("#### 📝 Professional Summary")
        
        original_summary = profile.get('summary', 'No summary provided')
        tailored_summary = generator.generate_professional_summary(profile, job_analysis)
        
        if original_summary != tailored_summary:
            st.markdown("**Standard:**")
            st.write(original_summary)
            st.markdown("**Tailored:**")
            st.write(tailored_summary)
        else:
            st.write("Summary remains the same for both versions.")
        
        st.info("💡 The tailored version prioritizes skills and experiences that best match the job requirements.")