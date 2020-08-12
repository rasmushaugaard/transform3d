import setuptools

with open("readme.md") as f:
    long_description = f.read()

setuptools.setup(
    name='transform3d',
    version='0.0.2',
    author='Rasmus Laurvig Haugaard',
    author_email='rasmus.l.haugaard@gmail.com',
    description='Handy classes for working with trees of 3d transformations.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RasmusHaugaard/transform3d',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy>=1.18',
        'scipy>=1.4',
        'werkzeug>=0.16'
    ],
    python_requires='>=3.6',
)