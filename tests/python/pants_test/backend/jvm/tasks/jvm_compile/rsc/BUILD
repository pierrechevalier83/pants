# Copyright 2018 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_library(
  name='rsc_compile_integration_base',
  sources=['rsc_compile_integration_base.py'],
  dependencies=[
    'src/python/pants/util:contextutil',
    'tests/python/pants_test/backend/jvm/tasks/jvm_compile:base_compile_integration_test',
    'tests/python/pants_test:test_base',
  ],
)

python_tests(
  name='rsc_compile_integration',
  sources=['test_rsc_compile_integration.py'],
  dependencies=[
    ':rsc_compile_integration_base',
    'contrib/node:examples_directory',
    'examples/src/scala/org/pantsbuild/example:hello_directory',
    'testprojects/src/scala/org/pantsbuild/testproject:javadepsonscalatransitive_directory',
    'testprojects/src/scala/org/pantsbuild/testproject:javasources_directory',
    'testprojects/src/scala/org/pantsbuild/testproject:mutual_directory',
  ],
  timeout = 600,
  tags = {'integration'},
)

python_tests(
  name='rsc_compile_integration_youtline',
  sources=['test_rsc_compile_integration_youtline.py'],
  dependencies=[
    ':rsc_compile_integration_base',
    'examples/src/scala/org/pantsbuild/example:hello_directory',
    'testprojects/src/scala/org/pantsbuild/testproject:mutual_directory',
    'testprojects/src/scala/org/pantsbuild/testproject:public_inference_directory',
  ],
  timeout = 600,
  tags = {'integration'},
)


python_tests(
  name = 'rsc_compile',
  sources = ['test_rsc_compile.py'],
  dependencies = [
    'src/python/pants/backend/jvm/tasks/jvm_compile',
    'src/python/pants/backend/jvm/tasks/jvm_compile/rsc',
    'src/python/pants/backend/jvm/tasks:classpath_products',
    'tests/python/pants_test/jvm:nailgun_task_test_base',
  ],
)
