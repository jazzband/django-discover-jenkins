Developer instructions
======================

Here you can find some instructions when developing for this package.

Release a new version
---------------------

When you are ready to release a new version you need to follow these steps.

For example version 1.0.3:

1. Change the version number at ```discover_jenkins/__init__.py```
2. Commit ```git commit -m "Release 1.0.3"```
3. Tag ```git tag 1.0.3```
4. Push changes ```git push origin master```
5. Push tags ```git push --tags```
6. Upload release to Pypi ```python setup.py sdist upload```
7. Dance!
