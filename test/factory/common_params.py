OPTIONS = {
    'base_url': 'https://raw.githubusercontent.com/stat-kwon/plugin-http-file-cost-datasource/master/examples/cost_example.csv',
}

data = {}
data['options'] = OPTIONS

import yaml

f = open('meta.yaml', 'w+')
yaml.dump(data, f, allow_unicode=True)
