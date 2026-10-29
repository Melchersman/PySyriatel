import unittest
from unittest.mock import AsyncMock
from syriatel import SyriatelV2,SyriatelV2Sync

class V2ClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client=SyriatelV2('test-token')
        self.request=AsyncMock(return_value={})
        self.client._transport._request=self.request

    async def asyncTearDown(self):await self.client.close()

    async def test_read_selector_dates_and_transfer_ids_are_sent_to_v2(self):
        await self.client.incoming_transactions(pay_code='001234',start_at='2026-10-29',transaction_ids=['A','B'],limit=50)
        args,kwargs=self.request.call_args
        self.assertEqual(args,('GET','/transactions/incoming'))
        self.assertEqual([value for key,value in kwargs['params'] if key=='transaction_ids'],['A','B'])
        self.assertIn(('pay_code','001234'),kwargs['params'])
        self.assertTrue(self.client._transport.base_url.endswith('/v2'))

    async def test_subscriptions_select_parent_and_gsm_and_keep_renewal_separate(self):
        await self.client.subscribe('akrab_12','0912345678',idempotency_key='purchase-unique-1')
        args,kwargs=self.request.call_args
        self.assertEqual(args[1],'/accounts/akrab_12/numbers/0912345678/subscription')
        self.assertNotIn('auto_renew',kwargs['body'])
        self.assertEqual(kwargs['idempotency_key'],'purchase-unique-1')
        await self.client.set_auto_renew('akrab_12','0912345678',False)
        self.assertEqual(self.request.call_args.kwargs['body'],{'auto_renew':False})

    async def test_pin_and_sms_preserve_leading_zeros(self):
        await self.client.verify_pin('akrab_12','0912345678','0123')
        self.assertEqual(self.request.call_args.kwargs['body'],{'pin':'0123'})
        await self.client.verify_link_session('link_1','012345')
        self.assertEqual(self.request.call_args.kwargs['body'],{'code':'012345'})

    async def test_parent_and_number_lists_return_their_own_arrays(self):
        self.request.return_value={'accounts':[{'id':'akrab_12'}]}
        self.assertEqual(await self.client.list_accounts(),[{'id':'akrab_12'}])
        self.request.return_value={'numbers':[{'gsm':'0912345678'}]}
        self.assertEqual(await self.client.list_numbers('akrab_12'),[{'gsm':'0912345678'}])

    async def test_invalid_selectors_and_pin_do_not_send_requests(self):
        for kwargs in ({},{'gsm':'0912345678','pay_code':'001234'},{'gsm':'123'}):
            with self.assertRaises(ValueError):await self.client.get_balance(**kwargs)
        with self.assertRaises(ValueError):await self.client.verify_pin('akrab_12','0912345678',123)
        with self.assertRaises(ValueError):await self.client.subscribe('akrab_12','0912345678',periods=True,idempotency_key='key-test-123')
        self.request.assert_not_called()

class V2SyncTests(unittest.TestCase):
    def test_sync_closes_its_own_loop(self):
        client=SyriatelV2Sync('test-token')
        client._async_client.get_status=AsyncMock(return_value={'status':'operational'})
        self.assertEqual(client.get_status(),{'status':'operational'})
        loop=client._loop;client.close();self.assertTrue(loop.is_closed())
