# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module is a stand-alone tool to help convert between dollars (or any fiat, really) and the bitcoins

Mmmm, the bitcoins.
"""

from pywebio import pin
from pywebio import output
from pywebio import session

from data import get_price
from constants import ONE_HUNDRED_MILLION

if __name__ == '__main__':
    def updateprice():
        pin.pin['price'] = get_price()

    def convert_to_sat():
        amnt = float(pin.pin["amount"])
        price = float(pin.pin["price"])

        r = float(ONE_HUNDRED_MILLION * (amnt / price))

        output.put_text(f"[{amnt:,.2f} fiat @ price:{price:,.2f}] = {r:,.2f} satoshi")

    def convert_to_fiat():
        amnt = float(pin.pin["amount"])
        price = float(pin.pin["price"])
        r = amnt * (price / ONE_HUNDRED_MILLION)
        output.put_text(f"[{amnt:,.2f} satoshi @ price:{price:,.2f}] = {r:,.2f} fiat")

    output.put_markdown( """# uhhh... how many sats is that?""" )
    output.put_row(content=[
        output.put_column(content=[
            pin.put_input("price", type="float", label="What is the current price of bitcoin?", value=get_price()),
            output.put_button("refresh price", onclick=updateprice)
            ]),
        output.put_column(content=[
            pin.put_input("amount", type="float", label="Amount to convert"),
            output.put_column(content=[
                output.put_button("sats -> fiat", onclick=convert_to_fiat),
                output.put_button("fiat -> sats", onclick=convert_to_sat)
                ])
            ])
    ])

    session.hold()
