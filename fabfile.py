# pylint: skip-file
"""
Application development tasks
"""
# pylint: skip-file
from fabrips import all_tasks

# from fabrips.helpers import Hooks
from invoke import Collection, Context, Result, task

namespace = all_tasks()

clproc = Collection("clproc")
namespace.add_collection(clproc)
