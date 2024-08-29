import sys
import argparse
from auth import authenticate
from request import analyse_image
from utils import save_to_json, select_file


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for api call.
    
    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Functions of gpt")
    parser.add_argument(
        '-pb', '--process-batch', 
        type=str, 
        metavar='<FILE_PATH>',
        help='upload a batch file path to be processed (batch process takes 24 hrs)'
    )

    parser.add_argument(
        '-lb', '--list-batches', 
        action='store_true', 
        help='list all batch processes'
    )

    parser.add_argument(
        '-cb', '--check-batch', 
        type=str,
        metavar='<BATCH_ID>',
        help='check the status of a specific batch ID. use -lb to list all batches'
    )

    # NOTE: THis section may be a little complicated if a fine tuned model requires further fine tuning,
    # this will require the id of the fine tuned model?
    parser.add_argument(
        '-ft', '--fine-tune', 
        type=str, 
        nargs=2,  # Specifies that this option requires exactly two arguments
        metavar=('<DATASET_PATH>', '[MODEL_NAME]'),  # Optional: specify argument names
        help='Upload a fine-tune dataset path and specify a model to be processed (Default model: 4o-mini)'
    )

    parser.add_argument(
        '-lft', '--list-fine-tune', 
        action='store_true', 
        help='list all fine-tune processes'
    )

    parser.add_argument(
        '-cft', '--check-fine-tune', 
        type=str, 
        metavar='<FINE_TUNE_ID>',

        help='check the status of a specific fine-tune ID. use -lft to list all fine tuning'
    )

    parser.add_argument(
        '-ai', '--analyse-image', 
        type=str, 
        metavar='<IMAGE_PATH>',
        help='analyse the image from the specified path'
    )
    return parser.parse_args()  


def main() -> None:
    "Main function to parse arguments, set up client, analyse the image and save as a json"
    args = parse_arguments()
    
    key_file = select_file()
    client = authenticate(key_file)

    if args.analyse_image:
        result = analyse_image(client, args.analyse_image)
        print(result)
        # TODO: instead of save as a json, give json to export_to_csv
        # save_to_json(result)


if __name__ == "__main__":
    main()
