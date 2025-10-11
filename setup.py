from setuptools import setup, find_packages

setup(
    name='mkdoc-setup',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'typer',
        'mkdocs',
        'mkdocs-material',
        'mkdocstrings[python]',
        'mkdocs-jupyter',
        'mkdocs-glightbox',
        'pyyaml',
        # Add any other dependencies your tool needs
    ],
    entry_points={
        'console_scripts': [
            # This line maps the command 'mkdoc-setup' to the Typer app function
            'mkdoc-setup = mkdoc_setup.cli:app',
        ],
    },
    author='Your Name',
    description='A CLI tool for setting up Material for MkDocs in Python projects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mkdoc-setup-tool',
)