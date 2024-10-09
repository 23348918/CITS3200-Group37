# Test cases for batch_operations.py
# To run the tests, run the following command (add -v for more verbose output):
#     python3 -m unittest Tests/test_batch_operations.py
# or
#     pytest Tests/test_batch_operations.py


# NOTE: Delete later
# generate batch file - generates a jsonl file for a batch of files to be processed
# upload batch file - uploads the created json entry to the server. used in generate batch file and returns the batch id
# batch process_chatgpt - calls generate batch file and upload batch file
# process batch - calls batch_process_chatgpt and if auto is true, calls check_batch and export_batch
# list batches - list all batches
# check batch - check the status of a batch return the status and status message
# export batch - retrieve the results of a batch and write to a csv file

    # Case 1: Create JSON Entry success
    # Case 2: Create JSON Entry failure
    # Case 3: Upload JSON Entry success and return batch id
    # Case 4: Upload JSON Entry failure 
    # Case 5: Process Batch success
    # Case 6: Process Batch failure
    # Case 7: List Batches success
    # Case 8: Check Batch success
    # Case 9: Export Batch success
    # Case 10: Export Batch failure
    # Case 11: Process Batch with auto success
    # Case 12: Process Batch with auto failure
import sys
import os

# Add the Scripts/api directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts/api')))
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import pytest
from batch_operations import generate_batch_file, process_batch, check_batch, export_batch, list_batches, batch_process_chatgpt, upload_batch_file, get_file_dict
from common import verbose_print
from utils import get_file_dict, encode_image, encode_video, create_dynamic_response_model
from process import generate_csv_output
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
        # Simulate a valid file_dict
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
        
        

class TestBatchProcessChatGPT(unittest.TestCase):

    #process -> batch_process_chatgpt -> upload_batch_file 
    # Case 11: Test batch process success
    @patch('batch_operations.upload_batch_file', return_value = "Upload Batch Success")  # Mock upload_batch_file
    def test_process_batch_success(self, mock_upload_batch_file):
        file_path_str = "/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir"
        process_batch(file_path_str, auto=False)
        mock_upload_batch_file.assert_called_once() # ensure that the mock function was called
        
            
    # Case 12: Test batch process with auto enabled
    @patch('batch_operations.check_batch', return_value=("completed", "Processing success"))  # Mock check_batch
    @patch('batch_operations.export_batch')  # Mock export_batch
    @patch('batch_operations.upload_batch_file', return_value = "Batch ID")  # Mock upload_batch_file
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
    ])  # Mock check_batch to return different statuses
    @patch('batch_operations.upload_batch_file', return_value="Batch ID")  # Mock upload_batch_file
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
            
    # @patch('batch_operations.check_batch', return_value=("failed", "Processing failed"))  # Mock check_batch
    # @patch('batch_operations.upload_batch_file', return_value = "Batch ID")  # Mock upload_batch_file
    # @patch('batch_operations.export_batch')  # Mock export_batch
    # def test_process_batch_auto_failure(self, mock_upload_batch_file, mock_check_batch, Mock_export_batch):
    #     file_path_str = "/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir"
    #     mock_check_batch.return_value = {"failed": "Processing failed", 
    #                                      "expired": "Processing expired",
    #                                      "cancelled": "Processing cancelled",
    #                                      "cancellied": "Processing cancelled"
    #                                      }
    #     for each in mock_check_batch.return_value:
    #         with self.assertRaises(RuntimeError):
    #             process_batch(file_path_str, auto=True)
    #             mock_upload_batch_file.assert_called_once()
    #             self.assertGreaterEqual(mock_check_batch.call_count, 1)
    #             Mock_export_batch.assert_not_called()
    #             self.assertEqual(mock_check_batch.return_value[each], mock_check_batch.return_value[each])
    #     # with self.assertRaises(RuntimeError):
    #     #     process_batch(file_path_str, auto=True)
    #     #     mock_upload_batch_file.assert_called_once()
    #     #     self.assertGreaterEqual(mock_check_batch.call_count, 1)
        
        
    
