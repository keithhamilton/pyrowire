Receiving Messages
==================

pyrowire's primary object of note is a message. When an SMS (or MMS) is received by your application, pyrowire will construct a
dictionary object from it, using most of the properties provided by the TwiML request body.

See `Anatomy of a Message <./doc_sections/appendices#appendix-b-the-anatomy-of-a-pyrowire-message>`_  for more information message properties.

Message Endpoints
-----------------
pyrowire uses a topic-based approach to handling incoming messages. One pyrowire instance can scale to handle
many, many different Twilio SMS applications, and separates logic for each by the use of topics. Each topic is
considered to be a separate Twilio application, has its own definition in your config file, and has the endpoint:
::

    http(s)://my-rad-pyrowire-instance.mydomain.com/queue/<topic>

where ``<topic>`` is a keyword of your choice that identifies messages as being for a specific application.

Because pyrowire handles incoming messages, and can assign workers, on a per-topic basis, you could run as many
different applications off of one cluster as you want, provided you scale up for it. Every time a message is received
via Twilio's REST interface, it will be forwarded to your pyrowire instance, queued by its topic, then routed to,
and processed by, a handler specifically designed for that topic/application. Business logic across applications can vary
as much as you need it to, as each topic is handled independently by its defined handler.

Message Validation
------------------
pyrowire has three default message validators. By default, all messages received will be passed through the following:

- **profanity**: checks the incoming message against a list of about 1,000 graphically profane terms (trust us).
- **length**: checks that the length of the incoming message does not exceed some threshold; Twilio, by default, uses 160 characters as a limit, so we do too. Also ensures incoming messages have a length > 0.
- **parseable**: Twilio can't parse everything. Take emoji for example. The default parseable validator allows inclusion of all alphanumeric characters and most punctuation characters. For a comprehensive list of valid characters, see `Valid Message Characters <./doc_sections/appendices.html#appendix-c-valid-message-characters>`_.


Custom Validators
-----------------
As described in the previous section, pyrowire uses the concept of topics to distinguish handling for each message,
but you can also create custom validators that can be used on messages for one or more topics.

Defining a Validator
~~~~~~~~~~~~~~~~~~~~
Defining a custom validator is easy. Just annotate a method that takes a message, checks to make sure it conforms to some
rule the method identifies, and returns a boolean, and you're set.

.. code:: python

    @pyrowire.validator(name='my_min_length_validator')
    def min_length(message_data):
        if not message_data:
            raise TypeError("message_data must not be None.")
        # return True if message is less than 5 chars long
        return len(message_data['message']) < 5

Validator Criteria
~~~~~~~~~~~~~~~~~~
All validators must satisfy the following criteria:

    1. the ``pyrowire.validator`` annotation must take one kwarg, *name*, and should be used to identify the validator.
    2. the method definition must take one arg, *message_data*
    3. validators must be designed to return True if the message is not valid, *i.e., they are trying to prove that the message received is invalid.*


Sample Validator
~~~~~~~~~~~~~~~~
Let's check it out by creating, say, a validator that requires the word 'yo' be present in all messages:

.. code:: python

    # all app.validator methods need to be annotated with the name of the validator
    # and take one kwarg, 'message_data'
    @pyrowire.validator(name='must_include_yo')
    def must_include_yo(message_data):
        if not message_data:
            raise TypeError("message_data must not be None.")

        import re.search
        # assert that 'yo' is not found in the message
        return not re.search(r'*yo*', message_data['message'].lower())

By using the ``@pyrowire.validator`` annotation, any twilio topics you define in `your configuration file <./settings.html#defining-a-topic>`__
that require the validator 'must\_include\_yo' will have to pass this validator in addition to the three defaults. By convention,
the name of the method should match the name passed into the ``@pyrowire.validator`` decorator, but it doesn't have to.

Overriding Default Validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to omit a validator from your application, you can just remove it from your configuration file for the topic
in question (see `this example <./tutorial.html#settings>`_).

If you want to change the validator's behavior, just define it again in your app file:

.. code:: python

    # profanity validator that considers 'reaver' to be the only bad word in the verse
    @pyrowire.validator(name='profanity')
    def profanity(message_data):
        if not message_data:
            raise TypeError("message_data must not be None.")

        import re.search
        return re.search(r'\breaver\b', message_data['message'].lower())

