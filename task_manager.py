import logging
import subprocess

from PIL import Image

from twitter_statuses import TwitterStatuses

log = logging.getLogger(__name__)


class TaskManager:
    _TASK_PREFIX = "task_"

    _TASK_TYPE_SCRIPT = "script"
    _TASK_TYPE_SHUTDOWN = "shutdown"
    _TASK_TYPE_TWITTER = "twitter"

    def __init__(self):
        # A cache to avoid reloading the same tasks.
        self._tasks = {}

        # List of tasks to run for each action type.
        self._daily_tasks = []
        self._hold_tasks = []
        self._interval_tasks = []
        self._tap_tasks = []

    def run_daily_tasks(self):
        log.debug("Executing [%s] daily tasks", len(self._daily_tasks))
        for task in self._daily_tasks:
            task()

    def run_hold_tasks(self):
        log.debug("Executing [%s] hold tasks", len(self._hold_tasks))
        for task in self._hold_tasks:
            task()

    def run_interval_tasks(self):
        log.debug("Executing [%s] interval tasks", len(self._interval_tasks))
        for task in self._interval_tasks:
            task()

    def run_tap_tasks(self):
        log.debug("Executing [%s] tap tasks", len(self._tap_tasks))
        for task in self._tap_tasks:
            task()

    def load_daily_tasks(self, *, config, section, printer):
        tasks = self._load_tasks(config, section, printer)

        self._daily_tasks.extend(tasks)

    def load_hold_tasks(self, *, config, section, printer):
        tasks = self._load_tasks(config, section, printer)

        self._hold_tasks.extend(tasks)

    def load_interval_tasks(self, *, config, section, printer):
        tasks = self._load_tasks(config, section, printer)

        self._interval_tasks.extend(tasks)

    def load_tap_tasks(self, *, config, section, printer):
        tasks = self._load_tasks(config, section, printer)

        self._tap_tasks.extend(tasks)

    def _load_tasks(self, config, section, printer):
        tasks = []
        for task_name in config[section]:
            task_section = "{}{}".format(self._TASK_PREFIX, task_name)
            if not config.has_section(task_section):
                log.warning(
                    "Task [%s] in section [%s] has no configuration, skipping it",
                    task_name,
                    section,
                )
                continue

            task_def = self._make_task(task_name, config[task_section], printer)
            if task_def:
                tasks.append(task_def)

        return tasks

    def _make_task(self, task_name, config, printer):
        # Return already-constructed task if available.
        if task_name in self._tasks:
            return self._tasks[task_name]

        # Otherwise, construct and save a new task.
        task_type = config.get("task_type")
        if task_type == "script":
            task_def = self._make_task_script(config)
        elif task_type == "shutdown":
            task_def = self._make_task_shutdown(config, printer)
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

    def _make_task_shutdown(self, config, printer):
        image_filepath = config.get("image")

        def printer_shutdown():
            if image_filepath:
                printer.printImage(Image.open(image_filepath), True)
                printer.feed(3)

            subprocess.call("sync")
            subprocess.call(["sudo", "shutdown", "-h", "now"])

        return printer_shutdown
