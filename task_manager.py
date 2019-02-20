import twitter_statuses
import subprocess


class TaskManager:
    def __init__(self):
        self._tasks = {}

    def load_tasks(self, load_function, config_section):
        for task_name in config.section(config_section):
            if not config.has_section(task_name):
                log.warning(
                    "Task [%s] in section [%s] has no configuration, skipping it",
                    task_name,
                    config_section,
                )
                continue

            task_def = self._make_task(task_name, config[task_name])
            if task_def:
                load_function(task_def)

    def _make_task(self, task_name, task_config):
        # Return already-constructed task if available.
        if task_name in self._tasks:
            return self._tasks[task_name]

        # Otherwise, construct and save a new task.
        task_type = task_config.get("task_type")
        if task_type == "script":
            task_def = self._make_task_script(config)
        elif task_type == "twitter":
            task_def = self._make_task_twitter(config)
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

    def _make_task_twitter(self, config):
        consumer_key = config.get("consumer_key")
        consumer_secret = config.get("consumer_secret")
        query_string = config.get("query_string")

        twitter = TwitterStatuses(
            consumer_key=args.consumer_key,
            consumer_secret=args.consumer_secret,
            query_string=args.query_string,
            printer=printer,
        )

        return twitter.update_and_print
