
from baseframe import localize_timezone
from boxoffice import app
from boxoffice.models import OnlinePayment, LINE_ITEM_STATUS, PaymentTransaction, TRANSACTION_TYPE
from boxoffice.extapi.razorpay import get_settlements


def get_settled_transactions(date_range):
    settled_transactions = get_settlements(date_range)
    headers = ['settlement_id', 'transaction_type', 'order_id', 'payment_id', 'refund_id', 'item_collection', 'description', 'base_amount', 'discounted_amount', 'final_amount', 'order_paid_amount', 'transaction_date', 'settled_at', 'razorpay_fees', 'order_amount', 'credit', 'debit', 'receivable_amount', 'settlement_amount', 'buyer_fullname']
    rows = []
    external_transaction_msg = u"Transaction external to Boxoffice. Credited directly to Razorpay?"
    
    for settled_transaction in settled_transactions:
        if settled_transaction['type'] == 'settlement':
          rows.append({
              'settlement_id': settled_transaction['entity_id'],
              'settlement_amount': settled_transaction['amount'],
              'settled_at': settled_transaction['settled_at']

          })  
        elif settled_transaction['type'] == 'payment':
            payment = OnlinePayment.query.filter_by(pg_paymentid=settled_transaction['entity_id']).one_or_none()
            if payment:
                order = payment.order
                rows.append({
                    'settlement_id': settled_transaction['settlement_id'],
                    'transaction_type': settled_transaction['type'],
                    'order_id': order.id,
                    'payment_id': settled_transaction['entity_id'],
                    'razorpay_fees': settled_transaction['fee'],
                    'transaction_date': localize_timezone(order.paid_at, 'Asia/Kolkata'),
                    'credit': settled_transaction['credit'],
                    'buyer_fullname': order.buyer_fullname,
                    'item_collection': order.item_collection.title
                })
                for line_item in order.get_initial_line_items:
                    # some line items are voided or cancelled
                    # how do you retrieve the line items that were created during the order was created?
                    rows.append([settled_transaction['settlement_id'], settled_transaction['entity_id'], order.id, order.item_collection.title, line_item.item.title, '-', line_item.final_amount, '-', '-', '-'])
            else:
                # Transaction outside of Boxoffice
                rows.append({
                    'settlement_id': settled_transaction['settlement_id'],
                    'payment_id': settled_transaction['entity_id'],
                    'credit': settled_transaction['credit'],
                    'description': external_transaction_msg
                })
        elif settled_transaction['type'] == 'refund':
            payment = OnlinePayment.query.filter_by(settled_transactionid=settled_transaction['payment_id']).one()
            refund = PaymentTransaction.query.filter(PaymentTransaction.online_payment == payment,
                PaymentTransaction.transaction_type == TRANSACTION_TYPE.REFUND,
                PaymentTransaction.settled_transactionid == settled_transaction['entity_id']
                ).one()
            order = refund.order
            rows.append({
                'settlement_id': settled_transaction['settlement_id'],
                'refund_id': settled_transaction['entity_id'],
                'payment_id': settled_transaction['payment_id'],
                'order_id': order.id,
                'razorpay_fees': settled_transaction['fee'],
                'debit': settled_transaction['debit'],
                'buyer_fullname': order.buyer_fullname,
                'description': refund.refund_description,
                'amount': refund.amount,
                'item_collection': order.item_collection.title
            })
    return (headers, rows)
