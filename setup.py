from setuptools import setup, find_packages

setup(
    name='mkdocs-setup',
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
        'python-dotenv',
        'openai',
        'google-generativeai',
        'mistralai',
        'questionary',
        # Add any other dependencies your tool needs
    ],
    entry_points={
        'console_scripts': [
            # This line maps the command 'mkdocs-setup' to the Typer app function
            'mkdocs-setup = mkdocs_setup.cli:main',
        ],
    },
    author='Your Name',
    description='A CLI tool for setting up Material for MkDocs in Python projects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mkdocs-setup-tool',
)