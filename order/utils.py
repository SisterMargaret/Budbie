import datetime
import simplejson as json

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number
    
def get_order_total_by_vendor(order, vendor):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor.id))
    
    subtotal=0
    tax = 0
    tax_dictionary= {}
    
    for key, val in data.items():
        
        subtotal += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)
        tax_dictionary.update(val)

        for i in val:
            for j in val[i]:
                tax += float(val[i][j])
    grand_total = float(subtotal) + float(tax)
        
    return { 'subtotal' : subtotal,
            'total_tax' : tax, 
            'tax_dictionary' : tax_dictionary, 
            'grand_total' : round(grand_total,2)  }