class TestOthers(unittest.TestCase):
    pass




    # # Case 3: Process Batch success
    # @patch('batch_operation.batch_process_chatgpt', return_value="batch_id")
    # @patch('batch_operation.check_batch', return_value=("completed", "Processing success"))
    # @patch('batch_operation.export_batch')
    # def test_process_batch_success(self, mock_export, mock_check_batch, mock_batch_process):
    #     process_batch("test_dir", auto=True)
    #     mock_batch_process.assert_called_once()
    #     mock_check_batch.assert_called_once()
    #     mock_export.assert_called_once()
    #     print("Test case for process_batch_success passed.")
    
    # # Case 4: List Batches success
    # @patch('batch_operation.common.chatgpt_client.batches.list')
    # def test_list_batches_success(self, mock_batch_list):
    #     mock_batch_list.return_value = [
    #         MagicMock(id="batch_1", status="completed", error_file_id=None),
    #         MagicMock(id="batch_2", status="failed", error_file_id="error_id")
    #     ]
    #     list_batches()
    #     mock_batch_list.assert_called_once()
    #     print("Test case for list_batches_success passed.")

    # # Case 5: Check Batch success
    # @patch('batch_operation.common.chatgpt_client.batches.retrieve')
    # def test_check_batch_success(self, mock_batch_retrieve):
    #     mock_batch_retrieve.return_value = MagicMock(status="completed", error_file_id=None)
    #     status, status_message = check_batch("batch_id")
    #     self.assertEqual(status, "completed")
    #     self.assertEqual(status_message, "Processing success. You can now extract the file the file")
    #     print("Test case for check_batch_success passed.")
    
    # # Case 6: Export Batch success
    # @patch('batch_operation.common.chatgpt_client.batches.retrieve')
    # @patch('batch_operation.common.chatgpt_client.files.content')
    # @patch('batch_operation.generate_csv_output')
    # def test_export_batch_success(self, mock_generate_csv, mock_file_content, mock_batch_retrieve):
    #     mock_batch_retrieve.return_value = MagicMock(output_file_id="file_id", error_file_id=None)
    #     mock_file_content.return_value.read.return_value = b'{"id":"file1","response":{"body":{"model":"gpt-4o-mini","choices":[{"message":{"content":"file details"}}]}}}\n'

    #     export_batch("batch_id")
    #     mock_file_content.assert_called_once()
    #     mock_generate_csv.assert_called_once()
    #     print("Test case for export_batch_success passed.")
    
    # # Case 7: Export Batch failure
    # @patch('batch_operation.common.chatgpt_client.batches.retrieve')
    # def test_export_batch_failure(self, mock_batch_retrieve):
    #     mock_batch_retrieve.return_value = MagicMock(error_file_id="error_id")
    #     with self.assertRaises(SystemExit):
    #         export_batch("batch_id")
    #     print("Test case for export_batch_failure passed.")

    # # 
    
    #     # Case 9: Export Batch success with valid file
    # @patch('batch_operation.common.chatgpt_client.batches.retrieve')
    # @patch('batch_operation.common.chatgpt_client.files.content')
    # def test_export_batch_with_valid_file_success(self, mock_file_content, mock_batch_retrieve):
    #     mock_batch_retrieve.return_value = MagicMock(output_file_id="valid_file_id")
    #     mock_file_content.return_value.read.return_value = b'{"id":"file1","response":{"body":{"model":"gpt-4o-mini","choices":[{"message":{"content":"valid file"}}]}}}\n'

    #     export_batch("batch_id")
    #     mock_file_content.assert_called_once()
    #     print("Test case for export_batch_with_valid_file_success passed.")

    # # Case 10: Export Batch failure due to invalid file size
    # @patch('batch_operation.common.chatgpt_client.batches.retrieve')
    # @patch('batch_operation.common.chatgpt_client.files.content')
    # def test_export_batch_failure_due_to_invalid_file(self, mock_file_content, mock_batch_retrieve):
    #     mock_batch_retrieve.return_value = MagicMock(error_file_id="invalid_file_id")
    #     with self.assertRaises(SystemExit):
    #         export_batch("batch_id")
    #     print("Test case for export_batch_failure_due_to_invalid_file passed.")





        




if __name__ == "__main__":
    unittest.main()

