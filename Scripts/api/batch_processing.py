from openai import OpenAI
from typing import Optional


def upload_batch_file(client: OpenAI, file_path: str) -> OpenAI.File:
    """Uploads a JSONL file to be processed as a batch.

    Args:
        file_path: Path to the batch input file.

    Returns:
        The uploaded batch file object.
    """
    batch_input_file: OpenAI.File = client.files.create(
        file=open(file_path, "rb"),
        purpose="batch"
    )
    return batch_input_file


def create_batch_file(client: OpenAI, upload_batch: OpenAI.File, description: str = "Default Description") -> OpenAI.Batch:
    """Creates a batch object for LLM to process, requires the output of upload_batch_file function.

    Args:
        upload_batch (OpenAI.File): The uploaded batch file object.
        description (str, optional): Description of the batch. Defaults to "Default Description".

    Returns:
        OpenAI.Batch: The created batch object.
    """
    batch_object: OpenAI.Batch = client.batches.create(
        input_file_id=upload_batch.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": description}
    )
    return batch_object


def list_batches(client: OpenAI, limit: Optional[int] = 20) -> OpenAI.BatchList:
    """Returns a list of all batch processes.

    Args:
        limit: The maximum number of batch processes to return. Defaults to 20.

    Returns:
        OpenAI.BatchList: A list of all batch processes.
    """
    batch_list: OpenAI.BatchList = client.batches.list(limit=limit)
    return batch_list


def check_batch_process(client: OpenAI, batch_id: str) -> OpenAI.Batch:
    """Returns the status of the batch requested.

    Args:
        batch_id: The ID of the batch to check.

    Returns:
        The status of the requested batch.
    """
    batch_status: OpenAI.Batch = client.batches.retrieve(batch_id)
    return batch_status