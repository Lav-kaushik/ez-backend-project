import os
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.base_path = 'ez_inter_project/'
    
    def upload_file(self, file, file_name: str):
        """
        Upload a file to an S3 bucket
        :param file: File object to upload
        :param file_name: S3 object name
        :return: S3 path if file was uploaded, else None
        """
        try:
            object_name = f"{self.base_path}{file_name}"
            self.s3_client.upload_fileobj(file, self.bucket_name, object_name)
            return f"s3://{self.bucket_name}/{object_name}"
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading file to S3"
            )
    
    def get_file_key_from_path(self, s3_path: str):
        """
        Extract the file key from an S3 path
        :param s3_path: Full S3 path (s3://bucket-name/key)
        :return: File key
        """
        if s3_path.startswith(f"s3://{self.bucket_name}/"):
            return s3_path.replace(f"s3://{self.bucket_name}/", "")
        return s3_path
    
    def generate_presigned_url(self, file_key: str, expiration: int = 3600):
        """
        Generate a presigned URL to share an S3 object
        :param file_key: S3 object key
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            response = self.s3_client.generate_presigned_url('get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating download URL"
            )

# Initialize S3 service
s3_service = S3Service()
