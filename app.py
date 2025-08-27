import streamlit as st
from streamlit_option_menu import option_menu
import json
import os
from datetime import datetime
from modules.resume_generator import ResumeGenerator
from modules.resume_preview import ResumePreview
from modules.llm_job_analyzer import LLMJobAnalyzer
from modules.database_manager import db_manager
from modules.job_storage_service import job_storage

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

if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Dashboard"

# Initialize components
@st.cache_resource
def get_resume_generator():
    return ResumeGenerator()

@st.cache_resource
def get_resume_preview():
    return ResumePreview()

@st.cache_resource
def get_job_analyzer():
    return LLMJobAnalyzer()

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
    # DeepSeek API Key Configuration
    with st.expander("🔑 LLM Configuration"):
        api_key = st.text_input(
            "DeepSeek API Key", 
            type="password",
            value=os.getenv("DEEPSEEK_API_KEY", ""),
            help="Enter your DeepSeek API key for enhanced job analysis"
        )
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key
            st.success("✅ API key configured")
        else:
            st.warning("⚠️ No API key - using fallback analysis")
    
    # Database Configuration
    with st.expander("🗄️ Database Settings"):
        available_dbs = db_manager.get_available_databases()
        current_db = db_manager.get_current_database_type()
        
        selected_db = st.selectbox(
            "Database Type",
            options=list(available_dbs.keys()),
            format_func=lambda x: available_dbs[x],
            index=list(available_dbs.keys()).index(current_db) if current_db in available_dbs else 0,
            key="db_selector"
        )
        
        # MongoDB configuration
        if selected_db == "mongodb":
            st.subheader("MongoDB Atlas Setup")
            connection_string = st.text_input(
                "Connection String",
                value=db_manager.config["mongodb"]["connection_string"],
                type="password",
                help="mongodb+srv://username:password@cluster-url/database"
            )
            database_name = st.text_input(
                "Database Name",
                value=db_manager.config["mongodb"]["database_name"],
                help="Name of the MongoDB database"
            )
            
            if st.button("Update MongoDB Config"):
                db_manager.update_mongodb_config(connection_string, database_name)
                st.success("MongoDB configuration updated!")
                st.rerun()
        
        # SQLite configuration
        elif selected_db == "sqlite":
            st.subheader("SQLite Setup")
            db_path = st.text_input(
                "Database File Path",
                value=db_manager.config["sqlite"]["db_path"],
                help="Path to SQLite database file"
            )
            
            if st.button("Update SQLite Config"):
                db_manager.update_sqlite_config(db_path)
                st.success("SQLite configuration updated!")
                st.rerun()
        
        # Switch database button
        if st.button(f"Switch to {available_dbs[selected_db]}"):
            with st.spinner("Switching database..."):
                if db_manager.switch_database(selected_db):
                    st.success(f"Successfully switched to {available_dbs[selected_db]}")
                    db_manager.initialize_collections()
                    st.rerun()
                else:
                    st.error(f"Failed to switch to {available_dbs[selected_db]}")
        
        # Database status
        db_info = db_manager.get_database_info()
        st.caption(f"Current: {available_dbs.get(db_info['type'], db_info['type'])}")
        if db_info['connected']:
            st.caption("🟢 Connected")
        else:
            st.caption("🔴 Not Connected")
    
    st.divider()
    
    menu_options = ["Dashboard", "Profile Manager", "Export Resume", "Job History"]
    
    # Get current index based on session state
    try:
        current_index = menu_options.index(st.session_state.selected_page)
    except ValueError:
        current_index = 0
        st.session_state.selected_page = "Dashboard"
    
    selected = option_menu(
        "Resume Builder",
        menu_options,
        icons=['house', 'person', 'download', 'clock-history'],
        menu_icon="cast",
        default_index=current_index,
        key="main_menu"
    )
    
    # Update session state when menu selection changes
    if selected != st.session_state.selected_page:
        st.session_state.selected_page = selected

# Dashboard Page
if st.session_state.selected_page == "Dashboard":
    st.title("📄 Resume Builder & Refiner")
    st.markdown("Welcome to your intelligent resume refinement tool!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Profile Completeness", "0%", "Complete your profile")
    
    with col2:
        st.metric("Resumes Generated", "0", "No resumes yet")
    

