from setuptools import setup , find_packages

setup(
    name='galleryman',
    version='1.0.0',
    description='A Tool To Manage Your Memories!',
    author='0xsapphir3',
    author_email='0xsapphir3@gmail.com',
    url='https://github.com/0xsapphir3/galleryman',
    entry_points={
        'console_scripts': [
            'galleryman = GalleryMan.main:main',
        ],
    },
    install_requires=['pyqt5' , 'pillow' , 'numpy' , 'functools' , 'configparser' , 'pathlib'],
    packages=find_packages()
)