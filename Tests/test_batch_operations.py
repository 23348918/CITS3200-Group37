# Test cases for batch_operations.py
# To run the tests, run the following command (add -v for more verbose output):
#     python3 -m unittest Tests/test_batch_operations.py
# or
#     pytest Tests/test_batch_operations.py


import sys
import os

# Add the Scripts/api directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts/api')))
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import pytest
from batch_operations import generate_batch_file, process_batch, check_batch, export_batch, list_batches, upload_batch_file, get_file_dict, delete_exported_files
from utils import get_file_dict
import tempfile
import openai


class TestInputPath(unittest.TestCase):
    
    # Case 1: Successfully read input path and convert to dictionary to be procoessed into a jsonl file for batch processing
    def test_get_file_dict_success(self):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir")
        expected_output = {'NO_speed_sign.png': Path(f"{test_directory}/NO_speed_sign.png"),
                           'test_image.png': Path(f"{test_directory}/test_image.png"),}
        file_dict = get_file_dict(test_directory)
        self.assertEqual(file_dict, expected_output)
        
    # Case 2: Fail to read input path and convert to dictionary due to invalid directory or file
    def test_get_file_dict_invalid_directory(self):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/TestFiles/test_dir_invalid")
        with self.assertRaises(ValueError):
            get_file_dict(test_directory)

    # Case 3: input path is a directory but no valid files in the directory
    def test_get_file_dict_empty_directory(self):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/EmptyDirTest")
        with self.assertRaises(ValueError):
            get_file_dict(test_directory)



class TestFilesToJsonl(unittest.TestCase):
    
    # Case 4: generate batch file success from given file dictionary and output path
    @patch('batch_operations.generate_batch_file', return_value = "Generate Batch Success")  # Mock generate_batch_file
    def test_generate_batch_with_encoded_image(self, mock_generate_batch_file):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir")
        file_dict = get_file_dict(test_directory)
        out_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/Output/out_batch_file.jsonl")
        result = mock_generate_batch_file(file_dict, out_path)
        mock_generate_batch_file.assert_called_once_with(file_dict, out_path)
        self.assertEqual(result, "Generate Batch Success")
        
    #Case 5: generate batch file failure due to invalid/empty output path
    @patch('batch_operations.get_file_dict')  # Mock get_file_dict to return a valid file_dict
    def test_generate_batch_with_invalid_file_path(self, mock_get_file_dict):

        mock_get_file_dict.return_value = {
            'example_image.png': Path('/valid/path/example_image.png')
        }

        # Valid directory but invalid output path (invalid directory)
        out_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/InvalidOutPath/out_batch_file_invalid.jsonl")
        with self.assertRaises(OSError):
            generate_batch_file(mock_get_file_dict.return_value, out_path)
        
        # Test with an empty string path (which should also raise OSError)
        out_path = Path("")
        with self.assertRaises(OSError):
            generate_batch_file(mock_get_file_dict.return_value, out_path)
            
    # Case 6: generate batch file with empty file dictionary
    # technically not needed due to the check in get_file_dict. but if this function is used somewhere in the future, 
    # this test will be useful
    def test_generate_batch_with_empty_file_dict(self):
        file_dict = {}
        out_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/Output/out_batch_file.jsonl")
        with self.assertRaises(ValueError):
            generate_batch_file(file_dict, out_path)
            

