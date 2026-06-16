try:
    import importlib.metadata

    __version__ = importlib.metadata.version("clictagger")
except ImportError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("clictagger").version
