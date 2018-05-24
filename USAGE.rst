=====
Usage
=====

To use terraform-lint:

.. code-block:: bash

    terraform-lint --help

    [-h] [--log-config LOGGER_CONFIG]
         [--log-level {debug,info,warning,error,critical}]
          -r rules.yaml -p positioning.yaml -s
          tf_plans_dir

    Cli to lint naming conventions of terraform plans based on a provided rule set

    optional arguments:
      -h, --help            show this help message and exit
      --log-config LOGGER_CONFIG, -l LOGGER_CONFIG
                            The location of the logging config json file
      --log-level {debug,info,warning,error,critical}, -L {debug,info,warning,error,critical}
                            Provide the log level. Defaults to INFO.
      -n naming.yaml, --naming naming.yaml
      -p positioning.yaml, --positioning positioning.yaml
      -s tf_plans_dir, --stack tf_plans_dir



.. code-block:: bash

    terraform-lint -s dir_with_tf_files/ -n naming.yaml -p positioning.yaml

    Naming convention not followed on file prfxa015-pc01/compute.tf for resource prfxa015-pc01 for field tags.Name
            Regex not matched : ^prfx[dtaps]a[0-9]{3}-[a-z]{1,3}[0-9]{2}$
            Value             : prfxa015-pc01



.. code-block:: bash

    # naming.yaml should follow the following schema
    #
    # Schema([{'resource': basestring,
    #          'regex': is_valid_regex,
    #         Optional('fields'): [{'value': basestring,
    #                               'regex': is_valid_regex}]}])
    #
    # Example

    ---

    - resource: terraform_resource_name
      regex: .* # regex to lint terraform id
      fields:
        - value: tags.Name
          regex: ^cust[dtaps](?:ew1)-pc[0-9]{2}$  # regex to lint the name of the tag
        - value: tags.Other
          regex: ^cust[dtaps](?:ew1)-other[0-9]{2}$  # regex to lint the name of the tag


.. code-block:: bash

    # positioning.yaml should follow the following schema
    #
    # Schema({And(basestring, lambda x: x.endswith('.tf')): [basestring]})
    #
    #
    # Example


    _data.tf:
       - terraform
       - data
    _provider.tf:
       - provider
    _variables.tf:
       - variable
    compute.tf:
       - azurerm_app_service
       - azurerm_app_service_plan
       - azurerm_virtual_machine
       - aws_instance