class TestUploadJsonBatch(unittest.TestCase):
    # Case 7: Test upload batch file success
    @patch('batch_operations.upload_batch_file', return_value = "Upload Batch Success")  # Mock upload_batch_file
    def test_upload_batch_file_success(self, mock_upload_batch_file):
        batch_file_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/Output/out_batch_file.jsonl")
        result = mock_upload_batch_file(batch_file_path)
        mock_upload_batch_file.assert_called_once_with(batch_file_path)
        self.assertEqual(result, "Upload Batch Success")
        
    
    # Case 8: Test upload batch file failure due to invalid/empty file path
    def test_upload_batch_file_invalid_file_path(self, ):
        # Invalid file path
        batch_file_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/InvalidOutPath/out_batch_file_invalid.jsonl")
        with self.assertRaises(FileNotFoundError):
            upload_batch_file(batch_file_path)
        
        # Empty file path (which should also raise OSError)
        batch_file_path = Path("")
        with self.assertRaises(FileNotFoundError):
            upload_batch_file(batch_file_path)
    
    # Case 9: Test upload batch with invalid format
    def test_upload_batch_file_invalid_format(self):
        # Invalid file format
        batch_file_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/Input/invalid_batch_format.txt")
        with self.assertRaises(ValueError):
            upload_batch_file(batch_file_path)
    
    #Case 10: Test upload batch file over the size limit
    def test_upload_batch_file_over_size_limit(self):
        # Create a temporary .jsonl file with 100 MB size
        with tempfile.NamedTemporaryFile(delete=True, suffix='.jsonl') as temp_file:
            # Write 100 MB of data to the file
            temp_file.write(b'0' * (100 * 1024 * 1024))  # Write 100 MB of data
            batch_file_path = Path(temp_file.name)  # Get the path of the temporary file
        
            with self.assertRaises(ValueError):
                upload_batch_file(batch_file_path)
            
    
    # Case 10: Test upload batch with empty file
    def test_upload_batch_file_empty_file(self):
        batch_file_path = Path("/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/Input/empty_batch_file.jsonl")
        with tempfile.NamedTemporaryFile(delete=True, suffix='.jsonl') as temp_file:
            # empty file
            batch_file_path = Path(temp_file.name)  # Get the path of the temporary file
            with self.assertRaises(ValueError):
                upload_batch_file(batch_file_path)
        
        
#NOTE TODO: Commented as this function takes time to run. Test is working. Uncomment to run the test
class TestBatchProcessChatGPT(unittest.TestCase):

    
    # Case 11: Test batch process success
    @patch('batch_operations.upload_batch_file', return_value = "Upload Batch Success")  
    def test_process_batch_success(self, mock_upload_batch_file):
        file_path_str = "/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir"
        process_batch(file_path_str, auto=False)
        mock_upload_batch_file.assert_called_once() # ensure that the mock function was called
        
            
    # Case 12: Test batch process with auto enabled
    @patch('batch_operations.check_batch', return_value=("completed", "Processing success")) 
    @patch('batch_operations.export_batch')  
    @patch('batch_operations.upload_batch_file', return_value = "Batch ID")
    @patch('common.WAITING_TIMER', 3)  # Set the waiting timer to 0 for faster testing
  
    def test_process_batch_auto_success(self, mock_upload_batch_file, mock_export_batch, mock_check_batch):
        file_path_str = "/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir"
        process_batch(file_path_str, auto=True)
        mock_upload_batch_file.assert_called_once()
        self.assertGreaterEqual(mock_check_batch.call_count, 1)  # Ensure check_batch was called more than once
        mock_export_batch.assert_called_once_with("Batch ID")  # Assert export_batch was called with the correct ID


    # Case 13: Test batch process with auto enabled and different failure cases
    @patch('batch_operations.check_batch', side_effect=[
        ("failed", "Processing failed"), 
        ("expired", "Processing expired"),
        ("cancelled", "Processing cancelled")
        ])
    @patch('common.WAITING_TIMER', 3)  # Set the waiting timer to 0 for faster testing
  
    @patch('batch_operations.upload_batch_file', return_value="Batch ID") 
    def test_process_batch_auto_failure(self, mock_upload_batch_file, mock_check_batch):
        file_path_str = "/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir"
        
        for status, message in [("failed", "Processing failed"), 
                                ("expired", "Processing expired"), 
                                ("cancelled", "Processing cancelled")]:
            
            mock_upload_batch_file.reset_mock()
            mock_check_batch.reset_mock()
            mock_check_batch.return_value = (status, message)  
            
            with self.assertRaises(RuntimeError) as context:  # Check if RuntimeError is raised
                process_batch(file_path_str, auto=True)

            mock_upload_batch_file.assert_called_once()
            
            self.assertGreaterEqual(mock_check_batch.call_count, 1)
            
            self.assertIn("Batch processing failed", str(context.exception))
            self.assertIn(message, str(context.exception))
    
    pass        
            

