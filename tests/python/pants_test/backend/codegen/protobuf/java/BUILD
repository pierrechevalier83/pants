# Copyright 2016 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_tests(
  sources = globs('*.py', exclude=[globs('*_integration.py')]),
  dependencies = [
    'src/python/pants/backend/codegen/protobuf/java',
    'src/python/pants/java/jar',
    'src/python/pants/backend/jvm:plugin',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/build_graph',
    'tests/python/pants_test:test_base',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:task_test_base',
  ]
)


python_tests(
  name = 'integration',
  sources = globs('*_integration.py'),
  dependencies = [
    'tests/python/pants_test:int-test',
    'examples/src/java/org/pantsbuild/example:protobuf_directory',
    'testprojects/src/java/org/pantsbuild/testproject:proto-ordering_directory',
    'testprojects/src/protobuf/org/pantsbuild/testproject:import_from_buildroot_directory',
  ],
  tags = {'integration'},
  timeout = 240,
)
