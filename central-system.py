import asyncio
import logging
import websockets
from datetime import datetime
import random

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, AuthorizationStatus
from enums import OcppMisc as oc

from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.Authorize)
    async def on_auth(self,id_tag,**kwargs):
        if id_tag == "test_cp2" or id_tag == "test_cp3":
            print("authorized")
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
            )
        else:
            print("Not Authorized")
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
            )

    @on(Action.BootNotification)
    async def on_boot_notification(self, charge_point_model,charge_point_vendor, **kwargs):

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    @on(Action.StartTransaction)
    async def on_startTX(self,id_tag,connector_id, meter_start, timestamp, **kwargs):
        print("session for user", id_tag)
        if id_tag == "test_cp2" or id_tag == "test_cp3":
            print("valid transaction for connector, ",connector_id)
            print("meter value at start of transaction ", meter_start)
            return call_result.StartTransactionPayload(
                transaction_id=random.randint(122,6666666666), id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
            )
        else:
            print("Not Authorized transaction")
            return call_result.StartTransactionPayload(
                transaction_id=0 , id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
            )

    @on(Action.StopTransaction)
    async def on_stopTX(self,meter_stop,timestamp,transaction_id, **kwargs):
        print("Transaction stopped at value", meter_stop, " for transaction id", transaction_id,"at", timestamp)
        return call_result.StopTransactionPayload(
            None
        )






async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                 "Closing Connection")
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    try:

        if charge_point_id =='CP_3' or charge_point_id == 'CP_4':

            print("Valid Chargepoint")
            cp = ChargePoint(charge_point_id, websocket)

            await cp.start()

        else:
            print('Invalid chargepoint')


    except:
        pass


async def main():

    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9005,
        subprotocols=['ocpp1.6'],
        close_timeout=10,
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
