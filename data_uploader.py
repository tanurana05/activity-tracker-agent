import os
import shutil
import boto3
import gzip
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime

class DataUploader:
    def __init__(self, base_directory, cloud_upload=False, bucket_name=None, aws_access_key_id=None, aws_secret_access_key=None):
        self.base_directory = base_directory
        self.cloud_upload = cloud_upload
        self.bucket_name = bucket_name
        self.s3_client = None
        
        # Initialize S3 client if cloud upload is enabled
        if self.cloud_upload and bucket_name and aws_access_key_id and aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        elif self.cloud_upload:
            raise ValueError("Cloud upload requires valid AWS credentials and a bucket name.")
        
        # Ensure the base directory exists for local storage
        os.makedirs(self.base_directory, exist_ok=True)

    def upload_file(self, file_path, destination_name):
        """Uploads a single file to either local storage or cloud."""
        destination = os.path.join(self.base_directory, destination_name)
        try:
            if not os.path.exists(file_path):
                print(f"File {file_path} not found")
                return

            if self.cloud_upload:
                self.upload_to_cloud(file_path, destination_name)
            else:
                # Handle file overwrite by renaming the destination if it exists
                destination = self.handle_file_conflict(destination_name)
                shutil.move(file_path, destination)  # Use shutil.move to handle file operations
                print(f"Saved locally: {file_path} to {destination}")

        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")

    def handle_file_conflict(self, destination_name):
        """Handles potential file conflicts by renaming the file."""
        destination = os.path.join(self.base_directory, destination_name)
        if os.path.exists(destination):
            base, ext = os.path.splitext(destination_name)
            counter = 1
            new_destination_name = f"{base}_{counter}{ext}"
            while os.path.exists(os.path.join(self.base_directory, new_destination_name)):
                counter += 1
                new_destination_name = f"{base}_{counter}{ext}"
            destination = os.path.join(self.base_directory, new_destination_name)
        return destination

    def upload_multiple_files(self, file_paths):
        """Uploads multiple files by delegating to `upload_file`."""
        for file_path in file_paths:
            destination_name = os.path.basename(file_path)
            self.upload_file(file_path, destination_name)

    def upload_to_cloud(self, file_path, destination_name):
        """Handles file compression and cloud upload to S3."""
        compressed_file_path = self.compress_file(file_path)

        # Create a timestamped directory structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_name = os.path.join("screenshots", f"screenshot_{timestamp}.png.gz")  # Modify the extension as needed

        try:
            self.s3_client.upload_file(
                compressed_file_path,
                self.bucket_name,
                destination_name,
                ExtraArgs={'ContentType': 'application/octet-stream', 'ACL': 'private'}
            )
            print(f"Uploaded {file_path} to cloud storage as {destination_name}.")
        except FileNotFoundError:
            print(f"The file {file_path} was not found.")
        except (NoCredentialsError, PartialCredentialsError):
            print("AWS credentials not available.")
        except Exception as e:
            print(f"An error occurred during cloud upload: {e}")
        finally:
            # Remove the compressed file after upload
            if os.path.exists(compressed_file_path):
                os.remove(compressed_file_path)

    def compress_file(self, file_path):
        """Compresses the file using gzip if its size is greater than 5 MB."""
        compressed_file_path = f"{file_path}.gz"
        try:
            # Check file size
            if os.path.getsize(file_path) > 5 * 1024 * 1024:  # 5 MB in bytes
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"Compressed {file_path} to {compressed_file_path}")
                return compressed_file_path
            else:
                print(f"File {file_path} is not larger than 5 MB. Skipping compression.")
                return file_path  # Return the original file path if not compressed
        except Exception as e:
            print(f"Error while compressing {file_path}: {e}")
            return file_path  # Return the original file path in case of an error

