import PyPDF2
import docx
import os

# List of common tech skills to look for in the resume
COMMON_SKILLS = [
    "python", "django", "javascript", "react", "next.js", "node.js", 
    "sql", "html", "css", "tailwind", "php", "laravel", "c++", "java", 
    "aws", "docker", "git", "api", "rest", "machine learning", "ai",
    "typescript", "mongodb", "postgresql"
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
    Calculates a strict score out of 100 based on skills, experience type, and content.
    """
    score = 0
    text_lower = text.lower()
    
    # 1. Skills Score (Max 40 points) - 4 points per skill
    skill_score = min(len(skills_found) * 4, 40) 
    score += skill_score

    # 2. Experience Score (Max 30 points)
    if 'experience' in text_lower or 'worked' in text_lower or 'job' in text_lower or 'company' in text_lower:
        score += 30  # Full points for actual job experience
    elif 'intern' in text_lower or 'internship' in text_lower:
        score += 15  # Half points for internship
    elif 'project' in text_lower:
        score += 10  # Fewer points for just projects

    # 3. Content & Education Score (Max 30 points)
    word_count = len(text.split())
    has_education = any(word in text_lower for word in ['university', 'degree', 'bs', 'bachelor', 'ms', 'master', 'education'])
    
    if word_count > 150 and has_education:
        score += 30
    elif word_count > 80:
        score += 15

    return min(score, 100)

def generate_suggestions(skills_found, text):
    """
    Generates actionable suggestions based on missing skills and text length.
    """
    suggestions = []
    target_skills = ["python", "django", "javascript", "react", "sql", "html", "css", "git"]
    
    skills_found_lower = [s.lower() for s in skills_found]
    missing_skills = [skill.title() for skill in target_skills if skill not in skills_found_lower]
    
    if missing_skills:
        suggestions.append(f"Consider learning and adding these core skills to your resume: {', '.join(missing_skills)}.")
    
    text_lower = text.lower()
    if 'experience' not in text_lower and 'intern' not in text_lower and 'project' not in text_lower:
        suggestions.append("Add an 'Experience' or 'Projects' section to showcase your practical work.")
        
    if len(text.split()) < 50:
        suggestions.append("Your resume is too short. Add more details about your education, projects, and achievements.")

    if not suggestions:
        suggestions.append("Your resume looks great! No major improvements suggested.")
        
    return suggestions

def match_with_job_description(resume_text, jd_text):
    """
    Compares the resume text with a job description to find a match percentage.
    """
    resume_skills = set(detect_skills(resume_text))
    jd_skills = set(detect_skills(jd_text))
    
    if not jd_skills:
        return {"match_percentage": 0, "missing_skills": [], "message": "No recognizable tech skills found in the Job Description."}

    missing_skills = list(jd_skills - resume_skills)
    matched_skills = list(jd_skills.intersection(resume_skills))
    
    # Calculate Match Percentage based on how many JD skills the resume has
    match_percentage = (len(matched_skills) / len(jd_skills)) * 100
    
    return {
        "match_percentage": round(match_percentage, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }