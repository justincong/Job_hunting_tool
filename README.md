# Resume Builder & Refiner

An intelligent web application built with Streamlit that helps you refine and tailor your resume for different job applications.

## Features

- **Profile Management**: Store and manage your professional information, experiences, and skills
- **Resume Upload**: Upload existing PDF/Word resumes to extract information
- **Job Matching**: Analyze job descriptions and generate tailored resumes
- **Export Options**: Download refined resumes in PDF or Word format

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Setup Profile**: Add your personal information, experiences, and skills
2. **Upload Resume**: (Optional) Upload existing resume to populate profile
3. **Match Job**: Input job description to generate tailored resume
4. **Export**: Download your refined resume in preferred format

## Project Structure

```
resume_builder/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── modules/           # Core functionality modules
│   ├── resume_parser.py
│   ├── job_analyzer.py
│   ├── resume_generator.py
│   └── profile_manager.py
└── data/              # Data storage
    └── profile_data.json
```