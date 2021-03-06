pyrowire |release|
==================

pyrowire is a framework you can use to quickly create Twilio-based SMS/MMS applications, licensed under the BSD 3-Clause license.

Quickstart
==========
*For the purposes of this quickstart, it is assumed that you have an account with both Heroku and Twilio,
and that you have at minimum the following installed:*
    * pip
    * virtualenv

In your virtual environment's root directory, execute:

::

    $ pip install pyrowire && pyrowire --init

| This will install ``pyrowire``, and copy into the root folder the following files:

* `app.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/app.py>`_ (the application file)
* `settings.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/settings.py>`_ (the configuration file)
* `Procfile <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/Procfile>`_ (a Heroku Procfile)
* `requirements.txt <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/requirements.txt>`_ (pip requirements file)

Usage
-----
::

  $ ENV=(DEV|STAGING|PROD) [RUN=(WEB|WORKER)] [TOPIC=] python my_app.py

Sample Application
------------------
Here's what the my_app.py file (created by running ``pyrowire --init``) looks like:

.. code:: python

    import pyrowire
    import my_settings

    # configure the pyrowire application
    pyrowire.configure(my_settings)

    # all app.processor methods need to be annotated with the topic
    # for which they process and take one kwarg, 'message_data'
    @pyrowire.handler(topic='my_topic')
    def my_processor(message_data):
        if not message_data:
            raise TypeError("message_data must not be None")

        # insert handler logic here
        return message_data

    # all pyro.filter methods need to be annotated with the name
    # of the filter and take one kwarg, 'message_data'
    @pyrowire.validator(name='my_validator')
    def my_filter(message_data):
        if not message_data:
            raise TypeError("message_data must not be None")

        # insert validation logic here
        # validators should try to prove that the message is invalid, i.e., return True
        return True

    if __name__ == '__main__':
        pyrowire.run()

As you can see, it's rather straightforward; to start out you are given placeholders for both a handler and a validator.
The handler is where you will write the business logic for your Twilio application, and additional validators can be added
if needed, or removed altogether. See their `Handlers <./doc_sections/working_with_messages.html#handlers>`_ and
`Message Validation <./doc_sections/messages.html#message-validation>`_ for more information.

pyrowire Tutorial
~~~~~~~~~~~~~~~~~
If you feel like getting the walkthrough now, head over to the `tutorial section <./doc_sections/tutorial.html>`_.

Slowstart
=========

.. toctree::
   :maxdepth: 2

   1. Installation <doc_sections/installation.rst>
   2. Application Landscape <doc_sections/landscape.rst>
   3. Receiving Messages <doc_sections/messages.rst>
   4. Working with Messages<doc_sections/working_with_messages.rst>
   5. Settings (Configuration) <doc_sections/settings.rst>
   6. Running pyrowire <doc_sections/running.rst>
   7. Full Tutorial <doc_sections/tutorial.rst>
   8. Appendices <doc_sections/appendices.rst>

