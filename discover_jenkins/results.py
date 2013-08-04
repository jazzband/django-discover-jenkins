import os
import traceback
from datetime import datetime
from itertools import groupby
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from django.utils.unittest import TextTestResult
from discover_jenkins.utils import total_seconds

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


class TestInfo(object):

    class RESULT(object):
        SUCCESS = 0
        ERROR = 1
        FAILURE = 2
        EXPECTED_FAILURE = 3
        UNEXPECTED_SUCCESS = 4
        SKIPPED = 5

    __slots__ = ('test_method', 'start_time', 'end_time',
                 'err', 'stdout', 'stderr', 'result', 'reason')

    def __init__(self, **kwargs):
        for slot_name in self.__slots__:
            setattr(self, slot_name, None)
        for key, value in kwargs.items():
            setattr(self, key, value)


class XMLTestResult(TextTestResult):
    """
    Dumps xml junit output as well as text
    """
    def __init__(self, *args, **kwargs):
        super(XMLTestResult, self).__init__(*args, **kwargs)
        self.testInfos = []
        self.currentTestInfo = None

    def startTestRun(self):
        """
        Called once before any tests are executed.
        """
        super(XMLTestResult, self).startTestRun()

    def startTest(self, test):
        """
        Called when the given test is about to be run
        """
        self.currentTestInfo = TestInfo(test_method=test,
                                        start_time=datetime.now())
        super(XMLTestResult, self).startTest(test)

    def stopTest(self, test):
        """
        Called when the given test has been run
        """
        self.currentTestInfo.end_time = datetime.now()
        self.currentTestInfo.stdout = self._stdout_buffer.getvalue()
        self.currentTestInfo.stderr = self._stderr_buffer.getvalue()
        self.testInfos.append(self.currentTestInfo)
        super(XMLTestResult, self).stopTest(test)

    def addError(self, test, err):
        """
        Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()
        """
        self.currentTestInfo.result = TestInfo.RESULT.ERROR
        self.currentTestInfo.err = err
        super(XMLTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        """
        Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        self.currentTestInfo.result = TestInfo.RESULT.FAILURE
        self.currentTestInfo.err = err
        super(XMLTestResult, self).addFailure(test, err)

    def addSuccess(self, test):
        """
        Called when a test has completed successfully
        """
        self.currentTestInfo.result = TestInfo.RESULT.SUCCESS
        super(XMLTestResult, self).addSuccess(test)

    def addSkip(self, test, reason):
        """
        Called when a test is skipped.
        """
        self.currentTestInfo.result = TestInfo.RESULT.SKIPPED
        self.currentTestInfo.reason = reason
        super(XMLTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        """
        Called when an expected failure/error occured.
        """
        self.currentTestInfo.result = TestInfo.RESULT.EXPECTED_FAILURE
        self.currentTestInfo.err = err
        super(XMLTestResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        """
        Called when a test was expected to fail, but succeed.
        """
        self.currentTestInfo.result = TestInfo.RESULT.UNEXPECTED_SUCCESS
        super(XMLTestResult, self).addUnexpectedSuccess(test)

    def _exc_info_to_string(self, err, test):
        """
        Converts a sys.exc_info()-style tuple of values into a string.
        """
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            output = self._stdout_buffer.getvalue()
            error = self._stderr_buffer.getvalue()
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        return ''.join(msgLines)

    def test_method_name(self, test):
        """
        Returns the test method name.
        """
        test_id = test.id()
        return test_id.split('.')[-1]

    def test_case_name(self, test):
        """
        Returns test case name
        """
        testcase = type(test)
        module = testcase.__module__ + '.'
        if module == '__main__.':
            module = ''
        return module + testcase.__name__

    def dump_xml(self, output_dir):
        """
        Dumps test result to xml
        """
        self.buffer = False

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(os.path.join(output_dir, 'junit.xml'), 'w') as output:
            document = XMLGenerator(output, 'utf-8')
            document.startDocument()
            document.startElement('testsuites', AttributesImpl({}))

            suites = groupby(self.testInfos,
                             key=lambda test_info: self.test_case_name(
                                                        test_info.test_method))
            for suite_name, suite in suites:
                document.startElement('testsuite',
                                      AttributesImpl({'name': suite_name}))

                for test_info in suite:
                    document.startElement('testcase', AttributesImpl({
                        'classname': suite_name,
                        'name': self.test_method_name(test_info.test_method),
                        'time': '%3f' % total_seconds(
                                    test_info.end_time - test_info.start_time)
                    }))

                    if test_info.result == TestInfo.RESULT.ERROR:
                        document.startElement('error', AttributesImpl({
                            'message': smart_text(test_info.err[1])
                        }))
                        document.characters(self._exc_info_to_string(
                                        test_info.err, test_info.test_method))
                        document.endElement('error')
                    elif test_info.result == TestInfo.RESULT.FAILURE:
                        document.startElement('failure', AttributesImpl({
                            'message': smart_text(test_info.err[1])
                        }))
                        document.characters(self._exc_info_to_string(
                                        test_info.err, test_info.test_method))
                        document.endElement('failure')
                    elif test_info.result == \
                                    TestInfo.RESULT.UNEXPECTED_SUCCESS:
                        document.startElement('error', AttributesImpl({
                            'message': 'Unexpected success'
                        }))
                        document.endElement('error')
                    elif test_info.result == TestInfo.RESULT.SKIPPED:
                        document.startElement('skipped', AttributesImpl({}))
                        document.characters(test_info.reason)
                        document.endElement('skipped')

                    if test_info.stdout:
                        document.startElement('system-out', AttributesImpl({}))
                        document.characters(test_info.stdout)
                        document.endElement('system-out')

                    if test_info.stderr:
                        document.startElement('system-err', AttributesImpl({}))
                        document.characters(test_info.stderr)
                        document.endElement('system-err')
                    document.endElement('testcase')

                document.endElement('testsuite')

            document.endElement('testsuites')
            document.endDocument()
