# Test cases for the input path to command line with testing for format and validity of the input path

# To run the tests, run the following command (add -v for more verbose output):
#     python3 -m unittest test_batch_operations.py
# or
#     pytest test_batch_operations.py


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
from process import process_model
from main import main, parse_arguments
from llm_requests import chatgpt_request, gemini_request, claude_request
from common import LLMS, VALID_EXTENSIONS


class TestInputPath(unittest.TestCase):
    # Case 1: Valid Model Names
    @patch('process.sys.exit')  # Mock sys.exit so it doesn't stop the test
    @patch('process.REQUEST_FUNCTIONS')  # Mock the request functions
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    @patch.object(Path, 'is_file', return_value=True)  # Mock the is_file method
    @patch.object(Path, 'suffix', '.txt')  # Mock the suffix property
    @patch('sys.exit')  # Mock sys.exit so it doesn't stop the test
    def test_valid_model_name(self, mock_suffix, mock_is_file, mock_generate_csv_output, mock_request_functions, mock_sys_exit):
        # Arrange
        valid_model_name = 'chatgpt'
        valid_file_path = '/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/'
        request_output= "test"

        # Mock the LLMS list to include the valid model name
        with patch('common.LLMS', ['chatgpt', 'gemini', 'claude']):
            # Act
            process_model(valid_model_name, valid_file_path)

            # Assert
            # Since the model name is valid, sys.exit should not be called
            mock_sys_exit.assert_not_called()
            # Ensure REQUEST_FUNCTIONS is called with the valid model
            mock_request_functions.__getitem__.assert_called_once_with(valid_model_name)
            
            
            
            
    # Case 2: Invalid Model Name
    def test_invalid_model_name(self):
        # Arrange
        invalid_model_name = "invalid_model"
        valid_file_path = '/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/'

        # Mock the LLMS list to include the valid model name
        with self.assertRaises(SystemExit) as cm:
            process_model(invalid_model_name, valid_file_path)
            self.assertEqual(cm.exception.code, 1)
            self.assertEqual(sys.stdout, "Invalid model name")
    
    
    
    # Case 3: valid file path of directory - test for all valid model names defined in common.LLMS
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    @patch('process.parallel_process')  # Mock the parallel process
    @patch.object(Path, 'is_dir', return_value=True)  # Mock is_dir to always return True
    @patch.object(Path, 'is_file', return_value=False)  # Mock is_file to return False
    @patch('process.REQUEST_FUNCTIONS', new_callable=MagicMock)  # Mock the REQUEST_FUNCTIONS dictionary
    def test_valid_directory_path(self, mock_request_functions, mock_is_file, mock_is_dir, 
                                   mock_generate_csv_output, mock_parallel_process):
        valid_directory_path = '/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir'

        # Set up a mock return value for the model request function
        mock_request_function = MagicMock(return_value={})
        

        for model in LLMS:
            mock_request_functions.__getitem__.return_value = mock_request_function
            process_model(model, valid_directory_path)
            mock_request_functions.__getitem__.assert_any_call(model)  # Check that __getitem__ was called with any model name


        self.assertEqual(mock_is_file.call_count, len(LLMS))  # Check the count of is_file calls
        self.assertEqual(mock_is_dir.call_count, len(LLMS))  # Check the count of parallel_process calls
        self.assertEqual(mock_parallel_process.call_count, len(LLMS))  # Check the count of parallel_process calls
        self.assertEqual(mock_generate_csv_output.call_count, len(LLMS))  # Check the count of CSV output generation calls
        
    
    
    # Case 4: valid file path of file - test for all valid model names defined in common.LLMS
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    @patch.object(Path, 'is_dir', return_value=False)  # Mock is_file to always return True
    @patch.object(Path, 'is_file', return_value=True)  # Mock is_file to return False
    @patch('process.REQUEST_FUNCTIONS', new_callable=MagicMock)  # Mock the REQUEST_FUNCTIONS dictionary
    def test_valid_file_path(self, mock_request_functions,mock_is_file, mock_is_dir, mock_generate_csv_output):
        
        valid_file_path = '/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir/test_image.png'
        
        mock_request_function = MagicMock(return_value={})


        for model in LLMS:
            mock_request_functions.__getitem__.return_value = mock_request_function
            process_model(model, valid_file_path)  # Pass the mock object directly
            mock_request_functions.__getitem__.assert_any_call(model)

        self.assertEqual(mock_is_file.call_count, 3)  # Check the count of is_dir calls
        self.assertEqual(mock_is_dir.call_count, 0)  # Check the count of is_dir calls
        self.assertEqual(mock_generate_csv_output.call_count, len(LLMS))  # Check the count of CSV output generation calls


        
    # Case 5: valid file path of file but empty - test for all valid model names defined in common.LLMS
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    @patch('process.get_file_dict', side_effect=ValueError("Directory is empty."))  # Mock get_file_dict to raise ValueError

    def test_invalid_file_path(self, mock_get_file_dict, mock_generate_csv_output):
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            for model in LLMS:
                with self.assertRaises(ValueError) as e:
                    process_model(model, dir_path)
            self.assertEqual(mock_generate_csv_output.call_count, 0)
            self.assertEqual(mock_get_file_dict.call_count, len(LLMS)) # assert that get_file_dict was called for each model name
            self.assertEqual(str(e.exception), "Directory is empty.")

        
    
    
    # Case 6: invalid file path - does not exist - test for all valid model names defined in common.LLMS
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    def test_invalid_file_path(self, mock_generate_csv_output):
        # Arrange
        invalid_file_path = 'InvalidFilePath'
        for  model in LLMS:
            with self.assertRaises(SystemExit) as cm:
                process_model(model, invalid_file_path)
                self.assertEqual(cm.exception.code, 1)
                self.assertEqual(sys.stdout, f"{invalid_file_path} is not a valid file or directory.")
        self.assertEqual(mock_generate_csv_output.call_count, 0)
        
    
    #Case 7: valid file path of single file but invalid extension - test for all valid model names defined in common.LLMS
    @patch('process.generate_csv_output')  # Mock the CSV output generation
    def test_invalid_extensions(self, mock_generate_csv_output):
        INVALID_EXTENSIONS = ['.pdf', '.exe', '.txt', '.docx', '.xlsx','png']
        for ext in INVALID_EXTENSIONS:
            valid_file_path = f'/home/dave/UWA/CITS3200-Group37/Tests/TestFiles/ImagesDir/test_image{ext}'

            for model in LLMS:  # Loop through all valid models in common.LLMS
                with self.assertRaises(SystemExit) as cm:
                    process_model(model, valid_file_path)
                    self.assertEqual(cm.exception.code, 1)
                    self.assertIn(f"{valid_file_path} is not a valid file or directory.", sys.stdout.getvalue())
                    
            self.assertEqual(mock_generate_csv_output.call_count, 0)
                
    
    



if __name__ == '__main__':
    unittest.main()

