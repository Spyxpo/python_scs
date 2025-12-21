"""
SCS Database Service

Provides Firestore-like document database functionality with query builder.

SCS supports two database backends (configured server-side via DATABASE_TYPE):
- **eaZI Database** (DATABASE_TYPE=eazi): File-based NoSQL, ideal for development
- **RelaDB** (DATABASE_TYPE=mongodb): Production-grade NoSQL with advanced features

The SDK API remains the same regardless of backend - switching databases requires
no client-side code changes.

Example:
    # Get a collection reference
    users = scs.database.collection('users')

    # Add a document
    doc = users.add({'name': 'John', 'email': 'john@example.com'})

    # Query documents
    adults = users.where('age', '>=', 18).order_by('name').get()
"""

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

if TYPE_CHECKING:
    from ..client import SCS

QueryOperator = Literal["==", "!=", ">", ">=", "<", "<=", "in", "contains"]
OrderDirection = Literal["asc", "desc"]


class DocumentReference:
    """
    Reference to a single document in a collection.

    Usage:
        doc_ref = scs.database.collection('users').doc('user123')

        # Get document
        doc = doc_ref.get()

        # Set document (creates or overwrites)
        doc_ref.set({'name': 'John', 'age': 30})

        # Update document (partial update)
        doc_ref.update({'age': 31})

        # Delete document
        doc_ref.delete()

        # Access subcollection
        posts = doc_ref.collection('posts').get()
    """

    def __init__(self, scs: "SCS", path: str):
        """
        Initialize document reference.

        Args:
            scs: SCS client instance
            path: Full document path (e.g., 'users/user123')
        """
        self._scs = scs
        self._path = path

        # Parse path into collection and document ID
        parts = path.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid document path: {path}")

        self._collection_path = "/".join(parts[:-1])
        self._document_id = parts[-1]

    @property
    def id(self) -> str:
        """Get the document ID."""
        return self._document_id

    @property
    def path(self) -> str:
        """Get the full document path."""
        return self._path

    def get(self) -> Dict[str, Any]:
        """
        Get the document data.

        Returns:
            Document data with _id field
        """
        return self._scs.request(
            f"/api/database/collections/{self._collection_path}/documents/{self._document_id}"
        )

    def set(
        self,
        data: Dict[str, Any],
        merge: bool = False,
    ) -> Dict[str, Any]:
        """
        Set document data (creates or overwrites).

        Args:
            data: Document data
            merge: If True, merge with existing data instead of overwriting

        Returns:
            Updated document
        """
        if merge:
            return self.update(data)

        return self._scs.request(
            f"/api/database/collections/{self._collection_path}/documents/{self._document_id}",
            method="PUT",
            body=data,
        )

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update document with partial data.

        Args:
            data: Fields to update

        Returns:
            Updated document
        """
        return self._scs.request(
            f"/api/database/collections/{self._collection_path}/documents/{self._document_id}",
            method="PUT",
            body=data,
        )

    def delete(self) -> Dict[str, Any]:
        """
        Delete the document.

        Returns:
            Success message
        """
        return self._scs.request(
            f"/api/database/collections/{self._collection_path}/documents/{self._document_id}",
            method="DELETE",
        )

    def collection(self, name: str) -> "CollectionReference":
        """
        Get a reference to a subcollection.

        Args:
            name: Subcollection name

        Returns:
            CollectionReference for the subcollection
        """
        return CollectionReference(self._scs, f"{self._path}/{name}")


class CollectionReference:
    """
    Reference to a collection with query builder.

    Usage:
        users = scs.database.collection('users')

        # Get all documents
        docs = users.get()

        # Query with filters
        adults = users.where('age', '>=', 18).where('status', '==', 'active').get()

        # With ordering and pagination
        recent = users.order_by('createdAt', 'desc').limit(10).get()

        # Add a new document
        new_user = users.add({'name': 'John', 'email': 'john@example.com'})

        # Get specific document
        doc_ref = users.doc('user123')
    """

    def __init__(self, scs: "SCS", path: str):
        """
        Initialize collection reference.

        Args:
            scs: SCS client instance
            path: Collection path (e.g., 'users' or 'users/user123/posts')
        """
        self._scs = scs
        self._path = path

        # Query state
        self._filters: List[Dict[str, Any]] = []
        self._order_by_field: Optional[str] = None
        self._order_direction: OrderDirection = "asc"
        self._limit_value: Optional[int] = None
        self._skip_value: Optional[int] = None

    def _clone(self) -> "CollectionReference":
        """Create a clone of this reference with current query state."""
        ref = CollectionReference(self._scs, self._path)
        ref._filters = self._filters.copy()
        ref._order_by_field = self._order_by_field
        ref._order_direction = self._order_direction
        ref._limit_value = self._limit_value
        ref._skip_value = self._skip_value
        return ref

    @property
    def path(self) -> str:
        """Get the collection path."""
        return self._path

    def doc(self, document_id: str) -> DocumentReference:
        """
        Get a reference to a specific document.

        Args:
            document_id: Document ID

        Returns:
            DocumentReference
        """
        return DocumentReference(self._scs, f"{self._path}/{document_id}")

    def where(
        self,
        field: str,
        operator: QueryOperator,
        value: Any,
    ) -> "CollectionReference":
        """
        Add a filter condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator (==, !=, >, >=, <, <=, in, contains)
            value: Value to compare against

        Returns:
            Self for chaining
        """
        ref = self._clone()
        ref._filters.append({
            "field": field,
            "operator": operator,
            "value": value,
        })
        return ref

    def order_by(
        self,
        field: str,
        direction: OrderDirection = "asc",
    ) -> "CollectionReference":
        """
        Set ordering for results.

        Args:
            field: Field name to order by
            direction: Order direction ('asc' or 'desc')

        Returns:
            Self for chaining
        """
        ref = self._clone()
        ref._order_by_field = field
        ref._order_direction = direction
        return ref

    def limit(self, count: int) -> "CollectionReference":
        """
        Limit the number of results.

        Args:
            count: Maximum number of documents to return

        Returns:
            Self for chaining
        """
        ref = self._clone()
        ref._limit_value = count
        return ref

    def skip(self, count: int) -> "CollectionReference":
        """
        Skip a number of results (for pagination).

        Args:
            count: Number of documents to skip

        Returns:
            Self for chaining
        """
        ref = self._clone()
        ref._skip_value = count
        return ref

    def offset(self, count: int) -> "CollectionReference":
        """
        Alias for skip().

        Args:
            count: Number of documents to skip

        Returns:
            Self for chaining
        """
        return self.skip(count)

    def get(self) -> List[Dict[str, Any]]:
        """
        Execute the query and get matching documents.

        Returns:
            List of documents
        """
        # If no filters, use simple GET
        if not self._filters and not self._order_by_field:
            params = {}
            if self._limit_value:
                params["limit"] = self._limit_value
            if self._skip_value:
                params["skip"] = self._skip_value

            result = self._scs.request(
                f"/api/database/collections/{self._path}/documents",
                params=params if params else None,
            )

            return result.get("documents", result if isinstance(result, list) else [])

        # Use query endpoint for filtered queries
        query = {}

        if self._filters:
            query["filters"] = self._filters

        if self._order_by_field:
            query["orderBy"] = {
                "field": self._order_by_field,
                "direction": self._order_direction,
            }

        if self._limit_value:
            query["limit"] = self._limit_value

        if self._skip_value:
            query["skip"] = self._skip_value

        result = self._scs.request(
            f"/api/database/collections/{self._path}/query",
            method="POST",
            body=query,
        )

        return result.get("documents", result if isinstance(result, list) else [])

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new document to the collection.

        Args:
            data: Document data

        Returns:
            Created document with generated _id
        """
        return self._scs.request(
            f"/api/database/collections/{self._path}/documents",
            method="POST",
            body=data,
        )

    def count(self) -> int:
        """
        Get the count of documents matching the current query.

        Returns:
            Document count
        """
        # Build query for count
        if self._filters:
            query = {"filters": self._filters, "count": True}
            result = self._scs.request(
                f"/api/database/collections/{self._path}/query",
                method="POST",
                body=query,
            )
            return result.get("count", 0)

        # Simple count
        result = self._scs.request(
            f"/api/database/collections/{self._path}/documents",
            params={"count": True},
        )
        return result.get("count", result.get("total", 0))


class DatabaseService:
    """
    Database service for document storage.

    Usage:
        # Get collection reference
        users = scs.database.collection('users')

        # List collections
        collections = scs.database.list_collections()

        # Create collection
        scs.database.create_collection('new_collection')

        # Delete collection
        scs.database.delete_collection('old_collection')
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs

    def collection(self, path: str) -> CollectionReference:
        """
        Get a reference to a collection.

        Args:
            path: Collection path (e.g., 'users' or 'users/user123/posts')

        Returns:
            CollectionReference
        """
        return CollectionReference(self._scs, path)

    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections.

        Returns:
            List of collection info objects
        """
        result = self._scs.request("/api/database/collections")
        return result.get("collections", result if isinstance(result, list) else [])

    def create_collection(self, name: str) -> Dict[str, Any]:
        """
        Create a new collection.

        Args:
            name: Collection name

        Returns:
            Created collection info
        """
        return self._scs.request(
            "/api/database/collections",
            method="POST",
            body={"name": name},
        )

    def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection.

        Args:
            name: Collection name

        Returns:
            Success message
        """
        return self._scs.request(
            f"/api/database/collections/{name}",
            method="DELETE",
        )
