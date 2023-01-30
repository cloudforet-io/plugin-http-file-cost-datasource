OPTIONS = {
    'base_url': 'https://cloudforet.io/',
    'column_headers': {
        'resource_cost': 'cost',
        'currency': 'currency',
        'usage_quantity': 'usage_quantity',
        'infra_type': 'provider',
        'product_region': 'region_code',
        'category_name': 'category',
        'sub_category_name': 'resource_group',
        'product_service_code': 'product',
        'account_id': 'account',
        'usage_type': 'usage_type',
        'usage_date': 'billed_at'
    }
}

SECRET_DATA = {'auth_type': 'basic',
               'auth_options':
                   {
                       'username': 'seolmin',
                       'password': '1234'
                   }
               }

data = {}
data['options'] = OPTIONS
data['secret_data'] = SECRET_DATA

import yaml

f = open('meta.yaml', 'w+')
yaml.dump(data, f, allow_unicode=True)
