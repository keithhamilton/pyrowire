import ast
import json
import unittest
from multiprocessing import Process

from pyrowire import pyrowire as pyro
from pyrowire.decorators import handler
import pyrowire.tasks as pyroworker
import pyrowire.config.configurator as config
from redis import Redis
from test import test_settings


pyro.configure(settings=test_settings)
topic = 'sample'

@handler(topic=topic)
def my_processor(message_data=None):
    message_data['final_data'] = message_data['message']
    Process(target=pyro.sms, kwargs={'data': message_data, 'key': 'final_data'}).start()

class TestTasks(unittest.TestCase):

    def setUp(self):
        self.topic = topic

        self.redis = Redis(config.redis('host'),
                           config.redis('port'),
                           config.redis('db'),
                           config.redis('password'))

        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_sample_task(self):
        # queue task
        _message = {'message': 'You are strong in the ways of the Force.', 'number': '+1234567890', 'topic':'sample'}
        self.redis.rpush('%s.%s' % (self.topic, 'submitted'), json.dumps(_message))
        # process task
        _message_handler = config.handler(self.topic)
        _uuid = pyroworker.process_queue_item(self.topic,
                                              profile=config.profile(),
                                              handler=_message_handler,
                                              persist=False)
        # expect result in completed queue
        _pending = self.redis.hget('%s.%s' % (self.topic, 'pending'), _uuid)
        _complete = ast.literal_eval(self.redis.hget('%s.%s' % (self.topic, 'complete'), _uuid))

        self.assertIsNone(_pending)
        self.assertIsNotNone(_complete)
        self.assertEqual(_complete['number'], '+1234567890')
        self.assertTrue('final_data' in _complete)
        self.assertEqual(_complete['final_data'], _complete['message'])

    def test_pyro_work(self):
        # queue task
        _message = {'message': 'You are strong in the ways of the Force.', 'number': '+1234567890', 'topic':'sample'}
        self.redis.rpush('%s.%s' % (self.topic, 'submitted'), json.dumps(_message))
        # process task
        _uuid = pyro.work(topic=self.topic, persist=False)

        # expect result in completed queue
        _pending = self.redis.hget('%s.%s' % (self.topic, 'pending'), _uuid)
        _complete = ast.literal_eval(self.redis.hget('%s.%s' % (self.topic, 'complete'), _uuid))

        self.assertIsNone(_pending)
        self.assertIsNotNone(_complete)
        self.assertEqual(_complete['number'], '+1234567890')
        self.assertTrue('final_data' in _complete)
        self.assertEqual(_complete['final_data'], _complete['message'])


if __name__ == '__main__':
    unittest.main()