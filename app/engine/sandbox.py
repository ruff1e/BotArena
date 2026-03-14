# app/engine/sandbox.py
# same as test_tictactoe.py
import docker
import tempfile
import os
import json


# Maps each supported language to the Docker image,
# the filename to write the bot code to and the command to run it.
LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.12-alpine",
        "filename": "main.py",
        "command": "python /code/main.py",
    },
    "javascript": {
        "image": "node:20-alpine",
        "filename": "main.js",
        "command": "node /code/main.js",
    },
}


def get_bot_move(language: str, code: str, state_dict: dict, timeout_seconds: int = 3) -> dict:
    #   1. Writes the bot code to a temp directory
    #   2. Writes the game state as a JSON file in the same temp directory
    #   3. Starts a Docker container that runs the bot with the state piped into stdin
    #   4. Waits for the container to finish (with a timeout)
    #   5. Reads the bot's output from the container logs
    #   6. Parses and returns the move
    #   7. Always cleans up the container and temp directory

    config = LANGUAGE_CONFIG.get(language)
    if config is None:
        raise ValueError(f"Unsupported language: {language}")

    # Create a temp directory on the host.
    # Both the bot code and the input file will live here.
    # This directory gets mounted into the container at /code (read-only).
    temp_dir = tempfile.mkdtemp()

    os.chmod(temp_dir, 0o755)

    try:
        # Write the bot's source code to a file.
        code_path = os.path.join(temp_dir, config["filename"])
        with open(code_path, "w") as f:
            f.write(code)
            os.chmod(code_path, 0o644)

        # Write the game state as JSON to input.json.
        # The container command will redirect this file into the bot's stdin,
        # so when the bot calls input() or sys.stdin.read(), it reads this.
        input_path = os.path.join(temp_dir, "input.json")
        with open(input_path, "w") as f:
            json.dump(state_dict, f)
            os.chmod(input_path, 0o644)

        # Use sh -c to redirect input.json into the bot's stdin.
        command = f'sh -c "{config["command"]} < /code/input.json"'

        client = docker.from_env()

        # Pull image if not available locally.
        try:
            client.images.get(config["image"])
        except docker.errors.ImageNotFound:
            print(f"[sandbox] Pulling image {config['image']}...")
            client.images.pull(config["image"])

        # Start the container in detached mode with a timeout and read its logs after it finishes.
        container = client.containers.run(
            image=config["image"],
            command=command,

            # Mount the temp dir as read-only at /code inside the container.
            # The bot can read its own code and input.json but cannot write anything.
            volumes={temp_dir: {"bind": "/code", "mode": "ro"}},

            # --- Security restrictions ---
            network_disabled=True,   # no internet access
            mem_limit="64m",         # max 64MB memory
            cpu_period=100000,
            cpu_quota=25000,         # max 25% of one CPU core
            pids_limit=50,           # prevents fork bombs
            cap_drop=["ALL"],        # drop all Linux capabilities
            security_opt=["no-new-privileges"],

            detach=True,
        )

        try:
            # Wait for the container to finish, with a hard timeout.
            # If the bot runs an infinite loop, this raises an exception
            # after timeout_seconds and after disqualifying the bot.
            container.wait(timeout=timeout_seconds)
        except Exception:
            raise TimeoutError(
                f"Bot did not respond within {timeout_seconds} seconds"
            )

        # Read only stdout (not stderr) from the container logs.
        # The bot must print exactly one line of JSON to stdout.
        output = container.logs(stdout=True, stderr=False).decode("utf-8").strip()

        if not output:
            # Get stderr to help debug what went wrong
            err = container.logs(stdout=False, stderr=True).decode("utf-8").strip()
            raise ValueError(f"Bot produced no output. stderr: {err}")

        try:
            move = json.loads(output)
        except json.JSONDecodeError:
            raise ValueError(f"Bot returned invalid JSON: {output}")

        return move

    finally:
        # Always clean up
        try:
            container.remove(force=True)
        except Exception:
            pass

        try:
            for filename in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, filename))
            os.rmdir(temp_dir)
        except Exception:
            pass