# Profile Manager Page
elif st.session_state.selected_page == "Profile Manager":
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Profile Completeness", f"{completeness:.0f}%")
            with col2:
                st.metric("Experience Entries", len(profile.get('experiences', [])))
            with col3:
                st.metric("Education Entries", len(profile.get('education', [])))
            with col4:
                # Count all skills across categories
                all_skills = []
                for category in ['programming_skills', 'technologies', 'language_skills', 'certifications']:
                    skills_text = profile.get(category, '')
                    if skills_text:
                        all_skills.extend([s.strip() for s in skills_text.split(',') if s.strip()])
                skills_count = len(all_skills)
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
            skills_categories = {
                'Programming Skills': profile.get('programming_skills', ''),
                'Technologies & Tools': profile.get('technologies', ''),
                'Language Skills': profile.get('language_skills', ''),
                'Certifications': profile.get('certifications', '')
            }
            
            # Check if any skills exist
            has_skills = any(skills for skills in skills_categories.values())
            
            if has_skills:
                st.subheader("🛠️ Skills")
                
                for category, skills_text in skills_categories.items():
                    if skills_text:
                        st.markdown(f"**{category}:**")
                        skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                        
                        # Display skills as tags with different colors for each category
                        color_map = {
                            'Programming Skills': '#e1f5fe',
                            'Technologies & Tools': '#f3e5f5', 
                            'Language Skills': '#e8f5e8',
                            'Certifications': '#fff3e0'
                        }
                        
                        skills_html = ""
                        for skill in skills_list:
                            color = color_map.get(category, '#e1f5fe')
                            skills_html += f'<span style="background-color: {color}; color: #333; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{skill}</span>'
                        
                        st.markdown(skills_html, unsafe_allow_html=True)
                        st.write("")  # Add space between categories
            
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
            
            # Education
            education = profile.get('education', [])
            if education:
                st.subheader("🎓 Education")
                
                for i, edu in enumerate(education):
                    degree_field = f"{edu.get('degree', 'Degree')}"
                    if edu.get('field'):
                        degree_field += f" in {edu.get('field')}"
                    
                    with st.expander(f"🏫 {degree_field} - {edu.get('institution', 'Institution')}", expanded=i==0):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Institution:** {edu.get('institution', 'Not specified')}")
                            st.write(f"**Degree:** {edu.get('degree', 'Not specified')}")
                            st.write(f"**Field of Study:** {edu.get('field', 'Not specified')}")
                        
                        with col2:
                            st.write(f"**Year:** {edu.get('year', 'Not specified')}")
                        
                        if edu.get('details'):
                            st.write("**Additional Details:**")
                            st.write(edu['details'])
            
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
        st.markdown("Organize your skills into categories for better presentation on your resume.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            programming_skills = st.text_area(
                "Programming Skills", 
                value=profile.get('programming_skills', ''), 
                height=80,
                help="e.g., Python, Java, JavaScript, C++, SQL"
            )
            
            language_skills = st.text_area(
                "Language Skills", 
                value=profile.get('language_skills', ''), 
                height=80,
                help="e.g., English (Native), Spanish (Fluent), Mandarin (Conversational)"
            )
        
        with col2:
            technologies = st.text_area(
                "Technologies & Tools", 
                value=profile.get('technologies', ''), 
                height=80,
                help="e.g., React, AWS, Docker, Git, Tableau, Excel"
            )
            
            certifications = st.text_area(
                "Certifications", 
                value=profile.get('certifications', ''), 
                height=80,
                help="e.g., AWS Certified Solutions Architect, PMP, Google Analytics"
            )
        
        # Experience
        st.subheader("Work Experience")
        
        # Initialize experiences in session state if not exists
        if 'temp_experiences' not in st.session_state:
            st.session_state.temp_experiences = profile.get('experiences', []).copy()
        
        # Add new experience
        if st.button("➕ Add Experience"):
            st.session_state.temp_experiences.append({
                'title': '',
                'company': '',
                'duration': '',
                'description': ''
            })
            st.rerun()
        
        # Display experiences
        experiences = st.session_state.temp_experiences
        updated_experiences = []
        
        for i, exp in enumerate(experiences):
            with st.expander(f"Experience {i+1}", expanded=True if exp.get('title', '') == '' else False):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input(f"Job Title", value=exp.get('title', ''), key=f"title_{i}")
                    company = st.text_input(f"Company", value=exp.get('company', ''), key=f"company_{i}")
                with col2:
                    duration = st.text_input(f"Duration (e.g., Jan 2020 - Dec 2022)", value=exp.get('duration', ''), key=f"duration_{i}")
                
                description = st.text_area(f"Job Description", value=exp.get('description', ''), key=f"desc_{i}", height=100,
                                         help="Describe your responsibilities, achievements, and key accomplishments")
                
                # Store updated values
                updated_exp = {
                    'title': title,
                    'company': company,
                    'duration': duration,
                    'description': description
                }
                updated_experiences.append(updated_exp)
                
                # Remove experience button
                if st.button(f"🗑️ Remove Experience {i+1}", key=f"remove_{i}"):
                    st.session_state.temp_experiences.pop(i)
                    st.rerun()
        
        # Update session state with current values
        st.session_state.temp_experiences = updated_experiences
        
        # Education
        st.subheader("Education")
        
        # Initialize education in session state if not exists
        if 'temp_education' not in st.session_state:
            st.session_state.temp_education = profile.get('education', []).copy()
        
        # Add new education
        if st.button("➕ Add Education"):
            st.session_state.temp_education.append({
                'institution': '',
                'degree': '',
                'field': '',
                'year': '',
                'details': ''
            })
            st.rerun()
        
        # Display education
        education = st.session_state.temp_education
        updated_education = []
        
        for i, edu in enumerate(education):
            with st.expander(f"Education {i+1}", expanded=True if edu.get('institution', '') == '' else False):
                col1, col2 = st.columns(2)
                with col1:
                    institution = st.text_input(f"Institution/School", value=edu.get('institution', ''), key=f"edu_inst_{i}")
                    degree = st.text_input(f"Degree/Certification", value=edu.get('degree', ''), key=f"edu_degree_{i}")
                with col2:
                    field = st.text_input(f"Field of Study", value=edu.get('field', ''), key=f"edu_field_{i}")
                    year = st.text_input(f"Year/Duration (e.g., 2018-2022)", value=edu.get('year', ''), key=f"edu_year_{i}")
                
                details = st.text_area(f"Additional Details", value=edu.get('details', ''), key=f"edu_details_{i}", height=80,
                                     help="GPA, honors, relevant coursework, achievements, etc.")
                
                # Store updated values
                updated_edu = {
                    'institution': institution,
                    'degree': degree,
                    'field': field,
                    'year': year,
                    'details': details
                }
                updated_education.append(updated_edu)
                
                # Remove education button
                if st.button(f"🗑️ Remove Education {i+1}", key=f"remove_edu_{i}"):
                    st.session_state.temp_education.pop(i)
                    st.rerun()
        
        # Update session state with current values
        st.session_state.temp_education = updated_education
        
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
                'programming_skills': programming_skills,
                'technologies': technologies,
                'language_skills': language_skills,
                'certifications': certifications,
                'experiences': st.session_state.temp_experiences,
                'education': st.session_state.temp_education,
                'last_updated': datetime.now().isoformat()
            }
            save_profile(profile_data)
            st.success("Profile saved successfully!")
            st.info("💡 Switch to 'View Profile' tab to see your updated information.")
        
        # Reset changes buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Experience Changes"):
                st.session_state.temp_experiences = profile.get('experiences', []).copy()
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Education Changes"):
                st.session_state.temp_education = profile.get('education', []).copy()
                st.rerun()


