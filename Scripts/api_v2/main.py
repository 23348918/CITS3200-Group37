import argparse
import common
from common import set_verbose, set_prompt
from auth import authenticate
from actions import process_model, check_model, export_model, list_models

ACTIONS: dict[str, callable] = {
    "prompt": lambda args: set_prompt(args.prompt),
    "process": lambda args: process_model(args.llm_model, args.process, args.auto),  # Passes the file path
    "check": lambda args: check_model(args.check),        # Passes the batch ID
    "export": lambda args: export_model(args.export),     # Passes the batch ID
    "list": lambda args: list_models(),                   # No argument required
}

def parse_arguments() -> argparse.Namespace:
    """Parse the arguments from the command line."""
    
    parser = argparse.ArgumentParser(
        description="CLI for LLM models processing and batch operations."
    )

    exclusive_group = parser.add_mutually_exclusive_group(required=True)

    # Dynamically add arguments based on common.ARG_INFO
    for arg in common.ARG_INFO:
        kwargs = {k: v for k, v in arg.items() if k not in ("group", "flags", "name")}
        
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
    args: argparse.Namespace = parse_arguments()
    if args.verbose:
        set_verbose()

    authenticate(args.llm_model)

    # Execute corresponding action from the ACTIONS dictionary
    for arg in vars(args):
        if (arg in ACTIONS and 
            getattr(args, arg) is not None and 
            getattr(args, arg) is not False):
            ACTIONS[arg](args)

if __name__ == "__main__":
    main()
