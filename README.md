# plugin-http-file-cost-datasource
* Plugin for collecting cost data from **CSV file**
---

## 1) CSV format
![img.png](examples/img.png)
* The above is an example of a csv file, and the fields that exist in the csv must exist.
* Here is a list of available fields.
Of these, `cost`, `currency`, `year`, `month`, and `day` fields are required fields.
  * **cost(required)**
  * **currency(required)**
  * usage_quantity
  * provider
  * region_code
  * product
  * account
  * **year(required)**
  * **month(required)**
  * **day(required)**


## 2) How to use
In order to use the plugin, how to use [spacectl CLI tools](https://github.com/cloudforet-io/spacectl) must be preceded.

1. Check if the plugin you want to use from the marketplace exists.
```shell
 $ spacectl list repository.Plugin -p service_type=cost_analysis.DataSource --minimal
 
 plugin_id                        | name                                | image                                     | state   | service_type             | registry_type
----------------------------------+-------------------------------------+-------------------------------------------+---------+--------------------------+-----------------
 plugin-http-file-cost-datasource | HTTP file Cost Analysis Data Source | pyengine/plugin-http-file-cost-datasource | ENABLED | cost_analysis.DataSource | DOCKER_HUB
```

2. Register with the DataSource resource of cost-analysis.
```shell
$ spacectl exec register cost-analysis.DataSource -f create_data_source.yml
```
```yaml
# register_data_source.yml
---
name: HTTP File Data Source
service_type: EXTERNAL
image: pyengine/plugin-http-file-cost-datasource
tags: {}
template: {}
```

3. Check the registered CSV Plugin information.
```shell
$ spacectl exec get cost-analysis.DataSource -p data_source_id=<data_source_id>

---
created_at: '2023-02-06T11:04:34.348Z'
data_source_id: ds-123456789012
data_source_type: EXTERNAL
domain_id: domain-123456789012
last_synchronized_at: '2023-02-06T16:00:08.356Z'
name: HTTP File Data Source
plugin_info:
  metadata:
    data_source_rules:
    - actions:
        match_service_account:
          source: account
          target: data.account
      conditions: []
      conditions_policy: ALWAYS
      name: match_service_account
      options:
        stop_processing: true
      tags: {}
  plugin_id: plugin-http-file-cost-datasource
  upgrade_mode: AUTO
  version: 1.0.0.20230206.225536
state: ENABLED
tags: {}
template: {}
```

4. Sets the options corresponding to the url where the csv file is located in the plugin.
```shell
$ spacectl exec update_plugin cost-analysis.DataSource -p data_source_id=<data_source_id> -f update_data_source.yml
```
```yaml
# update_data_source.yml
---
data_source_id: ds-123456789012
options:
  base_url: https://github.com/cloudforet-io/plugin-http-file-cost-datasource/blob/master/examples/cost_example.csv
```

5. Manually sync the cost information of the csv file in step 4.
```shell
$ spacectl exec sync cost-analysis.DataSource -p data_source_id=<data_source_id>
```