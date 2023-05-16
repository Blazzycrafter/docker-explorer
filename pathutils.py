import os

class PathUtils:
    target_system = os.name

    @staticmethod
    def normalize(path):
        """
        Normalize a given path and adapt it to the target system.

        Args:
            path (str): The path to be normalized.

        Returns:
            str: The normalized path.

        """
        normalized_path = os.path.normpath(path)

        if PathUtils.target_system == 'nt' and '/' in normalized_path:
            normalized_path = normalized_path.replace('/', '\\')
        elif PathUtils.target_system != 'nt' and '\\' in normalized_path:
            normalized_path = normalized_path.replace('\\', '/')

        return normalized_path
