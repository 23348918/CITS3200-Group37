

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



import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import os
import sys
import pytest

# Add the Scripts/api directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts/api')))

# Importing from 'batch_operations' (with 's')
from batch_operations import generate_batch_file, process_batch, check_batch, export_batch, list_batches, batch_process_chatgpt, upload_batch_file, get_file_dict
from common import verbose_print
from utils import get_file_dict, encode_image, encode_video, create_dynamic_response_model
from process import generate_csv_output

class TestGPTBatchOperations(unittest.TestCase):
    # Case 0: Get File Dict success
    def test_get_file_dict_success(self):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/Tests/test_dir")
        
        expected_output = {'NO_speed_sign.png': Path('/home/dave/UWA/CITS3200-Group37/Tests/test_dir/NO_speed_sign.png'),
                           'test_image.png': Path('/home/dave/UWA/CITS3200-Group37/Tests/test_dir/test_image.png')}
        
        file_dict = get_file_dict(test_directory)
        self.assertEqual(file_dict, expected_output)
        
    # Case 1: Get file dict failure due to invalid directory/file path
    def test_get_file_dict_invalid_directory(self):
        test_directory = Path("/home/dave/UWA/CITS3200-Group37/Tests/test_dir_invalid")
        with self.assertRaises(ValueError):
            get_file_dict(test_directory)
            

    
    # # Case 1: Create JSON Entry success
    # @patch('batch_operations.encode_image', return_value="encoded_image_data")  # Updated to 'batch_operations'
    # @patch('batch_operations.common.prompt', "Test prompt")  # Updated to 'batch_operations'
    # def test_create_json_entry_success(self, mock_encode_image):
    #     # Mocking a correct file_dict structure
    #     file_dict = {
    #         "label": Path("test_image.jpg")
    #     }
    #     out_path = Path("out_batch_file.jsonl")

    #     # Calling the generate_batch_file function with the correct file_dict
    #     generate_batch_file(file_dict, out_path)

    #     # Check if the file was written correctly (this assumes you are mocking file writing)
    #     self.assertTrue(out_path.exists(), "Batch file should exist after generation.")
    #     print("Test case for create_json_entry_success passed.")



    # # Case 2: Upload JSON Entry success and return batch id
    # @patch('batch_operation.open', new_callable=mock_open, read_data='batch_data')
    # @patch('batch_operation.common.chatgpt_client.files.create')
    # @patch('batch_operation.common.chatgpt_client.batches.create')
    # def test_upload_batch_file_success(self, mock_batch_create, mock_file_create, mock_open_file):
    #     mock_batch_create.return_value.id = "batch_id"
    #     mock_file_create.return_value.id = "file_id"

    #     batch_file_path = Path("test_batch.jsonl")
    #     batch_id = upload_batch_file(batch_file_path)
    #     self.assertEqual(batch_id, "batch_id")
    #     print("Test case for upload_batch_file_success passed.")

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

    # # Case 8: Process Batch with auto failure
    # @patch('batch_operation.batch_process_chatgpt', return_value="batch_id")
    # @patch('batch_operation.check_batch', return_value=("failed", "Processing failed"))
    # def test_process_batch_auto_failure(self, mock_check_batch, mock_batch_process):
    #     process_batch("test_dir", auto=True)
    #     mock_batch_process.assert_called_once()
    #     mock_check_batch.assert_called_once()
    #     print("Test case for process_batch_auto_failure passed.")
    
    
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

    # # Case 11: Process Batch with auto success
    # @patch('batch_operation.batch_process_chatgpt', return_value="batch_id")
    # @patch('batch_operation.check_batch', return_value=("completed", "Processing success"))
    # @patch('batch_operation.export_batch')
    # def test_process_batch_auto_success(self, mock_export, mock_check_batch, mock_batch_process):
    #     process_batch("test_dir", auto=True)
    #     mock_batch_process.assert_called_once()
    #     mock_check_batch.assert_called_once()
    #     mock_export.assert_called_once()
    #     print("Test case for process_batch_auto_success passed.")

    # # Case 12: Process Batch with auto failure due to size limit
    # @patch('batch_operation.batch_process_chatgpt', return_value="batch_id")
    # @patch('batch_operation.check_batch', return_value=("failed", "Processing failed due to size limit"))
    # def test_process_batch_auto_failure_due_to_size_limit(self, mock_check_batch, mock_batch_process):
    #     process_batch("large_batch_dir", auto=True)
    #     mock_batch_process.assert_called_once()
    #     mock_check_batch.assert_called_once()
    #     print("Test case for process_batch_auto_failure_due_to_size_limit passed.")

if __name__ == "__main__":
    unittest.main()

