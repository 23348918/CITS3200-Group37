import argparse
import common
from common import set_verbose, set_custom, verbose_print, set_prompt
from auth import authenticate
from process import process_model
from batch_operations import print_check_batch, export_batch, list_batches, process_batch
import sys
sys.tracebacklimit = 0 # Disable traceback for non-verbose mode


ACTIONS: dict[str, callable] = {
    "process": lambda args: process_model(args.llm_model, args.process),
    "check": lambda args: print_check_batch(args.check),
    "export": lambda args: export_batch(args.export),
    "list": lambda args: list_batches(),
    "batch": lambda args: process_batch(args.batch, args.auto),
}

def parse_arguments() -> argparse.Namespace:
    """Parse the arguments from the command line.
    
    Returns:
        The parsed arguments.
    """
    
    parser = argparse.ArgumentParser(
        description="CLI for LLM models processing and batch operations."
    )

    exclusive_group = parser.add_mutually_exclusive_group(required=True)

    # Dynamically add arguments based on common.ARG_INFO
    for arg in common.ARG_INFO:
        kwargs: dict = {k: v for k, v in arg.items() if k not in ("group", "flags", "name")}
        
        if arg.get("group") == "exclusive":
            exclusive_group.add_argument(*arg["flags"], **kwargs)
        elif "name" in arg:
            parser.add_argument(arg["name"], **kwargs)
        else:
            parser.add_argument(*arg["flags"], **kwargs)

    args = parser.parse_args()

    # Ensure llm_model is required if not listing batches
    if not args.list and args.llm_model is None:
        parser.error("llm_model is required for processing, checking, or exporting.")

    return args

def main():
    """Main function that redirects to relevent functions based on the arguments."""
    args: argparse.Namespace = parse_arguments()
    if args.llm_model != "chatgpt" and any  ([args.batch, args.auto, args.check, args.export]): # only chatgpt model is supported for batch operations
        print("Only chatgpt model is supported for batch processing commands (-b, -l, -e, -ch). see python3 main.py -h for more help.\nTerminating....")
        sys.exit(1)
    
    if args.verbose:
        set_verbose()
        sys.tracebacklimit = 1 # Enable traceback for verbose mode

    authenticate(args.llm_model)
    if args.custom:
        set_custom(args.custom)

    set_prompt(args.prompt)
    set_custom(args.custom)
    
    # Execute corresponding action from the ACTIONS dictionary
    for arg in vars(args):
        if (arg in ACTIONS and 
            getattr(args, arg) is not None and 
            getattr(args, arg) is not False):
            verbose_print(arg, args)
            ACTIONS[arg](args)


if __name__ == "__main__":
    main()