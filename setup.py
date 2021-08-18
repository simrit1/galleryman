from setuptools import setup , find_packages

setup(
    name='GalleryMan',
    version='1.0.0',
    description='A Tool To Manage Your Memories!',
    author='0xsapphir3',
    author_email='0xsapphir3@gmail.com',
    url='https://github.com/0xsapphir3/galleryman',
    download_url='https://github.com/0xsapphir3/galleryman/tarball/1.0.0',
    entry_points={
        'console_scripts': [
            'galleryman = GalleryMan.main:main',
        ],
    },
    install_requires=['PyQt5' , 'pillow'],
    packages=find_packages()
)