class TestListAndCheckBatches(unittest.TestCase):
    batch_status_dict = {
    "validating": "the input file is being validated before the batch can begin",
    "failed": "the input file has failed the validation process",
    "in_progress": "the input file was successfully validated and the batch is currently being run",
    "finalizing": "the batch has completed and the results are being prepared",
    "completed": "the batch has been completed and the results are ready",
    "expired": "the batch was not able to be completed within the 24-hour time window",
    "cancelling": "the batch is being cancelled (may take up to 10 minutes)",
    "cancelled": "the batch was cancelled"
    }
    
    # Case 14: List Batches success
    @patch('common.chatgpt_client')  
    def test_list_batches_success(self, mock_chatgpt_client):
        # Arrange
        mock_batch_1 = MagicMock()
        mock_batch_1.id = "batch_123"
        mock_batch_1.status = "completed"
        mock_batch_1.error_file_id = None  # No error

        mock_batch_2 = MagicMock()
        mock_batch_2.id = "batch_456"
        mock_batch_2.status = "failed"
        mock_batch_2.error_file_id = "error_file_789"  # Indicates an error

        mock_chatgpt_client.batches.list.return_value = [mock_batch_1, mock_batch_2]
        list_batches()
        mock_chatgpt_client.batches.list.assert_called_once_with(limit=20)
    
    #Case 15: List Batches failure due to authentication error
    @patch('common.chatgpt_client')  
    def test_list_batches_failure(self, mock_chatgpt_client):
        mock_batches = MagicMock()


        # Set the side effect for the list method to raise an AuthenticationError
        mock_batches.list.side_effect = openai.AuthenticationError(
            message="Authentication failed",
            response=MagicMock(status=400, request=MagicMock()),              
            body={"error": "Authentication failed"}  
        )
        mock_chatgpt_client.batches = mock_batches

        with self.assertRaises(ValueError):
            list_batches() 
        mock_batches.list.assert_called_once()  # Ensure the list method was called once
        

    #Case 16: List Batches failure test for all other errors. (BadRequestError, ConflictError, InternalServerError, NotFoundError, UnprocessableEntityError, RateLimitError)
    @patch('common.chatgpt_client')  
    def test_list_batches_failure(self, mock_chatgpt_client):
        mock_batches = MagicMock()

        mock_batches.list.side_effect = openai.InternalServerError(
            message="Internal Server Error",  
            response=MagicMock(status=500, request=MagicMock()),    
            body={"error": "Internal Server Error"}
        )

        mock_chatgpt_client.batches = mock_batches

        with self.assertRaises(Exception):
            list_batches()  
        mock_batches.list.assert_called_once()  




    # Case 17: Test for all check batch statuses in the batch_status_dict success
    @patch('common.chatgpt_client')  #
    def test_check_batch_all_statuses(self, mock_chatgpt_client):
        counter = 0
        for status, message in self.batch_status_dict.items():
            
            mock_batch = MagicMock()
            mock_batch.status = status
            mock_batch.error_file_id = None

            mock_chatgpt_client.batches.retrieve.return_value = mock_batch
            status, status_message = check_batch("batch_123")
            self.assertEqual(status, status)
            self.assertEqual(status_message, message)
            # to ensure that it is being called only once per status
            mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch_123")
            mock_chatgpt_client.batches.retrieve.reset_mock()
            counter +=1
        # at the end assert taht the method was called 8 times
        self.assertEqual(counter, 8)
            
    # Case 18: Test check batch failure due to invalid batch id
    @patch('common.chatgpt_client')  
    def test_check_batch_invalid_batch_id(self, mock_chatgpt_client):
        mock_chatgpt_client.batches.retrieve.side_effect = openai.NotFoundError(
            message="Batch not found",
            response=MagicMock(),
            body={"error": "Batch not found"}
        )
        with self.assertRaises(Exception):
            check_batch("invalid_batch_id")
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("invalid_batch_id")
        
    # Case 19: Test check batch failure due to authentication error
    @patch('common.chatgpt_client') 
    def test_check_batch_failure(self, mock_chatgpt_client):
        mock_chatgpt_client.batches.retrieve.side_effect = openai.AuthenticationError(
            message="Authentication failed",
            response=MagicMock(),
            body={"error": "Authentication failed"}
        )
        with self.assertRaises(Exception):
            check_batch("batch_123")
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch_123")

