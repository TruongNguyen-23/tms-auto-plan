import copy 
def split_order(order, max_volume):
    orders = []
    original_volume = order['Volume']
    original_qty = order['Qty']
    original_weight = order['Weight']
    
    num_splits = int(original_volume // max_volume)
    remaining_volume = original_volume % max_volume
    
    for i in range(num_splits):
        new_order = copy.deepcopy(order)
        ratio = max_volume / original_volume
        new_order['OrderId'] = f"{order['OrderId']}_{i+1}"
        new_order['Volume'] = max_volume
        new_order['Qty'] = round(original_qty * ratio, 2)
        new_order['Weight'] = round(original_weight * ratio, 2)
        orders.append(new_order)
    
    if remaining_volume > 0:
        new_order = copy.deepcopy(order)
        ratio = remaining_volume / original_volume
        new_order['OrderId'] = f"{order['OrderId']}_{num_splits+1}"
        new_order['Volume'] = remaining_volume
        new_order['Qty'] = round(original_qty * ratio, 2)
        new_order['Weight'] = round(original_weight * ratio, 2)
        orders.append(new_order)
    
    return orders