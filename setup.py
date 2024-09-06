from setuptools import find_packages, setup

setup(
	name='rec_sizing',
	packages=find_packages(include=['rec_sizing', 'rec_sizing.*']),
	version='0.3.0',
	description='REC Sizing Tool for optimal REC planning and sizing.',
	author='ricardo.emanuel@inesctec.pt',
	install_requires=[
		'joblib~=1.3.2',
		'loguru~=0.7.2',
		'matplotlib~=3.8.0',
		'numpy~=1.26.1',
		'pandas~=2.1.2',
		'pulp~=2.8.0',
		'scikit-learn~=1.4.1.post1',
		'scikit-learn-extra==0.3.0',
		'setuptools~=68.0.0'
	],
	setup_requires=['pytest_runner==6.0.0'],
	tests_require=['pytest==7.4.2'],
	test_suite='tests'
)
