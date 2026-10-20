from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Resume
from .utils import extract_text, detect_skills, calculate_score, generate_suggestions, match_with_job_description

class ResumeUploadAPIView(APIView):
    """
    Handles uploading a single resume, extracting text, scoring it, and generating suggestions.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        jd_text = request.data.get('job_description', '') 
        
        if not file_obj:
            return Response({"error": "No file provided"}, status=400)

        # Save the uploaded file to the database
        resume = Resume.objects.create(user=request.user, file=file_obj)
        
        # Extract text from the file
        extracted = extract_text(resume.file.path)
        
        if extracted.startswith("Error:"):
            resume.delete() # Remove invalid file
            return Response({"error": extracted}, status=400)

        resume.extracted_text = extracted
        
        # AI Analysis: Skills, Score, Suggestions
        skills_found = detect_skills(extracted)
        final_score = calculate_score(extracted, skills_found)
        suggestions = generate_suggestions(skills_found, extracted)
        
        resume.score = final_score
        resume.save()

        # Match with Job Description if provided
        match_data = None
        if jd_text.strip():
            match_data = match_with_job_description(extracted, jd_text)

        return Response({
            "message": "Resume uploaded successfully!",
            "resume_id": resume.id,
            "skills_found": skills_found, 
            "score": final_score,
            "suggestions": suggestions,
            "match_data": match_data,
            "text_preview": extracted[:500] + "..." if len(extracted) > 500 else extracted
        }, status=201)


class ResumeRankingAPIView(APIView):
    """
    Handles uploading multiple resumes at once, analyzing them, and ranking them.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Get the list of files from the request
        files = request.FILES.getlist('files')
        jd_text = request.data.get('job_description', '')

        if not files:
            return Response({"error": "No files provided"}, status=400)

        results = []

        for file_obj in files:
            # Save each file temporarily
            resume = Resume.objects.create(user=request.user, file=file_obj)
            extracted = extract_text(resume.file.path)
            
            # Skip broken or unsupported files
            if extracted.startswith("Error:"):
                resume.delete()
                continue 

            resume.extracted_text = extracted
            skills_found = detect_skills(extracted)
            final_score = calculate_score(extracted, skills_found)
            resume.score = final_score
            resume.save()

            # Calculate Job Description Match %
            match_percentage = 0
            if jd_text.strip():
                match_data = match_with_job_description(extracted, jd_text)
                match_percentage = match_data["match_percentage"]

            results.append({
                "filename": file_obj.name,
                "score": final_score,
                "match_percentage": match_percentage,
                "skills_count": len(skills_found)
            })

        # Sort the results from highest score to lowest
        results.sort(key=lambda x: x['score'], reverse=True)

        # Assign a Rank to each result
        for index, res in enumerate(results):
            res['rank'] = index + 1

        return Response({
            "message": "Batch processed successfully",
            "total_files": len(files),
            "ranking": results
        }, status=200)