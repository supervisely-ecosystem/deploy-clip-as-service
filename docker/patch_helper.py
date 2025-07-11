import os
import sys
import site


def find_helper_py():
    """Find the helper.py file in installed packages"""
    # First, try the specific known location
    specific_path = "/usr/local/lib/python3.8/dist-packages/docarray/document/mixins/helper.py"
    if os.path.exists(specific_path):
        return specific_path

    # Try standard site-packages directories
    for site_dir in site.getsitepackages():
        helper_path = os.path.join(site_dir, "docarray", "document", "mixins", "helper.py")
        if os.path.exists(helper_path):
            return helper_path

    # Try common system-wide installation paths
    system_paths = [
        "/usr/local/lib/python3.8/dist-packages",
        "/usr/lib/python3.8/dist-packages",
        "/usr/local/lib/python3.8/site-packages",
        "/usr/lib/python3.8/site-packages",
    ]

    for base_path in system_paths:
        helper_path = os.path.join(base_path, "docarray", "document", "mixins", "helper.py")
        if os.path.exists(helper_path):
            return helper_path

    # Fallback for virtual environments
    try:
        import docarray

        docarray_path = os.path.dirname(docarray.__file__)
        helper_path = os.path.join(docarray_path, "document", "mixins", "helper.py")
        if os.path.exists(helper_path):
            return helper_path
    except ImportError:
        pass

    return None


def patch_helper():
    """Apply patch to helper.py"""
    helper_path = find_helper_py()
    if not helper_path:
        print("helper.py not found!")
        return

    print(f"Patching {helper_path}")

    # Read the original file
    with open(helper_path, "r") as f:
        content = f.read()

    # Add imports at the beginning of the file
    imports_to_add = """
import json
import logging
import base64
from datetime import datetime
"""

    if "import json" not in content:
        content = content.replace("import os", f"import os{imports_to_add}")

    # Configure logging
    logging_setup = """
# Logging setup for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/debug_logs/uri_to_blob.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
"""

    if "logger = logging.getLogger" not in content:
        content = content.replace(
            "from contextlib import nullcontext",
            f"from contextlib import nullcontext{logging_setup}",
        )

    # Replace the _uri_to_blob function
    new_function = '''def _uri_to_blob(uri: str, **kwargs) -> bytes:
    """Convert uri to blob
    Internally it reads uri into blob.
    :param uri: the uri of Document
    :param kwargs: keyword arguments to pass to `urlopen` such as timeout
    :return: blob bytes.
    """
    timeout = kwargs.get('timeout', None)
    logger.info(f"_uri_to_blob called with uri: {uri}")
    
    if urllib.parse.urlparse(uri).scheme in {'http', 'https', 'data'}:
        req = urllib.request.Request(uri, headers={'User-Agent': 'Mozilla/5.0'})
        urlopen_kwargs = {'timeout': timeout} if timeout is not None else {}
        
        try:
            with urllib.request.urlopen(req, **urlopen_kwargs) as fp:
                # Save response information
                response_info = {
                    'timestamp': datetime.now().isoformat(),
                    'uri': uri,
                    'method': 'http_request',
                    'status': fp.status if hasattr(fp, 'status') else 'unknown',
                    'headers': dict(fp.headers) if hasattr(fp, 'headers') else {},
                    'url': fp.url if hasattr(fp, 'url') else uri
                }
                
                # Read data
                data = fp.read()
                
                # Add data information
                response_info.update({
                    'data_length': len(data),
                    'data_base64': base64.b64encode(data).decode('utf-8'),
                    'data_preview': data[:100].hex() if len(data) > 100 else data.hex()
                })
                
                # Save to JSON file
                log_filename = f"/debug_logs/uri_blob_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
                try:
                    with open(log_filename, 'w') as log_file:
                        json.dump(response_info, log_file, indent=2)
                    logger.info(f"Saved response info to {log_filename}")
                except Exception as e:
                    logger.error(f"Failed to save response info: {e}")
                
                return data
                
        except Exception as e:
            logger.error(f"Error fetching URI {uri}: {e}")
            raise
            
    elif os.path.exists(uri):
        logger.info(f"Reading local file: {uri}")
        try:
            with open(uri, 'rb') as fp:
                data = fp.read()
                
                # Save local file information
                file_info = {
                    'timestamp': datetime.now().isoformat(),
                    'uri': uri,
                    'method': 'local_file',
                    'file_size': len(data),
                    'file_stats': {
                        'size': os.path.getsize(uri),
                        'mtime': os.path.getmtime(uri),
                        'ctime': os.path.getctime(uri)
                    },
                    'data_base64': base64.b64encode(data).decode('utf-8'),
                    'data_preview': data[:100].hex() if len(data) > 100 else data.hex()
                }
                
                # Save to JSON file
                log_filename = f"/debug_logs/local_file_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
                try:
                    with open(log_filename, 'w') as log_file:
                        json.dump(file_info, log_file, indent=2)
                    logger.info(f"Saved file info to {log_filename}")
                except Exception as e:
                    logger.error(f"Failed to save file info: {e}")
                
                return data
                
        except Exception as e:
            logger.error(f"Error reading local file {uri}: {e}")
            raise
    else:
        logger.error(f"URI not found: {uri}")
        raise FileNotFoundError(f'`{uri}` is not a URL or a valid local path')'''

    # Заменяем функцию в содержимом
    import re

    pattern = r"def _uri_to_blob\(uri: str, \*\*kwargs\) -> bytes:.*?raise FileNotFoundError\(f\'`\{uri\}` is not a URL or a valid local path\'\)"
    content = re.sub(pattern, new_function, content, flags=re.DOTALL)

    # Создаем резервную копию
    backup_path = helper_path + ".backup"
    with open(backup_path, "w") as f:
        f.write(content)

    # Записываем измененный файл
    with open(helper_path, "w") as f:
        f.write(content)

    print(f"Патч применен успешно. Резервная копия: {backup_path}")


if __name__ == "__main__":
    patch_helper()
