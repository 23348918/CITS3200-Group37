import os
import unittest
from unittest.mock import patch, mock_open
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from pydantic import BaseModel, create_model
from typing import List, Dict
import cv2
import base64
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts/api')))
from utils import create_dynamic_response_model, extract_dynamic_fields, read_customs, \
check_file_size, ask_save_location, get_file_dict, get_media_type, encode_image, encode_video
import common
from common import AnalysisResponse

class TEST_create_dynamic_response_model(unittest.TestCase):
    
    def test_no_custom_string(self):
        result: BaseModel = create_dynamic_response_model(None)
        self.assertEqual(result, AnalysisResponse)

    def test_empty_string(self):
        result: BaseModel = create_dynamic_response_model("")
        self.assertTrue(issubclass(result, AnalysisResponse))

class TEST_extract_dynamic_fields(unittest.TestCase):

    def test_empty_list(self):
        result: Dict = extract_dynamic_fields([])
        self.assertEqual(result, {})
    
    def test_no_dynamic_fields(self):
        result: Dict = extract_dynamic_fields(["part1", "part2", "part3"])
        self.assertEqual(result, {})
    
    def test_valid_dynamic_fields(self):
        parts: List = ["part1", "part2", "part3", "field_one: value1", "field_two: value2"]
        result: Dict = extract_dynamic_fields(parts)
        expected: Dict = {
            "field_one": "value1",
            "field_two": "value2"
        }
        self.assertEqual(result, expected)
    
    def test_malformed_fields(self):
        parts: List = ["part1", "part2", "part3", "field_one value1", "field_two: value2"]
        result: Dict = extract_dynamic_fields(parts)
        expected: Dict = {
            "field_two": "value2"
        }
        self.assertEqual(result, expected)
    
    def test_trailing_spaces(self):
        parts: List = ["part1", "part2", "part3", "field_one  :  value1  ", "field_two:  value2  "]
        result: Dict = extract_dynamic_fields(parts)
        expected: Dict = {
            "field_one": "value1",
            "field_two": "value2"
        }
        self.assertEqual(result, expected)
    
    def test_multiple_colons_in_value(self):
        parts: List = ["part1", "part2", "part3", "field_one: value1: part2", "field_two: value2"]
        result: Dict = extract_dynamic_fields(parts)
        expected: Dict = {
            "field_one": "value1: part2",
            "field_two": "value2"
        }
        self.assertEqual(result, expected)

class TEST_read_customs(unittest.TestCase):
    
    def test_invalid_file_extension(self):
        with self.assertRaises(ValueError) as context:
            read_customs("invalid_file.csv")
        self.assertEqual(str(context.exception), "The file must be of type .txt")

    @patch("builtins.open", new_callable=mock_open, read_data="sample content")
    def test_valid_txt_file(self, mock_file):
        file_path: str = "valid_file.txt"
        result: str = read_customs(file_path)
        self.assertEqual(result, "sample content")
        mock_file.assert_called_once_with(file_path, 'r')
    
    @patch("builtins.open", new_callable=mock_open, read_data="another sample content")
    def test_read_empty_file(self, mock_file):
        mock_file.return_value.read.return_value = ""
        file_path: str = "empty_file.txt"
        result: str = read_customs(file_path)
        self.assertEqual(result, "")
        mock_file.assert_called_once_with(file_path, 'r')
    
    @patch("builtins.open", new_callable=mock_open, read_data="multiline\ncontent")
    def test_multiline_content(self, mock_file):
        file_path: str = "multiline_file.txt"
        result: str = read_customs(file_path)
        self.assertEqual(result, "multiline\ncontent")
        mock_file.assert_called_once_with(file_path, 'r')
    
    @patch("builtins.open", new_callable=mock_open)
    def test_file_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        file_path: str = "INVALIDFILE.txt"
        with self.assertRaises(FileNotFoundError):
            read_customs(file_path)

class TEST_check_file_size(unittest.TestCase):
    
    @patch('os.path.getsize')
    def test_file_within_limit(self, mock_getsize):
        mock_getsize.return_value: int = 50 * 1024 * 1024  # 50 MB
        file_path: str = "small_file.txt"
        result: bool = check_file_size(file_path)
        self.assertTrue(result)
        mock_getsize.assert_called_once_with(file_path)
    
    @patch('os.path.getsize')
    def test_file_exactly_at_limit(self, mock_getsize):
        mock_getsize.return_value: int = 99 * 1024 * 1024  # 99 MB
        file_path: str = "exact_limit_file.txt"
        result: bool = check_file_size(file_path)
        self.assertFalse(result)
        mock_getsize.assert_called_once_with(file_path)
    
    @patch('os.path.getsize')
    def test_file_below_limit_by_1_byte(self, mock_getsize):
        mock_getsize.return_value: int = (99 * 1024 * 1024) - 1  # 99 MB - 1 byte
        file_path: str = "just_below_limit_file.txt"
        result: bool = check_file_size(file_path)
        self.assertTrue(result)
        mock_getsize.assert_called_once_with(file_path)

