import logging
import subprocess

from twitter_statuses import TwitterStatuses

log = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, *, config):
        self._config = config
        self._tasks = {}

    def load_tasks(self, *, load_function, config_section, printer):
        for task_name in self._config[config_section]:
            if not self._config.has_section(task_name):
                log.warning(
                    "Task [%s] in section [%s] has no configuration, skipping it",
                    task_name,
                    config_section,
                )
                continue

            task_def = self._make_task(task_name, self._config[task_name], printer)
            if task_def:
                load_function(task=task_def)

    def _make_task(self, task_name, config, printer):
        # Return already-constructed task if available.
        if task_name in self._tasks:
            return self._tasks[task_name]

        # Otherwise, construct and save a new task.
        task_type = config.get("task_type")
        if task_type == "script":
            task_def = self._make_task_script(config)
        elif task_type == "twitter":
            task_def = self._make_task_twitter(config, printer)
        else:
            log.warning("Unknown task type [%s], skipping it", task_type)
            task_def = None

        self._tasks[task_name] = task_def

        return self._tasks[task_name]

    def _make_task_script(self, config):
        command = config.get("command")

        def run_command():
            subprocess.call([command])

        return run_command

    def _make_task_twitter(self, config, printer):
        consumer_key = config.get("consumer_key")
        consumer_secret = config.get("consumer_secret")
        query_string = config.get("query_string")

        twitter = TwitterStatuses(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            query_string=query_string,
            printer=printer,
        )

        return twitter.update_and_print
