import streamlit as st
from streamlit_option_menu import option_menu
import json
import os
from datetime import datetime
from modules.resume_parser import ResumeParser
from modules.job_analyzer import JobAnalyzer
from modules.resume_generator import ResumeGenerator
from modules.resume_preview import ResumePreview

# Page config
st.set_page_config(
    page_title="Resume Builder & Refiner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = {}

if 'job_analysis' not in st.session_state:
    st.session_state.job_analysis = None

# Initialize parsers
@st.cache_resource
def get_resume_parser():
    return ResumeParser()

@st.cache_resource
def get_job_analyzer():
    return JobAnalyzer()

@st.cache_resource
def get_resume_generator():
    return ResumeGenerator()

@st.cache_resource
def get_resume_preview():
    return ResumePreview()

# Load profile data if exists
PROFILE_FILE = 'profile_data.json'

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profile(data):
    with open(PROFILE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Main navigation
with st.sidebar:
    selected = option_menu(
        "Resume Builder",
        ["Dashboard", "Profile Manager", "Upload Resume", "Job Matcher", "Export Resume"],
        icons=['house', 'person', 'upload', 'briefcase', 'download'],
        menu_icon="cast",
        default_index=0,
    )

# Dashboard Page
if selected == "Dashboard":
    st.title("📄 Resume Builder & Refiner")
    st.markdown("Welcome to your intelligent resume refinement tool!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Profile Completeness", "0%", "Complete your profile")
    
    with col2:
        st.metric("Resumes Generated", "0", "No resumes yet")
    
    with col3:
        st.metric("Jobs Matched", "0", "Start matching jobs")
    
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 Setup Profile", use_container_width=True):
            st.switch_page("Profile Manager")
    
    with col2:
        if st.button("📤 Upload Resume", use_container_width=True):
            st.switch_page("Upload Resume")
    
    with col3:
        if st.button("🎯 Match Job", use_container_width=True):
            st.switch_page("Job Matcher")

# Profile Manager Page
elif selected == "Profile Manager":
    st.title("👤 Profile Manager")
    st.markdown("Manage your professional information, experiences, and skills.")
    
    # Load existing profile
    profile = load_profile()
    
    # Add tabs for editing and viewing
    tab1, tab2 = st.tabs(["✏️ Edit Profile", "👁️ View Profile"])
    
    with tab2:
        st.subheader("📋 Profile Overview")
        
        if not profile:
            st.info("No profile data found. Please create your profile in the Edit Profile tab.")
        else:
            # Profile completeness calculation
            required_fields = ['name', 'email', 'skills']
            completed_fields = sum(1 for field in required_fields if profile.get(field))
            completeness = (completed_fields / len(required_fields)) * 100
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Profile Completeness", f"{completeness:.0f}%")
            with col2:
                st.metric("Experience Entries", len(profile.get('experiences', [])))
            with col3:
                skills_count = len([s.strip() for s in profile.get('skills', '').split(',') if s.strip()])
                st.metric("Skills Listed", skills_count)
            
            st.divider()
            
            # Contact Information
            st.subheader("📞 Contact Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {profile.get('name', '❌ Not set')}")
                st.write(f"**Email:** {profile.get('email', '❌ Not set')}")
                st.write(f"**Phone:** {profile.get('phone', '❌ Not set')}")
            
            with col2:
                st.write(f"**Location:** {profile.get('location', '❌ Not set')}")
                st.write(f"**LinkedIn:** {profile.get('linkedin', '❌ Not set')}")
                st.write(f"**Website:** {profile.get('website', '❌ Not set')}")
            
            # Professional Summary
            if profile.get('summary'):
                st.subheader("📝 Professional Summary")
                st.write(profile['summary'])
            
            # Skills
            if profile.get('skills'):
                st.subheader("🛠️ Skills")
                skills_list = [skill.strip() for skill in profile['skills'].split(',') if skill.strip()]
                
                # Display skills as tags
                skills_html = ""
                for skill in skills_list:
                    skills_html += f'<span style="background-color: #e1f5fe; color: #01579b; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{skill}</span>'
                
                st.markdown(skills_html, unsafe_allow_html=True)
            
            # Experience
            experiences = profile.get('experiences', [])
            if experiences:
                st.subheader("💼 Work Experience")
                
                for i, exp in enumerate(experiences):
                    with st.expander(f"📍 {exp.get('title', 'Position')} - {exp.get('company', 'Company')}", expanded=i==0):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Position:** {exp.get('title', 'Not specified')}")
                            st.write(f"**Company:** {exp.get('company', 'Not specified')}")
                        
                        with col2:
                            st.write(f"**Duration:** {exp.get('duration', 'Not specified')}")
                        
                        if exp.get('description'):
                            st.write("**Description:**")
                            st.write(exp['description'])
            
            # Last updated
            if profile.get('last_updated'):
                st.caption(f"Last updated: {profile['last_updated']}")
    
    with tab1:
        st.subheader("Edit Profile Information")
        
        # Personal Information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=profile.get('name', ''))
            email = st.text_input("Email", value=profile.get('email', ''))
            phone = st.text_input("Phone", value=profile.get('phone', ''))
        
        with col2:
            location = st.text_input("Location", value=profile.get('location', ''))
            linkedin = st.text_input("LinkedIn URL", value=profile.get('linkedin', ''))
            website = st.text_input("Website/Portfolio", value=profile.get('website', ''))
        
        # Professional Summary
        st.subheader("Professional Summary")
        summary = st.text_area("Professional Summary", value=profile.get('summary', ''), height=100)
        
        # Skills
        st.subheader("Skills")
        skills = st.text_area("Skills (comma-separated)", value=profile.get('skills', ''), height=100)
        
        # Experience
        st.subheader("Work Experience")
        experiences = profile.get('experiences', [])
        
        # Add new experience
        if st.button("➕ Add Experience"):
            experiences.append({
                'title': '',
                'company': '',
                'duration': '',
                'description': ''
            })
        
        # Display experiences
        for i, exp in enumerate(experiences):
            with st.expander(f"Experience {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    exp['title'] = st.text_input(f"Job Title {i+1}", value=exp.get('title', ''), key=f"title_{i}")
                    exp['company'] = st.text_input(f"Company {i+1}", value=exp.get('company', ''), key=f"company_{i}")
                with col2:
                    exp['duration'] = st.text_input(f"Duration {i+1}", value=exp.get('duration', ''), key=f"duration_{i}")
                
                exp['description'] = st.text_area(f"Description {i+1}", value=exp.get('description', ''), key=f"desc_{i}")
                
                if st.button(f"🗑️ Remove Experience {i+1}", key=f"remove_{i}"):
                    experiences.pop(i)
                    st.rerun()
        
        # Save profile
        if st.button("💾 Save Profile", type="primary"):
            profile_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'location': location,
                'linkedin': linkedin,
                'website': website,
                'summary': summary,
                'skills': skills,
                'experiences': experiences,
                'last_updated': datetime.now().isoformat()
            }
            save_profile(profile_data)
            st.success("Profile saved successfully!")

# Upload Resume Page
elif selected == "Upload Resume":
    st.title("📤 Upload Resume")
    st.markdown("Upload your existing resume to extract and populate your profile.")
    
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx'])
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Parse Resume", type="primary"):
            try:
                with st.spinner("Parsing resume..."):
                    parser = get_resume_parser()
                    parsed_data = parser.parse_resume(uploaded_file)
                
                st.success("Resume parsed successfully!")
                
                # Display extracted information
                st.subheader("Extracted Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Contact Information:**")
                    st.write(f"Name: {parsed_data.get('name', 'Not found')}")
                    st.write(f"Email: {parsed_data.get('email', 'Not found')}")
                    st.write(f"Phone: {parsed_data.get('phone', 'Not found')}")
                    st.write(f"LinkedIn: {parsed_data.get('linkedin', 'Not found')}")
                
                with col2:
                    st.write("**Skills Found:**")
                    skills = parsed_data.get('skills', '')
                    if skills:
                        st.write(skills)
                    else:
                        st.write("No skills extracted")
                
                # Experience
                if parsed_data.get('experiences'):
                    st.write("**Work Experience:**")
                    for i, exp in enumerate(parsed_data['experiences']):
                        with st.expander(f"Experience {i+1}"):
                            st.write(f"**Title/Company:** {exp.get('title', 'N/A')}")
                            st.write(f"**Duration:** {exp.get('duration', 'N/A')}")
                            st.write(f"**Description:** {exp.get('description', 'N/A')}")
                
                # Option to update profile with parsed data
                if st.button("📝 Update Profile with Parsed Data"):
                    # Load existing profile
                    existing_profile = load_profile()
                    
                    # Merge with parsed data (keeping existing data where available)
                    updated_profile = {
                        'name': parsed_data.get('name') or existing_profile.get('name', ''),
                        'email': parsed_data.get('email') or existing_profile.get('email', ''),
                        'phone': parsed_data.get('phone') or existing_profile.get('phone', ''),
                        'linkedin': parsed_data.get('linkedin') or existing_profile.get('linkedin', ''),
                        'location': existing_profile.get('location', ''),
                        'website': existing_profile.get('website', ''),
                        'summary': existing_profile.get('summary', ''),
                        'skills': parsed_data.get('skills') or existing_profile.get('skills', ''),
                        'experiences': parsed_data.get('experiences', []) + existing_profile.get('experiences', []),
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    save_profile(updated_profile)
                    st.success("Profile updated with parsed resume data!")
                    st.info("Go to Profile Manager to review and edit the information.")
                
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                st.info("Please try uploading a different file or check the file format.")

# Job Matcher Page
elif selected == "Job Matcher":
    st.title("🎯 Job Matcher")
    st.markdown("Input a job description to generate a tailored resume.")
    
    # Load profile to check if it exists
    profile = load_profile()
    
    if not profile:
        st.warning("⚠️ Please set up your profile first before matching jobs.")
        if st.button("Go to Profile Manager"):
            st.switch_page("Profile Manager")
    else:
        job_description = st.text_area("Job Description", height=200, placeholder="Paste the job description here...")
        
        if st.button("🔍 Analyze Job Description", type="primary"):
            if job_description:
                try:
                    with st.spinner("Analyzing job description..."):
                        analyzer = get_job_analyzer()
                        analysis = analyzer.analyze_job_description(job_description)
                        
                        # Calculate match score with profile
                        profile_skills = profile.get('skills', '').split(',')
                        profile_skills = [skill.strip() for skill in profile_skills if skill.strip()]
                        match_score = analyzer.calculate_match_score(profile_skills, analysis)
                        analysis['matching_score'] = match_score
                        
                        # Store analysis in session state
                        st.session_state.job_analysis = analysis
                    
                    st.success("Job description analyzed successfully!")
                    
                    # Display analysis results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Job Analysis")
                        st.metric("Match Score", f"{match_score}%", "Based on your skills")
                        st.write(f"**Experience Level:** {analysis['experience_level'].title()}")
                        
                        # Technical skills
                        if analysis['skills']['technical']:
                            st.write("**Technical Skills Required:**")
                            for skill in analysis['skills']['technical'][:10]:  # Show top 10
                                st.write(f"• {skill}")
                        
                        # Soft skills
                        if analysis['skills']['soft']:
                            st.write("**Soft Skills Required:**")
                            for skill in analysis['skills']['soft'][:5]:  # Show top 5
                                st.write(f"• {skill}")
                    
                    with col2:
                        st.subheader("🎯 Priority Skills")
                        if analysis['priority_skills']:
                            for skill in analysis['priority_skills'][:8]:
                                priority_indicator = "🔥" if skill['in_requirements'] else "⭐"
                                st.write(f"{priority_indicator} {skill['skill']} (mentioned {skill['frequency']} times)")
                        
                        st.subheader("🔑 Top Keywords")
                        keywords = analysis['keywords'][:10]
                        keyword_text = ", ".join([kw[0] for kw in keywords])
                        st.write(keyword_text)
                    
                    # Requirements and Responsibilities
                    if analysis['requirements']:
                        st.subheader("📋 Key Requirements")
                        for req in analysis['requirements'][:5]:  # Show top 5
                            st.write(f"• {req}")
                    
                    if analysis['responsibilities']:
                        st.subheader("💼 Key Responsibilities")
                        for resp in analysis['responsibilities'][:5]:  # Show top 5
                            st.write(f"• {resp}")
                    
                    # Tailoring suggestions
                    st.subheader("💡 Resume Tailoring Suggestions")
                    
                    # Skills analysis
                    your_skills = set([skill.lower().strip() for skill in profile_skills])
                    job_skills = set([skill.lower() for skill in analysis['skills']['technical'] + analysis['skills']['soft']])
                    
                    matching_skills = your_skills & job_skills
                    missing_skills = job_skills - your_skills
                    
                    if matching_skills:
                        st.success(f"✅ **Skills to Highlight:** {', '.join(matching_skills)}")
                    
                    if missing_skills:
                        st.warning(f"⚠️ **Skills to Consider Adding:** {', '.join(list(missing_skills)[:5])}")
                    
                    # Experience suggestions
                    if analysis['experience_level'] == 'entry':
                        st.info("💡 Emphasize education, projects, internships, and relevant coursework")
                    elif analysis['experience_level'] == 'senior':
                        st.info("💡 Highlight leadership experience, major projects, and team management")
                    
                except Exception as e:
                    st.error(f"Error analyzing job description: {str(e)}")
            else:
                st.error("Please provide a job description.")
        
        # Show generate resume option if analysis exists
        if st.session_state.job_analysis:
            st.divider()
            st.subheader("📄 Generate Tailored Resume")
            
            if st.button("🚀 Generate Tailored Resume", type="primary"):
                try:
                    with st.spinner("Generating tailored resume..."):
                        generator = get_resume_generator()
                        
                        # Store generated resume info in session state
                        st.session_state.generated_resume = {
                            'profile': profile,
                            'job_analysis': st.session_state.job_analysis,
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    st.success("✅ Tailored resume generated successfully!")
                    st.info("📥 Go to 'Export Resume' to download your customized resume.")
                    
                    # Show preview of changes
                    st.subheader("📋 Resume Tailoring Preview")
                    
                    # Show prioritized skills
                    tailored_skills = generator.generate_tailored_skills(
                        profile.get('skills', ''), st.session_state.job_analysis
                    )
                    if tailored_skills != profile.get('skills', ''):
                        st.write("**Skills (Reordered for Relevance):**")
                        st.write(tailored_skills)
                    
                    # Show prioritized experiences
                    experiences = profile.get('experiences', [])
                    if experiences:
                        prioritized_exp = generator.prioritize_experiences(
                            experiences, st.session_state.job_analysis
                        )
                        st.write("**Experience (Prioritized by Relevance):**")
                        for i, exp in enumerate(prioritized_exp[:3]):  # Show top 3
                            st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
                
                except Exception as e:
                    st.error(f"Error generating resume: {str(e)}")

# Export Resume Page
elif selected == "Export Resume":
    st.title("📥 Export Resume")
    st.markdown("Download your tailored resume in your preferred format.")
    
    # Load profile
    profile = load_profile()
    
    if not profile:
        st.warning("⚠️ Please set up your profile first.")
        if st.button("Go to Profile Manager"):
            st.switch_page("Profile Manager")
    else:
        # Check if a tailored resume was generated
        has_tailored = hasattr(st.session_state, 'generated_resume') and st.session_state.generated_resume
        
        if has_tailored:
            st.success("✅ Tailored resume ready for export")
            generated_time = st.session_state.generated_resume.get('timestamp', 'Unknown')
            st.info(f"Generated: {generated_time}")
        else:
            st.info("ℹ️ No job-specific tailoring applied. Will generate standard resume.")
        
        # Resume type selection
        col1, col2 = st.columns(2)
        
        with col1:
            resume_type = st.radio(
                "Resume Type",
                ["Standard Resume", "Tailored Resume (if available)"]
            )
        
        with col2:
            format_choice = st.selectbox("Export Format", ["PDF", "Word Document"])
        
        # Use tailored data if available and selected
        use_tailored = (resume_type == "Tailored Resume (if available)" and has_tailored)
        job_analysis = st.session_state.generated_resume.get('job_analysis') if use_tailored else None
        
        generator = get_resume_generator()
        preview = get_resume_preview()
        
        # Preview options
        st.subheader("📋 Resume Preview Options")
        
        preview_tab1, preview_tab2 = st.tabs(["👁️ Visual Preview", "📊 Quick Summary"])
        
        with preview_tab1:
            # Show visual preview
            if use_tailored and has_tailored:
                # Option to show comparison
                show_comparison = st.checkbox("🔄 Show Standard vs Tailored Comparison")
                
                if show_comparison:
                    preview.show_comparison(profile, job_analysis, generator)
                else:
                    preview.display_preview(profile, job_analysis, generator)
            else:
                preview.display_preview(profile)
        
        with preview_tab2:
            # Show quick summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Contact Information:**")
                st.write(f"Name: {profile.get('name', 'Not set')}")
                st.write(f"Email: {profile.get('email', 'Not set')}")
                st.write(f"Phone: {profile.get('phone', 'Not set')}")
                
                if use_tailored:
                    st.write("**Professional Summary (Tailored):**")
                    summary = generator.generate_professional_summary(profile, job_analysis)
                    st.write(summary[:200] + "..." if len(summary) > 200 else summary)
            
            with col2:
                if use_tailored:
                    st.write("**Skills (Prioritized for Job):**")
                    tailored_skills = generator.generate_tailored_skills(
                        profile.get('skills', ''), job_analysis
                    )
                    st.write(tailored_skills[:150] + "..." if len(tailored_skills) > 150 else tailored_skills)
                else:
                    st.write("**Skills:**")
                    skills = profile.get('skills', 'Not set')
                    st.write(skills[:150] + "..." if len(skills) > 150 else skills)
            
            # Experience preview
            experiences = profile.get('experiences', [])
            if experiences:
                if use_tailored:
                    st.write("**Experience (Prioritized by Relevance):**")
                    prioritized_exp = generator.prioritize_experiences(experiences, job_analysis)
                    for i, exp in enumerate(prioritized_exp[:3]):
                        st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
                else:
                    st.write("**Experience:**")
                    for i, exp in enumerate(experiences[:3]):
                        st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
        
        # Export buttons
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Generate & Download", type="primary", use_container_width=True):
                try:
                    with st.spinner(f"Generating {format_choice.lower()}..."):
                        if format_choice == "PDF":
                            buffer = generator.generate_pdf_resume(profile, job_analysis)
                            filename = f"resume_{'tailored' if use_tailored else 'standard'}.pdf"
                            mime_type = "application/pdf"
                        else:  # Word Document
                            buffer = generator.generate_word_resume(profile, job_analysis)
                            filename = f"resume_{'tailored' if use_tailored else 'standard'}.docx"
                            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    
                    st.download_button(
                        label=f"📥 Download {format_choice}",
                        data=buffer.getvalue(),
                        file_name=filename,
                        mime=mime_type,
                        type="primary"
                    )
                    
                    st.success(f"✅ {format_choice} generated successfully! Click the download button above.")
                    
                except Exception as e:
                    st.error(f"Error generating {format_choice.lower()}: {str(e)}")
        
        with col2:
            if st.button("🔄 Clear Tailored Resume", use_container_width=True):
                if hasattr(st.session_state, 'generated_resume'):
                    del st.session_state.generated_resume
                if hasattr(st.session_state, 'job_analysis'):
                    del st.session_state.job_analysis
                st.success("Tailored resume data cleared.")
                st.rerun()