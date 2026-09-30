"""Bootstrap and verify the VLE 6 Jenkins host entirely from AWS CodeBuild."""

import ast
import base64
import subprocess
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


ROOT = Path(__file__).resolve().parents[1]
source = ast.parse(ROOT.joinpath("ansible/bootstrap_ssm.py").read_text())
script_node = next(
    node.value
    for node in source.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "script" for target in node.targets)
)
script = ast.literal_eval(script_node)
encoded_script = base64.b64encode(script.encode()).decode("ascii")
instance_id = subprocess.check_output(
    ["terraform", "output", "-raw", "instance_id"],
    cwd=ROOT / "terraform",
    text=True,
).strip()
ssm = boto3.client("ssm", region_name="us-east-1")


def run_ssm(commands, comment, timeout=1800):
    result = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands, "executionTimeout": [str(timeout)]},
        Comment=comment,
        TimeoutSeconds=timeout,
    )
    command_id = result["Command"]["CommandId"]
    print(f"SSM command {command_id}: {comment}", flush=True)

    for _ in range(timeout // 5 + 12):
        time.sleep(5)
        try:
            invocation = ssm.get_command_invocation(
                CommandId=command_id, InstanceId=instance_id
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvocationDoesNotExist":
                continue
            raise
        status = invocation["Status"]
        if status in {"Success", "Failed", "Cancelled", "TimedOut", "Cancelling"}:
            print(invocation.get("StandardOutputContent", ""), flush=True)
            if invocation.get("StandardErrorContent"):
                print(invocation["StandardErrorContent"], flush=True)
            if status != "Success":
                raise SystemExit(f"SSM command {command_id} ended with {status}")
            return command_id
    raise SystemExit(f"SSM command {command_id} timed out")


run_ssm(
    [f"printf '%s' '{encoded_script}' | base64 -d | bash"],
    "VLE 6 Jenkins and Maven cloud bootstrap",
)
run_ssm(
    [
        "set -eu",
        "systemctl is-active jenkins",
        "mvn -version | head -4",
        "curl --globoff --fail --silent --show-error 'http://127.0.0.1:8080/job/vle6-maven-ci/lastBuild/api/json?tree=number,result,artifacts[fileName]' | python3 -c 'import json,sys; b=json.load(sys.stdin); print(b); assert b[\"result\"] == \"SUCCESS\"; assert any(a[\"fileName\"].endswith(\".jar\") for a in b[\"artifacts\"])'",
    ],
    "VLE 6 Jenkins Maven cloud verification",
    timeout=300,
)
print("VLE 6: Terraform apply, Jenkins bootstrap, and Maven CI verification completed in AWS.")
