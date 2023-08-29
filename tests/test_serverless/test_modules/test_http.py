'''
Test rp_http.py module.
'''
import json
import unittest
from unittest.mock import patch, AsyncMock
import aiohttp

from runpod.serverless.modules import rp_http


class TestHTTP(unittest.IsolatedAsyncioTestCase):
    ''' Test HTTP module. '''

    def setUp(self) -> None:
        self.job = {"id": "test_id"}
        self.job_data = {"output": "test_output"}

    async def test_send_result(self):
        '''
        Test send_result function.
        '''
        with patch('runpod.serverless.modules.rp_http.log') as mock_log, \
             patch('runpod.serverless.modules.rp_http.job_list.jobs') as mock_jobs, \
             patch('runpod.serverless.modules.rp_http.RetryClient') as mock_retry:

            mock_retry.return_value.post.return_value = AsyncMock()
            mock_retry.return_value.post.return_value.__aenter__.return_value.text.return_value = "response text" # pylint: disable=line-too-long

            mock_jobs.return_value = set(['test_id'])
            send_return_local = await rp_http.send_result(AsyncMock(), self.job_data, self.job)

            assert send_return_local is None
            assert mock_log.debug.call_count == 1
            assert mock_log.error.call_count == 0
            assert mock_log.info.call_count == 1

            mock_retry.return_value.post.assert_called_with(
                'JOB_DONE_URL',
                data=str(json.dumps(self.job_data, ensure_ascii=False)),
                headers={
                    "charset": "utf-8",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                raise_for_status=True
            )


    async def test_send_result_client_response_error(self):
        '''
        Test send_result function with ClientResponseError.
        '''
        with patch('runpod.serverless.modules.rp_http.log') as mock_log, \
             patch('runpod.serverless.modules.rp_http.job_list.jobs') as mock_jobs, \
             patch('runpod.serverless.modules.rp_http.RetryClient') as mock_retry, \
             patch.object(aiohttp.RequestInfo, "__init__", lambda *args, **kwargs: None):

            mock_request_info = aiohttp.RequestInfo(
                url="http://test_url",
                method="POST",
                headers={"Content-Type": "application/json"},
                real_url="http://test_url"
            )

            mock_response = AsyncMock()
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=mock_request_info,
                history=None,
                status=500,
                message="Error message"
            )

            mock_retry.return_value.post.return_value.__aenter__.return_value = mock_response
            mock_retry.return_value.post.return_value.__aenter__.return_value.text.return_value = "response text" # pylint: disable=line-too-long

            mock_jobs.return_value = set(['test_id'])
            send_return_local = await rp_http.send_result(AsyncMock(), self.job_data, self.job)

            mock_retry.side_effect = aiohttp.ClientResponseError(
                request_info=mock_request_info,
                history=None,
                status=500,
                message="Error message"
            )


            assert mock_retry.return_value.post.call_count == 1
            assert mock_response.raise_for_status.call_count == 1

            assert send_return_local is None
            assert mock_log.debug.call_count == 1
            assert mock_log.error.call_count == 1
            assert mock_log.info.call_count == 1


    async def test_send_result_type_error(self):
        '''
        Test send_result function with TypeError.
        '''
        with patch('runpod.serverless.modules.rp_http.log') as mock_log, \
             patch('runpod.serverless.modules.rp_http.job_list.jobs') as mock_jobs, \
             patch('runpod.serverless.modules.rp_http.json.dumps') as mock_dumps:

            mock_dumps.side_effect = TypeError("Forced exception")

            mock_jobs.return_value = set(['test_id'])
            send_return_local = await rp_http.send_result(AsyncMock(), self.job_data, self.job)

            assert send_return_local is None
            assert mock_log.debug.call_count == 0
            assert mock_log.error.call_count == 1
            assert mock_log.info.call_count == 1


    async def test_stream_result(self):
        '''
        Test stream_result function.
        '''
        with patch('runpod.serverless.modules.rp_http.log') as mock_log, \
             patch('runpod.serverless.modules.rp_http.job_list.jobs') as mock_jobs, \
             patch('runpod.serverless.modules.rp_http.RetryClient') as mock_retry:

            mock_retry.return_value.post.return_value = AsyncMock()
            mock_retry.return_value.post.return_value.__aenter__.return_value.text.return_value = "response text" # pylint: disable=line-too-long

            mock_jobs.return_value = set(['test_id'])
            send_return_local = await rp_http.stream_result(AsyncMock(), self.job_data, self.job)

            assert send_return_local is None
            assert mock_log.debug.call_count == 1
            assert mock_log.error.call_count == 0
            assert mock_log.info.call_count == 0

            mock_retry.return_value.post.assert_called_with(
                'JOB_STREAM_URL',
                data=str(json.dumps(self.job_data, ensure_ascii=False)),
                headers={
                    "charset": "utf-8",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                raise_for_status=True
            )


if __name__ == '__main__':
    unittest.main()
