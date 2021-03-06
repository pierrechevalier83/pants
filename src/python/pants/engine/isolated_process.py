# Copyright 2016 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union

from pants.engine.fs import EMPTY_DIRECTORY_DIGEST, Digest
from pants.engine.platform import PlatformConstraint
from pants.engine.rules import RootRule, rule
from pants.util.meta import frozen_after_init


logger = logging.getLogger(__name__)

_default_timeout_seconds = 15 * 60


@dataclass(frozen=True)
class ProductDescription:
  value: str


@frozen_after_init
@dataclass(unsafe_hash=True)
class ExecuteProcessRequest:
  """Request for execution with args and snapshots to extract."""

  # TODO: add a method to hack together a `process_executor` invocation command line which
  # reproduces this process execution request to make debugging remote executions effortless!
  argv: Tuple[str, ...]
  input_files: Digest
  description: str
  env: Tuple[str, ...]
  output_files: Tuple[str, ...]
  output_directories: Tuple[str, ...]
  timeout_seconds: Union[int, float]
  unsafe_local_only_files_because_we_favor_speed_over_correctness_for_this_rule: Digest
  jdk_home: Optional[str]
  is_nailgunnable: bool

  def __init__(
    self,
    argv: Tuple[str, ...],
    *,
    input_files: Digest,
    description: str,
    env: Optional[Dict[str, str]] = None,
    output_files: Optional[Tuple[str, ...]] = None,
    output_directories: Optional[Tuple[str, ...]] = None,
    timeout_seconds: Union[int, float] = _default_timeout_seconds,
    unsafe_local_only_files_because_we_favor_speed_over_correctness_for_this_rule: Digest = EMPTY_DIRECTORY_DIGEST,
    jdk_home: Optional[str] = None,
    is_nailgunnable: bool = False,
  ) -> None:
    self.argv = argv
    self.input_files = input_files
    self.description = description
    self.env = tuple(item for pair in env.items() for item in pair) if env else ()
    self.output_files = output_files or ()
    self.output_directories = output_directories or ()
    self.timeout_seconds = timeout_seconds
    self.unsafe_local_only_files_because_we_favor_speed_over_correctness_for_this_rule = unsafe_local_only_files_because_we_favor_speed_over_correctness_for_this_rule
    self.jdk_home = jdk_home
    self.is_nailgunnable = is_nailgunnable


@frozen_after_init
@dataclass(unsafe_hash=True)
class MultiPlatformExecuteProcessRequest:
  # args collects a set of tuples representing platform constraints mapped to a req,
  # just like a dict constructor can.
  platform_constraints: Tuple[str, ...]
  execute_process_requests: Tuple[ExecuteProcessRequest, ...]

  def __init__(
    self, request_dict: Dict[Tuple[PlatformConstraint, PlatformConstraint], ExecuteProcessRequest]
  ) -> None:
    if len(request_dict) == 0:
      raise ValueError("At least one platform constrained ExecuteProcessRequest must be passed.")
    validated_constraints = tuple(
      constraint.value
      for pair in request_dict.keys() for constraint in pair
      if PlatformConstraint(constraint.value)
    )
    if len({req.description for req in request_dict.values()}) != 1:
      raise ValueError(f"The `description` of all execute_process_requests in a {self.__name__} must be identical.")

    self.platform_constraints = validated_constraints
    self.execute_process_requests = tuple(request_dict.values())

  @property
  def product_description(self):
    # we can safely extract the first description because we guarantee that at
    # least one request exists and that all of their descriptions are the same
    # in __new__
    return ProductDescription(self.execute_process_requests[0].description)


@dataclass(frozen=True)
class ExecuteProcessResult:
  """Result of successfully executing a process.

  Requesting one of these will raise an exception if the exit code is non-zero."""
  stdout: bytes
  stderr: bytes
  output_directory_digest: Digest


@dataclass(frozen=True)
class FallibleExecuteProcessResult:
  """Result of executing a process.

  Requesting one of these will not raise an exception if the exit code is non-zero."""
  stdout: bytes
  stderr: bytes
  exit_code: int
  output_directory_digest: Digest


class ProcessExecutionFailure(Exception):
  """Used to denote that a process exited, but was unsuccessful in some way.

  For example, exiting with a non-zero code.
  """

  MSG_FMT = """process '{desc}' failed with exit code {code}.
stdout:
{stdout}
stderr:
{stderr}
"""

  def __init__(self, exit_code, stdout, stderr, process_description):
    # These are intentionally "public" members.
    self.exit_code = exit_code
    self.stdout = stdout
    self.stderr = stderr

    msg = self.MSG_FMT.format(
      desc=process_description,
      code=exit_code,
      stdout=stdout.decode(),
      stderr=stderr.decode()
    )

    super().__init__(msg)


@rule
def get_multi_platform_request_description(
  req: MultiPlatformExecuteProcessRequest
) -> ProductDescription:
  return req.product_description


@rule
def upcast_execute_process_request(
  req: ExecuteProcessRequest
) -> MultiPlatformExecuteProcessRequest:
  """This rule allows an ExecuteProcessRequest to be run as a
  platform compatible MultiPlatformExecuteProcessRequest.
  """
  return MultiPlatformExecuteProcessRequest(
    {(PlatformConstraint.none, PlatformConstraint.none): req}
  )


@rule
def fallible_to_exec_result_or_raise(
  fallible_result: FallibleExecuteProcessResult, description: ProductDescription
) -> ExecuteProcessResult:
  """Converts a FallibleExecuteProcessResult to a ExecuteProcessResult or raises an error."""

  if fallible_result.exit_code == 0:
    return ExecuteProcessResult(
      fallible_result.stdout,
      fallible_result.stderr,
      fallible_result.output_directory_digest
    )
  else:
    raise ProcessExecutionFailure(
      fallible_result.exit_code,
      fallible_result.stdout,
      fallible_result.stderr,
      description.value
    )


def create_process_rules():
  """Creates rules that consume the intrinsic filesystem types."""
  return [
    RootRule(ExecuteProcessRequest),
    RootRule(MultiPlatformExecuteProcessRequest),
    upcast_execute_process_request,
    fallible_to_exec_result_or_raise,
    get_multi_platform_request_description,
  ]
