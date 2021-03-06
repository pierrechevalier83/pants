# Copyright 2017 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from pants.goal.task_registrar import TaskRegistrar as task

from pants.contrib.errorprone.tasks.errorprone import ErrorProne


def register_goals():
  task(name='errorprone', action=ErrorProne).install('compile')