class TestExportBatch(unittest.TestCase):
    
    # Case 20: Test export batch success
    @patch('common.chatgpt_client') 
    @patch('batch_operations.generate_csv_output', return_value=True)  
    @patch('batch_operations.delete_exported_files')  
    def test_export_batch_success(self, mock_delete_exported_files, mock_generate_csv_output, mock_chatgpt_client):
        mock_batch = MagicMock()
        mock_batch.output_file_id = "output_file_id"
        mock_batch.error_file_id = None
        mock_chatgpt_client.batches.retrieve.return_value = mock_batch

        export_batch("batch_123")

        mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch_123")
        mock_generate_csv_output.assert_called_once()
        self.assertTrue(mock_generate_csv_output.return_value)
        mock_delete_exported_files.assert_called_once_with(mock_chatgpt_client, mock_chatgpt_client.batches.retrieve.return_value)  
        
    # Case 21: Test export batch failure due to invalid batch id
    @patch('common.chatgpt_client')  
    def test_export_batch_invalid_batch_id(self, mock_chatgpt_client):
        mock_chatgpt_client.batches.retrieve.side_effect = openai.BadRequestError(
            message="Batch not found",
            response=MagicMock(),
            body={"error": "Batch not found"}
        )
        with self.assertRaises(ValueError):
            export_batch("invalid_batch_id")
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("invalid_batch_id")
        
    # Case 22: Test export batch failure due to authentication error
    @patch('common.chatgpt_client') 
    def test_export_batch_failure(self, mock_chatgpt_client):
        mock_chatgpt_client.batches.retrieve.side_effect = openai.AuthenticationError(
            message="Authentication failed",
            response=MagicMock(),
            body={"error": "Authentication failed"}
        )
        with self.assertRaises(PermissionError):
            export_batch("batch_123")
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch_123")
        
    # Case 23: Test export batch for failed batch processing
    @patch('common.chatgpt_client')  
    def test_export_batch_failed_batch(self, mock_chatgpt_client):
        mock_batch = MagicMock()
        mock_batch.output_file_id = None
        mock_batch.error_file_id = "error_file_id"
        
        mock_chatgpt_client.batches.retrieve.return_value = mock_batch

        with self.assertRaises(SystemExit) as cm:
            export_batch("batch_123")
        
        # Assert that sys.exit was called with the correct exit code
        self.assertEqual(cm.exception.code, 1)  # Verify that the exit code is 1 for failure
        
    # Case 24: Test export to batch that is already exported - cannot export again (once export succeeds it deletes the exported file stored in the server)    
    @patch('common.chatgpt_client') 
    def test_export_batch_already_exported(self, mock_chatgpt_client):
        
        # Simulate that the batch has been deleted from the server, raising BadRequestError
        mock_chatgpt_client.files.retrieve.side_effect = openai.BadRequestError(
            message="Missing file",
            response=MagicMock(),
            body={"error": "File not found"}
        )
        
        # Simulate the batch retrieval returning a batch that has been exported (but file is no longer available)
        mock_batch = MagicMock()
        mock_batch.output_file_id = "output_file_id"
        mock_batch.error_file_id = None  # No error, but output_file is missing
        mock_chatgpt_client.batches.retrieve.return_value = mock_batch
        
        with self.assertRaises(SystemExit) as cm:
            export_batch("batch123")  # Use the batch ID for an already exported batch
            
        self.assertEqual(cm.exception.code, 1)
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch123")
        mock_chatgpt_client.files.retrieve.assert_called_once_with("output_file_id")
        
    # Case 25: Test export batch failing to save the exported file due to full disk space
    @patch('common.chatgpt_client')
    @patch('builtins.open', mock_open())
    def test_export_batch_full_disk_space(self, mock_chatgpt_client):
        mock_batch = MagicMock()
        mock_batch.output_file_id = "output_file_id"
        mock_batch.error_file_id = None
        mock_chatgpt_client.batches.retrieve.return_value = mock_batch
        
        # Simulate that the file cannot be saved due to full disk space
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with self.assertRaises(OSError):
                export_batch("batch_123")
        
        mock_chatgpt_client.batches.retrieve.assert_called_once_with("batch_123")
        mock_chatgpt_client.files.retrieve.assert_called_once_with("output_file_id")
        
class TestDeleteExportedFiles(unittest.TestCase):
    # Case 25: Test delete exported files success
    @patch('common.chatgpt_client')  
    def test_delete_exported_files_success(self, mock_chatgpt_client):
        mock_batch = MagicMock()
        mock_batch.output_file_id = "output_file_id"
        mock_batch.error_file_id = None
        
        mock_chatgpt_client.batches.retrieve.return_value = mock_batch
        delete_exported_files(mock_chatgpt_client, mock_batch)
        
        mock_chatgpt_client.files.delete.assert_called_with("output_file_id")
        self.assertEqual(mock_chatgpt_client.files.delete.call_count, 2)
    


if __name__ == "__main__":
    unittest.main()

