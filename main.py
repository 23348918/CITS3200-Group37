import argparse
import common
from common import set_verbose, set_prompt, set_custom, verbose_print
from auth import authenticate
from process import process_model
from batch_operations import print_check_batch, export_batch, list_batches, process_batch
import sys

ACTIONS: dict[str, callable] = {
    "prompt": lambda args: set_prompt(args.custom_prompt),
    "process": lambda args: process_model(args.llm_model, args.process),
    "check": lambda args: print_check_batch(args.check),
    "export": lambda args: export_batch(args.export),
    "list": lambda args: list_batches(),
    "batch": lambda args: process_batch(args.batch, args.auto),
}

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI for LLM models processing and batch operations."
    )

    exclusive_group = parser.add_mutually_exclusive_group(required=True)

    for arg in common.ARG_INFO:
        kwargs: dict = {k: v for k, v in arg.items() if k not in ("group", "flags", "name")}
        
        if arg.get("group") == "exclusive":
            exclusive_group.add_argument(*arg["flags"], **kwargs)
        elif "name" in arg:
            parser.add_argument(arg["name"], **kwargs)
        else:
            parser.add_argument(*arg["flags"], **kwargs)

    parser.add_argument("--custom-prompt", metavar="PROMPT", help="Custom prompt for processing.")
    
    args = parser.parse_args()

    return args

def main():
    args: argparse.Namespace = parse_arguments()

    if args.verbose:
        set_verbose()

    authenticate(args.llm_model)

    if args.custom_prompt:
        set_prompt(args.custom_prompt)

    set_custom(args.custom)

    for arg in vars(args):
        if (arg in ACTIONS and 
            getattr(args, arg) is not None and 
            getattr(args, arg) is not False):
            verbose_print(arg, args)
            ACTIONS[arg](args)


if __name__ == "__main__":
    main()
