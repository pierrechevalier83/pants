# Copyright 2019 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import re
import subprocess
import unittest
from contextlib import contextmanager
from typing import List

from pants.util.collections import assert_single_element
from pants.util.contextutil import http_server, temporary_dir
from pants.util.process_handler import SubprocessProcessHandler
from pants.util.reporting_util import (find_child_processes_that_send_spans, wait_spans_to_be_sent,
                                       zipkin_handler)
from pants_test.pants_run_integration_test import PantsRunIntegrationTest


class TestReportingRemoteIntegration(PantsRunIntegrationTest, unittest.TestCase):
  @contextmanager
  def run_mock_server(self, bin_name: str, arguments: List[str]):
    """
    Build and run a Rust mock server binary.
    Mainly used for remoting integration tests.
    It assumes that the server will print a line like `localhost:99999` to indicate its port.
    :param bin_name: The name of the binary that you want to run. It must be in the main engine's workspace.
    :param arguments: Passthrough arguments to pass to the binary.
    """
    args = ["./" + bin_name]
    if len(arguments) > 0:
      args = args + arguments
    process = subprocess.Popen(args, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    try:
      port = None
      while port is None:
        line = process.stdout.readline().decode("utf-8")
        print(f"{line}")
        match = re.search("at address:.*:([0-9]+)", line)
        if match is not None:
          port = int(match.group(1))
      yield port
    finally:
      SubprocessProcessHandler(process).communicate_teeing_stdout_and_stderr(b"\n")

  @contextmanager
  def run_cas_server(self):
    with self.run_mock_server("local_cas", []) as port:
      yield port

  @contextmanager
  def run_execution_server(self):
    # These are the output paths that the cloc command produces
    with self.run_mock_server("local_execution_server", ["--output_paths", "report", "ignored"]) as port:
      yield port

  def test_zipkin_reporter_for_remote_execution_with_v2_engine(self):
    ZipkinHandler = zipkin_handler()
    with self.run_cas_server() as cas_port, self.run_execution_server() as execution_port, http_server(ZipkinHandler) as zipkin_port, temporary_dir() as store_dir:
      zipkin_endpoint = f"http://localhost:{zipkin_port}"
      command = [
        'cloc',
        'src/python/pants:version',
        '-ldebug',
        '--process-execution-speculation-strategy=none',
        '--reporting-zipkin-trace-v2',
        f'--reporting-zipkin-endpoint={zipkin_endpoint}',
        '--remote-execution',
        f'--remote-execution-server=localhost:{execution_port}',
        f'--remote-store-server=localhost:{cas_port}',
        '--cache-cloc-ignore',
        f'--local-store-dir={store_dir}'
      ]

      pants_run = self.run_pants(command, extra_env={"RUST_BACKTRACE": "FULL"})
      self.assert_success(pants_run)

      child_processes = find_child_processes_that_send_spans(pants_run.stderr_data)
      self.assertTrue(child_processes)

      wait_spans_to_be_sent(child_processes)

      trace = assert_single_element(ZipkinHandler.traces.values())

    remote_list_missing_digests = "list_missing_digests"
    self.assertTrue(any(remote_list_missing_digests in span['name'] for span in trace),
      "There is no span that contains '{}' in its name.\nCommand: {}\n The trace:{}".format(
          remote_list_missing_digests, command, trace
      ))

    remote_store_bytes = "store_bytes"
    self.assertTrue(any(remote_store_bytes in span['name'] for span in trace),
      "There is no span that contains '{}' in its name. The trace:{}".format(
      remote_store_bytes, trace
      ))
