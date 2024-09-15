from rest_framework.views import APIView
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from .serializers import CandidateSerializer
from .services import extract_resume_info, fallback_extract_resume_info

@method_decorator(require_http_methods(["POST"]), name='dispatch')
class ExtractResumeView(APIView):
    def post(self, request):
        try:
            resume_file = request.FILES.get('resume')
            if not resume_file:
                return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check file type
            allowed_types = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if resume_file.content_type not in allowed_types:
                return Response({'error': 'Invalid file type. Only PDF and Word documents are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Uploaded file name: {resume_file.name}")
            print(f"Uploaded file size: {resume_file.size} bytes")
            print(f"Uploaded file content type: {resume_file.content_type}")

            # Try primary extraction method
            extracted_info = extract_resume_info(resume_file)
            
            # If primary method fails, use fallback method
            if 'error' in extracted_info:
                print("Primary extraction failed. Using fallback method.")
                extracted_info = fallback_extract_resume_info(resume_file)
            
            print(f"Final extracted info: {extracted_info}")
            
            serializer = CandidateSerializer(data=extracted_info)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)