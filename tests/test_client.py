import asyncio
import unittest
from unittest.mock import AsyncMock
from syriatel import (SyriatelAPI, SyriatelAPISync, InvalidTokenError, RateLimitError,
                      InsufficientBalanceError, ManagementDisabledError)


class Response:
    def __init__(self,data,status=200,headers=None):self.data,self.status,self.headers=data,status,headers or {}
    async def json(self):
        if isinstance(self.data,Exception):raise self.data
        return self.data
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass


class Session:
    closed=False
    def __init__(self,*responses):self.responses=list(responses);self.calls=[]
    def request(self,*args,**kwargs):self.calls.append((args,kwargs));return self.responses.pop(0)
    async def close(self):self.closed=True


def success(data):return Response({'success':True,'code':'SUCCESS','data':data})


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_both_generations_keep_the_account_token(self):
        session=Session(success({'accounts':[{'id':'acc_1'}]}),success({'balance':24000}))
        async with SyriatelAPI('test-token',session=session) as api:
            self.assertEqual(await api.list_accounts(),[{'id':'acc_1'}])
            self.assertEqual(await api.syrcash.balance('+963912345678'),24000)
        self.assertFalse(session.closed)
        for call in session.calls:self.assertEqual(call[1]['headers']['api-token'],'test-token')
        self.assertTrue(session.calls[0][0][1].endswith('/v1/accounts'))
        self.assertEqual(session.calls[1][1]['params']['query'],'0912345678')

    async def test_published_legacy_keywords_and_status_remain_supported(self):
        session=Session(success({'balance':100}),success({'transactions':[]}))
        api=SyriatelAPI('test',session=session)
        self.assertEqual(await api.syrcash.balance(code=12345678),100)
        await api.syrcash.get_incoming_history(query='12345678',status='all',page=2)
        self.assertEqual(session.calls[0][1]['params'],{'code':'12345678'})
        self.assertEqual(session.calls[1][1]['params'],{'query':'12345678','status':'all','page':2})

    async def test_typed_errors_are_not_wrapped_as_network_errors(self):
        for code,exception,status in [('INVALID_TOKEN',InvalidTokenError,401),('API_MANAGEMENT_DISABLED',ManagementDisabledError,403),('INSUFFICIENT_BALANCE',InsufficientBalanceError,409)]:
            session=Session(Response({'success':False,'code':code,'data':None,'error':{'message':'Example','request_id':'req_123'}},status))
            api=SyriatelAPI('test',session=session)
            with self.assertRaises(exception) as error:await api.get_profile()
            self.assertEqual(error.exception.status_code,status)
            self.assertEqual(error.exception.request_id,'req_123')

    async def test_rate_limit_exposes_retry_after_without_retrying(self):
        session=Session(Response({'success':False,'code':'RATE_LIMITED','error':{'message':'Wait'}},429,{'Retry-After':'120'}))
        api=SyriatelAPI('test',session=session)
        with self.assertRaises(RateLimitError) as error:await api.get_balance('acc_1')
        self.assertEqual(error.exception.retry_after,120)
        self.assertEqual(len(session.calls),1)

    async def test_non_json_throttle_still_has_a_typed_error(self):
        session=Session(Response(ValueError('not json'),429,{'Retry-After':'60'}))
        with self.assertRaises(RateLimitError) as error:await SyriatelAPI('test',session=session).get_profile()
        self.assertEqual(error.exception.retry_after,60)

    async def test_mutations_preserve_idempotency_and_leading_zeros(self):
        session=Session(success({'id':'link_1'}),success({'status':'verified'}),success({'charged_usd':'2.00'}))
        api=SyriatelAPI('test',session=session)
        await api.create_link_session('0999999999','not-a-real-password',idempotency_key='link-request-001')
        await api.verify_pin('acc_1','0123')
        await api.subscribe('acc_1',idempotency_key='purchase-request-001',auto_renew=False)
        self.assertEqual(session.calls[0][1]['headers']['Idempotency-Key'],'link-request-001')
        self.assertEqual(session.calls[1][1]['json'],{'pin':'0123'})
        self.assertEqual(session.calls[2][1]['json']['auto_renew'],False)
        self.assertEqual(len(session.calls),3)

    async def test_invalid_input_does_not_send_a_request(self):
        session=Session();api=SyriatelAPI('test',session=session)
        for function in [lambda:api.verify_pin('acc_1','123'),lambda:api.verify_link_session('link_1','12345'),lambda:api.subscribe('acc_1',periods=True,idempotency_key='request-001'),lambda:api.update_subscription('acc_1')]:
            with self.assertRaises(ValueError):await function()
        self.assertEqual(session.calls,[])

    async def test_account_id_is_escaped_in_paths(self):
        session=Session(success({}));api=SyriatelAPI('test',session=session)
        await api.get_account('acc_1/../other')
        self.assertIn('acc_1%2F..%2Fother',session.calls[0][0][1])

    async def test_wallet_cursor_and_history_direction_are_preserved(self):
        session=Session(success({'entries':[]}),success({'transactions':[]}));api=SyriatelAPI('test',session=session)
        await api.get_wallet(limit=10,before_id=123)
        await api.get_transactions('acc_1',direction='outgoing',page=2,search='example')
        self.assertEqual(session.calls[0][1]['params'],{'limit':10,'before_id':123})
        self.assertEqual(session.calls[1][1]['params']['direction'],'outgoing')
        self.assertEqual(session.calls[1][1]['params']['page'],2)

    async def test_public_endpoints_use_the_platform_root(self):
        session=Session(success({}),success({}));api=SyriatelAPI('test',session=session)
        await api.get_service_status();await api.get_public_plans()
        self.assertTrue(session.calls[0][0][1].endswith('/syr-cash/public/status'))
        self.assertTrue(session.calls[1][0][1].endswith('/syr-cash/public/plans'))

    async def test_sync_client_rejects_an_async_context_without_leaking_a_coroutine(self):
        api=SyriatelAPISync('test')
        try:
            with self.assertRaisesRegex(RuntimeError,'Use SyriatelAPI'):api.list_accounts()
        finally:api._loop.close()


class SyncTests(unittest.TestCase):
    def test_sync_client_reuses_and_closes_its_own_loop(self):
        with SyriatelAPISync('test') as api:
            api._async_client.list_accounts=AsyncMock(return_value=[{'id':'acc_1'}])
            self.assertEqual(api.list_accounts(),[{'id':'acc_1'}])
            self.assertEqual(api.list_accounts(),[{'id':'acc_1'}])
        self.assertTrue(api._loop.is_closed())
        api.close()

    def test_legacy_inventory_keeps_its_shape(self):
        async def run():
            session=Session(success({'numbers':[{'number':'0912345678','code':'1234'}]}))
            return await SyriatelAPI('test',session=session).get_numbers_codes()
        self.assertEqual(asyncio.run(run()),[('0912345678','1234')])


if __name__=='__main__':unittest.main()
