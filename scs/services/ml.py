"""
ML Service - Machine Learning features
"""

import os
from typing import Any, BinaryIO, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..client import SCS


class MLService:
    """
    Machine learning service for text recognition, image labeling, and custom models.

    Usage:
        # Text recognition (OCR)
        result = scs.ml.recognize_text("image.jpg")

        # Image labeling
        result = scs.ml.label_image("image.jpg")

        # Custom model prediction
        result = scs.ml.predict(model_id, "input.jpg")
    """

    def __init__(self, client: "SCS"):
        self._client = client

    def _prepare_image_file(
        self, image: Union[str, bytes, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Prepare image file for upload.

        Args:
            image: File path, bytes, or file-like object

        Returns:
            Files dict for requests
        """
        if isinstance(image, str):
            # File path
            filename = os.path.basename(image)
            return {"image": (filename, open(image, "rb"))}
        elif isinstance(image, bytes):
            # Raw bytes
            return {"image": ("image.jpg", image)}
        else:
            # File-like object
            return {"image": image}

    def recognize_text(self, image: Union[str, bytes, BinaryIO]) -> Dict[str, Any]:
        """
        Recognize text in an image (OCR).

        Args:
            image: Image file path, bytes, or file-like object

        Returns:
            Text recognition result with detected text
        """
        files = self._prepare_image_file(image)
        return self._client.upload_request("/api/ml/text-recognition", files=files)

    def label_image(self, image: Union[str, bytes, BinaryIO]) -> Dict[str, Any]:
        """
        Label objects in an image.

        Args:
            image: Image file path, bytes, or file-like object

        Returns:
            Image labeling result with detected labels
        """
        files = self._prepare_image_file(image)
        return self._client.upload_request("/api/ml/image-labeling", files=files)

    # Custom model management

    def upload_model(
        self,
        name: str,
        model_type: str,
        model_file: Union[str, bytes, BinaryIO],
        weights_file: Optional[Union[str, bytes, BinaryIO]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a custom ML model.

        Args:
            name: Model name
            model_type: Model type
            model_file: Model file path, bytes, or file-like object
            weights_file: Optional weights file

        Returns:
            Uploaded model details
        """
        files = {}
        data = {"name": name, "type": model_type}

        # Prepare model file
        if isinstance(model_file, str):
            files["model"] = (os.path.basename(model_file), open(model_file, "rb"))
        elif isinstance(model_file, bytes):
            files["model"] = ("model.json", model_file)
        else:
            files["model"] = model_file

        # Prepare weights file if provided
        if weights_file:
            if isinstance(weights_file, str):
                files["weights"] = (os.path.basename(weights_file), open(weights_file, "rb"))
            elif isinstance(weights_file, bytes):
                files["weights"] = ("weights.bin", weights_file)
            else:
                files["weights"] = weights_file

        response = self._client.upload_request("/api/ml/models", files=files, data=data)
        return response.get("model", response)

    def list_models(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all models.

        Args:
            limit: Maximum number of models
            skip: Number to skip

        Returns:
            List of models
        """
        params = {}
        if limit:
            params["limit"] = limit
        if skip:
            params["skip"] = skip

        response = self._client.request("/api/ml/models", params=params)
        return response.get("models", [])

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get a model by ID.

        Args:
            model_id: Model ID

        Returns:
            Model details
        """
        response = self._client.request(f"/api/ml/models/{model_id}")
        return response.get("model", response)

    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model.

        Args:
            model_id: Model ID

        Returns:
            True if successful
        """
        self._client.request(f"/api/ml/models/{model_id}", method="DELETE")
        return True

    def predict(
        self,
        model_id: str,
        image: Union[str, bytes, BinaryIO],
    ) -> Dict[str, Any]:
        """
        Run prediction with a custom model.

        Args:
            model_id: Model ID
            image: Input image file path, bytes, or file-like object

        Returns:
            Prediction result
        """
        files = self._prepare_image_file(image)
        return self._client.upload_request(
            f"/api/ml/models/{model_id}/predict",
            files=files
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get ML statistics.

        Returns:
            ML usage statistics
        """
        response = self._client.request("/api/ml/stats")
        return response.get("stats", response)
