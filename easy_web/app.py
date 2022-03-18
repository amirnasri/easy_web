import os
import sys
import typing as t

from werkzeug.routing import Map
from werkzeug.routing import Rule

class EasyWeb:
    def __init__(
        self,
        import_name: str
    ):
        self.url_map = Map()
        self.view_functions: t.Dict[str, t.Callable] = {}
        self.root_path = get_root_path(import_name)
    
    def get_root_path(import_name: str) -> str:
        """Detect the root path for this app. If it cannot be detected, default to
        current directory. 

        Args:
            import_name (str): name of the module that contains the app.

        Returns:
            str: detected root path.
        """

        mod = sys.modules.get(import_name)

        if mod and hasattr(mod, '__file__') and mod.__file__:
            return os.path.dirname(os.path.abspath(mod.__file__))
        else:
            return os.getcwd()

    def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = None,
        view_func: t.Callable = None,
        methods: t.Tuple[str] = None,
        **options: t.Any
    ) -> None:
        """Add a url rule and associated data to the url map.

        Args:
            rule (str): The rule to be added.
            endpoint (t.Optional[str], optional): An optional string to lookup the rule by. 
                Defaults to None.
            view_func (t.Callable, optional): The callback function to call when the rule rule
                is matched. Defaults to None.
            methods (t.Tuple[str], optional): HTTP methods which this rule responds to. Defaults
                to None.

        Raises:
            ValueError: When View function is None
            Exception: When the endpoint is already mapped.
        """
        if not view_func:
            raise ValueError("View function cannot be None")
        
        if not endpoint:
            endpoint = view_func.__name__
        
        if not methods:
            methods = ("GET",)
        else:
            methods = tuple(item.upper() for item in methods)
            
        rule = Rule(rule, methods=methods, **options)
        self.url_map.add(rule)
        
        old_func = self.view_functions.get(endpoint)
        if old_func and old_func != view_func:
            raise Exception(
                f"View function mapping is overriding an existing endpoint: {endpoint}"    
            )
        self.view_functions[endpoint] = view_func
              
    def run(
        self,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        debug: t.Optional[bool] = True,
        **options: t.Any,
    ) -> None:
        """Run the application on a local dev server.

        Args:
            host (t.Optional[str], optional): the host to listen on. Defaults to ``localhost``
                or the host in ``SERVER_NAME`` local variable if present.
            port (t.Optional[int], optional): the port to use. Default to ``5000`` or the port
                defined in ``SERVER_NAME`` config variable if present.
            debug (t.Optional[bool], optional): enable or disable debug mode. Defaults to True.
            options : the options to be forwared to the underlying werkzeug server.
        """

        server_name = os.environ.get("SERVER_NAME")
        sn_host = sn_port = None

        if server_name:
            sn_host, _, sn_port = server_name.partition(":")

        if not host:
            if sn_host:
                host = sn_host
            else:
                host = "127.0.0.1"

        if port or port == 0:
            port = int(port)
        elif sn_port:
            port = int(sn_port)
        else:
            port = 5000

        from werkzeug.serving import run_simple

        run_simple(host, port, self, **options)
