"""
SCS Serverless Functions Service

Provides serverless function management and invocation.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import SCS


class FunctionsService:
    """
    Functions service for serverless execution.

    Usage:
        # Invoke a function
        result = scs.functions.invoke('myFunction', {'param': 'value'})

        # Admin: Create a function
        scs.functions.create(
            name='processOrder',
            code='module.exports = async (data, context) => { return { success: true }; }',
            runtime='nodejs18'
        )

        # Admin: List functions
        functions = scs.functions.list()

        # Admin: Get function logs
        logs = scs.functions.get_logs('function-id')
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs

    def invoke(
        self,
        function_id: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        Invoke a serverless function.

        Args:
            function_id: Function ID or name
            data: Optional data payload to pass to the function
            timeout: Optional timeout in milliseconds

        Returns:
            Function execution result
        """
        body = {}

        if data:
            body["data"] = data
        if timeout:
            body["timeout"] = timeout

        return self._scs.request(
            f"/api/functions/{function_id}/invoke",
            method="POST",
            body=body if body else None,
        )

    def call(
        self,
        name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Alias for invoke() - call a function by name.

        Args:
            name: Function name
            data: Optional data payload

        Returns:
            Function execution result
        """
        return self.invoke(name, data)

    # Admin methods

    def create(
        self,
        name: str,
        code: str,
        runtime: str = "nodejs18",
        description: Optional[str] = None,
        timeout: int = 30000,
        memory: int = 128,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new serverless function (admin).

        Args:
            name: Function name
            code: Function source code
            runtime: Runtime environment ('nodejs18', 'nodejs20', 'python3.10', etc.)
            description: Optional description
            timeout: Execution timeout in milliseconds (default: 30000)
            memory: Memory limit in MB (default: 128)
            environment: Optional environment variables

        Returns:
            Created function info
        """
        body = {
            "name": name,
            "code": code,
            "runtime": runtime,
            "timeout": timeout,
            "memory": memory,
        }

        if description:
            body["description"] = description
        if environment:
            body["environment"] = environment

        return self._scs.request(
            "/api/functions",
            method="POST",
            body=body,
        )

    def list(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List all functions (admin).

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of functions
        """
        return self._scs.request(
            "/api/functions",
            params={"page": page, "limit": limit},
        )

    def get(self, function_id: str) -> Dict[str, Any]:
        """
        Get function details (admin).

        Args:
            function_id: Function ID

        Returns:
            Function details
        """
        return self._scs.request(f"/api/functions/{function_id}")

    def update(
        self,
        function_id: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
        memory: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Update a function (admin).

        Args:
            function_id: Function ID
            code: New source code
            description: New description
            timeout: New timeout in milliseconds
            memory: New memory limit in MB
            environment: New environment variables

        Returns:
            Updated function info
        """
        body = {}

        if code is not None:
            body["code"] = code
        if description is not None:
            body["description"] = description
        if timeout is not None:
            body["timeout"] = timeout
        if memory is not None:
            body["memory"] = memory
        if environment is not None:
            body["environment"] = environment

        return self._scs.request(
            f"/api/functions/{function_id}",
            method="PUT",
            body=body,
        )

    def delete(self, function_id: str) -> Dict[str, Any]:
        """
        Delete a function (admin).

        Args:
            function_id: Function ID

        Returns:
            Confirmation message
        """
        return self._scs.request(
            f"/api/functions/{function_id}",
            method="DELETE",
        )

    def test(
        self,
        function_id: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Test a function without affecting production (admin).

        Args:
            function_id: Function ID
            data: Test data payload

        Returns:
            Test execution result with logs
        """
        return self._scs.request(
            f"/api/functions/{function_id}/test",
            method="POST",
            body={"data": data} if data else None,
        )

    def get_logs(
        self,
        function_id: str,
        page: int = 1,
        limit: int = 50,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get function execution logs (admin).

        Args:
            function_id: Function ID
            page: Page number
            limit: Items per page
            level: Optional log level filter ('info', 'warn', 'error')

        Returns:
            Paginated list of log entries
        """
        params = {"page": page, "limit": limit}

        if level:
            params["level"] = level

        return self._scs.request(
            f"/api/functions/{function_id}/logs",
            params=params,
        )

    def clear_logs(self, function_id: str) -> Dict[str, Any]:
        """
        Clear function logs (admin).

        Args:
            function_id: Function ID

        Returns:
            Confirmation message
        """
        return self._scs.request(
            f"/api/functions/{function_id}/logs",
            method="DELETE",
        )
