django-discover-jenkins
=======================

A minimal fork of django-jenkins designed to work with the discover runner, made with simplicity in mind.


Why?
----

The overall goal is to run tests on Jenkins the same way you do on your local machine. This project is designed to take advantage of [django-discover-runner](https://github.com/jezdez/django-discover-runner/), which is the default test runner in Django 1.6. Instead of using a setting to list which apps should be tested, or accepting Django-specific test labels, it uses the official test discovery feature of the new unittest2.

Also, the original [django-jenkins](https://github.com/kmmbvnr/django-jenkins) project doesn't take advantage of improvements to testing introduced in Django 1.4. Special management commandd are no longer needed, as test runners themself can add options that are handled by the built-in `test` command.


What's Changed?
---------------

* **It doesn't override the suite construction.** Use the included test runner based on the django-discover-runner, or use the included Mixin to add Jenkins functionality to your own runner. Your test suite will be built the same way on Jenkins as it is on your local machine.
* **No management commands are provided.** Since Django 1.4, the built in 'test' command has allowed the test runner to define additional options that the management command will accept.
* **It doesn't use signals.** Instead of using the event/callback style of signals and using `inspect.getmembers` to connect everything, the test runner simply checks for key methods on each task the same way Django's request handler checks for methods on middleware.
* **Not everything works yet.** Only a subset of the django-jenkins tasks have been ported at this point. I'd love to accept your pull requests to add more of them.

Who?
----

First and foremost, the authors of [django-jenkins](https://github.com/kmmbvnr/django-jenkins) are responsible for the basis of most of this code. I ([Brandon Konkle](https://github.com/bkonkle)) just took it apart and put it back together again in a different way. Thank you to the contributors of that project!

For the full list of original authors and for the contributors to this project, see the AUTHORS.md file.