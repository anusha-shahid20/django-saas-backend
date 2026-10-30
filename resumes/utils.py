import PyPDF2
import docx
import os

# A universal list of skills covering IT, Business, HR, Finance, and General fields
COMMON_SKILLS = [
    # IT & Software
    "python", "django", "javascript", "react", "node.js", "sql", "html", "css", "tailwind", "php", "laravel", "c++", "java", "aws", "docker", "git", "api", "rest", "machine learning", "ai", "data science", "typescript", "mongodb", "postgresql",
    # Business & Marketing
    "marketing", "sales", "seo", "social media", "content writing", "branding", "market research", "e-commerce", "business development", "crm", "email marketing",
    # HR & Management
    "recruitment", "human resources", "hr", "management", "leadership", "team building", "communication", "negotiation", "onboarding", "performance management", "training",
    # Finance & Accounting
    "finance", "accounting", "excel", "financial analysis", "budgeting", "auditing", "taxation", "quickbooks", "sap",
    # General / Soft Skills
    "project management", "microsoft office", "customer service", "problem solving", "analytical", "time management", "presentation", "research", "operations"
]

def extract_text(file_path):
    """
    Extracts text from a PDF or DOCX file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        else:
            return "Error: Unsupported file format. Only PDF and DOCX are allowed."
            
    except Exception as e:
        return f"Error: Could not read file. {str(e)}"
        
    return text.strip()

def detect_skills(text):
    """
    Scans the text and returns a list of found skills.
    """
    if not text:
        return []
        
    text_lower = text.lower()
    found_skills = []
    
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found_skills.append(skill.title())  # Capitalize nicely (e.g., "Python")
            
    return list(set(found_skills)) # Remove duplicates

def calculate_score(text, skills_found):
    """
    Strict scoring system. Rewards strong skills and real experience.
    Does not give full marks for just having a long CV.
    """
    score = 0
    text_lower = text.lower()
    
    # 1. Skills Score (Max 40 points) - STRICT
    # 4 points per skill, capped at 40 (Needs 10+ skills to get full 40)
    skill_score = min(len(skills_found) * 4, 40) 
    score += skill_score

    # 2. Experience Score (Max 30 points) - STRICT
    # Full 30 points ONLY for actual job. Internship gets 15. Projects get 5.
    if any(word in text_lower for word in ['experience', 'worked at', 'job', 'company', 'employment']):
        if 'seeking' not in text_lower and 'looking for' not in text_lower:
            score += 30 
    elif any(word in text_lower for word in ['intern', 'internship', 'volunteer']):
        score += 15 
    elif 'project' in text_lower or 'projects' in text_lower:
        score += 5 

    # 3. Education Score (Max 20 points) - STRICT
    # Must have a proper university degree
    education_score = 0
    if any(word in text_lower for word in ['university', 'college', 'bachelor', 'bs ', 'ms ', 'master']):
        education_score += 15
    if any(word in text_lower for word in ['certificate', 'certified', 'certification']):
        education_score += 5
    score += education_score

    # 4. CV Length Quality (Max 10 points) - LOW WEIGHTAGE
    # Word count matters less. Only needs to be at least 150 words.
    word_count = len(text.split())
    if word_count > 200:
        score += 10
    elif word_count > 100:
        score += 5

    # Ensure the score does not exceed 100
    return min(score, 100)

def generate_suggestions(skills_found, text):
    """
    Generates strict, actionable suggestions based on missing sections.
    """
    suggestions = []
    text_lower = text.lower()
    
    if len(skills_found) < 5:
        suggestions.append("Your CV lacks specific technical or professional skills. Add more relevant skills.")
    
    if 'experience' not in text_lower and 'intern' not in text_lower and 'job' not in text_lower:
        suggestions.append("You need to add a proper 'Experience' section with real job or internship details.")
        
    if 'university' not in text_lower and 'degree' not in text_lower and 'college' not in text_lower:
        suggestions.append("Your Education section is missing or incomplete. Add your degree and university name.")
        
    if len(text.split()) < 100:
        suggestions.append("Your CV is too short. Add more details about your projects, achievements, and skills.")

    if not suggestions:
        suggestions.append("Your CV looks strong and professional!")
        
    return suggestions

def match_with_job_description(resume_text, jd_text):
    """
    Compares the resume text with a job description to find a match percentage.
    """
    resume_skills = set(detect_skills(resume_text))
    jd_skills = set(detect_skills(jd_text))
    
    if not jd_skills:
        return {"match_percentage": 0, "missing_skills": [], "message": "No recognizable skills found in the Job Description."}

    missing_skills = list(jd_skills - resume_skills)
    matched_skills = list(jd_skills.intersection(resume_skills))
    
    # Calculate Match Percentage based on how many JD skills the resume has
    match_percentage = (len(matched_skills) / len(jd_skills)) * 100
    
    return {
        "match_percentage": round(match_percentage, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }