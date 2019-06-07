// Copyright 2019 Pants project contributors (see CONTRIBUTORS.md).
// Licensed under the Apache License, Version 2.0 (see LICENSE).

#![deny(warnings)]
// Enable all clippy lints except for many of the pedantic ones. It's a shame this needs to be copied and pasted across crates, but there doesn't appear to be a way to include inner attributes from a common source.
#![deny(
  clippy::all,
  clippy::default_trait_access,
  clippy::expl_impl_clone_on_copy,
  clippy::if_not_else,
  clippy::needless_continue,
  clippy::single_match_else,
  clippy::unseparated_literal_suffix,
  clippy::used_underscore_binding
)]
// It is often more clear to show that nothing is being moved.
#![allow(clippy::match_ref_pats)]
// Subjective style.
#![allow(
  clippy::len_without_is_empty,
  clippy::redundant_field_names,
  clippy::too_many_arguments
)]
// Default isn't as big a deal as people seem to think it is.
#![allow(clippy::new_without_default, clippy::new_ret_no_self)]
// Arc<Mutex> can be more clear than needing to grok Orderings:
#![allow(clippy::mutex_atomic)]

use parking_lot::Mutex;
use rand::thread_rng;
use rand::Rng;
use futures::task_local;

pub struct WorkUnit {
  pub name: String,
  pub start_timestamp: f64,
  pub end_timestamp: f64,
  pub span_id: String,
  pub parent_id: Option<String>,
}

pub trait WorkUnitStore: Send + Sync {
  fn get_workunits(&self) -> &Mutex<Vec<WorkUnit>>;
  fn add_workunit(&self, workunit: WorkUnit);
}

pub struct SafeWorkUnitStore {
  pub workunits: Mutex<Vec<WorkUnit>>,
}

impl SafeWorkUnitStore {
  pub fn new() -> SafeWorkUnitStore {
    SafeWorkUnitStore {
      workunits: Mutex::new(Vec::new()),
    }
  }
}

impl WorkUnitStore for SafeWorkUnitStore {
  fn get_workunits(&self) -> &Mutex<Vec<WorkUnit>> {
    &self.workunits
  }

  fn add_workunit(&self, workunit: WorkUnit) {
    self.workunits.lock().push(workunit);
  }
}

pub fn generate_random_64bit_string() -> String {
    let mut rng = thread_rng();
    let random_u64: u64 = rng.gen();
    format!("{:16.x}", random_u64)
}

task_local! {
  static TASK_PARENT_ID: Mutex<Option<String>> = Mutex::new(None)
}

pub fn set_parent_id(parent_id: String) {
  TASK_PARENT_ID.with(|task_parent_id| {
    *task_parent_id.lock() = Some(parent_id);
  })
}

pub fn get_parent_id() -> Option<String> {
  TASK_PARENT_ID.with(|task_parent_id| {
    let task_parent_id = task_parent_id.lock();
    (*task_parent_id).clone()
  })
}
