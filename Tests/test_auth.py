# to run tests, use the command 'pytest -v test_auth.py' in the terminal
# or use 'python3 -m unittest test_auth.py -v'

import os
import unittest
from unittest.mock import patch, mock_open
import sys
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from pathlib import Path
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts/api')))
from auth import authenticate  # Replace 'your_module' with the actual module name
import common  # Import the common module

class TestAuthenticate(unittest.TestCase):
    
    # Case 1: ChatGPT Authentication Success
    @patch('builtins.open', new_callable=mock_open, read_data='test_api_key')
    @patch('auth.Path.exists', return_value=True)  # Mock file existence
    @patch('auth.OpenAI')
    def test_authenticate_chatgpt_success(self, mock_openai, mock_exists, mock_open):
        model_name = 'chatgpt'
        authenticate(model_name)

        # Check if OpenAI client was created with the correct API key
        mock_openai.assert_called_once_with(api_key='test_api_key')
        self.assertEqual(common.chatgpt_client, mock_openai.return_value)

        # Optionally, check if the method correctly sets the chatgpt_client
        self.assertIsNotNone(common.chatgpt_client)


    # Case 2: Claude Authentication Success
    @patch('builtins.open', new_callable=mock_open, read_data='test_api_key')
    @patch('auth.Path.exists', return_value=True)  # Mock file existence
    @patch('auth.Anthropic')
    def test_authenticate_claude_success(self, mock_anthropic, mock_exists, mock_open):
        model_name = 'claude'
        authenticate(model_name)

        # Check if Anthropic client was created with the correct API key
        mock_anthropic.assert_called_once_with(api_key='test_api_key')
        self.assertEqual(common.claude_client, mock_anthropic.return_value)
        self.assertIsNotNone(common.claude_client)

        # Optionally, check if the method correctly sets the claude_client
        self.assertIsNotNone(common.claude_client)
        
    # Case 3: Invalid API Key for ChatGPT
    @patch('builtins.open', new_callable=mock_open, read_data='invalid_api_key')
    @patch('auth.Path.exists', return_value=True)  # Mock file existence
    @patch('auth.OpenAI')
    def test_authenticate_chatgpt_invalid_api_key(self, mock_openai, mock_exists, mock_open):
        mock_openai.side_effect = Exception("Invalid API key")  # Simulate invalid API key error

        model_name = 'chatgpt'
        with self.assertRaises(Exception):
            authenticate(model_name)
        
    # Case 4: Invalid API Key for Claude
    @patch('builtins.open', new_callable=mock_open, read_data='invalid_api_key')
    @patch('auth.Path.exists', return_value=True)  # Mock file existence
    @patch('auth.Anthropic')
    def test_authenticate_claude_invalid_api_key(self, mock_anthropic, mock_exists, mock_open):
        mock_anthropic.side_effect = Exception("Invalid API key")  # Simulate invalid API key error

        model_name = 'claude'
        with self.assertRaises(Exception):
            authenticate(model_name)

    # Case 5: Invalid API Key for Gemini
    @patch('builtins.open', new_callable=mock_open, read_data='invalid_api_key')
    @patch('auth.Path.exists', return_value=True)  # Mock file existence
    @patch('auth.genai')
    def test_authenticate_gemini_invalid_api_key(self, mock_genai, mock_exists, mock_open):
        mock_genai.configure.side_effect = Exception("Invalid API key")  # Simulate invalid API key error

        model_name = 'gemini'
        with self.assertRaises(Exception):
            authenticate(model_name)
            
     # Case 6: API Key File Does Not Exist for ChatGPT
    @patch('builtins.open', new_callable=mock_open)
    @patch('auth.Path.exists', return_value=False)  # Mock file not existing
    def test_authenticate_chatgpt_file_not_found(self, mock_exists, mock_open):
        model_name = 'chatgpt'
        with self.assertRaises(FileNotFoundError):
            authenticate(model_name)
        
    # Case 7: API Key File Does Not Exist for Claude
    @patch('builtins.open', new_callable=mock_open)
    @patch('auth.Path.exists', return_value=False)  # Mock file not existing
    def test_authenticate_claude_file_not_found(self, mock_exists, mock_open):
        model_name = 'claude'
        with self.assertRaises(FileNotFoundError):
            authenticate(model_name)
    # Case 8: API Key File Does Not Exist for Gemini
    @patch('builtins.open', new_callable=mock_open)
    @patch('auth.Path.exists', return_value=False)  # Mock file not existing
    def test_authenticate_gemini_file_not_found(self, mock_exists, mock_open):
        model_name = 'gemini'
        with self.assertRaises(FileNotFoundError):
            authenticate(model_name)


if __name__ == '__main__':
    unittest.main()