class TEST_ask_savfe_location(unittest.TestCase):
    
    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("tkinter.Tk")
    def test_user_provides_location(self, mock_tk, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value: str = "/user/selected/path/output.csv"
        default_filename: str = "output.csv"
        result = ask_save_location(default_filename)
        mock_tk().withdraw.assert_called_once()
        self.assertEqual(result, "/user/selected/path/output.csv")
    
    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("tkinter.Tk")
    def test_user_cancels_dialog(self, mock_tk, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value: str = ""
        default_filename: str = "output.csv"
        result = ask_save_location(default_filename)
        mock_tk().withdraw.assert_called_once()
        self.assertFalse(result)
    
    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("tkinter.Tk")
    def test_default_path_when_user_cancels(self, mock_tk, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value: str = ""
        default_filename: str = "output.csv"
        result = ask_save_location(default_filename)
        mock_tk().withdraw.assert_called_once()
        self.assertFalse(result)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("tkinter.Tk")
    def test_correct_initial_conditions(self, mock_tk, mock_asksaveasfilename):
        mock_asksaveasfilename.return_value: str = "/user/selected/path/output.csv"
        default_filename: str = "output.csv"
        ask_save_location(default_filename)
        mock_asksaveasfilename.assert_called_once_with(
            defaultextension=".csv",
            filetypes=[("CSV format", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename,
            initialdir=Path(Path(__file__).resolve().parents[1]),
            title="Select location to save your file"
        )

class TestGetFileDict(unittest.TestCase):

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_single_valid_file(self, mock_is_file, mock_is_dir):
        file_path: Path = Path("/mock/directory/file1.txt")
        result: dict = get_file_dict(file_path)
        expected: dict = {
            "file1.txt": file_path
        }
        self.assertEqual(result, expected)

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("pathlib.Path.glob", return_value=[])
    def test_empty_directory(self, mock_glob, mock_is_dir):
        with self.assertRaises(ValueError):
            get_file_dict(Path("/mock/directory"))

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("pathlib.Path.is_file", return_value=False)
    def test_invalid_path(self, mock_is_file, mock_is_dir):
        invalid_path: Path = Path("/invalid/path")
        with self.assertRaises(ValueError):
            get_file_dict(invalid_path)

class TestGetMediaType(unittest.TestCase):

    def test_valid_png_extension(self):
        file_path: Path = Path("/mock/path/image.png")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/png")

    def test_valid_jpg_extension(self):
        file_path: Path = Path("/mock/path/image.jpg")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/jpeg")

    def test_valid_jpeg_extension(self):
        file_path: Path = Path("/mock/path/image.jpeg")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/jpeg")

    def test_valid_gif_extension(self):
        file_path: Path = Path("/mock/path/image.gif")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/gif")

    def test_valid_bmp_extension(self):
        file_path: Path = Path("/mock/path/image.bmp")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/bmp")

    def test_valid_webp_extension(self):
        file_path: Path = Path("/mock/path/image.webp")
        result: str = get_media_type(file_path)
        self.assertEqual(result, "image/webp")

    def test_invalid_extension(self):
        file_path: Path = Path("/mock/path/image.txt")
        with self.assertRaises(ValueError) as context:
            get_media_type(file_path)
        self.assertEqual(str(context.exception), "Unsupported file extension: .txt")

class TestEncodeImage(unittest.TestCase):

    def test_encode_image_success(self):
        image_path: Path = Path("TestFiles/ImagesDir/test_image.png")
        result:str = encode_image(image_path)
        with open("TestFiles/ImagesDir/test_image.png", 'rb') as f:
            expected: str = base64.b64encode(f.read()).decode('utf-8')
        self.assertEqual(result, expected)

    @patch("builtins.open", new_callable=mock_open)
    def test_file_open_error(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        image_path: str = Path("TestFiles/ImagesDir/NO_IMAGE.png")
        with self.assertRaises(FileNotFoundError):
            encode_image(image_path)

class TestEncodeVideo(unittest.TestCase):

    def test_encode_video_success(self):
        video_path: Path = Path("TestFiles/VideoDir/test_video.mp4")
        result: List[str] = encode_video(video_path, frame_rate_divisor=2)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "The encoded frame list should not be empty")
        for encoded_frame in result:
            try:
                decoded_frame = base64.b64decode(encoded_frame)
                self.assertIsInstance(decoded_frame, bytes)
            except base64.binascii.Error:
                self.fail(f"Frame {encoded_frame} is not valid base64 encoded data")

if __name__ == '__main__':
    unittest.main()