# Export Resume Page
elif st.session_state.selected_page == "Export Resume":
    st.title("📥 Resume Builder & Export")
    st.markdown("Create, tailor, and download your professional resume.")
    
    # Load profile
    profile = load_profile()
    
    if not profile:
        st.warning("⚠️ Please set up your profile first.")
        if st.button("Go to Profile Manager", key="goto_profile_manager"):
            st.session_state.selected_page = "Profile Manager"
            # Clear the option menu state to force it to update
            if "main_menu" in st.session_state:
                del st.session_state.main_menu
            st.rerun()
    else:
        # Main workflow tabs
        tab1, tab2 = st.tabs(["🎯 Tailor Resume", "👁️ Preview & Download Resume"])
        
        with tab1:
            st.subheader("🎯 Job-Tailored Resume")
            st.markdown("Paste the job description below to create a resume tailored specifically for this position.")
            
            job_description = st.text_area(
                "Job Description", 
                height=200,
                placeholder="Paste the complete job description here...",
                help="Include the full job posting - responsibilities, requirements, qualifications, etc."
            )
            
            if st.button("🔍 Analyze Job & Tailor Resume", type="primary"):
                if job_description:
                    try:
                        with st.spinner("Analyzing job description and tailoring your resume..."):
                            analyzer = get_job_analyzer()
                            if not analyzer:
                                st.error("Something is wrong with the get_job_analyzer function.")
                                st.stop()
                            
                            analysis = analyzer.analyze_job_description(job_description)
                            
                            # Calculate skills coverage
                            all_skills = []
                            for category in ['programming_skills', 'technologies', 'language_skills', 'certifications']:
                                skills_text = profile.get(category, '')
                                if skills_text:
                                    all_skills.extend([s.strip() for s in skills_text.split(',') if s.strip()])
                            
                            coverage_score = analyzer.calculate_match_score(all_skills, analysis)
                            
                            # Auto-save job analysis to database
                            try:
                                # Extract job title and company from job description if possible
                                job_title = "Unknown Position"
                                company = "Unknown Company"
                                
                                # Try to extract from analysis if available
                                if analysis.get('job_title'):
                                    job_title = analysis['job_title']
                                if analysis.get('company'):
                                    company = analysis['company']
                                
                                analysis_id = job_storage.save_job_analysis(
                                    job_description=job_description,
                                    analysis=analysis,
                                    job_title=job_title,
                                    company=company
                                )
                                st.success(f"✅ Job analysis automatically saved to database!")
                            except Exception as e:
                                st.warning(f"Could not save to database: {e}")
                            
                            # Store tailored resume data
                            st.session_state.tailored_resume = {
                                'job_analysis': analysis,
                                'coverage_score': coverage_score,
                                'job_description': job_description,
                                'timestamp': datetime.now().isoformat()
                            }
                        
                        st.success("✅ Resume tailored successfully!")
                        
                        # Show tailoring results
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Skills Coverage", f"{coverage_score}%", "Based on job requirements")
                            st.write(f"**Experience Level Required:** {analysis['experience_level'].title()}")
                        
                        with col2:
                            if analysis['priority_skills']:
                                st.write("**Key Skills for This Job:**")
                                for skill in analysis['priority_skills'][:5]:
                                    # Handle different priority skill formats
                                    if isinstance(skill, dict):
                                        skill_name = skill.get('skill', str(skill))
                                        # Check for in_requirements (from regular analyzer) or importance (from LLM analyzer)
                                        is_high_priority = skill.get('in_requirements', False) or skill.get('importance') == 'high'
                                        priority_indicator = "🔥" if is_high_priority else "⭐"
                                    else:
                                        skill_name = str(skill)
                                        priority_indicator = "⭐"
                                    st.write(f"{priority_indicator} {skill_name}")
                        
                        # Tailoring insights
                        st.markdown("### 💡 Tailoring Applied")
                        
                        generator = get_resume_generator()
                        
                        # Skills insights
                        original_skills = generator.generate_categorized_skills_text(profile)
                        tailored_skills = generator.generate_tailored_skills(profile, analysis)
                        
                        if original_skills != tailored_skills:
                            with st.expander("🛠️ Skills Optimization"):
                                st.write("**Skills have been reordered to highlight job-relevant capabilities:**")
                                st.write(f"**Optimized Skills:** {tailored_skills[:200]}...")
                        
                        # Experience insights
                        experiences = profile.get('experiences', [])
                        if experiences:
                            prioritized_exp = generator.prioritize_experiences(experiences, analysis)
                            if experiences != prioritized_exp:
                                with st.expander("💼 Experience Prioritization"):
                                    st.write("**Experience has been reordered by relevance to this job:**")
                                    for i, exp in enumerate(prioritized_exp[:3]):
                                        st.write(f"{i+1}. {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
                        
                        st.info("🎯 Switch to the 'Preview Resume' tab to see your tailored resume!")
                        
                    except Exception as e:
                        st.error(f"Error analyzing job description: {str(e)}")
                else:
                    st.error("Please provide a job description.")
            
            # Show current tailored resume status
            if hasattr(st.session_state, 'tailored_resume'):
                with st.expander("ℹ️ Current Tailored Resume Status"):
                    tailored_data = st.session_state.tailored_resume
                    st.write(f"**Created:** {tailored_data.get('timestamp', 'Unknown')}")
                    st.write(f"**Skills Coverage:** {tailored_data.get('coverage_score', 0)}%")
                    
                    if st.button("🗑️ Clear Tailored Resume"):
                        del st.session_state.tailored_resume
                        st.rerun()
        
        with tab2:
            st.subheader("👁️ Preview & Download Resume")
            
            # Check if tailored resume exists
            has_tailored = hasattr(st.session_state, 'tailored_resume')
            
            if has_tailored:
                job_analysis = st.session_state.tailored_resume.get('job_analysis')
                coverage = st.session_state.tailored_resume.get('coverage_score', 0)
                
                # Status and controls
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.success("🎯 Job-Tailored Resume Ready")
                    st.metric("Skills Coverage", f"{coverage}%", "Optimized for analyzed job")
                
                with col2:
                    show_comparison = st.checkbox("🔄 Show Comparison")
                
                with col3:
                    format_choice = st.selectbox("Format", ["PDF", "Word Document"])
                
                # Download button at the top
                if st.button("📥 Generate & Download Resume", type="primary", use_container_width=True):
                    try:
                        with st.spinner(f"Generating {format_choice.lower()}..."):
                            generator = get_resume_generator()
                            
                            if format_choice == "PDF":
                                buffer = generator.generate_pdf_resume(profile, job_analysis)
                                filename = "resume_tailored.pdf"
                                mime_type = "application/pdf"
                            else:  # Word Document
                                buffer = generator.generate_word_resume(profile, job_analysis)
                                filename = "resume_tailored.docx"
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        
                        # Immediate download
                        st.download_button(
                            label=f"📥 Download {format_choice}",
                            data=buffer.getvalue(),
                            file_name=filename,
                            mime=mime_type,
                            type="primary",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Error generating {format_choice.lower()}: {str(e)}")
                
                st.divider()
                
                # Preview section
                generator = get_resume_generator()
                preview = get_resume_preview()
                
                if show_comparison:
                    preview.show_comparison(profile, job_analysis, generator)
                else:
                    preview.display_preview(profile, job_analysis, generator)
                
                # Tailoring details
                st.divider()
                
                with st.expander("📊 Tailoring Details", expanded=False):
                    analysis = st.session_state.tailored_resume.get('job_analysis', {})
                    col1, col2 = st.columns(2)
                    with col1:
                        # Handle different priority skill formats for display
                        priority_skills = analysis.get('priority_skills', [])
                        if priority_skills:
                            skill_names = []
                            for s in priority_skills[:5]:
                                if isinstance(s, dict):
                                    skill_names.append(s.get('skill', str(s)))
                                else:
                                    skill_names.append(str(s))
                            st.write(f"**Priority Skills:** {', '.join(skill_names)}")
                        else:
                            st.write("**Priority Skills:** None identified")
                        st.write(f"**Experience Level:** {analysis.get('experience_level', 'Unknown').title()}")
                    with col2:
                        st.write(f"**Key Requirements:** {len(analysis.get('requirements', []))} identified")
                        st.write(f"**Technical Skills:** {len(analysis.get('technical_skills', []))} found")
            
            else:
                st.warning("⚠️ No tailored resume available. Please analyze a job description in the 'Tailor Resume' tab first.")
                st.info("💡 Once you analyze a job description, your tailored resume preview will appear here.")

# Job History Page
elif st.session_state.selected_page == "Job History":
    st.title("📊 Job Analysis History")
    
    try:
        # Database status check
        db_info = db_manager.get_database_info()
        if not db_info['connected']:
            st.error("🔴 Database not connected. Please configure database in the sidebar.")
            st.stop()
        
        # Statistics
        stats = job_storage.get_analysis_stats()
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Analyses", stats.get('total_analyses', 0))
            with col2:
                st.metric("Unique Companies", stats.get('unique_companies', 0))
            with col3:
                top_skills = stats.get('top_skills', [])
                st.metric("Top Skill", top_skills[0][0] if top_skills else "None")
            with col4:
                exp_levels = stats.get('experience_levels', {})
                most_common_level = max(exp_levels.items(), key=lambda x: x[1])[0] if exp_levels else "None"
                st.metric("Common Level", most_common_level.title())
        
        st.divider()
        
        # Search and filters
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search job analyses", placeholder="Search by job title, company, or skills...")
        with col2:
            limit = st.selectbox("Show", [10, 20, 50], index=1)
        
        # Filter options
        with st.expander("🎯 Advanced Filters"):
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                companies = stats.get('companies', [])
                selected_company = st.selectbox("Company", ["All"] + companies, index=0)
            with filter_col2:
                exp_levels = list(stats.get('experience_levels', {}).keys())
                selected_exp_level = st.selectbox("Experience Level", ["All"] + exp_levels, index=0)
        
        # Get job analyses
        if search_term:
            analyses = job_storage.search_analyses(search_term, limit=limit)
        else:
            company_filter = None if selected_company == "All" else selected_company
            exp_level_filter = None if selected_exp_level == "All" else selected_exp_level
            analyses = job_storage.get_job_analyses(
                limit=limit, 
                company=company_filter, 
                experience_level=exp_level_filter
            )
        
        if analyses:
            st.subheader(f"📋 Found {len(analyses)} job analyses")
            
            for i, analysis in enumerate(analyses):
                with st.expander(f"#{i+1} {analysis.get('job_title', 'Unknown Position')} @ {analysis.get('company', 'Unknown Company')}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Job Title:** {analysis.get('job_title', 'N/A')}")
                        st.write(f"**Company:** {analysis.get('company', 'N/A')}")
                        st.write(f"**Experience Level:** {analysis.get('experience_level', 'N/A').title()}")
                        st.write(f"**Skills Count:** {analysis.get('skills_count', 0)}")
                        
                        # Show top skills
                        analysis_data = analysis.get('analysis', {})
                        technical_skills = analysis_data.get('technical_skills', [])[:5]
                        if technical_skills:
                            st.write(f"**Top Skills:** {', '.join(technical_skills)}")
                    
                    with col2:
                        created_at = analysis.get('created_at', '')
                        if created_at:
                            from datetime import datetime
                            try:
                                dt = datetime.fromisoformat(created_at)
                                st.write(f"**Analyzed:** {dt.strftime('%Y-%m-%d %H:%M')}")
                            except:
                                st.write(f"**Analyzed:** {created_at}")
                        
                        # Action buttons
                        if st.button(f"🗑️ Delete", key=f"delete_{analysis['_id']}"):
                            if job_storage.delete_job_analysis(analysis['_id']):
                                st.success("Analysis deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete analysis")
                    
                    # Job description preview
                    job_desc = analysis.get('job_description', '')
                    if job_desc:
                        st.write("**Job Description:**")
                        st.text_area("", value=job_desc[:500] + "..." if len(job_desc) > 500 else job_desc, height=100, disabled=True, key=f"desc_{analysis['_id']}")
        else:
            st.info("🔍 No job analyses found. Start by analyzing some job descriptions!")
            if st.button("📝 Analyze Your First Job"):
                st.session_state.selected_page = "Export Resume"
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading job history: {e}")
        st.info("Make sure your database is properly configured in the sidebar.")