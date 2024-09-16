from openai import OpenAI
from typing import Optional


def upload_training_file(client: OpenAI, file_path: str) -> OpenAI.File:
    """Uploads a training dataset file path (JSONL format) for training.

    Args:
        file_path: Path to the training file.

    Returns:
        The uploaded training file object.
    """
    training_file: OpenAI.File = client.files.create(
        file=open(file_path, "rb"),
        purpose="fine-tune"
    )
    return training_file


def create_fine_tune_model(client: OpenAI, upload_train: OpenAI.File, model: str = "gpt-4o-mini") -> OpenAI.FineTuningJob:
    """Used to fine-tune the model.

    Args:
        upload_train: The uploaded training file object.
        model: The model to fine-tune. Defaults to "gpt-4o-mini".

    Returns:
        The created fine-tuning job.
    """
    fine_tuned_model: OpenAI.FineTuningJob = client.fine_tuning.jobs.create(
        training_file=upload_train.id, 
        model=model
    )
    return fine_tuned_model


def list_fine_tunes(client: OpenAI, limit: Optional[int] = 10) -> OpenAI.FineTuningJobList:
    """Returns a list of fine-tuning/training jobs.

    Args:
        limit: The maximum number of fine-tuning jobs to return. Defaults to 10.

    Returns:
        A list of fine-tuning jobs.
    """
    fine_tune_list: OpenAI.FineTuningJobList = client.fine_tuning.jobs.list(limit=limit)
    return fine_tune_list


def check_fine_tuning_process(client: OpenAI, fine_tune_id: str) -> OpenAI.FineTuningJob:
    """Checks the progress status of fine-tuning.

    Args:
        fine_tune_id: The ID of the fine-tuning job to check.

    Returns:
        The status of the fine-tuning job.
    """
    fine_tune_status: OpenAI.FineTuningJob = client.fine_tuning.jobs.retrieve(fine_tune_id)
    return fine_tune_status
