from setuptools import setup

extra = {}

setup(
    name='TracDitaaPlugin',
    #description='',
    #keywords='',
    #url='',
    version='0.2',
    #license='',
    #author='',
    #author_email='',
    #long_description="",
    packages=['ditaa'],
    package_data={
        'ditaa': []
    },
    entry_points={
        'trac.plugins': [
            'ditaa.ditaa = ditaa.ditaa',
        ]
    },
    **extra
)
